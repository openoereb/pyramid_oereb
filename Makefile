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

# Environment variables for DB connection
PGDATABASE ?= pyramid_oereb_test
PGHOST ?= oereb-db
PGUSER ?= postgres
PGPASSWORD ?= postgres
PGPORT ?= 5432
EXPOSED_PGPORT ?= 15432
PYRAMID_OEREB_PORT ?= 6543

# Makefile internal aliases
PG_DROP_DB = DROP DATABASE IF EXISTS $(PGDATABASE) WITH (FORCE);
PG_CREATE_DB = CREATE DATABASE $(PGDATABASE);
PG_CREATE_EXT = CREATE EXTENSION IF NOT EXISTS postgis;
PG_CREATE_SCHEMA = CREATE SCHEMA plr;
SQLALCHEMY_URL = "postgresql://$(PGUSER):$(PGPASSWORD)@$(PGHOST):$(PGPORT)/$(PGDATABASE)"

PG_DEV_DATA_DIR = sample_data
PG_DEV_DATA = $(shell ls -1 $(PG_DEV_DATA_DIR)/*.json) \
	$(shell ls -1 $(PG_DEV_DATA_DIR)/contaminated_public_transport_sites/*.json) \
	$(shell ls -1 $(PG_DEV_DATA_DIR)/land_use_plans/*.json) \
	$(shell ls -1 $(PG_DEV_DATA_DIR)/groundwater_protection_zones/*.json) \
	$(shell ls -1 $(PG_DEV_DATA_DIR)/forest_perimeters/*.json) \
	$(shell ls -1 $(PG_DEV_DATA_DIR)/motorways_building_lines/*.json) \
	$(shell ls -1 $(PG_DEV_DATA_DIR)/contaminated_military_sites/*.json)

DEV_CONFIGURATION_YML = pyramid_oereb/standard/pyramid_oereb.yml
DEV_CREATE_FILL_SCRIPT = pyramid_oereb/standard/load_sample_data.py
DEV_CREATE_STANDARD_YML_SCRIPT = $(VENV_BIN)/create_standard_yaml
DEV_CREATE_TABLES_SCRIPT = $(VENV_BIN)/create_standard_tables
DEV_CREATE_SCRIPT = .db/12-create.sql
DEV_FILL_SCRIPT = .db/13-fill.sql

MODEL_PK_TYPE_IS_STRING ?= true

PRINT_BACKEND = MapFishPrint # Set to XML2PDF if preferred
PRINT_URL = http://oereb-print:8080/print/oereb

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
	$(VENV_BIN)/$(PIP_COMMAND) install --upgrade pip wheel
	$(VENV_BIN)/$(PIP_COMMAND) install -r requirements.txt -r requirements-tests.txt -r dev-requirements.txt
	touch $@

# ********************
# Set up database
# ********************

.db/.drop-db:
	psql -h $(PGHOST) -U $(PGUSER) -c "$(PG_DROP_DB)"

.db/.create-db:
	mkdir -p .db
	psql -h $(PGHOST) -U $(PGUSER) -c "$(PG_CREATE_DB)" || /bin/true
	touch $@

.db/.create-db-extension: .db/.create-db
	psql -h $(PGHOST) -U $(PGUSER) -d $(PGDATABASE) -c "$(PG_CREATE_EXT)"
	touch $@

.db/.create-db-schema: .db/.create-db-extension
	psql -h $(PGHOST) -U $(PGUSER) -d $(PGDATABASE) -c "$(PG_CREATE_SCHEMA)"
	touch $@

.db/.create-db-dev-tables: .db/.setup-db $(DEV_CREATE_SCRIPT)
	psql -h $(PGHOST) -U $(PGUSER) -d $(PGDATABASE) -f $(DEV_CREATE_SCRIPT)
	touch $@

.db/.fill-db-dev-tables: .db/.create-db-dev-tables $(DEV_FILL_SCRIPT)
	psql -h $(PGHOST) -U $(PGUSER) -d $(PGDATABASE) -f $(DEV_FILL_SCRIPT)
	touch $@

##########
# FEDERAL DATA SECTION
##########

# URLS to fed data
THEMES_XML_URL=http://models.geo.admin.ch/V_D/OeREB/OeREBKRM_V2_0_Themen_20210915.xml
LAWS_XML_URL=http://models.geo.admin.ch/V_D/OeREB/OeREBKRM_V2_0_Gesetze_20210414.xml
LOGOS_XML_URL=http://models.geo.admin.ch/V_D/OeREB/OeREBKRM_V2_0_Logos_20211021.xml
TEXTS_XML_URL=http://models.geo.admin.ch/V_D/OeREB/OeREBKRM_V2_0_Texte_20211021.xml

# XML files for creating XML files
FED_TMP = .fed
FED_TMP_TIMESTAMP = $(FED_TMP)/.create-timestamp
THEMES_XML = $(FED_TMP)/themes.xml
LAWS_XML = $(FED_TMP)/laws.xml
LOGOS_XML = $(FED_TMP)/logos.xml
TEXTS_XML = $(FED_TMP)/texts.xml

FED_XMLS = $(THEMES_XML) \
	$(LAWS_XML) \
	$(LOGOS_XML) \
	$(TEXTS_XML)

$(FED_TMP_TIMESTAMP):
	mkdir -p $(FED_TMP)
	touch $@

$(THEMES_XML): $(FED_TMP_TIMESTAMP)
	curl -X GET $(THEMES_XML_URL) > $@

$(LAWS_XML): $(FED_TMP_TIMESTAMP)
	curl -X GET $(LAWS_XML_URL) > $@

$(LOGOS_XML): $(FED_TMP_TIMESTAMP)
	curl -X GET $(LOGOS_XML_URL) > $@

$(TEXTS_XML): $(FED_TMP_TIMESTAMP)
	curl -X GET $(TEXTS_XML_URL) > $@


# JSON files for import into sample database
THEMES_JSON = $(PG_DEV_DATA_DIR)/ch.themes.json
THEMES_DOCS_JSON = $(PG_DEV_DATA_DIR)/ch.themes_docs.json
LAWS_JSON = $(PG_DEV_DATA_DIR)/ch.laws.json
LAW_RESPONSIBLE_OFFICES_JSON = $(PG_DEV_DATA_DIR)/ch.laws_responsible_office.json
LOGOS_JSON = $(PG_DEV_DATA_DIR)/ch.logo.json
LAW_STATUS_JSON = $(PG_DEV_DATA_DIR)/ch.law_status.json
DOCUMENT_TYPE_JSON = $(PG_DEV_DATA_DIR)/ch.document_type.json
REAL_ESTATE_TYPE_JSON = $(PG_DEV_DATA_DIR)/ch.real_estate_type.json
GLOSSARY_JSON = $(PG_DEV_DATA_DIR)/ch.glossary.json
DISCLAIMER_JSON = $(PG_DEV_DATA_DIR)/ch.disclaimer.json
GENERAL_INFORMATION_JSON = $(PG_DEV_DATA_DIR)/ch.general_information.json

# XSL files for transformation of XML to JSON
THEMES_XSL = fed/themes.json.xsl
THEMES_DOCS_XSL = fed/themes_docs.json.xsl
LAWS_XSL = fed/laws.json.xsl
LAW_RESPONSIBLE_OFFICES_XSL = fed/laws_responsible_office.json.xsl
LOGOS_XSL = fed/logos.json.xsl
LAW_STATUS_XSL = fed/law_status.json.xsl
DOCUMENT_TYPE_XSL = fed/document_type.json.xsl
REAL_ESTATE_TYPE_XSL = fed/real_estate_type.json.xsl
GLOSSARY_XSL = fed/glossary.json.xsl
DISCLAIMER_XSL = fed/disclaimer.json.xsl
GENERAL_INFORMATION_XSL = fed/general_information.json.xsl

$(THEMES_JSON): $(THEMES_XML) $(THEMES_XSL)
	xsltproc $(THEMES_XSL) $< > $@

$(THEMES_DOCS_JSON): $(THEMES_XML) $(THEMES_DOCS_XSL)
	xsltproc $(THEMES_DOCS_XSL) $< > $@

$(LAWS_JSON): $(LAWS_XML) $(LAWS_XSL)
	xsltproc $(LAWS_XSL) $< > $@

$(LAW_RESPONSIBLE_OFFICES_JSON): $(LAWS_XML) $(LAW_RESPONSIBLE_OFFICES_XSL)
	xsltproc $(LAW_RESPONSIBLE_OFFICES_XSL) $< > $@

$(LOGOS_JSON): $(LOGOS_XML) $(LOGOS_XSL)
	xsltproc $(LOGOS_XSL) $< > $@

$(LAW_STATUS_JSON): $(TEXTS_XML) $(LAW_STATUS_XSL)
	xsltproc $(LAW_STATUS_XSL) $< > $@

$(DOCUMENT_TYPE_JSON): $(TEXTS_XML) $(DOCUMENT_TYPE_XSL)
	xsltproc $(DOCUMENT_TYPE_XSL) $< > $@

$(REAL_ESTATE_TYPE_JSON): $(TEXTS_XML) $(REAL_ESTATE_TYPE_XSL)
	xsltproc $(REAL_ESTATE_TYPE_XSL) $< > $@

$(GLOSSARY_JSON): $(TEXTS_XML) $(GLOSSARY_XSL)
	xsltproc $(GLOSSARY_XSL) $< > $@

$(DISCLAIMER_JSON): $(TEXTS_XML) $(DISCLAIMER_XSL)
	xsltproc $(DISCLAIMER_XSL) $< > $@

$(GENERAL_INFORMATION_JSON): $(TEXTS_XML) $(GENERAL_INFORMATION_XSL)
	xsltproc $(GENERAL_INFORMATION_XSL) $< > $@

FED_JSONS = $(THEMES_JSON) \
	$(THEMES_DOCS_JSON) \
	$(LAWS_JSON) \
	$(LAW_RESPONSIBLE_OFFICES_JSON) \
	$(LOGOS_JSON) \
	$(LAW_STATUS_JSON) \
	$(DOCUMENT_TYPE_JSON) \
	$(REAL_ESTATE_TYPE_JSON) \
	$(GLOSSARY_JSON) \
	$(DISCLAIMER_JSON) \
	$(GENERAL_INFORMATION_JSON)

clean_fed_xmls:
	rm -f $(FED_XMLS)

clean_fed_jsons:
	rm -f $(FED_JSONS)

.PHONY: prepare_fed_data
prepare_fed_data: $(FED_JSONS)

clean_fed_data: clean_fed_xmls clean_fed_jsons

##########
# END FEDERAL DATA SECTION
##########


# **************
# Common targets
# **************

# Build dependencies
BUILD_DEPS += .venv/requirements-timestamp

$(DEV_CONFIGURATION_YML): .venv/requirements-timestamp $(DEV_CREATE_STANDARD_YML_SCRIPT)
	$(DEV_CREATE_STANDARD_YML_SCRIPT) --name $@ --database $(SQLALCHEMY_URL) --print_backend $(PRINT_BACKEND) --print_url $(PRINT_URL)

$(DEV_CREATE_SCRIPT): $(DEV_CONFIGURATION_YML) .venv/requirements-timestamp $(DEV_CREATE_TABLES_SCRIPT)
	$(DEV_CREATE_TABLES_SCRIPT) --configuration $< --sql-file $@

$(DEV_FILL_SCRIPT): $(DEV_CONFIGURATION_YML) .venv/requirements-timestamp $(DEV_CREATE_FILL_SCRIPT) $(FED_JSONS)
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
build: install $(DEV_CREATE_TABLES_SCRIPT) $(DEV_CREATE_STANDARD_YML_SCRIPT)

.PHONY: clean
clean: .db/.drop-db clean_fed_data
	rm -rf .db
	rm -f $(DEV_CONFIGURATION_YML)

.PHONY: clean-all
clean-all: clean
	rm -rf .venv
	rm -f *.png
	rm -f development.ini
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
test: .venv/requirements-timestamp .db/.setup-db-dev $(DEV_CONFIGURATION_YML)
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

development.ini: install
	$(VENV_BIN)/mako-render --var pyramid_oereb_port=$(PYRAMID_OEREB_PORT) development.ini.mako > development.ini
