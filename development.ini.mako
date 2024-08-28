###
# app configuration
###

[app:main]
use = egg:pyramid_oereb

pyramid.reload_templates = false
pyramid.debug_authorization = false
pyramid.debug_notfound = false
pyramid.debug_routematch = false
pyramid.default_locale_name = en

pyramid_oereb.cfg.file = %(here)s/pyramid_oereb.yml
pyramid_oereb.cfg.section = pyramid_oereb

sqlalchemy.url = sqlite:///%(here)s/pyramid_oereb.sqlite

###
# wsgi server configuration
###

[server:main]
use = egg:waitress#main
host = 0.0.0.0
port = ${pyramid_oereb_port}

###
# logging configuration
###

[loggers]
keys = root, pyramid_oereb, sqlalchemy, json

[handlers]
keys = console, sqlalchemylogger

[formatters]
keys = generic

[logger_root]
level = DEBUG
handlers = console

[logger_pyramid_oereb]
level = DEBUG
handlers =
qualname = pyramid_oereb

[logger_sqlalchemy]
level = DEBUG
handlers =
qualname = sqlalchemy.engine
# "level = INFO" logs SQL queries.
# "level = DEBUG" logs SQL queries and results.
# "level = WARN" logs neither.  (Recommended for production systems.)

[logger_json]
level = INFO
handlers = console, sqlalchemylogger
qualname = JSON
propagate = 0

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[handler_sqlalchemylogger]
class = c2cwsgiutils.sqlalchemylogger.handlers.SQLAlchemyHandler
args = ({'url':'${pyramid_stats_url}','tablename':'logs','tableargs': {'schema':'oereb_logs'}},'healthcheck')
level = NOTSET
formatter = generic
propagate = 0

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s:%(lineno)s][%(threadName)s] %(message)s

[pserve]
