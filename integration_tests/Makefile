.PHONY: test-setup test

test-setup:
	docker pull n3llyb0y/wait
	docker pull wazopbx/postgres
	docker pull swaggerapi/swagger-validator

test:
	nosetests suite
