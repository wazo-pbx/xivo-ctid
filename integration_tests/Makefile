.PHONY: test-setup test build-postgres

MANAGE_DB_DIR=../../xivo-manage-db/
POSTGRES_DOCKER=$(MANAGE_DB_DIR)/contribs/xivo-postgres/Dockerfile

build-postgres:
	docker pull postgres:9.4
	docker build -t xivo/xivo-postgres -f $(POSTGRES_DOCKER) $(MANAGE_DB_DIR)

test-setup: build-postgres
	docker pull n3llyb0y/wait
	docker build -t xivo/xivo-ctid -f ../Dockerfile ..
	docker pull rabbitmq
	docker pull progrium/consul
	docker pull xivo/asterisk
	docker pull xivo/xivo-agentd
	docker pull xivo/xivo-auth

test:
	nosetests suite
