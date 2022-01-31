.. _base-sources:

Sources
-------

<%! import glob, inspect, re, sys %>
<%
modules = [m for m in sys.modules.keys() if m.startswith('pyramid_oereb')]
files = glob.glob('../../pyramid_oereb/core/sources/*.py')
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

*${cls}*
${re.sub('.', underline[0], 'Class   ' + cls)}

.. autoclass:: ${module}.${cls}
   :members:
   :inherited-members:

   .. automethod:: __init__

%endfor
%endfor