<% import re%>
.. _api-${module_name}:

.. _api-${module_name.replace('.', '-').lower()}:

.. automodule:: ${module_name}


%for cls in classes[module_name]:
.. _api-${module_name.replace('.', '-').lower()}-${cls.lower()}:

*${module_name.split('.')[-1].title().replace('_', ' ')} ${cls}*
${re.sub('.', underline[0], module_name.split('.')[-1] + '   ' + cls)}

.. autoclass:: ${module_name}.${cls}
   :members:
   :inherited-members:

   .. automethod:: __init__

%endfor