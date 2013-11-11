How to run unit tests [![Build Status](https://travis-ci.org/xivo-pbx/xivo-ctid.png?branch=master)](https://travis-ci.org/xivo-pbx/xivo-ctid)
---------------------


Install pika :

pip install pika


Run unit tests

PYTHONPATH=.:../xivo-lib-python/xivo-lib-python/:../xivo-dao/xivo-dao/:../xivo-dird/xivo-dird/:../xivo-agent/xivo-agent/ nosetests xivo-ctid
