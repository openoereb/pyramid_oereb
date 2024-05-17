# use different venv in a docker composition to prevent access conflicts
VENV_ROOT ?= .venv
# Check if running on CI
ifeq ($(CI),true)
  PIP_REQUIREMENTS=.requirements-timestamp
  VENV_BIN=${VENV_ROOT}/bin
  PIP_COMMAND=pip
else
  PIP_REQUIREMENTS=${VENV_ROOT}/.requirements-timestamp
  VENV_BIN=${VENV_ROOT}/bin
  PIP_COMMAND=pip3
endif

# Environment variables for DB connection
PGDATABASE ?= pyramid_oereb_test
PGSTATSDB ?= oereb_stats
PGHOST ?= localhost
PGUSER ?= postgres
PGPASSWORD ?= postgres
PGPORT ?= 5432
EXPOSED_PGPORT ?= 5432
PYRAMID_OEREB_PORT ?= 6543

export PGHOST
export PGPORT
export PGUSER
export PGPASSWORD

DOCKER_AS_ROOT ?= FALSE
ifneq ($(DOCKER_AS_ROOT), TRUE)
LOCAL_UID := $(shell id -u)
LOCAL_GID := $(shell id -g)
DOCKER_USER_OPTION = -u ${LOCAL_UID}:${LOCAL_GID}
endif

SQLALCHEMY_URL = "postgresql://$(PGUSER):$(PGPASSWORD)@$(PGHOST):$(PGPORT)/$(PGDATABASE)"
STATS_URL = "postgresql://$(PGUSER):$(PGPASSWORD)@$(PGHOST):$(PGPORT)/$(PGSTATSDB)"

PG_DEV_DATA_DIR = dev/sample_data

DEV_CONFIGURATION_YML = pyramid_oereb.yml
DEV_CREATE_FILL_SCRIPT = dev/database/load_sample_data.py
DEV_CREATE_STANDARD_YML_SCRIPT = $(VENV_BIN)/create_example_yaml
DEV_CREATE_MAIN_TABLES_SCRIPT = $(VENV_BIN)/create_main_schema_tables
DEV_CREATE_STANDARD_TABLES_SCRIPT = $(VENV_BIN)/create_standard_tables
DEV_CREATE_OEREBLEX_TABLES_SCRIPT = $(VENV_BIN)/create_oereblex_tables

MODEL_PK_TYPE_IS_STRING ?= true

PRINT_URL ?= http://oereb-print:8080/print/oereb

# ********************
# Variable definitions
# ********************

# Package name
PACKAGE = pyramid_oereb

# *******************
# Set up environments
# *******************

${VENV_ROOT}/timestamp:
	python3 -m venv ${VENV_ROOT}
	touch $@

${VENV_ROOT}/requirements-timestamp: ${VENV_ROOT}/timestamp pyproject.toml
	$(VENV_BIN)/$(PIP_COMMAND) install --upgrade pip wheel
	$(VENV_BIN)/$(PIP_COMMAND) install .[recommend] .[testing] .[dev]
	$(VENV_BIN)/$(PIP_COMMAND) install --editable .
	touch $@

##########
# FEDERAL DATA SECTION
##########

# URLS to fed data
include fed.urls

# XML files for creating XML files
FED_TMP = .fed
FED_CHECK = .fed_check
FED_TMP_TIMESTAMP = $(FED_TMP)/.create-timestamp

THEMES_XML = $(FED_TMP)/FED_THEMES.xml
LAWS_XML = $(FED_TMP)/FED_LAWS.xml
LOGOS_XML = $(FED_TMP)/FED_LOGOS.xml
TEXTS_XML = $(FED_TMP)/FED_TEXTS.xml

$(FED_TMP_TIMESTAMP):
	mkdir -p $(FED_TMP)
	mkdir -p $(FED_CHECK)
	touch $@

$(FED_TMP)/FED_%.xml: $(FED_TMP_TIMESTAMP)
	curl -X GET $($*_XML_URL) > $@

# JSON files for import into sample database
JSON_PREFIXES = ch.themes \
	ch.themes_docs \
	ch.laws \
	ch.law_responsible_offices \
	ch.logo \
	ch.law_status \
	ch.document_type \
	ch.real_estate_type \
	ch.glossary \
	ch.disclaimer \
	ch.general_information

FED_JSONS = $(foreach prefix, $(JSON_PREFIXES), $(FED_CHECK)/$(prefix).json)

FED_XSL_PATH = dev/database/fed

# override derived xml from downloaded one via symlink
# use hard link so that the system is not confused by a relative path
# FED_THEMES.xml based
$(FED_TMP)/themes.xml $(FED_TMP)/themes_docs.xml: $(THEMES_XML)
	ln $< $@

#FED_LAWS.xml based
$(FED_TMP)/laws.xml $(FED_TMP)/law_responsible_offices.xml: $(LAWS_XML)
	ln $< $@

# FED_LOGOS.xml based
$(FED_TMP)/logo.xml: $(LOGOS_XML)
	ln $< $@

# FED_TEXTS.xml based
$(FED_TMP)/law_status.xml $(FED_TMP)/document_type.xml $(FED_TMP)/real_estate_type.xml $(FED_TMP)/glossary.xml $(FED_TMP)/disclaimer.xml $(FED_TMP)/general_information.xml: $(TEXTS_XML)
	ln $< $@

# rule to generate json from correctly named xsl and xml
$(FED_CHECK)/ch.%.json: $(FED_XSL_PATH)/%.json.xsl $(FED_TMP)/%.xml
	xsltproc $^ > $@

.PHONY: prepare_fed_data
prepare_fed_data: $(FED_JSONS)


# rules for automatic check of correct federal definitions
.PHONY: compare_files_%
compare_files_%:
	diff $(FED_CHECK)/$* $(PG_DEV_DATA_DIR)/$*

COMPARE_ALL_JSONS = $(foreach prefix, $(JSON_PREFIXES), compare_files_$(prefix).json)

.PHONY: check_fed_data
check_fed_data: clean_fed_data prepare_fed_data $(COMPARE_ALL_JSONS)


# rules for update of fed urls and data
NEW_URL_INDEX=fed.urls.new
$(NEW_URL_INDEX):
	curl 'https://models.geo.admin.ch/?delimiter=/&prefix=V_D/OeREB/' | grep -Po '<Key>(.*?)</Key>' > $@

.PHONY: update_url_%
update_url_%: $(NEW_URL_INDEX)
	sed -i "s/OeREBKRM_V2_0_$*\(_.*\)\?\.xml/$(shell grep -Po OeREBKRM_V2_0_$*\(_.*\)?\.xml $<)/" fed.urls

.PHONY: remove_url_index
remove_url_index:
	rm -f $(NEW_URL_INDEX)

# try to find the updated URLs on line using the website's index
.PHONY: update_fed_data_urls
update_fed_data_urls: \
    update_url_Gesetze \
    update_url_Themen \
    update_url_Logos \
    update_url_Texte \
    remove_url_index

# hard apply the newly generated data to the project. Changes must then be committed
.PHONY: update_fed_data
update_fed_data_urls: prepare_fed_data
	cp $(FED_JSONS) $(PG_DEV_DATA_DIR)

# do everything automatically: find the new URLs, generate json data, copy json to project
.PHONY: auto_update_fed_data
auto_update_fed_data: clean_fed_data update_fed_data_urls update_fed_data

clean_fed_xmls:
	rm -f $(THEMES_XML) $(LAWS_XML) $(LOGOS_XML) $(TEXTS_XML)

clean_fed_jsons:
	rm -f $(FED_JSONS)

clean_fed_data: clean_fed_xmls clean_fed_jsons
	rm -rf .fed
	rm -rf .fed_check

##########
# END FEDERAL DATA SECTION
##########


# **************
# Common targets
# **************

# Build dependencies
BUILD_DEPS += ${VENV_ROOT}/requirements-timestamp

# ***********************
# START DEV-YAML creation
# ***********************

$(DEV_CONFIGURATION_YML): ${VENV_ROOT}/requirements-timestamp $(DEV_CREATE_STANDARD_YML_SCRIPT)
	$(DEV_CREATE_STANDARD_YML_SCRIPT) --name $@ --database $(SQLALCHEMY_URL) --print_url $(PRINT_URL)

# *********************
# END DEV-YAML creation
# *********************

# *********************
# START Set up database
# *********************

DB_STRUCTURE_PATH = dev/database/structure

DB_CREATE_EXTENSION = $(DB_STRUCTURE_PATH)/01_create_extension.sql
DB_CREATE_EXTENSION_SQL = CREATE EXTENSION IF NOT EXISTS postgis;

DB_DEV_TABLES_CREATE_SCRIPT = $(DB_STRUCTURE_PATH)/02_create_dev_tables.sql
DEV_CREATE_MAIN_TABLES_SCRIPT = $(VENV_BIN)/create_main_schema_tables
DEV_CREATE_STANDARD_TABLES_SCRIPT = $(VENV_BIN)/create_standard_tables
DEV_CREATE_OEREBLEX_TABLES_SCRIPT = $(VENV_BIN)/create_oereblex_tables

DB_DEV_TABLES_FILL_SCRIPT = $(DB_STRUCTURE_PATH)/03_fill_dev_tables.sql

$(DB_CREATE_EXTENSION):
	echo "$(DB_CREATE_EXTENSION_SQL)" > $@

$(DB_DEV_TABLES_CREATE_SCRIPT): $(DEV_CONFIGURATION_YML) ${VENV_ROOT}/requirements-timestamp $(DEV_CREATE_STANDARD_TABLES_SCRIPT) \
								$(DEV_CREATE_OEREBLEX_TABLES_SCRIPT) $(DEV_CREATE_MAIN_TABLES_SCRIPT)
	$(DEV_CREATE_MAIN_TABLES_SCRIPT) --configuration $< --sql-file $@
	$(DEV_CREATE_STANDARD_TABLES_SCRIPT) --configuration $< --sql-file $@
	$(DEV_CREATE_OEREBLEX_TABLES_SCRIPT) --configuration $< --sql-file $@

$(DB_DEV_TABLES_FILL_SCRIPT): $(DEV_CONFIGURATION_YML) ${VENV_ROOT}/requirements-timestamp $(DEV_CREATE_FILL_SCRIPT)
	$(VENV_BIN)/python $(DEV_CREATE_FILL_SCRIPT) --configuration $< --sql-file $@ --dir $(PG_DEV_DATA_DIR)

DB_STRUCTURE_SCRIPTS = $(DB_CREATE_EXTENSION) \
	$(DB_DEV_TABLES_CREATE_SCRIPT) \
	$(DB_DEV_TABLES_FILL_SCRIPT)

# Creates the sql files for the DEV database from SQL-Alchemy models and
# the generated DEV configuration (standard tables only!)
.PHONY: create_dev_db_scripts
create_dev_db_scripts: $(DB_STRUCTURE_SCRIPTS)

.PHONY: clean_dev_db_scripts
clean_dev_db_scripts:
	rm -rf $(DB_STRUCTURE_SCRIPTS)

# *********************
# END Set up database
# *********************

.PHONY: install
install: ${VENV_ROOT}/requirements-timestamp

$(DEV_CREATE_MAIN_TABLES_SCRIPT) $(DEV_CREATE_STANDARD_TABLES_SCRIPT) $(DEV_CREATE_OEREBLEX_TABLES_SCRIPT) $(DEV_CREATE_STANDARD_YML_SCRIPT): pyproject.toml $(BUILD_DEPS)

development.ini: install
	$(VENV_BIN)/mako-render --var pyramid_oereb_port=$(PYRAMID_OEREB_PORT) --var pyramid_stats_url=$(STATS_URL) development.ini.mako > development.ini

.PHONY: build
build: install $(DEV_CREATE_MAIN_TABLES_SCRIPT) $(DEV_CREATE_STANDARD_TABLES_SCRIPT) $(DEV_CREATE_OEREBLEX_TABLES_SCRIPT) $(DEV_CONFIGURATION_YML) create_dev_db_scripts development.ini

.PHONY: clean
clean: clean_fed_data clean_dev_db_scripts
	rm -f $(DEV_CONFIGURATION_YML)
	rm -f coverage.core.xml
	rm -f coverage.core_adapter.xml
	rm -f coverage.contrib-data_sources-standard.xml
	rm -f coverage.contrib-data_sources-interlis.xml
	rm -f coverage.contrib-data_sources-oereblex.xml
	rm -f coverage.contrib-data_sources-swisstopo.xml
	rm -f coverage.contrib-print_proxy-mapfish_print.xml
	rm -f coverage.contrib-stats.xml
	rm -f .coverage
	rm -rf tmp

.PHONY: clean-all
clean-all: clean
	rm -rf ${VENV_ROOT}
	rm -rf build
	rm -f development.ini
	rm -rf $(PACKAGE).egg-info

.PHONY: git-attributes
git-attributes:
	git --no-pager diff --check `git log --oneline | tail -1 | cut --fields=1 --delimiter=' '`

.PHONY: lint
lint: ${VENV_ROOT}/requirements-timestamp
	$(VENV_BIN)/flake8

.PHONY: test-postgres
test-postgres:
	psql postgresql://postgres:postgres@localhost:5432 -t -c "select 'test postgres';"

.PHONY: test-postgis
test-postgis:
	psql postgresql://postgres:postgres@localhost:5432 -t -c "select 'test postgres';"

.PHONY: test-core
test-core: ${VENV_ROOT}/requirements-timestamp
	$(VENV_BIN)/py.test -vv $(PYTEST_OPTS) --cov-config .coveragerc.core --cov $(PACKAGE)/core --cov-report=term-missing --cov-report=xml:coverage.core.xml tests/core

.PHONY: test-core_adapter
test-core_adapter: ${VENV_ROOT}/requirements-timestamp
	$(VENV_BIN)/py.test -vv $(PYTEST_OPTS) --cov-config .coveragerc.core_adapter --cov $(PACKAGE)/core --cov-report=term-missing --cov-report=xml:coverage.core_adapter.xml tests/core_adapter

.PHONY: test-contrib-print_proxy-mapfish_print
test-contrib-print_proxy-mapfish_print: ${VENV_ROOT}/requirements-timestamp
	mkdir ./tmp
	$(VENV_BIN)/py.test -vv $(PYTEST_OPTS) --cov-config .coveragerc.contrib-print_proxy-mapfish_print --cov $(PACKAGE) --cov-report xml:coverage.contrib-print_proxy-mapfish_print.xml tests/contrib.print_proxy.mapfish_print

.PHONY: test-contrib-data_sources-standard
test-contrib-data_sources-standard: ${VENV_ROOT}/requirements-timestamp
	$(VENV_BIN)/py.test -vv $(PYTEST_OPTS) --cov-config .coveragerc.contrib-data_sources-standard --cov $(PACKAGE)/contrib/data_sources/standard --cov-report=term-missing:skip-covered --cov-report=xml:coverage.contrib-data_sources-standard.xml tests/contrib.data_sources.standard

.PHONY: test-contrib-data_sources-interlis
test-contrib-data_sources-interlis: ${VENV_ROOT}/requirements-timestamp
	$(VENV_BIN)/py.test -vv $(PYTEST_OPTS) --cov-config .coveragerc.contrib-data_sources-interlis --cov $(PACKAGE)/contrib/data_sources/interlis_2_3 --cov-report=term-missing:skip-covered --cov-report=xml:coverage.contrib-data_sources-interlis.xml tests/contrib.data_sources.interlis_2_3

.PHONY: test-contrib-data_sources-swisstopo
test-contrib-data_sources-swisstopo: ${VENV_ROOT}/requirements-timestamp
	$(VENV_BIN)/py.test -vv $(PYTEST_OPTS) --cov-config .coveragerc.contrib-data_sources-swisstopo --cov $(PACKAGE)/contrib/data_sources/swisstopo --cov-report=term-missing:skip-covered --cov-report=xml:coverage.contrib-data_sources-swisstopo.xml tests/contrib.data_sources.swisstopo

.PHONY: test-contrib-data_sources-oereblex
test-contrib-data_sources-oereblex: ${VENV_ROOT}/requirements-timestamp
	$(VENV_BIN)/py.test -vv $(PYTEST_OPTS) --cov-config .coveragerc.contrib-data_sources-oereblex --cov $(PACKAGE)/contrib/data_sources/oereblex --cov-report=term-missing:skip-covered --cov-report=xml:coverage.contrib-data_sources-oereblex.xml tests/contrib.data_sources.oereblex

.PHONY: test-contrib-stats
test-contrib-stats: ${VENV_ROOT}/requirements-timestamp
	$(VENV_BIN)/py.test -vv $(PYTEST_OPTS) --cov-config .coveragerc.contrib-stats --cov $(PACKAGE)/contrib/stats --cov-report=xml:coverage.contrib-stats.xml tests/contrib.stats

.PHONY: tests
tests: ${VENV_ROOT}/requirements-timestamp test-core test-core_adapter test-contrib-print_proxy-mapfish_print test-contrib-data_sources-standard test-contrib-data_sources-interlis test-contrib-stats test-contrib-data_sources-swisstopo test-contrib-data_sources-oereblex

.PHONY: docker-tests
docker-tests:
	echo "Running tests as user ${LOCAL_UID}:${LOCAL_GID}"
	docker compose run --rm -e PGHOST=oereb-db -e UID=${LOCAL_UID} -e GID=${LOCAL_GID} oereb-server make build lint tests
	docker compose down

.PHONY: docker-clean-all
docker-clean-all:
	docker compose run --rm oereb-make clean-all

.PHONY: check
check: git-attributes lint tests

.PHONY: doc-latex
doc-latex: ${VENV_ROOT}/requirements-timestamp
	rm -rf doc/build/latex
	$(VENV_BIN)/sphinx-build -b latex doc/source doc/build/latex

.PHONY: doc-html
doc-html: ${VENV_ROOT}/requirements-timestamp
	rm -rf doc/build/html
	$(VENV_BIN)/sphinx-build -b html doc/source doc/build/html

.PHONY: updates
updates: ${VENV_ROOT}/requirements-timestamp
	$(VENV_BIN)/pip list --outdated

.PHONY: serve-dev
serve-dev: development.ini build
	docker compose up -d oereb-db
	$(VENV_BIN)/pserve $< --reload

.PHONY: serve
serve: development.ini build
	docker compose up -d oereb-db
	$(VENV_BIN)/pserve $<
