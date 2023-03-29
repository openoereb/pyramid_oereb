.. _contrib-stats:

Statistics
==========

The statistics functionality allows you to gather usage information within pyramid_oereb
itself. The data gathered will be persisted in user defined configured database,
allowing the operator or owner of the application to query at any time
the usage statistics for that database.

The database structure necessary to hold the data will automatically be generated upon
first usage of the functionality. Once this structure has been generated, you may wish
to define in addition standard reporting views, see :ref:`standard-reporting` for more information.


Configuration
-------------

The functionality is configured via the server's ini file; see the project repository for a
complete example of such an ini file. Example of a configuration suitable for usage with Gunicorn:

.. code-block:: ini

    [loggers]
    keys = root, json, gunicorn.error

    [logger_json]
    level = INFO
    handlers = console, sqlalchemylogger
    qualname = JSON
    propagate = 0

    [handler_sqlalchemylogger]
    class = c2cwsgiutils.sqlalchemylogger.handlers.SQLAlchemyHandler
    args = ({'url':'postgresql://postgres:password@oereb-db:5432/oereb_stats','tablename':'logs','tableargs': {'schema':'oereb_logs'}},'healthcheck')
    level = NOTSET
    formatter = generic
    propagate = 0

    [logger_gunicorn.error]
    level=ERROR
    handlers=console
    propagate=0
    qualname=gunicorn.error

**args** is a tuple containing two elements:

- a dictionary: the db connection information
- a string: the blacklist regex

db connection information
~~~~~~~~~~~~~~~~~~~~~~~~~

The db connection information is a dictionary containing:

- *url* (mandatory): a db connection string compatible with sqlalchemy. Currently only sqlite and postgresql are supported. If using Docker, the db connection information has to be supplied in a file named *.env* at the root of the project (see file *sample.env* for an example)
- *tablename* (optional): if a special tablename has to be used within the database and will be mapped with *__tablename__* sqlalchemy class property
- *tableargs* (optional): another usual sqlalchemy class property (*__tableargs__*). In the above example we use it mainly to set a particular schema

The default values for the above optional arguments are:

- tablename = 'logs'
- tableargs = None (i.e. it will create the table in the *public* schema of the DB)

The sql logger source code with its documentation can be found here: https://github.com/camptocamp/c2cwsgiutils/tree/3.9.0/c2cwsgiutils/sqlalchemylogger

Blacklisting
~~~~~~~~~~~~

This is useful to avoid gathering statistics for non-relevant access logs, such as healthchecks.

The blacklist regex is any string compatible with the python module *re*. It will be compiled and used to avoid writing in the DB the logs that
match the given regex.  Please bear in mind that anything within the log that matches the
regex will prevent the log to be written. It is therefore discouraged to use regexes based on url path, which could match also user traffic
requests, which should be accounted in the statistics instead.

For example if *user-agent* http header of an healthcheck is set to some particular string (e.g. 'healthcheck' like in the above example),
then you should at least set 'healtcheck' explicitely and the logger will avoid writing any log containing the word healthcheck.

.. _standard-reporting:

Standard reporting
------------------

To fulfill the most common needs for statistics reporting, we recommend the usage of database views
based on the raw data table. You can create these views using the script *create_stats_tables*, or
by creating the following views in your database manually, and adapting them if needed:

.. code-block:: sql

  /*GetVersions view*/
  DROP VIEW IF EXISTS oereb_logs.stats_get_versions;
  CREATE OR REPLACE VIEW oereb_logs.stats_get_versions AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM oereb_logs.logs WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetVersions';
  /*GetCapabilities view*/
  DROP VIEW IF EXISTS oereb_logs.stats_get_capabilities;
  CREATE OR REPLACE VIEW oereb_logs.stats_get_capabilities AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM oereb_logs.logs WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetCapabilities';
  /*GetEgridCoord view*/
  DROP VIEW IF EXISTS oereb_logs.stats_get_egrid_coord;
  CREATE OR REPLACE VIEW oereb_logs.stats_get_egrid_coord AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'EN' AS en,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'GNSS' AS gnss,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM oereb_logs.logs WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetEgridCoord';
  /*GetEgridIdent view*/
  DROP VIEW IF EXISTS oereb_logs.stats_get_egrid_ident;
  CREATE OR REPLACE VIEW oereb_logs.stats_get_egrid_ident AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'IDENTDN' AS identdn,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'NUMBER' AS number,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM oereb_logs.logs WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetEgridIdent';
  /*GetEgridAddress view*/
  DROP VIEW IF EXISTS oereb_logs.stats_get_egrid_address;
  CREATE OR REPLACE VIEW oereb_logs.stats_get_egrid_address AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'POSTALCODE' AS postalcode,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'LOCALISATION' AS localisation,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> 'NUMBER' AS number,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM oereb_logs.logs WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetEgridAddress';
  /*GetExtractById view*/
  DROP VIEW IF EXISTS oereb_logs.stats_get_extract_by_id CASCADE;
  CREATE OR REPLACE VIEW oereb_logs.stats_get_extract_by_id AS
    SELECT cast(msg AS json) -> 'response' -> 'extras' ->> 'service' AS service ,
           cast(cast(msg AS json) -> 'response' ->> 'status_code' AS INTEGER) AS status_code,
           cast(msg AS json) -> 'response' -> 'extras' ->> 'output_format' AS output_format,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> '__flavour__' AS flavour,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> '__egrid__' AS egrid,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> '__identdn__' AS identdn,
           cast(msg AS json) -> 'response' -> 'extras' -> 'params' ->> '__number__' AS number,
           created_at,
           cast(msg AS json) -> 'request' ->> 'path' AS path
    FROM oereb_logs.logs WHERE logger = 'JSON' AND cast(msg AS json) -> 'response' ->'extras' ->> 'service' = 'GetExtractById';
  /*stats_daily_extract_by_id*/
  DROP VIEW IF EXISTS oereb_logs.stats_daily_extract_by_id;
  CREATE OR REPLACE VIEW oereb_logs.stats_daily_extract_by_id AS
    SELECT
        date_trunc('day', created_at) AS day,
        COUNT(1) AS nb_requests,
        COUNT(1) FILTER (WHERE  output_format = 'pdf') AS format_pdf,
        COUNT(1) FILTER (WHERE  output_format = 'json') AS format_json,
        COUNT(1) FILTER (WHERE  output_format = 'xml') AS format_xml
    FROM oereb_logs.stats_get_extract_by_id WHERE cast(status_code as INTEGER) = 200
    GROUP BY 1;


Implementation
--------------

<%! import glob, inspect, re, sys %>
<%
modules = [m for m in sys.modules.keys() if m.startswith('pyramid_oereb')]
files = glob.glob('../../pyramid_oereb/contrib/stats/*.py')
modules = [
    re.sub(r'\.__init__', '', f[6:-3].replace("/", ".")) for f in files
]

modules.sort()
delete_modules = []
for i, module in enumerate(modules):
    try:
        __import__(module)
    except ImportError:
        delete_modules.append(i)
delete_modules.reverse()
for i in delete_modules:
    del modules[i]

classes = {}
for module in modules:
    classes[module] = []
    for name, obj in inspect.getmembers(sys.modules[module]):
        if inspect.isclass(obj) and obj.__module__ == module:
            classes[module].append(name)

underline = ['^', '`', '\'', '.', '~', '*']
%>

%for module in modules:
.. _api-${module.replace('.', '-').lower()}:

.. automodule:: ${module}


%for cls in classes[module]:
.. _api-${module.replace('.', '-').lower()}-${cls.lower()}:

*${module.split('.')[-1].title().replace('_', ' ')} ${cls}*
${re.sub('.', underline[0], module.split('.')[-1] + '   ' + cls)}

.. autoclass:: ${module}.${cls}
   :members:
   :inherited-members:

   .. automethod:: __init__

%endfor
%endfor
