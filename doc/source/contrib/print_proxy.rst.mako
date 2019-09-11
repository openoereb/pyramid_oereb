.. _contrib-print_proxy:

Print Proxy
-----------

<%! import glob, inspect, re, sys %>
<%
modules = [m for m in sys.modules.keys() if m.startswith('pyramid_oereb')]
files = glob.glob('../../pyramid_oereb/contrib/print_proxy/*.py')
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

To properly configure the print service of GISDATEN AG you need to add the following in your yaml file inside
the print section:

.. code-block:: yaml

    print:
        renderer: pyramid_oereb.contrib.print_proxy.xml_2_pdf.Renderer
        # Base URL with application of the print server
        base_url: https://oereb-dev.gis-daten.ch/oereb/report/create
        token: 24ba4328-a306-4832-905d-b979388d4cab
        use_wms: "true"
        validate: "false"
        verify_certificate: false
        # The buffer on the map around the parcel in percent
        buffer: 10
        # The map size in pixel at 72 DPI (width, height), This is the defined size of a map image
        # (requested in wms urls) inside the static extract. On a pdf report, tha map size will
        # be calculated with the pdf_dpi and the pdf_map_size_millimeters below.
        basic_map_size: [493, 280]
        # The dpi used to calculate the size of the requested map (for pdf export only).
        pdf_dpi: 300
        # The map size (in millimeters) used to calculate the size of the requested map (for pdf export only).
        pdf_map_size_millimeters: [174, 99]
