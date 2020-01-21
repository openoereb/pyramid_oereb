.. _contrib-stats:

Statistics
----------

The statistics functionality allows you to gather usage information within pyramid_oereb
itself. The data gathered will be persisted in configured database,
allowing the operator or owner of the application to query at any time
the usage statistics for that database.

The functionality is configured via the server's ini file; see the project repository for a
complete example of such an ini file.

Example of a configuration:

.. code-block:: python

    args = ({'url':'postgresql://postgres:password@oereb-db:5432/oereb_stats','tablename':'logs','tableargs': {'schema':'oereb_logs'}},'healthcheck')

**args** is a tuple containing two elements:

- a dictionnary: the db connection information
- a string: the blacklist regex

The db connection information is a dictionary containing:

- *url* (mandatory): a db connection string compatible with sqlalchemy. Currently only sqlite and postgresql are supported
- *tablename* (optionnal): if a special tablename has to be used within the database and will be mapped with *__tablename__* sqlalchemy class property
- *tableargs* (optionnal): another usual sqlalchemy class property (*__tableargs__*). In the above example we use it mainly to set a particular schema

The default values for the above optional arguments are:

- tablename = 'logs'
- tableargs = None (i.e. it will create the table in the *public* schema of the DB)

The sql logger source code with its documentation can be found here: https://github.com/camptocamp/c2cwsgiutils/tree/master/c2cwsgiutils/sqlalchemylogger

The blacklist regex is any string compatible with the python module *re*. It will be compiled and used to avoid writing in the DB the logs that
match the given regex. This is useful to avoid filling a DB with healtcheck access logs. For example, if the *user-agent* http header of an
healthcheck is set to some particular string (e.g. 'healthcheck' like in the above example), then you should at least set 'healtcheck' explicitely
and the logger will avoid writing any log containing the word healthcheck. Please bear in mind that anything within the log that matches the 
regex will prevent the log to be written. It is therefore discouraged to use regexes based on url path, which could match also user traffic
requests, which should be accounted in the statistics instead.


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
