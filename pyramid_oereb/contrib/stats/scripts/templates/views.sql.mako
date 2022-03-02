/*GetVersions view*/
DROP VIEW IF EXISTS ${schema_name|u}.stats_get_versions;
CREATE OR REPLACE VIEW ${schema_name|u}.stats_get_versions AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM ${schema_name|u}.${tablename|u} WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetVersions';

/*GetCapabilities view*/
DROP VIEW IF EXISTS ${schema_name|u}.stats_get_capabilities;
CREATE OR REPLACE VIEW ${schema_name|u}.stats_get_capabilities AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM ${schema_name|u}.${tablename|u} WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetCapabilities';

/*GetEgridCoord view*/
DROP VIEW IF EXISTS ${schema_name|u}.stats_get_egrid_coord;
CREATE OR REPLACE VIEW ${schema_name|u}.stats_get_egrid_coord AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'EN' AS en,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'GNSS' AS gnss,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM ${schema_name|u}.${tablename|u} WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetEgridCoord';

/*GetEgridIdent view*/
DROP VIEW IF EXISTS ${schema_name|u}.stats_get_egrid_ident;
CREATE OR REPLACE VIEW ${schema_name|u}.stats_get_egrid_ident AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'IDENTDN' AS identdn,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'NUMBER' AS number,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM ${schema_name|u}.${tablename|u} WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetEgridIdent';

/*GetEgridAddress view*/
DROP VIEW IF EXISTS ${schema_name|u}.stats_get_egrid_address;
CREATE OR REPLACE VIEW ${schema_name|u}.stats_get_egrid_address AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'POSTALCODE' AS postalcode,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'LOCALISATION' AS localisation,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'NUMBER' AS number,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM ${schema_name|u}.${tablename|u} WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetEgridAddress';

/*GetExtractById view*/
DROP VIEW IF EXISTS ${schema_name|u}.stats_get_extract_by_id CASCADE;
CREATE OR REPLACE VIEW ${schema_name|u}.stats_get_extract_by_id AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> '__flavour__' AS flavour,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> '__egrid__' AS egrid,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> '__identdn__' AS identdn,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> '__number__' AS number,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM ${schema_name|u}.${tablename|u} WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetExtractById';

/*stats_daily_extract_by_id*/
DROP VIEW IF EXISTS ${schema_name|u}.stats_daily_extract_by_id;
CREATE OR REPLACE VIEW ${schema_name|u}.stats_daily_extract_by_id AS
    SELECT
        date_trunc('day', created_at) AS day,
        COUNT(1) AS nb_requests,
        COUNT(1) FILTER (WHERE  output_format = 'pdf') AS format_pdf,
        COUNT(1) FILTER (WHERE  output_format = 'json') AS format_json,
        COUNT(1) FILTER (WHERE  output_format = 'xml') AS format_xml
    FROM ${schema_name|u}.stats_get_extract_by_id WHERE cast(status_code as INTEGER) = 200
    GROUP BY 1;
