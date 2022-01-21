<% import re%>

.. _api-${module_name.replace('.', '-').lower()}:

*${module_name.split('.')[-1].title().replace('_', ' ')}*
${re.sub('.', '^', module_name.split('.')[-1].title().replace('_', ' ') + '  ')}

TODO: improve explication of how generic classes adapt to themes

The classes below are generated through a class builder factory and are customized for the different themes (TODO: insert link) which make up the app.

.. autoclass:: ${module_name}

%for cls in classes:

.. _api-${module_name.replace('.', '-').lower()}-${cls.lower()}:

${cls}
${re.sub('.', '~', cls)}

.. autoclass:: ${module_name}.${cls}

%endfor