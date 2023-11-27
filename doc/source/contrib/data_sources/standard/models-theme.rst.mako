.. _contrib-data-sources-standard-models-theme:

ORM Theme schema
````````````````

<%!
import glob, inspect, re, sys
from pyramid_oereb.core.config import Config
Config._config = {'srid': -1, 'app_schema': {'name': 'pyramid_oereb_main'}}
%>
<%
modules = [m for m in sys.modules.keys() if m.startswith('pyramid_oereb')]
files = glob.glob('../../pyramid_oereb/contrib/data_sources/standard/models/theme.py')
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

*${module.split('.')[-1].title()} ${cls}*
${underline[2]*len("*"+module.split('.')[-1].title()+' '+cls+"*")}

.. autoclass:: ${module}.${cls}
   :members:
   :inherited-members:
   :show-inheritance:

   .. automethod:: __init__

%endfor
%endfor