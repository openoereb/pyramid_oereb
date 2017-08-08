OPERATING_SYSTEM ?= LINUX

USE_DOCKER ?= TRUE
DOCKER_BASE = camptocamp/oereb
DOCKER_CONTAINER_BASE = camptocamp-oereb

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

.PHONY: install
install: $(PYTHON_VENV)

.venv/timestamp:
	virtualenv $(VENV_FLAGS) .venv
	touch $@

.venv/requirements-timestamp: .venv/timestamp setup.py $(REQUIREMENTS)
	$(VENV_BIN)pip$(PYTHON_BIN_POSTFIX) install -r $(REQUIREMENTS)
	touch $@

.venv/install-timestamp: .venv/timestamp setup.py $(REQUIREMENTS)
	$(VENV_BIN)pip$(PYTHON_BIN_POSTFIX) install -e .
	touch $@

.PHONY: do-pip
do-pip:
	pip install -r $(REQUIREMENTS)

$(SPHINXBUILD): .venv/requirements-timestamp
	$(VENV_BIN)pip$(PYTHON_BIN_POSTFIX) install Sphinx sphinxcontrib-napoleon sphinx_rtd_theme

.PHONY: doc
doc: $(SPHINXBUILD)
	$(VENV_BIN)python setup.py develop
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
@_POSTGIS_IP = $(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(DOCKER_CONTAINER_BASE)-db-test 2> /dev/null)
else
@_POSTGIS_IP = localhost
endif
export SQLALCHEMY_URL = "postgresql://$(PG_CREDENTIALS)@$(@_POSTGIS_IP):5432/pyramid_oereb_test"
export PNG_ROOT_DIR = pyramid_oereb/standard/

.coverage: $(PYTHON_VENV) $(TESTS_DROP_DB) $(TESTS_SETUP_DB) pyramid_oereb/standard/pyramid_oereb.yml .coveragerc $(shell find -name "*.py" -print)
	@echo Run tests using docker: $(USE_DOCKER)
	$(VENV_BIN)py.test$(PYTHON_BIN_POSTFIX) -vv --cov-config .coveragerc --cov-report term-missing:skip-covered --cov pyramid_oereb tests

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
	docker stop $(DOCKER_CONTAINER_BASE)-db-test || true
	docker build -t $(DOCKER_BASE)-db-test test-db
	docker run --detach \
		--name $(DOCKER_CONTAINER_BASE)-db-test \
		--publish=5432:5432 \
		--env=POSTGRES_DB=pyramid_oereb_test \
		$(DOCKER_BASE)-db-test
	bash wait-for-db.sh $(DOCKER_CONTAINER_BASE)-db-test $(PG_PASSWORD) $(PG_USER)

.PHONY: tests-docker-drop-db
tests-docker-drop-db:
	docker stop $(DOCKER_CONTAINER_BASE)-db-test || true
	docker rm $(DOCKER_CONTAINER_BASE)-db-test || true

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

pyramid_oereb_standard.yml: .venv/install-timestamp
	$(VENV_BIN)create_standard_yaml$(PYTHON_BIN_POSTFIX)

test-db/12-create.sql: pyramid_oereb_standard.yml .venv/install-timestamp
	$(VENV_BIN)create_standard_tables$(PYTHON_BIN_POSTFIX) --configuration $< --sql-file $@

test-db/13-fill.sql: pyramid_oereb_standard.yml .venv/install-timestamp
	$(VENV_BIN)python pyramid_oereb/standard/load_sample_data.py --configuration $< --sql-file $@

.PHONY: serve-db-dev
serve-db-dev: tests-docker-drop-db test-db/12-create.sql test-db/13-fill.sql
	docker build -t $(DOCKER_BASE)-db-dev test-db
	docker run --rm --name $(DOCKER_CONTAINER_BASE)-db-dev \
	    --publish=5432:5432 \
	    --env=POSTGRES_DB=pyramid_oereb \
	    $(DOCKER_BASE)-db-dev

.PHONY: serve-print-example
serve-print-example:
	docker build -t $(DOCKER_BASE)-print-dev print
	docker run --rm --name $(DOCKER_CONTAINER_BASE)-print-dev \
	    --publish=8280:8080 \
	    $(DOCKER_BASE)-print-dev

.PHONY: deploy
deploy:
	$(VENV_BIN)python setup.py sdist bdist_wheel upload
