.. _api:

API
===

<%!
import glob
%>
<%
files = glob.glob('../pyramid_oereb/*.py')
files += glob.glob('../pyramid_oereb/*/*.py')
modules = [
    f[3:-3].replace("/", ".") for f in files
    if not f.startswith("../pyramid_oereb/tests/")
]
%>

%for module in modules:
.. automodule:: ${module}
   :members:

%endfor
