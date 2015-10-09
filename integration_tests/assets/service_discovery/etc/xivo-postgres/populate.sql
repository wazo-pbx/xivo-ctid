INSERT INTO "entity" (name, displayname, description) VALUES ('xivotest', 'xivotest', '');

INSERT INTO "accesswebservice" (name, login, passwd, obj, description) VALUES ('admin', 'admin', 'proformatique', '', '');

INSERT INTO "context" (name, displayname, contexttype, description, entity) VALUES ('default', 'Default', 'internal', '', 'xivotest');
INSERT INTO "context" (name, displayname, contexttype, description, entity) VALUES ('from-extern', 'Incalls', 'incall', '', 'xivotest');
INSERT INTO "context" (name, displayname, contexttype, description, entity) VALUES ('to-extern', 'Outcalls', 'incall', '', 'xivotest');

INSERT INTO "contextinclude" (context, include) VALUES ('default', 'to-extern');

INSERT INTO "contextnumbers" (context, type, numberbeg, numberend, didlength) VALUES ('default', 'user', '1000', '1999', 0);
INSERT INTO "contextnumbers" (context, type, numberbeg, numberend, didlength) VALUES ('from-extern', 'incall', '1000', '4999', 4);
INSERT INTO "contextnumbers" (context, type, numberbeg, numberend, didlength) VALUES ('default', 'group', '2000', '2999', 0);
INSERT INTO "contextnumbers" (context, type, numberbeg, numberend, didlength) VALUES ('default', 'queue', '3000', '3999', 0);
INSERT INTO "contextnumbers" (context, type, numberbeg, numberend, didlength) VALUES ('default', 'meetme', '4000', '4999', 0);

INSERT INTO "netiface" (ifname, networktype, type, family, options) VALUES ('eth0', 'voip', 'iface', 'inet', '');

UPDATE provisioning set net4_ip_rest='provd';

CREATE DATABASE xivotemplate TEMPLATE asterisk;
