Changelog
=========

Notes:
------
- This python package specifies the version numbers only of directly imported python packages. This approach may result in a build failure of older versions of the project if incompatibilities arise between imported packages over time. The build process of the master branch is regularly tested in an automatic process.

Master
------
- Support of Oereblex API version 1.2.6 via geolink-formatter version 2.0.7 (#)

2.5.6
-----
Feature and maintenance release:

* Library upgrades (lxml, webtest, pyaml-env, geoalchemy2, flake8)
* Update JamesIves/github-pages-deploy-action action
* Improvements to the calculation of the number of pages of the table of contents (#2047)
* New parameter 'page_break_difference' allows customization of calculation of toc length (#2047)
* Initialization of pyramid_oereb processor at beginning of application start resulting in performance improvements (#2059)
  Changes to the configuration (municipalities, themes, etc.) of pyramid_oereb only apply after application restart now.
* Add workaround for failing test due to Python-version dependent numpy implementation (#2102)

2.5.5
-------------
- Library upgrades (pillow, pytest, webtest, waitress, codecov/codecov-action, geoalchemy, JamesIves/github-pages-deploy-action, urllib3)
- Reset Python Docker Tag to 3.12.5
- Support Oereblex API version 1.2.5 via geolink-formatter 2.0.6 (#2081)

2.5.4
-----
- New parameter default_toc_length to define a default table of content pages number (#2042)
- Add timeout in address source (#2043)
- Optimize legend entries retrieval (#2050)
- Library upgrades (waitress, sqlalchemy, psycopg2, urllib3)

2.5.3
-----
- Provide a general WMS verify certificate option
- Library upgrade (shapely)

2.5.2
-----
- Add configuration Option to check certificate for external WMS. Default setting: True
- Library upgrades (shapely, geoalchemy2, sqlalchemy, lxml)

2.5.1
-----
- Library upgrades (SQLAlchemy, shapely, geoalchemy2, responses, urllib3, lxml)

2.5.0
-----
- Use ST_DWithin instead of ST_Distance for performance reasons (#1930)
- Library upgrades (SQLAlchemy, geoalchemy2, urllib3, pypdf)

2.4.8
-----
- Support new Oereblex API version (via geolink-formatter 2.0.5)
- Enhance test coverage (#1904)
- Library upgrades (SQLAlchemy, lxml, jsonschema, c2cwsgiutils, pillow, pytest)
- Fix database setup scripts (#1913, #1914)
- Fix deprecation (#1915)

2.4.7
-----
- Add extract_index to disclaimer and general infomation (#1753). Note that this improvement requires an additional attribute "extract_index" in tables "general_information" and "disclaimer" of the main schema.
- Interlis bug fix (#1881)
- Library upgrades (geoalchemy2, SQLAlchemy, jsonschema, lxml, responses, urllib3, pypdf)
- Test coverage improvements
- Python 3.8 is no longer explicitly supported
- Remove print proxy xml2pdf, no longer used by the community (#1889)

2.4.6
-----
- Fix error with large of contents and new pdf library (#1813)
- Fix timestamp for archived PDF (#1815)
- Library upgrades (SQLAlchemy, geoalchemy2, shapely, psycopg2, pyreproj, pyramid, responses, urllib, pillow, pypdf, jsonschema)

2.4.5
-----
- Fix base layer usage in grouped PLRs (#1302)
- Various minor library upgrades (SQLAlchemy, geoalchemy2, pypdf, lxml, urllib3)

2.4.4
-----
- Add option for a hook method for LogoRef URLs (#929, #1744)
- Various minor library upgrades (urllib, requests, SQLAlchemy, geoalchemy2)

2.4.3
-----
- Add support for newest oereblex API (via geolink-formatter, #1703)
- Various minor library upgrades (SQLAlchemy, geoalchemy, psycopg2, pypdf)

2.4.2
-----
- Add print configuration parameter for municipality name (#1703)
- Various minor library upgrades (pyramid, shapely, grcode, pypdf)

2.4.1
-----
- Improve getegrid performance (#1680)
- Remove unwanted URL encoding for symbol_ref (#1678)
- Upgrade geolink_formatter library (#1682)
- Various minor library upgrades (#1688, #1689)

2.4.0
-----
- Upgrade to pyramid 2, shapely 2 (#1625, #1642, #1647, #1662)
- Various minor library upgrades
- Preparations for SQLAlchemy 2 upgrade (#1665)
- Python 3.8 is now the minimal recommended version of python

2.3.0
-----
- Add support for prepublinks (#1618)
- Allow to force real estate geometry output (#1619)
- Library updates (#1615, #1622)

2.2.6
-----
- Allow usage of xml2pdf service with embedded images (#1612, #1614)

2.2.5
-----
- Fix response code for parameter "url" (#1605)
- Fix order of change order of ExtractIdentifier & MunicipalityCode (#1606)
- Sort plr within themes (#1607)
- Minor library updates (#1609)

2.2.4
-----
- Support tolerance per geometry type (#1603)
- Library updates (#1604)

2.2.3
-----
- Fix xml2pdf proxy (#1596)
- Library updates (#1597, #1598)

2.2.2
-----
- Default index for oereblex documents (#1591)
- Sort theme lists (#1592)
- Library updates (#1593, #1595)

2.2.1
-----
- Add library needed for QR-Code (#1589)
- Various library updates (#1590)

2.2.0
-----
- Performance improvements (#1580)
- Add QR-Code functionality (#1579)
- Bug-fix for Other Legend (#1586)
- Add optional tolerance on geometric operations (#1571)
- Improve PDF filename when not using egrid (#1585)

2.1.1
-----
- Fix value for service version (#1576)
- Fix XML for localized image blob (#1577)
- Raise error in case of unsupported geometry type (#1578)

2.1.0
-----
- Move DataIntegration to application schema (#1549)
- Bug fix for document relevant only for one municipality (#1561)
- Bug fix for oereblex optional parameters (#1565)
- Library updates (#1567)

2.0.2
-----
- Oereblex integration: facilitate customization of title logic (#1556)
- Fix automated documentation publication (#1555)
- Improve automated testing of federal data (#1548)

2.0.1
-----
- Disclaimer, glossary and municipality are now read only on startup, to improve performance (#1544)
- Add support for OEREBlex prepubs URL (#1546)
- Fix real estate type in XML for GetEgrid (#1545)

2.0.0
-----
- Fix legend entry collection (#1529)
- Fix stats for GetEgrid (#1524)
- Update theme and texts URL according to swisstopo (#1526)
- Fix JSON response of GetEgrid (#1534)
- Fix error in Interlis model sub-code usage (#1538)
- Improve performance by moving availability to main schema and read only on startup (#1540)

2.0.0.rc2
---------
- Finalize stats reactivation (#1517)

2.0.0.rc1
---------
- Updates of all essential libraries used
- Fix multiple disclaimers in print (#1511)

2.0.0.b15
---------
- Fix capabilities extract (#1489)
- Fix real estate type in get egrid extract (#1491)
- Fix legend entry symbol selection (#1505)
- Add document sorting by index in print (#1504)

2.0.0.b14
---------
- Reorganize hook methos (#1484)
- Fix Office Record assignment (#1473)
- External library updates

2.0.0.b13
---------
- Fix collection of legend entries (#1482)

2.0.0.b12
---------
- Reactivate statistics functionality from V1 (#1480)
- Additional fix for static extract (#1478)

2.0.0.b11
---------
- Additional fix for static extract

2.0.0.b10
---------
- Fixes for static extract

2.0.0.b9
--------
- Fixes in configuration (#1445)

2.0.0.b8
--------
- Fix XML templates

2.0.0.b7
--------
- Fix sub-theme generation

2.0.0.b6
--------
- Improvements in error logging

2.0.0.b5
--------
- Fixes in Oereblex integration

2.0.0.b4
--------
- Fix JSON extract

2.0.0.b3
--------
- New federal data import tool and bug-fixes V2 (Status: beta)

2.0.0.b2
--------
- First fully functional implementation of new Oereb specification as per 28.10.11 (Status: beta)

2.0.0.b1
--------
- Implementation of the new Oereb specification 2021 (Status: beta)

1.9.2
-----
- Oereblex: improve testing functionality for Oereblex (#1197)
- Various library updates

1.9.1
-----
- Oereblex: support new Oereblex API version 1.2.1
- Various library updates

1.9.0
-----
- Oereblex: add configuration to pass URL parameters to the oereblex call (#1117)
- Various library updates
- Improve handling of empty geometries, in preparation of additional library updates (#1107)
- Print using MapFish Print: the inclusion of the cantonal logo is now configurable (#1139)

1.8.1
-----
- Update of external libraries such as numpy, SQLAlchemy, lxml, and more.
- oereblex support: avoid extract failure upon missing enactment_date in oereblex (#1093)
- Improve support of Python 3.7 in template Makefile and sample data loading (#1104, #1106)

1.8.0
-----
- Fix bug affecting concurrent requests (#1068)
- Enhance federal data import script to make it more usable with Docker (#1078)
- For full extracts, add configuration parameter to make additional sld usage optional (#1077)

1.7.6
-----
- Improve federal data import script (#1057)
- Last maintenance release with verified python2 compatibility

1.7.5
-----
- Update of all libraries used by pyramid_oereb that still work with python2

1.7.4
-----
- Federal data import script: add SLD_VERSION for legend_at_web (#1022)
- Oereblex integration: add optional configuration 'validation' (#1034)
- Restrict the version of the Shapely library used to 1.6 (#1037)

1.7.3
-----
- Fix import of federal data for cases including both coordinate reference systems (#1011)
- Oereblex: support geolink schema version 1.2.0 (#1010)
- Print: make geometry inclusion optional (performance improvement for MapFish Print) (#1006)

1.7.2
-----
- Test release only; not an official release.

1.7.1
-----
- Print: fix nr_of_points computation (#1002)

1.7.0
-----
- Oereblex: improve performance (implement per topic store) (#993)
- Add statistics functionality (#987)
- Print: fix table of contents page numbering (#983)

1.6.0
-----
- Improve multilingual support (#915, #918, #943, #950)
- Ensure XML schema compliance (#914, #926)
- Improve extract speed (#965)
- Additional options for sorting and grouping (#925, #931, #948, #979)
- Additional options for xml2pdf integration (#905, #938)
- Add PDF archive functionality (#982)
- Make WMS usage in print more flexible (#986)
- Bug fixes and debugging possibilities improvement (#910, #909, #897, #894, #916, #919, #870, #908, #932, #955, #958, #963, #970)

1.5.2
-----
- Provide multilingual OEREB logo (#915)
- Add file extension in logo and symbol URLs (#917)

1.5.1
-----
- Ensure XML Schema compliance (#872, #891)
- Fix polygon GML rendering (#830)
- Integration of ``XML2PDF`` service (#631, #883, #887)

1.5.0
-----
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
-----
- Fixed import script for federal topics (GitHub pull request 821)
- Added test for ordering of non-concerned themes (GitHub pull request 817)
- Fixed footer with disappearing page numbers with MapFish print 3.18 (GitHub pull request 814)

1.4.2
-----
- Downgrade version of pyproj to fix coordinate reprojections (GitHub pull request 810)
- Dependency updates

1.4.1
-----
- Fixed id types in oereblex models and model template, fixed documentation errors in standard models
  and model template  (GitHub pull request 807)
- Fixed warnings in tests (GitHub pull request 803)
- Dependency updates (GitHub pull request 805)

1.4.0
-----
- Additional multilingual functionality (GitHub issues 704, 705, 779)

1.3.1
-----
- Maintenance release (GitHub issues 447, 610, 590, 609, 757, 750, 681, 752, 753, 460, 736,
  666, 596, 678, 461, 751)

1.3.0
-----
- Import script for federal data

1.2.3
-----
- Bug-fix release for 1.2.2 (fix intersection bug, fix pdfreport template)

1.2.2
-----
- Further bug-fixes for oereb service versoin 1.0, notably regarding schema conformity
  and better support for other OS versions.
- New configuration parameter type_mapping in real_estate, which allows to configuratively
  define the texts to be used for realestate types (optional parameter).

1.2.1
-----
- Bug-fixes for service version 1.0 (pyramid_oereb 1.2.0),
  using results from pilot integration of new version at BL.

1.2.0
-----
- First implementation of federal extract requirements as per november 2017
  (service in version 1.0, extract in version 1.0.1, data model in version 1.0.1).
- Update of automated tests to correspond to new requirements.
- Static extract implementation update according to Weisung july 1st, 2018.
- Oereb lex model creation support and documentation.
- Bug fixes (legend entries, multiple view services, scaling in print, document titles in print).
- Facilitate customization of document title generation.

1.1.0
-----
- Final implementation of federal extract requirements as per november 2016
  (extract in version 0.8, data model in version 0.4).

1.0.1
-----

- introduce configurable pdf print service (print proxy)
- enable proxy configuration for external web api usage
- fix standard database
- improve python 3 compatibility
- minor bug fixing

1.0.0
-----

- improved doc
- fix bug for doc creation on python 3.6

1.0.0-beta.1
------------

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
-------------

-  proceed with renderer for xml and json
-  add metadata for embeddable flavour
-  images accessible via URL
-  add configurable methods for processing
-  improve geometry handling
-  add documentation on https://openoereb.github.io/pyramid_oereb/doc/
-  several bugfixes

1.0.0-alpha.1
-------------

-  first running approach of server
-  main web services are available (not all formats are implemented yet)
-  standard configuration can be used to run server out of the box
-  see README for more details

0.0.1
-----

-  initial version
