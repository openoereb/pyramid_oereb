OPERATING_SYSTEM ?= LINUX
ifeq ($(CI),true)
  PYTHON_VENV=do_pip
  VENV_BIN=
else
  PYTHON_VENV=.venv/requirements-timestamp
  ifeq ($(OPERATING_SYSTEM), WINDOWS)
    VENV_BIN = .venv/Scripts/
    PYTHON_BIN_POSTFIX = .exe
  else
    VENV_BIN ?= .venv/bin/
    PYTHON_BIN_POSTFIX =
  endif
endif


install: $(PYTHON_VENV)

.venv/timestamp:
	virtualenv .venv
	touch $@

.venv/requirements-timestamp: .venv/timestamp setup.py requirements.txt
	$(VENV_BIN)pip2$(PYTHON_BIN_POSTFIX) install -r requirements.txt
	touch $@

.PHONY: do_pip
do_pip:
	pip install --upgrade -r requirements.txt

.PHONY: checks
checks: git-attributes lint tests

.PHONY: tests
tests: $(PYTHON_VENV) setup_db
	$(eval $@_POSTGIS_IP := $(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgis))
	SQLALCHEMY_URL="postgresql://postgres:password@$($@_POSTGIS_IP):5432/pyramid_oereb_test" ;\
	export SQLALCHEMY_URL ;\
	printenv SQLALCHEMY_URL ;\
	$(VENV_BIN)py.test$(PYTHON_BIN_POSTFIX) -vv pyramid_oereb/tests

.PHONY: lint
lint: $(PYTHON_VENV)
	$(VENV_BIN)flake8

.PHONY: git-attributes
git-attributes:
	git --no-pager diff --check `git log --oneline | tail -1 | cut --fields=1 --delimiter=' '`

docker_setup:
	- docker run --name postgis -e POSTGRES_PASSWORD=password -d mdillon/postgis
	@echo Waiting 5s for server start up...
	@sleep 5s

.PHONY: setup_db
setup_db: docker_setup
	docker start postgis
	docker run -i --link postgis:postgres --rm postgres sh -c 'PGPASSWORD=password exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -U postgres -w -c "DROP DATABASE IF EXISTS pyramid_oereb_test;"'
	docker run -i --link postgis:postgres --rm postgres sh -c 'PGPASSWORD=password exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -U postgres -w -c "CREATE DATABASE pyramid_oereb_test;"'
	docker run -i --link postgis:postgres --rm postgres sh -c 'PGPASSWORD=password exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -d pyramid_oereb_test -U postgres -w -c "CREATE EXTENSION postgis;"'
	docker run -i --link postgis:postgres --rm postgres sh -c 'PGPASSWORD=password exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -d pyramid_oereb_test -U postgres -w -c "CREATE SCHEMA plr;"'


.PHONY: drop_db
drop_db: docker_setup
	docker run -i --link postgis:postgres --rm postgres sh -c 'PGPASSWORD=password exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -U postgres -w -c "DROP DATABASE pyramid_oereb_test;"'

.PHONY: tests_full
tests_full: tests drop_db

.PHONY: cleanall
cleanall:
	rm -rf .venv