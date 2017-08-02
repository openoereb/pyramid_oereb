<% import re%>

.. _api-${module_name.replace('.', '-').lower()}:

*${module_name.split('.')[-1].title().replace('_', ' ')}*
${re.sub('.', '^', module_name.split('.')[-1].title().replace('_', ' ') + '  ')}

.. automodule:: ${module_name}

%for cls in classes:

.. _api-${module_name.replace('.', '-').lower()}-${cls.lower()}:

${cls}
${re.sub('.', '~', cls)}

.. autoclass:: ${module_name}.${cls}
   :members:
   :inherited-members:

   .. automethod:: __init__

%endfor