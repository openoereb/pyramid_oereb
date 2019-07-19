---------
Changelog
---------

1.5.0
*****
- Fixed a number formatting problem in the legend list (Mapfish Print, GitHub issue 824, pull request 826)
- Fixed an encoding issue for PLR records (GitHub pull request 828)
- Allow configuration of custom parameters for WMS calls in Mapfish Print (GitHub pull request 831)
- Section 'Certification' is now optional, can be configured in the Mapfish Print config (GitHub pull request 841)
- Only prints the PLR section of the PDF if at least one PLR is available (Mapfish Print, GitHub pull request 846)
- Various layout fixes in the table of contents of the Mapfish Print PDF (GitHub pull requests 842, 856, 859)
- Legends are now sorted by geometry type and value (Mapfish Print, GitHub pull request 851)
- Multiple ResponsibleOffices per theme are now rendered correctly (Mapfish Print, GitHub issue 651, pull request 865)
- PDF/A conformance enabled by default (Mapfish Print, GitHub pull request 852)
- In the XML output, LengthShare and NrOfPoints elements were moved to their correct place (GitHub issue 834, GitHub pull request 854)
- Optimized theme sorting (GitHub issue 443, GitHub pull request 858)
- Updated Mapfish Print to 3.20.0
- Dependency updates, better test coverage

1.4.3
*****
- Fixed import script for federal topics (GitHub pull request 821)
- Added test for ordering of non-concerned themes (GitHub pull request 817)
- Fixed footer with disappearing page numbers with MapFish print 3.18 (GitHub pull request 814)

1.4.2
*****
- Downgrade version of pyproj to fix coordinate reprojections (GitHub pull request 810)
- Dependency updates

1.4.1
*****
- Fixed id types in oereblex models and model template, fixed documentation errors in standard models
  and model template  (GitHub pull request 807)
- Fixed warnings in tests (GitHub pull request 803)
- Dependency updates (GitHub pull request 805)

1.4.0
*****
- Additional multilingual functionality (GitHub issues 704, 705, 779)

1.3.1
*****
- Maintenance release (GitHub issues 447, 610, 590, 609, 757, 750, 681, 752, 753, 460, 736,
  666, 596, 678, 461, 751)

1.3.0
*****
- Import script for federal data

1.2.3
*****
- Bug-fix release for 1.2.2 (fix intersection bug, fix pdfreport template)

1.2.2
*****
- Further bug-fixes for oereb service versoin 1.0, notably regarding schema conformity
  and better support for other OS versions.
- New configuration parameter type_mapping in real_estate, which allows to configuratively
  define the texts to be used for realestate types (optional parameter).

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
- improved documentation on https://openoereb.github.io/pyramid_oereb/doc/
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
-  add documentation on https://openoereb.github.io/pyramid_oereb/doc/
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
