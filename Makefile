OPERATING_SYSTEM ?= WINDOWS

ifeq ($(CI),true)
  PYTHON=do_pip
  VENV_BIN=
else
  PYTHON=.venv/timestamp
  ifeq ($(OPERATING_SYSTEM), WINDOWS)
    VENV_BIN = .venv/Scripts/
    PYTHON_BIN_POSTFIX = .exe
  else
    VENV_BIN ?= .venv/bin/
    PYTHON_BIN_POSTFIX =
  endif
endif


install: $(PYTHON)

.venv/timestamp: setup.py requirements.txt
	virtualenv --system-site-packages .venv
	$(VENV_BIN)pip2$(PYTHON_BIN_POSTFIX) install -r requirements.txt
	touch $@

.PHONY: do_pip
do_pip:
	pip install --upgrade -r requirements.txt

.PHONY: tests
tests: $(PYTHON)
	$(VENV_BIN)py.test$(PYTHON_BIN_POSTFIX) -vv pyramid_oereb/tests

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
