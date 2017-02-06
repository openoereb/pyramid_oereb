ifeq ($(CI),true)
  PYTHON=do_pip
  VENV=
else
  PYTHON=.venv/timestamp
  VENV=.venv/bin/
endif

install: $(PYTHON)

.venv/timestamp: setup.py requirements.txt
	/usr/bin/virtualenv --python=/usr/bin/python2.7 .venv
	.venv/bin/pip install --upgrade -r requirements.txt
	touch $@

.PHONY: do_pip
do_pip:
	pip install --upgrade -r requirements.txt

.PHONY: tests
tests: $(PYTHON)
	$(VENV)py.test -vv pyramid_oereb/tests

.PHONY: setup_db
setup_db:
	psql -c 'CREATE DATABASE oereb_test;' -U postgres
	psql -c "CREATE USER \"www-data\" PASSWORD 'www-data';" -U postgres oereb_test || true
	psql -c 'CREATE TABLE example (id SERIAL PRIMARY KEY, value TEXT);' -U postgres oereb_test
	psql -c "INSERT INTO example (value) VALUES ('test');" -U postgres oereb_test
	psql -c 'grant ALL on example to "www-data"' -U postgres oereb_test

.PHONY: drop_db
drop_db:
	psql -c 'DROP DATABASE oereb_test;' -U postgres
