.PHONY: test-setup test

test-setup:
	docker pull wazopbx/wait
	docker pull wazopbx/postgres
	docker pull swaggerapi/swagger-validator

test:
	nosetests suite
