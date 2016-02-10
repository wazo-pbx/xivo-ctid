.PHONY: test-setup test

test-setup:
	docker pull n3llyb0y/wait
	docker pull xivo/postgres

test:
	nosetests suite
