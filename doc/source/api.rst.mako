.. _api:

OEREB API
=========

<%!
import glob, inspect, re, sys
%>
<%
modules = [m for m in sys.modules.keys() if m.startswith('pyramid_oereb')]
files = glob.glob('pyramid_oereb/*.py')
files += glob.glob('pyramid_oereb/*/*.py')
files += glob.glob('pyramid_oereb/*/*/*.py')
modules = [
    re.sub(r'\.__init__', '', f[:-3].replace("/", ".")) for f in files
    if not f.startswith("pyramid_oereb/tests/") and not f.startswith("pyramid_oereb/standard/templates/")
    and not f.startswith("pyramid_oereb/models.py")
]
for module in modules:
    __import__(module)
modules = [m for m in modules if m in sys.modules]

classes = {}
for module in modules:
    classes[module] = []
    for name, obj in inspect.getmembers(sys.modules[module]):
        if inspect.isclass(obj) and obj.__module__ == module:
            classes[module].append(name)
%>

%for module in modules:
    Module: ${module}
    --------${re.sub('.', '-', module)}

    .. automodule:: ${module}
       :members:

    %for cls in classes[module]:

    .. autoclass:: ${module}.${cls}
       :members:

    %endfor
%endfor
