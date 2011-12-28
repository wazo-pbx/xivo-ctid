#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2011  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cjson
import datetime
import logging
import os
import Queue
import select
import signal
import socket
import ssl
import sys
import time
import threading
import urllib

from logging.handlers import RotatingFileHandler

from xivo import daemonize

from xivo_cti import amiinterpret
from xivo_cti import cti_config
from xivo_cti import innerdata
from xivo_cti import interface_ami
from xivo_cti import interface_cti
from xivo_cti import interface_fagi
from xivo_cti import interface_info
from xivo_cti import interface_rcti
from xivo_cti import interface_webi
from xivo_cti import queue_logger
from xivo_cti.alarm import alarm
from xivo_cti.alarm import scheduler
from xivo_cti.client_connection import ClientConnection
from xivo_cti.dao.alchemy import dbconnection


class CTIServer:

    xivoversion = '1.2'
    revision = 'githash'
    xdname = 'XiVO CTI Server'

    def __init__(self):
        self.nreload = 0
        self.myami = {}
        self.mycti = {}
        self.safe = {}
        self.timeout_queue = None
        self.pipe_queued_threads = None
        self.scheduler = None
        self._config = None

    def _set_signal_handlers(self):
        signal.signal(signal.SIGINT, self.sighandler)
        signal.signal(signal.SIGTERM, self.sighandler)
        signal.signal(signal.SIGHUP, self.sighandler_reload)

    def _set_logger(self):
        logging.basicConfig(level=logging.INFO)
        global log
        log = logging.getLogger('main')
        try:
            logfilehandler = RotatingFileHandler(cti_config.LOGFILENAME)
            formatter = logging.Formatter(
                '%%(asctime)s %s[%%(process)d] (%%(levelname)s) (%%(name)s): %%(message)s'
                % cti_config.DAEMONNAME)
            logfilehandler.setFormatter(formatter)
            root_logger = logging.getLogger()
            root_logger.addHandler(logfilehandler)
            if cti_config.DEBUG_MODE:
                root_logger.setLevel(logging.DEBUG)
        except Exception:
            log.exception('logfilehandler')

    def _daemonize(self):
        if not cti_config.DEBUG_MODE:
            daemonize.daemonize()
        daemonize.lock_pidfile_or_die(cti_config.PIDFILE)

    def _setup_zones_and_alarms(self, persister, alarm):
        try:
            system_zone = alarm.get_system_zone()
        except Exception as e:
            log.warning('Error while getting system zone: %s', e)
            system_zone = None
        self.alarm_mgr = alarm.AlarmClockManager(
            self.scheduler, persister, self._alarm_callback, system_zone)
        self.global_zone = None

    def setup(self):
        self._config = cti_config.Config.get_instance()
        self._set_logger()
        self._daemonize()
        self.timeout_queue = Queue.Queue()
        self.scheduler = scheduler.Scheduler()
        persister = alarm.JSONPersister(cti_config.ALARM_DIRECTORY)
        persister = alarm.MaxDeltaPersisterDecorator(datetime.timedelta(hours=2),
                                                     persister)
        self._setup_zones_and_alarms(persister, alarm)
        self._set_signal_handlers()

    def run(self):
        while True:
            try:
                self.main_loop()
            except Exception:
                log.exception('main loop has crashed ... retrying in 5 seconds ...')
                time.sleep(5)

    def _alarm_callback(self, data):
        # WARNING: we are in the scheduler thread
        userid = data['userid']
        os.write(self.pipe_queued_threads[1], 'alarmclk:%s\n' % userid)

    ## \brief Handler for catching signals (in the main thread)
    # \param signum signal number
    # \param frame frame
    def sighandler(self, signum, frame):
        log.warning('(sighandler) signal %s lineno %s (atq = %s) received : quits'
                    % (signum, frame.f_lineno, self.askedtoquit))
        self.scheduler.shutdown()
        for t in filter(lambda x: x.getName() != 'MainThread', threading.enumerate()):
            print '--- living thread <%s>' % (t.getName())
            t._Thread__stop()
        self.askedtoquit = True

    ## \brief Handler for catching signals (in the main thread)
    # \param signum signal number
    # \param frame frame
    def sighandler_reload(self, signum, frame):
        log.warning('(sighandler_reload) signal %s lineno %s (atq = %s) received : reloads'
                    % (signum, frame.f_lineno, self.askedtoquit))
        self.askedtoquit = False

    def manage_tcp_connections(self, sel_i, msg, kind):
        """
        Dispatches the message's handling according to the connection's kind.
        """
        closemenow = False
        if not isinstance(kind, str):   # CTI, INFO, WEBI
            replies = kind.manage_connection(msg)
            for reply in replies:
                if reply:
                    if 'closemenow' in reply:
                        closemenow = reply.get('closemenow')
                    if 'message' in reply:
                        if reply.get('dest'):
                            self.send_to_cti_client(reply.get('dest'),
                                                    reply.get('message'))
                        else:
                            kind.reply(reply.get('message'))
                    elif 'warning' in reply:
                        kind.reply(reply.get('warning'))
        else:
            log.warning('unknown connection kind %s' % kind)
        return closemenow

    def find_matching_ipbxid(self, ipaddress):
        found_ipbxid = None
        for ipbxid, ipbxconfig in self._config.getconfig('ipbxes').iteritems():
            if 'ipbx_connection' in ipbxconfig:
                connparams = ipbxconfig.get('ipbx_connection')
                cfg_ip_address = connparams.get('ipaddress')
                if ipaddress == socket.gethostbyname(cfg_ip_address):
                    found_ipbxid = ipbxid
                    break
        return found_ipbxid

    def checkqueue(self):
        log.info('entering checkqueue')
        ncount = 0
        while self.timeout_queue.qsize() > 0:
            ncount += 1
            (toload,) = self.timeout_queue.get()
            action = toload.get('action')
            if action == 'ipbxup':
                sockparams = toload.get('properties').get('sockparams')
                data = toload.get('properties').get('data')
                if data.startswith('asterisk'):
                    got_ip_address = sockparams[0]
                    ipbxid = self.find_matching_ipbxid(got_ip_address)
                    if ipbxid:
                        if self.myami[ipbxid].connected():
                            log.info('do NOT attempt to reconnect to the AMI for %s' % ipbxid)
                        else:
                            log.info('attempt to reconnect to the AMI for %s' % ipbxid)
                            z = self.myami[ipbxid].connect()
                            if z:
                                self.fdlist_ami[z] = self.myami[ipbxid]
                    else:
                        log.warning('did not found a matching ipbxid for the address %s'
                                    % got_ip_address)
            elif action == 'xivoremote':
                for _, v in self.mycti.iteritems():
                    if not v.connected():
                        z = v.connect()
                        if z:
                            self.fdlist_remote_cti[z] = v
            elif action == 'ctilogin':
                connc = toload.get('properties')
                connc.close()
                if connc in self.fdlist_established:
                    del self.fdlist_established[connc]
                else:
                    log.warning('could not remove connexion : already done ...')
            else:
                log.warning('checkqueue : unknown action received : %s' % action)
        return ncount

    def cb_timer(self, *args):
        try:
            tname = threading.currentThread()
            tname.setName('Thread-main')
            log.info('cb_timer (timer finished at %s) %s' % (time.asctime(), args))
            self.timeout_queue.put(args)
            os.write(self.pipe_queued_threads[1], 'main:\n')
        except Exception:
            log.exception('cb_timer %s' % args)

    def updates_period(self):
        return int(self._config.getconfig('main').get('updates_period', '3600'))

    def _init_db_connection_pool(self):
        # XXX we should probably close the db_connection_pool when main loop exit
        dbconnection.unregister_db_connection_pool()
        dbconnection.register_db_connection_pool(self._new_db_connection_pool())

    def _new_db_connection_pool(self):
        return dbconnection.DBConnectionPool(dbconnection.DBConnection)

    def _init_queue_stats(self):
        queue_stats_uri = self._config.getconfig('main')['asterisk_queuestat_db']
        queue_logger.queue_logger.init(queue_stats_uri)
        dbconnection.add_connection_as(queue_stats_uri, 'queue_stats')

    def main_loop(self):    # {
        self.askedtoquit = False

        self.time_start = time.localtime()
        log.info('# STARTING XiVO CTI Server %s (pid %d) / git:%s # (0/3) Starting (%d)'
                 % (self.xivoversion, os.getpid(), self.revision, self.nreload))
        self.nreload += 1

        # global default definitions
        self.update_userlist = {}
        self.lastrequest_time = {}

        self._init_db_connection_pool()

        self._config.set_ipwebs(cti_config.XIVOIP)
        if cti_config.XIVO_CONF_OVER:
            urldata = urllib.urlopen(cti_config.XIVO_CONF_OVER)
            payload = urldata.read()
            urldata.close()
            overconf = cjson.decode(payload)
            self._config.set_rcti_override_ipbxes(overconf)
        self._config.update()
        self._config.set_rcti_special_profile()

        self._init_queue_stats()

        xivoconf_general = self._config.getconfig('main')

        # loads the general configuration
        ctilog = xivoconf_general.get('ctilog_db_uri')
        socktimeout = float(xivoconf_general.get('sockettimeout', '2'))
        prefixfile = xivoconf_general.get('prefixfile')
        parting_ipbxid_context = xivoconf_general.get('parting_ipbxid_context')

        socket.setdefaulttimeout(socktimeout)

        if not self.pipe_queued_threads:
            self.pipe_queued_threads = os.pipe()

        # sockets management
        self.fdlist_established = {}
        self.fdlist_listen_cti = {}
        self.fdlist_udp_cti = {}
        self.fdlist_ami = {}
        self.fdlist_remote_cti = {}

        log.info("the monitored ipbx's is/are : %s" % self._config.getconfig('ipbxes').keys())

        for ipbxid, ipbxconfig in self._config.getconfig('ipbxes').iteritems():
            if 'ipbx_connection' in ipbxconfig:
                self.myipbxid = ipbxid
                break
        else:
            self.myipbxid = None

        log.info('# STARTING %s # (1/3) Local AMI socket connection' % self.xdname)
        if self.myipbxid:
            ipbxconfig = self._config.getconfig('ipbxes').get(self.myipbxid)
            # interface : safe deposit
            self.safe[self.myipbxid] = innerdata.Safe(self, self.myipbxid,
                                                      ipbxconfig.get('urllists'))
            self.safe[self.myipbxid].update_directories()
            # interface : AMI
            self.myami[self.myipbxid] = interface_ami.AMI(self, self.myipbxid)
            self.commandclass = amiinterpret.AMI_1_8(self, self.myipbxid)

            log.info('# STARTING %s / git:%s / %d'
                     % (self.xdname, self.safe[self.myipbxid].version(), self.nreload))

            self.safe[self.myipbxid].set_ctilog(ctilog)
            self.safe[self.myipbxid].read_internatprefixes(prefixfile)
            self.safe[self.myipbxid].set_partings(parting_ipbxid_context)

            self.update_userlist[self.myipbxid] = []
            self.lastrequest_time[self.myipbxid] = time.time()

            z = self.myami[self.myipbxid].connect()
            if z:
                self.fdlist_ami[z] = self.myami[self.myipbxid]

            try:
                self.safe[self.myipbxid].update_config_list_all()
            except Exception:
                log.exception('%s : commandclass.updates()' % self.myipbxid)

        log.info('# STARTING %s # (2/3) Remote CTI connections' % self.xdname)
        for ipbxid, ipbxconfig in self._config.getconfig('ipbxes').iteritems():
            if ipbxid != self.myipbxid:
                log.info('other ipbx to connect to : %s' % ipbxid)
                try:
                    self.safe[ipbxid] = innerdata.Safe(self, ipbxid)
                    self.mycti[ipbxid] = interface_rcti.RCTI(self, ipbxid,
                                                             ipbxconfig.get('cti_connection'))
                except:
                    log.exception('remote CTI connection to %s' % ipbxid)

                self.update_userlist[ipbxid] = []
                self.lastrequest_time[ipbxid] = time.time()

                z = self.mycti[ipbxid].connect()
                if z:
                    self.fdlist_remote_cti[z] = self.mycti[ipbxid]
        # }

        log.info('# STARTING %s # (3/3) listening sockets (CTI, WEBI, FAGI, INFO)' % self.xdname)
        # opens the listening socket for incoming (CTI, WEBI, FAGI, INFO) connections
        for kind, bind_and_port in xivoconf_general.get('incoming_tcp', {}).iteritems():
            allow_kind = True
            if len(bind_and_port) > 2:
                allow_kind = bind_and_port[2]
            if not allow_kind:
                log.warning('%s kind listening socket has been explicitly disabled' % kind)
                continue
            try:
                (bind, port) = bind_and_port[:2]
                trueport = int(port) + cti_config.PORTDELTA
                gai = socket.getaddrinfo(bind, trueport, 0, socket.SOCK_STREAM, socket.SOL_TCP)
                if not gai:
                    continue
                (afinet, socktype, proto, dummy, bindtuple) = gai[0]
                UIsock = socket.socket(afinet, socktype)
                UIsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                UIsock.bind(bindtuple)
                UIsock.listen(10)
                self.fdlist_listen_cti[UIsock] = '%s:%s' % (kind, 1)
            except Exception:
                log.exception('tcp %s %d' % (bind, trueport))

        for kind, bind_and_port in xivoconf_general.get('incoming_udp', {}).iteritems():
            allow_kind = True
            if len(bind_and_port) > 2:
                allow_kind = bind_and_port[2]
            if not allow_kind:
                log.warning('%s kind listening socket has been explicitly disabled' % kind)
                continue
            try:
                (bind, port) = bind_and_port[:2]
                trueport = int(port) + cti_config.PORTDELTA
                gai = socket.getaddrinfo(bind, trueport, 0, socket.SOCK_DGRAM, socket.SOL_UDP)
                if not gai:
                    continue
                (afinet, socktype, proto, dummy, bindtuple) = gai[0]
                UIsock = socket.socket(afinet, socktype)
                UIsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                UIsock.bind(bindtuple)
                self.fdlist_udp_cti[UIsock] = '%s:%s' % (kind, 1)
            except Exception:
                log.exception('udp %s %d' % (bind, trueport))

        # Main select() loop - Receive messages
        if not self._config.getconfig():
            nsecs = 5
            log.info('waiting %d seconds in case a config would be available ...' % nsecs)
            try:
                time.sleep(nsecs)
                # select.select([], [], [], nsecs)
            except:
                sys.exit()
        else:
            # we call _schedule_alarms before starting the scheduler so that
            # alarms that have changed will be rescheduled before having a
            # chance to be fired
            self._schedule_alarms()
            self.scheduler.start()
            try:
                while not self.askedtoquit:
                    self.select_step()
            finally:
                self.scheduler.shutdown()

    def loop_over_cti_queue(self, innerdata):
        cti_queue = innerdata.events_cti
        queuesize = cti_queue.qsize()
        while cti_queue.qsize() > 0:
            it = cti_queue.get()
            for k in self.fdlist_established.itervalues():
                if not isinstance(k, str) and k.kind in ['CTI', 'CTIS']:
                    k.reply(it)
        return queuesize

    def get_connected(self, tomatch):
        clist = list()
        for k in self.fdlist_established.itervalues():
            if not isinstance(k, str) and k.kind in ['CTI', 'CTIS']:
                ipbxid = k.connection_details.get('ipbxid')
                userid = k.connection_details.get('userid')
                if self.safe.get(ipbxid).user_match(userid, tomatch):
                    clist.append(k)
        return clist

    def sendsheettolist(self, tsl, payload):
        for k in tsl:
            k.reply(payload)

    def loop_over_cti_queues(self):
        for ipbxid, innerdata in self.safe.iteritems():
            queuesize = self.loop_over_cti_queue(innerdata)

    def set_transfer_socket(self, faxobj, direction):
        for iconn, kind in self.fdlist_established.iteritems():
            if kind.kind in ['CTI', 'CTIS']:
                peername = '%s:%d' % iconn.getpeername()
                if peername == faxobj.socketref:
                    kind.set_as_transfer(direction, faxobj)
                    if direction == 's2c':
                        sendbuffer = ''
                        kind.reply(sendbuffer)
                    break

    def send_to_cti_client(self, who, what):
        (ipbxid, userid) = who.split('/')
        for k in self.fdlist_established.itervalues():
            if not isinstance(k, str) and k.kind in ['CTI', 'CTIS']:
                if ipbxid == self.myipbxid:
                    if k.connection_details.get('userid') == userid:
                        k.reply(what)
                else:
                    if k.connection_details.get('userid')[3:] == ipbxid:
                        k.reply(what)

    def _schedule_alarms(self):
        # Schedule new alarms/reschedule updated alarm
        global_zone = self._config.getconfig('ipbxes').get(self.myipbxid, {}).get('timezone')
        userlist = self.safe[self.myipbxid].xod_config['users']
        if global_zone != self.global_zone:
            log.info('Global zone changed to %s', global_zone)
            for userid, user in userlist.keeplist.iteritems():
                # ignore 'remote users'
                if not userid.startswith('cs:'):
                    alarmclock = user['alarmclock']
                    if alarmclock and not user['timezone']:
                        self.alarm_mgr.test_update_alarm_clock(int(userid), alarmclock, global_zone)
            self.global_zone = global_zone
        if userlist.alarm_clk_changes:
            for userid, (alarmclock, zone) in userlist.alarm_clk_changes.iteritems():
                log.info('Alarm clock changed for user %s', userid)
                if not zone:
                    zone = global_zone
                self.alarm_mgr.test_update_alarm_clock(int(userid), alarmclock, zone)
            userlist.alarm_clk_changes.clear()

    def select_step(self):
        self._schedule_alarms()

        try:
            fdtodel = []
            for cn in self.fdlist_established.keys():
                if isinstance(cn, ClientConnection):
                    if cn.isClosed and cn not in fdtodel:
                        fdtodel.append(cn)
                    if cn.toClose and not cn.need_sending():
                        cn.close()
                        if cn not in fdtodel:
                            fdtodel.append(cn)
            if fdtodel:
                log.warning('there are fd to delete : %s' % fdtodel)
                for cn in fdtodel:
                    del self.fdlist_established[cn]

            self.fdlist_full = list()
            self.fdlist_full.append(self.pipe_queued_threads[0])
            # put AMI fd's before FAGI ones in order to be properly synced
            self.fdlist_full.extend(self.fdlist_ami.keys())
            self.fdlist_full.extend(self.fdlist_listen_cti.keys())
            self.fdlist_full.extend(self.fdlist_udp_cti.keys())
            self.fdlist_full.extend(self.fdlist_established.keys())
            self.fdlist_full.extend(self.fdlist_remote_cti.keys())
            writefds = []
            for iconn, kind in self.fdlist_established.iteritems():
                if kind in ['CTI', 'CTIS'] and iconn.need_sending():
                    writefds.append(iconn)
            [sels_i, sels_o, sels_e] = select.select(self.fdlist_full, writefds, [],
                                                     self.updates_period())

        except Exception:
            log.exception('(select) probably Ctrl-C or daemon stop or daemon restart ...')
            log.warning('(select) self.askedtoquit=%s fdlist_full=%s'
                        % (self.askedtoquit, self.fdlist_full))
            log.warning('(select) current open TCP connections : (CTI, WEBI, FAGI, INFO) %s'
                        % self.fdlist_established)
            log.warning('(select) current open TCP connections : (AMI) %s'
                        % self.fdlist_ami.keys())
            log.warning('(select) current open TCP connections : (RCTI) %s'
                        % self.fdlist_remote_cti.keys())
            
            # we must close the scheduler early since scheduled jobs depends
            # on the AMI connection
            self.scheduler.shutdown()
            
            for s in self.fdlist_full:
                if s in self.fdlist_established:
                    if self.askedtoquit:
                        self.fdlist_established[s].disconnected('stop')
                    else:
                        self.fdlist_established[s].disconnected('reload')
                if not isinstance(s, int):
                    # the only one 'int' is the (read) pipe : no need to close/reopen it
                    s.close()

            if self.askedtoquit:
                # self.commandclass.reset('stop') # used to call __fill_ctilog__('daemon stop', mode)
                time_uptime = int(time.time() - time.mktime(self.time_start))
                log.info('# STOPPING XiVO CTI Server %s (pid %d) / git:%s # uptime %d s (since %s)'
                         % (self.xivoversion, os.getpid(), self.revision,
                            time_uptime, time.asctime(self.time_start)))
                for t in filter(lambda x: x.getName() != 'MainThread', threading.enumerate()):
                    print '--- (stop) killing thread <%s>' % t.getName()
                    t._Thread__stop()
                daemonize.unlock_pidfile(cti_config.PIDFILE)
                sys.exit(5)
            else:
                # self.commandclass.reset('reload')
                self.askedtoquit = True
                for t in filter(lambda x: x.getName() != 'MainThread', threading.enumerate()):
                    print '--- (reload) the thread <%s> remains' % t.getName()
                    # t._Thread__stop() # does not work in reload case (vs. stop case)
                return

        try:
            # connexions ready for sending(writing)
            if sels_o:
                log.warning('got some sels_o %s' % sels_o)
            for sel_o in sels_o:
                try:
                    sel_o.process_sending()
                except ClientConnection.CloseException, cexc:
                    if sel_o in self.fdlist_established:
                        kind = self.fdlist_established[sel_o]
                        log.info('TCP socket %s closed(sending %s) on %s'
                                 % (kind, cexc, sel_o.getpeername()))
                        kind.disconnected('end_sending')
                        sel_o.close()
                        del self.fdlist_established[sel_o]

            if sels_e:
                log.warning('got some sels_e %s' % sels_e)

            if sels_i:
                for sel_i in sels_i:
                    # these AMI connections are used in order to manage AMI commands and events
                    if sel_i in self.fdlist_ami.keys():
                        try:
                            amiint = self.fdlist_ami.get(sel_i)
                            ipbxid = amiint.ipbxid
                            buf = sel_i.recv(cti_config.BUFSIZE_LARGE)
                            if len(buf) == 0:
                                log.warning('AMI %s : CLOSING (%s)' % (ipbxid, time.asctime()))
                                del self.fdlist_ami[sel_i]
                                sel_i.close()
                                amiint.disconnect()
                            else:
                                try:
                                    amiint.handle_event(buf)
                                except Exception:
                                    log.exception('(handle_event) %s' % ipbxid)
                        except Exception:
                            log.exception('(amilist)')

                    elif sel_i in self.fdlist_remote_cti.keys():
                        try:
                            cticonn = self.fdlist_remote_cti.get(sel_i)
                            ipbxid = cticonn.ipbxid
                            buf = sel_i.recv(cti_config.BUFSIZE_LARGE)
                            if len(buf) == 0:
                                log.warning('RCTI %s : CLOSING' % ipbxid)
                                del self.fdlist_remote_cti[sel_i]
                                sel_i.close()
                                cticonn.disconnect()
                            else:
                                try:
                                    cticonn.handle_event(buf)
                                except Exception:
                                    log.exception('(handle_event) %s' % ipbxid)
                        except Exception:
                            log.exception('(remotecti)')

                    # } the UDP messages (ANNOUNCE) are catched here
                    elif sel_i in self.fdlist_udp_cti: # {
                        [kind, nmax] = self.fdlist_udp_cti[sel_i].split(':')
                        if kind == 'ANNOUNCE':
                            [data, sockparams] = sel_i.recvfrom(cti_config.BUFSIZE_LARGE)
                            log.info('UDP %s <%s> %s' % (kind, data.strip(), sockparams))
                            # scheduling AMI reconnection
                            k = threading.Timer(1, self.cb_timer,
                                                ({'action': 'ipbxup',
                                                  'properties': {'data': data,
                                                                 'sockparams': sockparams }},))
                            k.setName('Thread-ipbxup-%s' % data.strip())
                            k.start()
                        else:
                            log.warning('unknown kind %s received' % kind)

                    # } the new TCP connections (CTI, WEBI, FAGI, INFO) are catched here
                    elif sel_i in self.fdlist_listen_cti: # {
                        [kind, nmax] = self.fdlist_listen_cti[sel_i].split(':')
                        [connc, sockparams] = sel_i.accept()
                        ctiseparator = '\n'
                        log.info('TCP socket %s opened on %s:%d' % (kind,
                                                                    sockparams[0], sockparams[1]))

                        if kind == 'CTI':
                            connc = ClientConnection(connc, sockparams, ctiseparator)
                        elif kind == 'CTIS':
                            try:
                                connstream = ssl.wrap_socket(connc,
                                                             server_side = True,
                                                             certfile = self._config.getconfig('certfile'),
                                                             keyfile = self._config.getconfig('keyfile'),
                                                             ssl_version = cti_config.SSLPROTO)
                                connc = ClientConnection(connstream, sockparams, ctiseparator)
                            except ssl.SSLError:
                                log.exception('%s:%s:%d cert=%s key=%s)'
                                              % (kind, sockparams[0], sockparams[1],
                                                 self._config.getconfig('certfile'),
                                                 self._config.getconfig('keyfile')))
                                connc.close()
                                connc = None
                        # appending the opened socket to the ones watched
                        # connc.setblocking(0)
                        # connc.settimeout(2)
                        if connc:
                            if kind == 'INFO':
                                nc = interface_info.INFO(self)
                            elif kind == 'WEBI':
                                nc = interface_webi.WEBI(self)
                            elif kind in ['CTI', 'CTIS']:
                                nc = getattr(interface_cti, kind)(self)
                            elif kind == 'FAGI':
                                nc = interface_fagi.FAGI(self)

                            nc.connected(connc)
                            if kind in ['WEBI', 'FAGI', 'INFO']:
                                ipbxid = self.find_matching_ipbxid(sockparams[0])
                                ipbxid = self.myipbxid
                                if ipbxid:
                                    nc.set_ipbxid(ipbxid)
                                else:
                                    log.warning('(%s interface) did not find a matching ipbxid for %s'
                                                % (kind, sockparams[0]))

                            if kind in ['CTI', 'CTIS']:
                                logintimeout = int(self._config.getconfig('main').get('logintimeout', 5))
                                # logintimeout = 3600
                                nc.logintimer = threading.Timer(logintimeout, self.cb_timer,
                                                                ({'action': 'ctilogin',
                                                                  'properties': connc},))
                                nc.logintimer.start()
                            self.fdlist_established[connc] = nc
                        else:
                            log.warning('connc is not defined ...')

                    # } incoming TCP connections (CTI, WEBI, AGI, INFO)
                    elif sel_i in self.fdlist_established: # {
                        try: # {
                            kind = self.fdlist_established[sel_i]
                            requester = '%s:%d' % sel_i.getpeername()[:2]
                            closemenow = False
                            if isinstance(sel_i, ClientConnection):
                                try:
                                    lines = sel_i.readlines()
                                    for line in lines:
                                        if line:
                                            # XXX closemenow always take the latest value of the handled line, which
                                            #     might not be what we want (we want it to be True if it's been true
                                            #1    at least once)
                                            closemenow = self.manage_tcp_connections(sel_i, line, kind)
                                except ClientConnection.CloseException, cexc:
                                    kind.disconnected('end_receiving')
                                    # don't close since it has been done
                                    del self.fdlist_established[sel_i]
                                    # if requester in self.commandclass.transfers_ref:
                                    #   self.commandclass.transfer_endbuf(requester)
                                    log.info('TCP socket %s closed(A %s) on %s' % (kind.kind, cexc, requester))
                            else: # {
                                try:
                                    msg = sel_i.recv(cti_config.BUFSIZE_LARGE, socket.MSG_DONTWAIT)
                                    lmsg = len(msg)
                                except Exception:
                                    log.exception('connection to %s (%s)' % (requester, kind))
                                    lmsg = 0

                                if lmsg > 0:
                                    try:
                                        closemenow = self.manage_tcp_connections(sel_i, msg, kind)
                                    except Exception:
                                        log.exception('handling %s (%s)' % (requester, kind))
                                else:
                                    closemenow = True
                                    # XXX connc : kind.manage_logout('end_receiving')

                            if closemenow:
                                kind.disconnected('by_client')
                                sel_i.close()
                                del self.fdlist_established[sel_i]
                                # if requester in self.commandclass.transfers_ref:
                                #   self.commandclass.transfer_endbuf(requester)
                                log.info('TCP socket %s closed(B) on %s' % (kind.kind, requester))
                        except Exception:
                            # socket.error : exc.args[0]
                            log.exception('[%s] %s' % (kind, sel_i))
                            try:
                                log.warning('unexpected socket breakup')
                                kind.disconnected('exception')
                                sel_i.close()
                                del self.fdlist_established[sel_i]
                            except Exception:
                                log.exception('[%s] (2nd exception)' % kind)

                    # local pipe fd
                    elif self.pipe_queued_threads[0] == sel_i:
                        try:
                            pipebuf = os.read(sel_i, 1024)
                            if len(pipebuf) == 0:
                                log.warning('pipe_queued_threads has been closed')
                            else:
                                for pb in pipebuf.split('\n'):
                                    if not pb:
                                        continue
                                    [kind, where] = pb.split(':')
                                    if kind in ['main', 'innerdata', 'ami']:
                                        if kind == 'main':
                                            nactions = self.checkqueue()
                                        elif kind == 'innerdata':
                                            nactions = self.safe[where].checkqueue()
                                        elif kind == 'ami':
                                            nactions = self.myami[where].checkqueue()
                                        log.info('handled %d actions for %s' % (nactions, kind))
                                    elif kind == 'alarmclk':
                                        userid = where
                                        params = {'amicommand': 'alarmclk',
                                                  'amiargs': (userid,)}
                                        self.myami[self.myipbxid].execute_and_track(None, params)
                                    else:
                                        log.warning('unknown kind for %s' % pb)
                        except Exception:
                            log.exception('[pipe_queued_threads]')

                    self.loop_over_cti_queues()

                    for ipbxid, safe in self.safe.iteritems():
                        if ipbxid == self.myipbxid:
                            if (time.time() - self.lastrequest_time[ipbxid]) > self.updates_period() or self.update_userlist[ipbxid]:
                                self.lastrequest_time[ipbxid] = time.time()
                                log.info('[%s] %s : updates (computed timeout) %s (%s)'
                                         % (self.xdname, ipbxid, time.asctime(), self.update_userlist[ipbxid]))
                                try:
                                    # manage_connection.update_amisocks(ipbxid, self)
                                    self._config.update()
                                    safe.regular_update()
                                except Exception:
                                    log.exception('%s : failed while updating lists and sockets (computed timeout)'
                                                  % ipbxid)
                                try:
                                    if self.update_userlist[ipbxid]:
                                        while self.update_userlist[ipbxid]:
                                            tmp_ltr = self.update_userlist[ipbxid].pop()
                                            if tmp_ltr != 'xivo[cticonfig,update]':
                                                listtorequest = tmp_ltr[5:-12] + 's'
                                                safe.update_config_list(listtorequest)
                                                self.loop_over_cti_queues()
                                    else:
                                        safe.update_config_list_all()
                                        self.loop_over_cti_queues()
                                except Exception:
                                    log.exception('%s : commandclass.updates() (computed timeout)' % ipbxid)

            if not sels_i and not sels_o and not sels_e:
                # when nothing happens on the sockets, we fall here
                log.info('[%s] updates (select timeout) %s' % (self.xdname, time.asctime()))
                for ipbxid, safe in self.safe.iteritems():
                    if ipbxid == self.myipbxid:
                        try:
                            safe.update_config_list_all()
                        except Exception:
                            log.exception('%s : commandclass.updates() (select timeout)' % ipbxid)

                        self.lastrequest_time[ipbxid] = time.time()

                        try:
                            # manage_connection.update_amisocks(ipbxid, self)
                            self._config.update()
                            safe.regular_update()
                        except Exception:
                            log.exception('%s : failed while updating lists and sockets (select timeout)' % ipbxid)
        except Exception:
            log.exception('select step')
