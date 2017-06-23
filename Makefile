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

$(SPHINXBUILD): .venv/requirements-timestamp
	$(VENV_BIN)pip$(PYTHON_BIN_POSTFIX) install Sphinx sphinxcontrib-napoleon

.PHONY: doc
doc: $(SPHINXBUILD)
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: tests-setup-db
tests-setup-db: $(TESTS_SETUP_DB)

.PHONY: tests-drop-db
tests-drop-db: $(TESTS_DROP_DB)

.PHONY: checks
checks: git-attributes lint coverage-html

%: %.mako $(PYTHON_VENV) CONST_vars.yml
	$(VENV_BIN)c2c-template$(PYTHON_BIN_POSTFIX) --vars CONST_vars.yml --engine mako --files $<

.PHONY: tests
tests: .coverage

ifeq ($(USE_DOCKER), TRUE)
@_POSTGIS_IP = $(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(DOCKER_CONTAINER_PG))
else
@_POSTGIS_IP = localhost
endif
export SQLALCHEMY_URL = "postgresql://$(PG_CREDENTIALS)@$(@_POSTGIS_IP):5432/pyramid_oereb_test"
export PNG_ROOT_DIR = pyramid_oereb/standard/

.coverage: $(PYTHON_VENV) $(TESTS_DROP_DB) $(TESTS_SETUP_DB) pyramid_oereb/standard/pyramid_oereb.yml .coveragerc $(shell find -name "*.py" -print)
	@echo Run tests using docker: $(USE_DOCKER)
	$(VENV_BIN)py.test$(PYTHON_BIN_POSTFIX) -vv --cov-config .coveragerc --cov-report term-missing:skip-covered --cov pyramid_oereb pyramid_oereb/tests

.PHONY: lint
lint: $(PYTHON_VENV)
	$(VENV_BIN)flake8$(PYTHON_BIN_POSTFIX)

.PHONY: git-attributes
git-attributes:
	git --no-pager diff --check `git log --oneline | tail -1 | cut --fields=1 --delimiter=' '`

.PHONY: coverage-html
coverage-html: coverage_report/index.html

coverage_report/index.html: $(PYTHON_VENV) .coverage
	$(VENV_BIN)coverage$(PYTHON_BIN_POSTFIX) html

.PHONY: tests-docker-setup-db
tests-docker-setup-db:
	docker run --name $(DOCKER_CONTAINER_PG) -e POSTGRES_PASSWORD=$(PG_PASSWORD) -d mdillon/postgis:9.4-alpine
	bash wait-for-db.sh $(DOCKER_CONTAINER_PG) $(PG_PASSWORD) $(PG_USER)
	docker run -i --link $(DOCKER_CONTAINER_PG):postgres --rm postgres sh -c 'PGPASSWORD=$(PG_PASSWORD) exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -U $(PG_USER) -w -c "$(PG_CREATE_DB)"'
	docker run -i --link $(DOCKER_CONTAINER_PG):postgres --rm postgres sh -c 'PGPASSWORD=$(PG_PASSWORD) exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -d pyramid_oereb_test -U $(PG_USER) -w -c "$(PG_CREATE_EXT)"'
	docker run -i --link $(DOCKER_CONTAINER_PG):postgres --rm postgres sh -c 'PGPASSWORD=$(PG_PASSWORD) exec psql -h "$$POSTGRES_PORT_5432_TCP_ADDR" -p "$$POSTGRES_PORT_5432_TCP_PORT" -d pyramid_oereb_test -U $(PG_USER) -w -c "$(PG_CREATE_SCHEMA)"'

.PHONY: tests-docker-drop-db
tests-docker-drop-db:
	docker stop $(DOCKER_CONTAINER_PG)
	docker rm $(DOCKER_CONTAINER_PG)

.PHONY: tests-win-setup-db
tests-win-setup-db:
	psql -c $(PG_CREATE_DB) -U $(PG_USER)
	psql -c $(PG_CREATE_EXT) -U $(PG_USER) -d pyramid_oereb_test
	psql -c $(PG_CREATE_SCHEMA) -U $(PG_USER) -d pyramid_oereb_test

.PHONY: tests-win-drop-db
tests-win-drop-db:
	psql -c  $(PG_DROP_DB) -U $(PG_USER)

.PHONY: clean-all
clean-all:
	rm -rf .venv
	rm -rf $(BUILDDIR)
	rm pyramid_oereb/tests/resources/pyramid_oereb_test.yml

.PHONY: create-standard-tables
create-standard-tables: $(PYTHON_VENV)
	$(VENV_BIN)create_tables$(PYTHON_BIN_POSTFIX) -c pyramid_oereb.yml

.PHONY: drop-standard-tables
drop-standard-tables: $(PYTHON_VENV)
	$(VENV_BIN)drop_tables$(PYTHON_BIN_POSTFIX) -c pyramid_oereb.yml

.PHONY: serve
serve: $(PYTHON_VENV)
	$(VENV_BIN)pserve$(PYTHON_BIN_POSTFIX) development.ini

.PHONY: serve-print-example
serve-print-example:
	docker build -t camptocamp/oereb-print print
	docker run --publish=8280:8080 camptocamp/oereb-print

description.rst:
	awk 'FNR==1{print ""}1' README.md CHANGES.md | pandoc -f markdown -t rst -o description.rst

.PHONY: deploy
deploy: description.rst
	$(VENV_BIN)python setup.py sdist bdist_wheel upload
