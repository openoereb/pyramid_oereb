# Check if running on CI
ifeq ($(CI),true)
  PIP_REQUIREMENTS=.requirements-timestamp
  VENV_BIN=.venv/bin
  PIP_COMMAND=pip
else
  PIP_REQUIREMENTS=.venv/.requirements-timestamp
  VENV_BIN=.venv/bin
  PIP_COMMAND=pip3
endif

# Testing/DEV variables

PG_DB = pyramid_oereb_test
PG_HOST = db
PG_DROP_DB = DROP DATABASE IF EXISTS $(PG_DB);
PG_CREATE_DB = CREATE DATABASE $(PG_DB);
PG_CREATE_EXT = CREATE EXTENSION postgis;
PG_CREATE_SCHEMA = CREATE SCHEMA plr;
PG_USER = postgres
PG_PASSWORD = postgres
PG_CREDENTIALS ?= $(PG_USER):$(PG_PASSWORD)
SQLALCHEMY_URL = "postgresql://$(PG_CREDENTIALS)@$(PG_HOST):5432/$(PG_DB)"

PG_DEV_DATA_DIR = sample_data
PG_DEV_DATA = $(shell ls -1 $(PG_DEV_DATA_DIR)/*.json) \
	$(shell ls -1 $(PG_DEV_DATA_DIR)/plr119/contaminated_public_transport_sites/*.json) \
	$(shell ls -1 $(PG_DEV_DATA_DIR)/plr119/groundwater_protection_zones/*.json) \
	$(shell ls -1 $(PG_DEV_DATA_DIR)/plr119/forest_perimeters/*.json) \
	$(shell ls -1 $(PG_DEV_DATA_DIR)/plr119/motorways_building_lines/*.json) \
	$(shell ls -1 $(PG_DEV_DATA_DIR)/plr119/contaminated_military_sites/*.json)

DEV_CONFIGURATION_YML = pyramid_oereb/standard/pyramid_oereb.yml
DEV_CREATE_FILL_SCRIPT = pyramid_oereb/standard/load_sample_data.py
DEV_CREATE_STANDARD_YML_SCRIPT = $(VENV_BIN)/create_standard_yaml
DEV_CREATE_TABLES_SCRIPT = $(VENV_BIN)/create_standard_tables
DEV_CREATE_SCRIPT = .db/12-create.sql
DEV_FILL_SCRIPT = .db/13-fill.sql

MODEL_PK_TYPE_IS_STRING ?= true

PRINT_BACKEND = MapFishPrint # Set to XML2PDF if preferred

# ********************
# Variable definitions
# ********************

# Package name
PACKAGE = pyramid_oereb

# *******************
# Set up environments
# *******************

.venv/timestamp:
	python3 -m venv .venv
	touch $@

.venv/requirements-timestamp: .venv/timestamp setup.py requirements.txt requirements-tests.txt dev-requirements.txt
	$(VENV_BIN)/$(PIP_COMMAND) install --upgrade pip
	$(VENV_BIN)/$(PIP_COMMAND) install -r requirements.txt -r requirements-tests.txt -r dev-requirements.txt
	touch $@

# ********************
# Set up database
# ********************

.db/.drop-db:
	psql -h $(PG_HOST) -U $(PG_USER) -c "$(PG_DROP_DB)"

.db/.create-db:
	mkdir .db
	psql -h $(PG_HOST) -U $(PG_USER) -c "$(PG_CREATE_DB)"
	touch $@

.db/.create-db-extension: .db/.create-db
	psql -h $(PG_HOST) -U $(PG_USER) -d $(PG_DB) -c "$(PG_CREATE_EXT)"
	touch $@

.db/.create-db-schema: .db/.create-db-extension
	psql -h $(PG_HOST) -U $(PG_USER) -d $(PG_DB) -c "$(PG_CREATE_SCHEMA)"
	touch $@

.db/.create-db-dev-tables: .db/.setup-db $(DEV_CREATE_SCRIPT)
	psql -h $(PG_HOST) -U $(PG_USER) -d $(PG_DB) -f $(DEV_CREATE_SCRIPT)
	touch $@

.db/.fill-db-dev-tables: .db/.create-db-dev-tables $(DEV_FILL_SCRIPT)
	psql -h $(PG_HOST) -U $(PG_USER) -d $(PG_DB) -f $(DEV_FILL_SCRIPT)
	touch $@

# **************
# Common targets
# **************

# Build dependencies
BUILD_DEPS += .venv/requirements-timestamp

$(DEV_CONFIGURATION_YML): .venv/requirements-timestamp $(DEV_CREATE_STANDARD_YML_SCRIPT)
	$(DEV_CREATE_STANDARD_YML_SCRIPT) --name $@ --database $(SQLALCHEMY_URL) --print_backend $(PRINT_BACKEND)

$(DEV_CREATE_SCRIPT): $(DEV_CONFIGURATION_YML) .venv/requirements-timestamp $(DEV_CREATE_TABLES_SCRIPT)
	$(DEV_CREATE_TABLES_SCRIPT) --configuration $< --sql-file $@

$(DEV_FILL_SCRIPT): $(DEV_CONFIGURATION_YML) .venv/requirements-timestamp $(DEV_CREATE_FILL_SCRIPT)
	$(VENV_BIN)/python $(DEV_CREATE_FILL_SCRIPT) --configuration $< --sql-file $@ --dir $(PG_DEV_DATA_DIR)

.PHONY: setup-db
.db/.setup-db: .db/.create-db-schema
	touch $@

.PHONY: setup-db-dev
.db/.setup-db-dev: .db/.fill-db-dev-tables
	touch $@

.PHONY: install
install: .venv/requirements-timestamp

$(DEV_CREATE_TABLES_SCRIPT) $(DEV_CREATE_STANDARD_YML_SCRIPT): setup.py $(BUILD_DEPS)
	$(VENV_BIN)/python $< develop

.PHONY: build
build: $(DEV_CREATE_TABLES_SCRIPT) $(DEV_CREATE_STANDARD_YML_SCRIPT)

.PHONY: clean
clean: .db/.drop-db
	rm -rf .db

.PHONY: clean-all
clean-all: clean
	rm -rf .venv
	rm -f $(DEV_CONFIGURATION_YML)
	rm -f *.png
	rm -rf $(PACKAGE).egg-info

.PHONY: create-default-models
create-default-models:
	VENV_BIN=$(VENV_BIN) MODEL_SCRIPT=create_standard_model MODEL_PATH=pyramid_oereb/standard/models/ \
	MODEL_PK_TYPE_IS_STRING=$(MODEL_PK_TYPE_IS_STRING) bash generate_models.sh

.PHONY: git-attributes
git-attributes:
	git --no-pager diff --check `git log --oneline | tail -1 | cut --fields=1 --delimiter=' '`

.PHONY: lint
lint: .venv/requirements-timestamp
	$(VENV_BIN)/flake8

.PHONY: test
test: .venv/requirements-timestamp .db/.setup-db $(DEV_CONFIGURATION_YML)
	$(VENV_BIN)/py.test -vv $(PYTEST_OPTS) --cov-config .coveragerc --cov $(PACKAGE) --cov-report term-missing:skip-covered tests

.PHONY: check
check: git-attributes lint test

.PHONY: doc-latex
doc-latex: .venv/requirements-timestamp
	rm -rf doc/build/latex
	$(VENV_BIN)/sphinx-build -b latex doc/source doc/build/latex

.PHONY: doc-html
doc-html: .venv/requirements-timestamp
	rm -rf doc/build/html
	$(VENV_BIN)/sphinx-build -b html doc/source doc/build/html

.PHONY: updates
updates: $(PIP_REQUIREMENTS)
	$(VENV_BIN)/pip list --outdated

.PHONY: serve-dev
serve-dev: development.ini build .db/.setup-db-dev
	$(VENV_BIN)/pserve $< --reload

.PHONY: serve
serve: development.ini build
	$(VENV_BIN)/pserve $<
