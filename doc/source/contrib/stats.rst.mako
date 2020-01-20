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
