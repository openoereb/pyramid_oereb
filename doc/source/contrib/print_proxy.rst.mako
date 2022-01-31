.. _contrib-print_proxy:

Print Proxy
-----------

<%! import glob, inspect, re, sys %>
<%
modules = [m for m in sys.modules.keys() if m.startswith('pyramid_oereb')]
files = glob.glob('../../pyramid_oereb/contrib/print_proxy/mapfish_print/*.py')
files += glob.glob('../../pyramid_oereb/contrib/print_proxy/xml_2_pdf/*.py')
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


Sub themes
----------

To enable separate pages per sub theme, enable the option `split_sub_themes` in the `print` section of your
configuration.


.. code-block:: yaml

    print:
        split_sub_themes: true


You can influence the sort order for each theme separately. Per default, the sub themes are unsorted.

Example for alphabetic sort:

.. code-block:: yaml

    - name: plr119
      sub_themes:
        sorter:
            module: pyramid_oereb.contrib.print_proxy.sub_themes.sorting
            class_name: AlphabeticSort


The list sort provides a fix, non-alphabetic order. A ordered list as parameter defines the order. The sub theme names
have to match exactly, otherwise they will be added at the end. Example configuration:

.. code-block:: yaml

    - name: plr119
      sub_themes:
        sorter:
            module: pyramid_oereb.contrib.print_proxy.sub_themes.sorting
            class_name: ListSort
            params:
                list:
                    - First sub theme
                    - Another sub theme
                    - Last sub theme

Print configuration
-------------------

**XML2PDF**

To properly configure the XML2PDF print service of GISDATEN AG, you need specific configuration in the section
``print`` of your ``yaml`` file.
Please see the `standard configuration file
<https://github.com/openoereb/pyramid_oereb/blob/master/pyramid_oereb/standard/pyramid_oereb.yml.mako>`__
as an example, or use the ``create_standard_yaml`` script to regenerate your configuration file with the desired options.
