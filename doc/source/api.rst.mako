.. _api:

API
===

<%!
import glob, inspect, re, sys, pyramid_oereb
%>
<%
reload(pyramid_oereb)
modules = [m for m in sys.modules.keys() if m.startswith('pyramid_oereb')]
files = glob.glob('../../pyramid_oereb/*.py')
files += glob.glob('../../pyramid_oereb/*/*.py')
files += glob.glob('../../pyramid_oereb/*/*/*.py')
files += glob.glob('../../pyramid_oereb/*/*/*/*.py')
files += glob.glob('../../pyramid_oereb/*/*/*/*/*.py')
modules = [
    re.sub(r'\.__init__', '', f[6:-3].replace("/", ".")) for f in files
    if not f.startswith("../../pyramid_oereb/tests/")
      and not f.startswith("../../pyramid_oereb/standard/templates/")
      and not f.startswith("../../pyramid_oereb/models.py")
]
modules.sort()
for module in modules:
    __import__(module)
modules = [m for m in modules if m in sys.modules]

classes = {}
for module in modules:
    classes[module] = []
    for name, obj in inspect.getmembers(sys.modules[module]):
        if inspect.isclass(obj) and obj.__module__ == module:
            classes[module].append(name)

underline = ['-', '`', '\'', '.', '~', '*']
%>

%for module in modules:
%if module != 'pyramid_oereb':
.. _api-${module.replace('.', '-').lower()}:

Module *${module.split('.')[-1]}*
${re.sub('.', underline[len(module.split('.')) - 2], 'Module   ' + module)}

.. automodule:: ${module}
   :members:

%for cls in classes[module]:
.. _api-${module.replace('.', '-').lower()}-${cls.lower()}:

Class *${cls}*
${re.sub('.', underline[len(module.split('.')) - 1], 'Class   ' + cls)}

.. autoclass:: ${module}.${cls}
   :members:

%endfor
%endif
%endfor
