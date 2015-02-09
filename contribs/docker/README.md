To run ctid in a docker please run it like :

    docker run -i -p 5003:5003 -p 5004:5004 -v /config/ctid/:/etc/xivo-ctid/conf.d -t xivo-ctid /bin/bash

and launch the xivo-ctid

    xivo-ctid -f -d

or

    docker run --name xivo-ctid -d -p 5003:5003 -p 5004:5004 -v /config/ctid/:/etc/xivo-ctid/conf.d -t xivo-ctid
