OPERATING_SYSTEM ?= LINUX

USE_DOCKER ?= TRUE
DOCKER_CONTAINER_PG ?= postgis-oereb-test

PG_DROP_DB ?= DROP DATABASE IF EXISTS pyramid_oereb_test;
PG_CREATE_DB ?= CREATE DATABASE pyramid_oereb_test;
PG_CREATE_EXT ?= CREATE EXTENSION postgis;
PG_CREATE_SCHEMA ?= CREATE SCHEMA plr;
PG_USER ?= postgres
PG_PASSWORD ?= password
PG_CREDENTIALS ?= $(PG_USER):$(PG_PASSWORD)

VENV_FLAGS ?=

REQUIREMENTS ?= requirements.txt

ifeq ($(CI),true)
  PYTHON_VENV = do-pip
  VENV_BIN =
else
  PYTHON_VENV=.venv/requirements-timestamp
  ifeq ($(OPERATING_SYSTEM), WINDOWS)
    export PGPASSWORD = $(PG_PASSWORD)
    VENV_BIN = .venv/Scripts/
    VENV_FLAGS += --system-site-packages
    PYTHON_BIN_POSTFIX = .exe
    USE_DOCKER = FALSE
    TESTS_SETUP_DB = tests-win-setup-db
    TESTS_DROP_DB = tests-win-drop-db
    PG_DROP_DB = "DROP DATABASE IF EXISTS pyramid_oereb_test;"
    PG_CREATE_DB = "CREATE DATABASE pyramid_oereb_test;"
    PG_CREATE_EXT = "CREATE EXTENSION postgis;"
    PG_CREATE_SCHEMA = "CREATE SCHEMA plr;"
    REQUIREMENTS = requirements-windows.txt
  else
    VENV_BIN ?= .venv/bin/
    PYTHON_BIN_POSTFIX =
    TESTS_SETUP_DB = tests-docker-setup-db
    TESTS_DROP_DB = tests-docker-drop-db
  endif
endif

SPHINXOPTS =
SPHINXBUILD = $(VENV_BIN)sphinx-build$(PYTHON_BIN_POSTFIX)
SPHINXPROJ = OEREB
SOURCEDIR = doc/source
BUILDDIR = doc/build

install: $(PYTHON_VENV)

.venv/timestamp:
	virtualenv $(VENV_FLAGS) .venv
	touch $@

.venv/requirements-timestamp: .venv/timestamp setup.py $(REQUIREMENTS)
	$(VENV_BIN)pip$(PYTHON_BIN_POSTFIX) install -r $(REQUIREMENTS)
	touch $@

.PHONY: do-pip
do-pip:
	pip install --upgrade -r $(REQUIREMENTS)

.venv/bin/sphinx-build: .venv/requirements-timestamp
	$(VENV_BIN)pip$(PYTHON_BIN_POSTFIX) install Sphinx

.PHONY: doc
doc: .venv/bin/sphinx-build doc/source/api.rst
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

doc/source/api.rst: doc/source/api.rst.mako
	$(VENV_BIN)mako-render$(PYTHON_BIN_POSTFIX) $< > $@

.PHONY: tests-setup-db
tests-setup-db: $(TESTS_SETUP_DB)

.PHONY: tests-drop-db
tests-drop-db: $(TESTS_DROP_DB)

.PHONY: checks
checks: git-attributes lint tests

.PHONY: tests
tests: $(PYTHON_VENV) $(TESTS_DROP_DB) $(TESTS_SETUP_DB)
	@echo Run tests using docker: $(USE_DOCKER)
	$(eval $@_POSTGIS_IP := $(if $(filter TRUE,$(USE_DOCKER)), $(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(DOCKER_CONTAINER_PG)), localhost))
	SQLALCHEMY_URL="postgresql://$(PG_CREDENTIALS)@$($@_POSTGIS_IP):5432/pyramid_oereb_test" ;\
	export SQLALCHEMY_URL ;\
	printenv SQLALCHEMY_URL ;\
	$(VENV_BIN)c2c-template --vars CONST_vars.yml --engine mako --files pyramid_oereb_test.yml.mako ;\
	$(VENV_BIN)py.test$(PYTHON_BIN_POSTFIX) -vv --cov-config .coveragerc --cov-report term-missing:skip-covered --cov pyramid_oereb pyramid_oereb/tests ;\
	$(VENV_BIN)coverage html

.PHONY: lint
lint: $(PYTHON_VENV)
	$(VENV_BIN)flake8$(PYTHON_BIN_POSTFIX)

.PHONY: git-attributes
git-attributes:
	git --no-pager diff --check `git log --oneline | tail -1 | cut --fields=1 --delimiter=' '`


tests-docker-setup-db:
	docker run --name $(DOCKER_CONTAINER_PG) -e POSTGRES_PASSWORD=$(PG_PASSWORD) -d mdillon/postgis:9.4-alpine
	@echo Waiting 10s for server start up...
	@sleep 10s
	docker run -i --link $(DOCKER_CONTAINER_PG):postgres --rm postgres sh -c 'PGPASSWORD=$(PG_PASSWORD) exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -U $(PG_USER) -w -c "$(PG_CREATE_DB)"'
	docker run -i --link $(DOCKER_CONTAINER_PG):postgres --rm postgres sh -c 'PGPASSWORD=$(PG_PASSWORD) exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -d pyramid_oereb_test -U $(PG_USER) -w -c "$(PG_CREATE_EXT)"'
	docker run -i --link $(DOCKER_CONTAINER_PG):postgres --rm postgres sh -c 'PGPASSWORD=$(PG_PASSWORD) exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -d pyramid_oereb_test -U $(PG_USER) -w -c "$(PG_CREATE_SCHEMA)"'

tests-docker-drop-db:
	- docker container stop $(DOCKER_CONTAINER_PG)
	- docker container rm $(DOCKER_CONTAINER_PG)

tests-win-setup-db:
	psql -c $(PG_CREATE_DB) -U $(PG_USER)
	psql -c $(PG_CREATE_EXT) -U $(PG_USER) -d pyramid_oereb_test
	psql -c $(PG_CREATE_SCHEMA) -U $(PG_USER) -d pyramid_oereb_test

tests-win-drop-db:
	psql -c  $(PG_DROP_DB) -U $(PG_USER)

.PHONY: clean-all
clean-all:
	rm -rf .venv
	rm -rf $(BUILDDIR)

.PHONY: create-standard-tables
create-standard-tables: $(PYTHON_VENV)
	$(VENV_BIN)create_tables$(PYTHON_BIN_POSTFIX) -c pyramid_oereb.yml

.PHONY: drop-standard-tables
drop-standard-tables: $(PYTHON_VENV)
	$(VENV_BIN)drop_tables$(PYTHON_BIN_POSTFIX) -c pyramid_oereb.yml

.PHONY: serve
serve: $(PYTHON_VENV)
	$(VENV_BIN)pserve$(PYTHON_BIN_POSTFIX) development.ini

.PHONY: description
description:
	awk 'FNR==1{print ""}1' README.md CHANGES.md | pandoc -f markdown -t rst -o description.rst

.PHONY: deploy
deploy: description
	$(VENV_BIN)python setup.py sdist bdist_wheel upload
