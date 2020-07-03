OPERATING_SYSTEM ?= LINUX
PYTHON_VERSION ?= python3
VIRTUALENV = virtualenv --python=$(PYTHON_VERSION)
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

INSTALL_REQUIREMENTS ?= requirements.txt

PYTHON_VENV=.venv/requirements-timestamp
ifeq ($(OPERATING_SYSTEM), WINDOWS)
    export PGPASSWORD = $(PG_PASSWORD)
    VENV_BIN = .venv/Scripts/
    PYTHON_BIN_POSTFIX = .exe
    USE_DOCKER = FALSE
    TESTS_SETUP_DB = tests-win-setup-db
    TESTS_DROP_DB = tests-win-drop-db
    PG_DROP_DB = "DROP DATABASE IF EXISTS pyramid_oereb_test;"
    PG_CREATE_DB = "CREATE DATABASE pyramid_oereb_test;"
    PG_CREATE_EXT = "CREATE EXTENSION postgis;"
    PG_CREATE_SCHEMA = "CREATE SCHEMA plr;"
    INSTALL_REQUIREMENTS = requirements-windows.txt
else
    VENV_BIN ?= .venv/bin/
    PYTHON_BIN_POSTFIX =
    TESTS_SETUP_DB = tests-docker-setup-db
    TESTS_DROP_DB = tests-docker-drop-db
endif
PIP_UPDATE = $(VENV_BIN)pip install --upgrade pip setuptools

SPHINXOPTS =
SPHINXBUILD = $(VENV_BIN)sphinx-build$(PYTHON_BIN_POSTFIX)
SPHINXPROJ = OEREB
SOURCEDIR = doc/source
BUILDDIR = doc/build

MODEL_PK_TYPE_IS_STRING ?= true

.PHONY: install
install: $(PYTHON_VENV)

.venv/timestamp:
	$(VIRTUALENV) --no-site-packages .venv
	touch $@

.venv/requirements-timestamp: .venv/install-timestamp .venv/timestamp setup.py dev-requirements.txt
	$(VENV_BIN)pip$(PYTHON_BIN_POSTFIX) install --requirement dev-requirements.txt
	touch $@

.venv/install-timestamp: .venv/timestamp setup.py $(INSTALL_REQUIREMENTS)
	$(PIP_UPDATE)
	$(VENV_BIN)pip$(PYTHON_BIN_POSTFIX) install --requirement $(INSTALL_REQUIREMENTS)
	$(VENV_BIN)pip$(PYTHON_BIN_POSTFIX) install --editable .
	touch $@

$(SPHINXBUILD): .venv/requirements-timestamp
	$(VENV_BIN)pip$(PYTHON_BIN_POSTFIX) install "Sphinx<1.6" sphinx_rtd_theme

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
export PRINT_BACKEND = MapFishPrint # Set to XML2PDF if preferred

.coverage: $(PYTHON_VENV) $(TESTS_DROP_DB) $(TESTS_SETUP_DB) pyramid_oereb/standard/pyramid_oereb.yml .coveragerc $(shell find -name "*.py" -print | fgrep -v /.venv)
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
	rm -rf coverage_report
	rm -f pyramid_oereb_standard.yml pyramid_oereb/standard/pyramid_oereb.yml docker/config.yaml
	rm -f test-db/12-create.sql test-db/13-fill.sql

.PHONY: create-default-models
create-default-models:
	VENV_BIN=$(VENV_BIN) MODEL_SCRIPT=create_standard_model MODEL_PATH=pyramid_oereb/standard/models/ \
	MODEL_PK_TYPE_IS_STRING=$(MODEL_PK_TYPE_IS_STRING) bash generate_models.sh

.PHONY: create-oereblex-models
create-oereblex-models:
	VENV_BIN=$(VENV_BIN) MODEL_SCRIPT=create_oereblex_model MODEL_PATH=pyramid_oereb/contrib/models/oereblex/ \
	MODEL_PK_TYPE_IS_STRING=$(MODEL_PK_TYPE_IS_STRING) bash generate_models.sh

.PHONY: create-standard-tables
create-standard-tables: $(PYTHON_VENV)
	$(VENV_BIN)create_tables$(PYTHON_BIN_POSTFIX) -c pyramid_oereb.yml

.PHONY: drop-standard-tables
drop-standard-tables: $(PYTHON_VENV)
	$(VENV_BIN)drop_tables$(PYTHON_BIN_POSTFIX) -c pyramid_oereb.yml

.PHONY: serve
serve: install pyramid_oereb_standard.yml docker/config.yaml test-db/12-create.sql test-db/13-fill.sql
	docker-compose up --build --remove-orphans -d

pyramid_oereb_standard.yml: .venv/install-timestamp
	$(VENV_BIN)create_standard_yaml$(PYTHON_BIN_POSTFIX) --database $(SQLALCHEMY_URL) --print_backend $(PRINT_BACKEND)

test-db/12-create.sql: pyramid_oereb_standard.yml .venv/install-timestamp
	$(VENV_BIN)create_standard_tables$(PYTHON_BIN_POSTFIX) --configuration $< --sql-file $@
	docker rm pyramidoereb_db_1 | true

test-db/13-fill.sql: pyramid_oereb_standard.yml .venv/install-timestamp \
	$(shell ls -1 sample_data/*.json) \
	$(shell ls -1 sample_data/plr119/contaminated_public_transport_sites/*.json) \
	$(shell ls -1 sample_data/plr119/groundwater_protection_zones/*.json) \
	$(shell ls -1 sample_data/plr119/forest_perimeters/*.json) \
	$(shell ls -1 sample_data/plr119/motorways_building_lines/*.json) \
	$(shell ls -1 sample_data/plr119/contaminated_military_sites/*.json)
	$(VENV_BIN)python pyramid_oereb/standard/load_sample_data.py --configuration $< --sql-file $@
	docker rm pyramidoereb_db_1 | true

.PHONY: deploy
deploy:
	$(VENV_BIN)python setup.py sdist bdist_wheel upload

logo_%.png: pyramid_oereb_standard.yml
	touch --no-create $@

.PHONY: build-docker
build-docker: logo_oereb.png logo_confederation.png logo_canton.png docker/config.yaml
	docker build --tag camptocamp/pyramid-oereb:latest .
