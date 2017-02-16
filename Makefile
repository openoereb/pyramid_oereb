OPERATING_SYSTEM ?= WINDOWS

ifeq ($(CI),true)
  PYTHON_VENV=do_pip
  VENV_BIN=
else
  PYTHON_VENV=.venv/timestamp
  ifeq ($(OPERATING_SYSTEM), WINDOWS)
    VENV_BIN = .venv/Scripts/
    PYTHON_BIN_POSTFIX = .exe
  else
    VENV_BIN ?= .venv/bin/
    PYTHON_BIN_POSTFIX =
  endif
endif


install: $(PYTHON_VENV)

.venv/timestamp: setup.py requirements.txt
	virtualenv --system-site-packages .venv
	$(VENV_BIN)pip2$(PYTHON_BIN_POSTFIX) install -r requirements.txt
	touch $@

.PHONY: do_pip
do_pip:
	pip install --upgrade -r requirements.txt

.PHONY: checks
checks: git-attributes lint tests

.PHONY: tests
tests: $(PYTHON_VENV)
	$(VENV_BIN)py.test$(PYTHON_BIN_POSTFIX) -vv pyramid_oereb/tests

.PHONY: lint
lint: $(PYTHON_VENV)
	$(VENV_BIN)flake8

.PHONY: git-attributes
git-attributes:
	git --no-pager diff --check `git log --oneline | tail -1 | cut --fields=1 --delimiter=' '`

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
