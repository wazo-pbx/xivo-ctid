XiVO CTI [![Build Status](https://travis-ci.org/wazo-pbx/xivo-ctid.png?branch=master)](https://travis-ci.org/wazo-pbx/xivo-ctid)
========

XiVO CTI is a [Computer telephony integration](http://en.wikipedia.org/Computer_telephony_integration) server
that provides advanced telephony services such as automatic phone control and
[Call center](http://en.wikipedia.org/wiki/Call_center) monitoring. CTI services are controlled by connecting to
the server with the [XiVO CTI client](https://github.com/xivo-pbx/xivo-client-qt)

Requirements
------------

xivo-ctid needs the XIVO_UUID environment variable to start. This environment
variable is already defined on a XiVO.

Installing XiVO CTI
-------------------

The server is already provided as a part of [XiVO](http://documentation.xivo.io).
Please refer to [the documentation](http://documentation.xivo.io/en/stable/installation/installsystem.html) for
further details on installing one.

Running unit tests
------------------

```
apt-get install libpq-dev python-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py27
```


Running integration tests
-------------------------

You need Docker installed.

```
cd integration_tests
pip install -U -r test-requirements.txt
make test-setup
make test
```
