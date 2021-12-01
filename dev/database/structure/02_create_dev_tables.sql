CREATE SCHEMA IF NOT EXISTS pyramid_oereb_main;

CREATE TABLE pyramid_oereb_main.address (
	street_name VARCHAR NOT NULL, 
	street_number VARCHAR NOT NULL, 
	zip_code INTEGER NOT NULL, 
	geom geometry(POINT,2056), 
	PRIMARY KEY (street_name, street_number, zip_code)
)

;

CREATE TABLE pyramid_oereb_main.disclaimer (
	id VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	content JSON NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE pyramid_oereb_main.document_types (
	code VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	PRIMARY KEY (code)
)

;

CREATE TABLE pyramid_oereb_main.general_information (
	id VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	content JSON NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE pyramid_oereb_main.glossary (
	id VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	content JSON NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE pyramid_oereb_main.law_status (
	code VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	PRIMARY KEY (code)
)

;

CREATE TABLE pyramid_oereb_main.logo (
	id VARCHAR NOT NULL, 
	code VARCHAR NOT NULL, 
	logo JSON NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE pyramid_oereb_main.map_layering (
	id VARCHAR NOT NULL, 
	view_service JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE pyramid_oereb_main.municipality (
	fosnr INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	published BOOLEAN DEFAULT FALSE NOT NULL, 
	geom geometry(MULTIPOLYGON,2056), 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE pyramid_oereb_main.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE pyramid_oereb_main.real_estate (
	id SERIAL NOT NULL, 
	identdn VARCHAR, 
	number VARCHAR, 
	egrid VARCHAR, 
	type VARCHAR NOT NULL, 
	canton VARCHAR NOT NULL, 
	municipality VARCHAR NOT NULL, 
	subunit_of_land_register VARCHAR, 
	subunit_of_land_register_designation VARCHAR, 
	fosnr INTEGER NOT NULL, 
	metadata_of_geographical_base_data VARCHAR, 
	land_registry_area INTEGER NOT NULL, 
	"limit" geometry(MULTIPOLYGON,2056), 
	PRIMARY KEY (id)
)

;

CREATE TABLE pyramid_oereb_main.real_estate_type (
	id VARCHAR NOT NULL, 
	code VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE pyramid_oereb_main.theme (
	id VARCHAR NOT NULL, 
	code VARCHAR NOT NULL, 
	sub_code VARCHAR, 
	title JSON NOT NULL, 
	extract_index INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (code, sub_code)
)

;

CREATE TABLE pyramid_oereb_main.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES pyramid_oereb_main.office (id)
)

;

CREATE TABLE pyramid_oereb_main.theme_document (
	theme_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	article_numbers JSON, 
	PRIMARY KEY (theme_id, document_id), 
	FOREIGN KEY(theme_id) REFERENCES pyramid_oereb_main.theme (id), 
	FOREIGN KEY(document_id) REFERENCES pyramid_oereb_main.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS land_use_plans;

CREATE TABLE land_use_plans.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE land_use_plans.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE land_use_plans.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE land_use_plans.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES land_use_plans.office (id)
)

;

CREATE TABLE land_use_plans.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES land_use_plans.office (id)
)

;

CREATE TABLE land_use_plans.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES land_use_plans.view_service (id)
)

;

CREATE TABLE land_use_plans.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES land_use_plans.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES land_use_plans.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES land_use_plans.legend_entry (id)
)

;

CREATE TABLE land_use_plans.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(GEOMETRYCOLLECTION,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES land_use_plans.public_law_restriction (id)
)

;

CREATE TABLE land_use_plans.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES land_use_plans.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES land_use_plans.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS motorways_project_planing_zones;

CREATE TABLE motorways_project_planing_zones.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE motorways_project_planing_zones.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE motorways_project_planing_zones.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE motorways_project_planing_zones.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES motorways_project_planing_zones.office (id)
)

;

CREATE TABLE motorways_project_planing_zones.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES motorways_project_planing_zones.office (id)
)

;

CREATE TABLE motorways_project_planing_zones.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES motorways_project_planing_zones.view_service (id)
)

;

CREATE TABLE motorways_project_planing_zones.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES motorways_project_planing_zones.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES motorways_project_planing_zones.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES motorways_project_planing_zones.legend_entry (id)
)

;

CREATE TABLE motorways_project_planing_zones.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(MULTIPOLYGON,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES motorways_project_planing_zones.public_law_restriction (id)
)

;

CREATE TABLE motorways_project_planing_zones.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES motorways_project_planing_zones.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES motorways_project_planing_zones.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS motorways_building_lines;

CREATE TABLE motorways_building_lines.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE motorways_building_lines.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE motorways_building_lines.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE motorways_building_lines.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES motorways_building_lines.office (id)
)

;

CREATE TABLE motorways_building_lines.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES motorways_building_lines.office (id)
)

;

CREATE TABLE motorways_building_lines.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES motorways_building_lines.view_service (id)
)

;

CREATE TABLE motorways_building_lines.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES motorways_building_lines.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES motorways_building_lines.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES motorways_building_lines.legend_entry (id)
)

;

CREATE TABLE motorways_building_lines.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(LINESTRING,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES motorways_building_lines.public_law_restriction (id)
)

;

CREATE TABLE motorways_building_lines.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES motorways_building_lines.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES motorways_building_lines.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS railways_project_planning_zones;

CREATE TABLE railways_project_planning_zones.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE railways_project_planning_zones.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE railways_project_planning_zones.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE railways_project_planning_zones.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES railways_project_planning_zones.office (id)
)

;

CREATE TABLE railways_project_planning_zones.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES railways_project_planning_zones.office (id)
)

;

CREATE TABLE railways_project_planning_zones.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES railways_project_planning_zones.view_service (id)
)

;

CREATE TABLE railways_project_planning_zones.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES railways_project_planning_zones.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES railways_project_planning_zones.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES railways_project_planning_zones.legend_entry (id)
)

;

CREATE TABLE railways_project_planning_zones.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(POLYGON,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES railways_project_planning_zones.public_law_restriction (id)
)

;

CREATE TABLE railways_project_planning_zones.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES railways_project_planning_zones.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES railways_project_planning_zones.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS railways_building_lines;

CREATE TABLE railways_building_lines.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE railways_building_lines.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE railways_building_lines.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE railways_building_lines.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES railways_building_lines.office (id)
)

;

CREATE TABLE railways_building_lines.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES railways_building_lines.office (id)
)

;

CREATE TABLE railways_building_lines.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES railways_building_lines.view_service (id)
)

;

CREATE TABLE railways_building_lines.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES railways_building_lines.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES railways_building_lines.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES railways_building_lines.legend_entry (id)
)

;

CREATE TABLE railways_building_lines.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(LINESTRING,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES railways_building_lines.public_law_restriction (id)
)

;

CREATE TABLE railways_building_lines.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES railways_building_lines.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES railways_building_lines.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS airports_project_planning_zones;

CREATE TABLE airports_project_planning_zones.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE airports_project_planning_zones.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE airports_project_planning_zones.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE airports_project_planning_zones.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES airports_project_planning_zones.office (id)
)

;

CREATE TABLE airports_project_planning_zones.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES airports_project_planning_zones.office (id)
)

;

CREATE TABLE airports_project_planning_zones.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES airports_project_planning_zones.view_service (id)
)

;

CREATE TABLE airports_project_planning_zones.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES airports_project_planning_zones.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES airports_project_planning_zones.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES airports_project_planning_zones.legend_entry (id)
)

;

CREATE TABLE airports_project_planning_zones.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(POLYGON,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES airports_project_planning_zones.public_law_restriction (id)
)

;

CREATE TABLE airports_project_planning_zones.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES airports_project_planning_zones.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES airports_project_planning_zones.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS airports_building_lines;

CREATE TABLE airports_building_lines.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE airports_building_lines.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE airports_building_lines.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE airports_building_lines.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES airports_building_lines.office (id)
)

;

CREATE TABLE airports_building_lines.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES airports_building_lines.office (id)
)

;

CREATE TABLE airports_building_lines.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES airports_building_lines.view_service (id)
)

;

CREATE TABLE airports_building_lines.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES airports_building_lines.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES airports_building_lines.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES airports_building_lines.legend_entry (id)
)

;

CREATE TABLE airports_building_lines.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(LINESTRING,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES airports_building_lines.public_law_restriction (id)
)

;

CREATE TABLE airports_building_lines.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES airports_building_lines.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES airports_building_lines.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS airports_security_zone_plans;

CREATE TABLE airports_security_zone_plans.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE airports_security_zone_plans.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE airports_security_zone_plans.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE airports_security_zone_plans.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES airports_security_zone_plans.office (id)
)

;

CREATE TABLE airports_security_zone_plans.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES airports_security_zone_plans.office (id)
)

;

CREATE TABLE airports_security_zone_plans.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES airports_security_zone_plans.view_service (id)
)

;

CREATE TABLE airports_security_zone_plans.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES airports_security_zone_plans.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES airports_security_zone_plans.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES airports_security_zone_plans.legend_entry (id)
)

;

CREATE TABLE airports_security_zone_plans.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(MULTIPOLYGON,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES airports_security_zone_plans.public_law_restriction (id)
)

;

CREATE TABLE airports_security_zone_plans.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES airports_security_zone_plans.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES airports_security_zone_plans.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS contaminated_sites;

CREATE TABLE contaminated_sites.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE contaminated_sites.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE contaminated_sites.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE contaminated_sites.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES contaminated_sites.office (id)
)

;

CREATE TABLE contaminated_sites.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES contaminated_sites.office (id)
)

;

CREATE TABLE contaminated_sites.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES contaminated_sites.view_service (id)
)

;

CREATE TABLE contaminated_sites.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES contaminated_sites.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES contaminated_sites.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES contaminated_sites.legend_entry (id)
)

;

CREATE TABLE contaminated_sites.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(GEOMETRYCOLLECTION,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES contaminated_sites.public_law_restriction (id)
)

;

CREATE TABLE contaminated_sites.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES contaminated_sites.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES contaminated_sites.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS contaminated_military_sites;

CREATE TABLE contaminated_military_sites.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE contaminated_military_sites.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE contaminated_military_sites.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE contaminated_military_sites.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES contaminated_military_sites.office (id)
)

;

CREATE TABLE contaminated_military_sites.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES contaminated_military_sites.office (id)
)

;

CREATE TABLE contaminated_military_sites.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES contaminated_military_sites.view_service (id)
)

;

CREATE TABLE contaminated_military_sites.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES contaminated_military_sites.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES contaminated_military_sites.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES contaminated_military_sites.legend_entry (id)
)

;

CREATE TABLE contaminated_military_sites.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(GEOMETRYCOLLECTION,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES contaminated_military_sites.public_law_restriction (id)
)

;

CREATE TABLE contaminated_military_sites.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES contaminated_military_sites.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES contaminated_military_sites.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS contaminated_public_transport_sites;

CREATE TABLE contaminated_public_transport_sites.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE contaminated_public_transport_sites.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE contaminated_public_transport_sites.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE contaminated_public_transport_sites.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES contaminated_public_transport_sites.office (id)
)

;

CREATE TABLE contaminated_public_transport_sites.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES contaminated_public_transport_sites.office (id)
)

;

CREATE TABLE contaminated_public_transport_sites.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES contaminated_public_transport_sites.view_service (id)
)

;

CREATE TABLE contaminated_public_transport_sites.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES contaminated_public_transport_sites.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES contaminated_public_transport_sites.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES contaminated_public_transport_sites.legend_entry (id)
)

;

CREATE TABLE contaminated_public_transport_sites.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(GEOMETRYCOLLECTION,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES contaminated_public_transport_sites.public_law_restriction (id)
)

;

CREATE TABLE contaminated_public_transport_sites.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES contaminated_public_transport_sites.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES contaminated_public_transport_sites.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS groundwater_protection_zones;

CREATE TABLE groundwater_protection_zones.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE groundwater_protection_zones.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE groundwater_protection_zones.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE groundwater_protection_zones.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES groundwater_protection_zones.office (id)
)

;

CREATE TABLE groundwater_protection_zones.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES groundwater_protection_zones.office (id)
)

;

CREATE TABLE groundwater_protection_zones.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES groundwater_protection_zones.view_service (id)
)

;

CREATE TABLE groundwater_protection_zones.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES groundwater_protection_zones.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES groundwater_protection_zones.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES groundwater_protection_zones.legend_entry (id)
)

;

CREATE TABLE groundwater_protection_zones.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(POLYGON,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES groundwater_protection_zones.public_law_restriction (id)
)

;

CREATE TABLE groundwater_protection_zones.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES groundwater_protection_zones.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES groundwater_protection_zones.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS groundwater_protection_sites;

CREATE TABLE groundwater_protection_sites.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE groundwater_protection_sites.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE groundwater_protection_sites.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE groundwater_protection_sites.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES groundwater_protection_sites.office (id)
)

;

CREATE TABLE groundwater_protection_sites.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES groundwater_protection_sites.office (id)
)

;

CREATE TABLE groundwater_protection_sites.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES groundwater_protection_sites.view_service (id)
)

;

CREATE TABLE groundwater_protection_sites.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES groundwater_protection_sites.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES groundwater_protection_sites.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES groundwater_protection_sites.legend_entry (id)
)

;

CREATE TABLE groundwater_protection_sites.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(POLYGON,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES groundwater_protection_sites.public_law_restriction (id)
)

;

CREATE TABLE groundwater_protection_sites.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES groundwater_protection_sites.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES groundwater_protection_sites.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS noise_sensitivity_levels;

CREATE TABLE noise_sensitivity_levels.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE noise_sensitivity_levels.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE noise_sensitivity_levels.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE noise_sensitivity_levels.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES noise_sensitivity_levels.office (id)
)

;

CREATE TABLE noise_sensitivity_levels.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES noise_sensitivity_levels.office (id)
)

;

CREATE TABLE noise_sensitivity_levels.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES noise_sensitivity_levels.view_service (id)
)

;

CREATE TABLE noise_sensitivity_levels.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES noise_sensitivity_levels.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES noise_sensitivity_levels.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES noise_sensitivity_levels.legend_entry (id)
)

;

CREATE TABLE noise_sensitivity_levels.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(POLYGON,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES noise_sensitivity_levels.public_law_restriction (id)
)

;

CREATE TABLE noise_sensitivity_levels.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES noise_sensitivity_levels.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES noise_sensitivity_levels.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS forest_perimeters;

CREATE TABLE forest_perimeters.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE forest_perimeters.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE forest_perimeters.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE forest_perimeters.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES forest_perimeters.office (id)
)

;

CREATE TABLE forest_perimeters.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES forest_perimeters.office (id)
)

;

CREATE TABLE forest_perimeters.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES forest_perimeters.view_service (id)
)

;

CREATE TABLE forest_perimeters.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES forest_perimeters.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES forest_perimeters.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES forest_perimeters.legend_entry (id)
)

;

CREATE TABLE forest_perimeters.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(LINESTRING,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES forest_perimeters.public_law_restriction (id)
)

;

CREATE TABLE forest_perimeters.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES forest_perimeters.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES forest_perimeters.document (id)
)

;
CREATE SCHEMA IF NOT EXISTS forest_distance_lines;

CREATE TABLE forest_distance_lines.availability (
	fosnr VARCHAR NOT NULL, 
	available BOOLEAN NOT NULL, 
	PRIMARY KEY (fosnr)
)

;

CREATE TABLE forest_distance_lines.office (
	id VARCHAR NOT NULL, 
	name JSON NOT NULL, 
	office_at_web JSON, 
	uid VARCHAR(12), 
	line1 VARCHAR, 
	line2 VARCHAR, 
	street VARCHAR, 
	number VARCHAR, 
	postal_code INTEGER, 
	city VARCHAR, 
	PRIMARY KEY (id)
)

;

CREATE TABLE forest_distance_lines.view_service (
	id VARCHAR NOT NULL, 
	reference_wms JSON NOT NULL, 
	layer_index INTEGER NOT NULL, 
	layer_opacity FLOAT NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE forest_distance_lines.data_integration (
	id VARCHAR NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	office_id VARCHAR NOT NULL, 
	checksum VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES forest_distance_lines.office (id)
)

;

CREATE TABLE forest_distance_lines.document (
	id VARCHAR NOT NULL, 
	document_type VARCHAR NOT NULL, 
	index INTEGER NOT NULL, 
	law_status VARCHAR NOT NULL, 
	title JSON NOT NULL, 
	office_id VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	text_at_web JSON, 
	abbreviation JSON, 
	official_number JSON, 
	only_in_municipality INTEGER, 
	file VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(office_id) REFERENCES forest_distance_lines.office (id)
)

;

CREATE TABLE forest_distance_lines.legend_entry (
	id VARCHAR NOT NULL, 
	symbol VARCHAR NOT NULL, 
	legend_text JSON NOT NULL, 
	type_code VARCHAR(40) NOT NULL, 
	type_code_list VARCHAR NOT NULL, 
	theme VARCHAR NOT NULL, 
	sub_theme VARCHAR, 
	view_service_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES forest_distance_lines.view_service (id)
)

;

CREATE TABLE forest_distance_lines.public_law_restriction (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	view_service_id VARCHAR NOT NULL, 
	office_id VARCHAR NOT NULL, 
	legend_entry_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(view_service_id) REFERENCES forest_distance_lines.view_service (id), 
	FOREIGN KEY(office_id) REFERENCES forest_distance_lines.office (id), 
	FOREIGN KEY(legend_entry_id) REFERENCES forest_distance_lines.legend_entry (id)
)

;

CREATE TABLE forest_distance_lines.geometry (
	id VARCHAR NOT NULL, 
	law_status VARCHAR NOT NULL, 
	published_from DATE NOT NULL, 
	published_until DATE, 
	geo_metadata VARCHAR, 
	geom geometry(LINESTRING,2056) NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES forest_distance_lines.public_law_restriction (id)
)

;

CREATE TABLE forest_distance_lines.public_law_restriction_document (
	id VARCHAR NOT NULL, 
	public_law_restriction_id VARCHAR NOT NULL, 
	document_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(public_law_restriction_id) REFERENCES forest_distance_lines.public_law_restriction (id), 
	FOREIGN KEY(document_id) REFERENCES forest_distance_lines.document (id)
)

;
