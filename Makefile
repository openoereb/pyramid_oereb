OPERATING_SYSTEM ?= LINUX

USE_DOCKER ?= TRUE
DOCKER_CONTAINER_PG ?= postgis-oereb-test

PG_DROP_DB ?= DROP DATABASE IF EXISTS pyramid_oereb_test;
PG_CREATE_DB ?= CREATE DATABASE pyramid_oereb_test;
PG_CREATE_EXT ?= CREATE EXTENSION postgis;
PG_CREATE_SCHEMA ?= CREATE SCHEMA plr;

ifeq ($(CI),true)
  PYTHON_VENV=do_pip
  VENV_BIN=
else
  PYTHON_VENV=.venv/requirements-timestamp
  ifeq ($(OPERATING_SYSTEM), WINDOWS)
    VENV_BIN = .venv/Scripts/
    PYTHON_BIN_POSTFIX = .exe
    USE_DOCKER = FALSE
    SETUP_DB = win-setup-db
    DROP_DB = win-drop-db
    PG_START=
	PG_DROP_DB = psql -U postgres -c "DROP DATABASE IF EXISTS pyramid_oereb_test;"
	PG_CREATE_DB = psql -U postgres -c "CREATE DATABASE pyramid_oereb_test;"
	PG_CREATE_EXT = psql -U postgres -c "CREATE EXTENSION postgis;"
	PG_CREATE_SCHEMA = psql -U postgres -d pyramid_oereb_test -c "CREATE SCHEMA plr;"
  else
    VENV_BIN ?= .venv/bin/
    PYTHON_BIN_POSTFIX =
    SETUP_DB = docker-setup-db
    DROP_DB = docker-drop-db
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

.PHONY: setup-db
setup-db: $(SETUP_DB)

.PHONY: drop-db
drop-db: $(DROP_DB)

.PHONY: checks
checks: git-attributes lint tests

.PHONY: tests
tests: $(PYTHON_VENV) drop-db setup-db
	@echo Run tests using docker: $(USE_DOCKER)
	$(eval $@_POSTGIS_IP := $(if $(filter TRUE,$(USE_DOCKER)), $(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(DOCKER_CONTAINER_PG)), @echo localhost))
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


docker-setup-db:
	docker run --name $(DOCKER_CONTAINER_PG) -e POSTGRES_PASSWORD=password -d mdillon/postgis
	@echo Waiting 10s for server start up...
	@sleep 10s
	docker run -i --link $(DOCKER_CONTAINER_PG):postgres --rm postgres sh -c 'PGPASSWORD=password exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -U postgres -w -c "$(PG_CREATE_DB)"'
	docker run -i --link $(DOCKER_CONTAINER_PG):postgres --rm postgres sh -c 'PGPASSWORD=password exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -d pyramid_oereb_test -U postgres -w -c "$(PG_CREATE_EXT)"'
	docker run -i --link $(DOCKER_CONTAINER_PG):postgres --rm postgres sh -c 'PGPASSWORD=password exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -d pyramid_oereb_test -U postgres -w -c "$(PG_CREATE_SCHEMA)"'

docker-drop-db:
	- docker container stop $(DOCKER_CONTAINER_PG)
	- docker container rm $(DOCKER_CONTAINER_PG)


win-setup-db:
	psql -c '$(PG_CREATE_DB)' -U postgres
	psql -c '$(PG_CREATE_EXT)' -U postgres
	psql -c '$(PG_CREATE_SCHEMA)' -U postgres

win-drop-db:
	- psql -c '$(PG_DROP_DB)' -U postgres


.PHONY: cleanall
cleanall:
	rm -rf .venv