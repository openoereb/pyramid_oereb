---------
Changelog
---------

1.2.1
*****
- Bug-fixes for service version 1.0 (pyramid_oereb 1.2.0),
  using results from pilot integration of new version at BL.

1.2.0
*****
- First implementation of federal extract requirements as per november 2017
  (service in version 1.0, extract in version 1.0.1, data model in version 1.0.1).
- Update of automated tests to correspond to new requirements.
- Static extract implementation update according to Weisung july 1st, 2018.
- Oereb lex model creation support and documentation.
- Bug fixes (legend entries, multiple view services, scaling in print, document titles in print).
- Facilitate customization of document title generation.

1.1.0
*****
- Final implementation of federal extract requirements as per november 2016
  (extract in version 0.8, data model in version 0.4).

1.0.1
*****

- introduce configurable pdf print service (print proxy)
- enable proxy configuration for external web api usage
- fix standard database
- improve python 3 compatibility
- minor bug fixing

1.0.0
*****

- improved doc
- fix bug for doc creation on python 3.6

1.0.0-beta.1
************

- first approach of OEREB server
- improved documentation on https://camptocamp.github.io/pyramid_oereb/doc/
- cleaned and reorganized code
- binding to OEREB-LEX and GeoAdmin-Api-Address-Service
  (http://api.geo.admin.ch/services/sdiservices.html#search) as sources
- providing pyconizer as icon generator (https://pypi.python.org/pypi/pyconizer)
- proxy binding of geomapfish_print for pdf output as renderer
  (http://mapfish.github.io/mapfish-print-doc/#/overview)
- providing extensive standard configuration for out-of-the-box-usage
- general bug fixing
- add python 3.x support

1.0.0-alpha.2
*************

-  proceed with renderer for xml and json
-  add metadata for embeddable flavour
-  images accessible via URL
-  add configurable methods for processing
-  improve geometry handling
-  add documentation on https://camptocamp.github.io/pyramid_oereb/doc/
-  several bugfixes

1.0.0-alpha.1
*************

-  first running approach of server
-  main web services are available (not all formats are implemented yet)
-  standard configuration can be used to run server out of the box
-  see README for more details

0.0.1
*****

-  initial version
