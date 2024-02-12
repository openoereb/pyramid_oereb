.. _changes:

Changes/Hints for migration
===========================

This chapter will give you hints on how to handle version migration, in particular regarding what you may need
to adapt in your project configuration, database etc. when upgrading to a new version.

Version 2.5.0
-------------
Performance optimization release:

* Use ST_DWithin instead of ST_Distance for performance reasons (#1930)
* Library upgrades (SQLAlchemy, geoalchemy2, urllib3, pypdf)

Version 2.4.8
-------------
Maintenance release:

* Support new Oereblex API version (via geolink-formatter 2.0.5)
* Enhance test coverage (#1904)
* Library upgrades (SQLAlchemy, lxml, jsonschema, c2cwsgiutils, pillow, pytest)
* Fix database setup scripts (#1913, #1914)
* Fix deprecation (#1915)

Version 2.4.7
-------------
Bug-fix and maintenance release:

* Interlis bug fix (#1881)
* Library upgrades (geoalchemy2, SQLAlchemy, jsonschema, lxml, responses, urllib3, pypdf)
* Test coverage improvements
* Python 3.8 is no longer explicitly supported
* Remove print proxy xml2pdf, no longer used by the community (#1889)

Version 2.4.6
-------------
Bug-fix and maintenance release:

* Fix error with large of contents and new pdf library (#1813)
* Fix timestamp for archived PDF (#1815)
* Library upgrades (SQLAlchemy, geoalchemy2, shapely, psycopg2, pyreproj, pyramid, responses, urllib, pillow, pypdf, jsonschema)

Version 2.4.5
-------------
Bug-fix and maintenance release:

* Fix base layer usage in grouped PLRs (#1302)
* Various minor library upgrades (SQLAlchemy, geoalchemy2, pypdf, lxml, urllib3)

Version 2.4.4
-------------
Make the logo lookup logic configurable:

* Add option for a hook method for LogoRef URLs (#929, #1744).
  In the section ``logos``, you must add a configuration section ``hooks``
  defining the logic for the logo and the QR code. To use the standard logic, define:

.. code-block:: python

    logos:
      ...
      hooks:
        get_logo_ref: pyramid_oereb.core.hook_methods.get_logo_ref
        get_qr_code_ref: pyramid_oereb.core.hook_methods.get_qr_code_ref

* Various minor library upgrades (urllib, requests, SQLAlchemy, geoalchemy2)

Version 2.4.3
-------------
Maintenance release:

* Add support for newest oereblex API (via geolink-formatter, #1703)
* Various minor library upgrades (SQLAlchemy, geoalchemy, psycopg2, pypdf)
  

Version 2.4.2
-------------
Maintenance release, with a new configuration option:

* Various minor library upgrades (pyramid, shapely, grcode, pypdf)

MapFish Print related changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you are using MapFish Print, you must update your print templates and configuration to v2.4.2.
The following configuration option has been added:

 * The output of the municipality name is now configurable (#1703).
   MapFish Print users who do not want the municipality name should set the print configuration parameter
   ``print_municipality_name`` to ``false``.


.. _changes-version-2.4.1:

Version 2.4.1
-------------
Maintenance release with performance improvement:

* Improve getegrid performance (#1680)
* Remove unwanted URL encoding for symbol_ref (#1678)
* Upgrade geolink_formatter library (#1682)
* Various minor library upgrades (#1688, #1689)

.. _changes-version-2.4.0:

Version 2.4.0
-------------
Maintenance release with major library updates:

* Upgrade to pyramid 2, shapely 2 (#1625, #1642, #1647, #1662)
* Various minor library upgrades
* Preparations for SQLAlchemy 2 upgrade (#1665)
* Python 3.8 is now the minimal recommended version of python

.. _changes-version-2.3.0:

Version 2.3.0
-------------
New functionality for prepub, and maintenance issues:

* Add support for prepublinks (#1618)
* Allow to force real estate geometry output (#1619), useful for xml2pdf
* Library updates (#1615, #1622)

.. _changes-version-2.2.6:

Version 2.2.6
-------------
Bug-fix release to allow usage of xml2pdf service with embedded images (#1612, #1614)

.. _changes-version-2.2.5:

Version 2.2.5
-------------
Bug-fix and maintenance release:

* Fix response code for parameter "url" (#1605)
* Fix order of change order of ExtractIdentifier & MunicipalityCode (#1606)
* Sort plr within themes (#1607)
* Minor library updates (#1609)

.. _changes-version-2.2.4:

Version 2.2.4
-------------
New functionality for configuring tolerance (optional):

* Support tolerance per geometry type (#1603). See example definitions in the example project configuration file. 
* Library updates (#1604)

.. _changes-version-2.2.3:

Version 2.2.3
-------------
Bug-fix and maintenance release:

* Fix xml2pdf proxy (#1596)
* Library updates (#1597, #1598)

.. _changes-version-2.2.2:

Version 2.2.2
-------------
Bug-fix and maintenance release:

* Default index for oereblex documents (#1591)
* Sort theme lists (#1592)
* Library updates (#1593, #1595)

.. _changes-version-2.2.1:

Version 2.2.1
-------------
Maintenance release building on the features introduced in 2.2.0:

 * Add library needed for QR-Code (#1589)
 * Various library updates (#1590)

.. _changes-version-2.2.0:

Version 2.2.0
-------------
This version introduces new features, performance improvements and include a bug-fix:

 * Performance improvements (#1580)
 * Add QR-Code functionality (#1579)
 * Bug-fix for Other Legend (#1586)
 * Add optional tolerance on geometric operations (#1571)
 * Improve PDF filename when not using egrid (#1585)

.. _changes-version-2.1.1:

Version 2.1.1
-------------
Bug-fix release:

 * Fix value for service version (#1576)
 * Fix XML for localized image blob (#1577)
 * Raise error in case of unsupported geometry type (#1578)

.. _changes-version-2.1.0:

Version 2.1.0
-------------
To update to this version, if you are using data_integration tables, you must consolidate this content in
the main application schema instead. Full list of changes in this version:

 * Move DataIntegration to application schema (#1549)
 * Bug fix for document relevant only for one municipality (#1561)
 * Bug fix for oereblex optional parameters (#1565)
 * Library updates (#1567

.. _changes-version-2.0.2:

Version 2.0.2
-------------
Bug-fix release:

 * Oereblex integration: facilitate customization of title logic (#1556)
 * Fix automated documentation publication (#1555)
 * Improve automated testing of federal data (#1548)

.. _changes-version-2.0.1:

Version 2.0.1
-------------
Bug-fix and performance optimization release:

 * Disclaimer, glossary and municipality are now read only on startup (#1544)
 * Add support for OEREBlex prepubs URL (#1546)
 * Fix real estate type in XML for GetEgrid (#1545)

.. _changes-version-2.0.0:

Version 2.0.0
-------------
Version 2 is the implementation of the new federal requirements 2021. Because the data model specified by
the federation is not compatible with the model in the previous version, a migration to version 2
requires a new setup.

.. _changes-version-1.9.2:

Version 1.9.2
-------------

 * Oereblex: improve testing functionality for Oereblex (#1197)
 * Various library updates


.. _changes-version-1.9.1:

Version 1.9.1
-------------

 * Oereblex: support new Oereblex API version 1.2.1
 * Various library updates


.. _changes-version-1.9.0:

Version 1.9.0
-------------

 * Oereblex: add configuration option to pass URL parameters to the oereblex call (#1117)
 * Various library updates
 * Improve handling of empty geometries, in preparation of additional library updates (#1107)

MapFish Print related changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you are using MapFish Print, you must update your print templates and configuration to v1.9.0.
The following improvements have been made:

 * The inclusion of the cantonal logo is now configurable (#1139).
   MapFish Print users who do not want the cantonal logo should set the print configuration parameter
   ``print_canton_logo`` to ``false``.


.. _changes-version-1.8.1:

Version 1.8.1
-------------
This is a maintenance release with minor updates:

 * Update of external libraries such as numpy, SQLAlchemy, lxml, and more.
 * oereblex support: avoid extract failure upon missing enactment_date in oereblex (#1093)
 * Improve support of Python 3.7 in template Makefile and sample data loading (#1104, #1106)


.. _changes-version-1.8.0:

Version 1.8.0
-------------
This release contains the following bug-fixes and improvements:

 * Fix bug affecting concurrent requests (#1068)
 * Enhance federal data import script to make it more usable with Docker (#1078)
 * For full extracts, add configuration parameter to make additional sld usage optional (#1077)

Note that this release requires Python 3.6 or higher.


.. _changes-version-1.7.6:

Version 1.7.6
-------------
This is a maintenance release with the following changes:

 * Improve federal data import script (#1057)
 * Update of all libraries used by pyramid_oereb that still work with Python2

This is the final maintenance release that includes Python2 compatibility.


.. _changes-version-1.7.4:

Version 1.7.4
-------------
This is a maintenance release with the following changes:

 * Federal data import script: add SLD_VERSION for legend_at_web (#1022)
 * Oereblex integration: add optional configuration 'validation' to be able to deactivate
   XML validation (#1034)
 * Restrict the version of the Shapely library used to 1.6 (#1037), to avoid problems with
   geometries which are valid according to INTERLIS but invalid according to OGC.


.. _changes-version-1.7.3:

Version 1.7.3
-------------
This is a maintenance release, with some bug-fixes (#1005, #1012) and library dependency updates,
and the following new functionality:

Oereblex related changes
^^^^^^^^^^^^^^^^^^^^^^^^
pyramid_oereb now supports and uses by default the Oereblex geoLink schema version 1.2.0 (#1010):

* New doctype 'notice' (will be classified as 'HintRecord'). If you want to add related notices as
  additional legal provisions directly on public law restrictions, you should set the new oereblex
  'related_notice_as_main' flag in the config of the project.
* 'Notice' can have no authority nor enactment_date. In this case, the enactment date will be
  '01.01.1970' and the authority '-'.
* 'Notice' can have no authority_at_web. In previous versions, this was not supported by MapFish Print.
  If you use MapFish Print with Oereblex 1.2.0, you must update your MapFish Print templates.
* The new document attribute 'language' and the new file attribute 'description' are currently not used by
  pyramid_oereb, but are now available to custom code, for example for document title generation.

MapFish Print related changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you are using MapFish Print, you must update your print templates and configuration to v1.7.3.
The following improvements have been made:

* The inclusion of all geometry data in the print payload is now configurable (#1006).
  MapFish Print users should set the print configuration parameter ```with_geometry``` to ```False```
  to improve performance.
* It is now allowed to print reports with missing OfficeAtWeb information in documents, because
  OfficeAtWeb is an optional attribute in the specification (#62).


.. _changes-version-1.7.1:

Version 1.7.1
-------------
This is a bug-fix release, relevant only for users of MapFish Print.

MapFish Print related changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The computation of the "nr_of_points" used in the PDF generation has been fixed (#1002),
and a redundant comma has been removed from the templates (pyramid_oereb_mfp #59).
You should update your print templates and print configuration to release v1.7.1 of pyramid_oereb_mfp.


.. _changes-version-1.7.0:

Version 1.7.0
-------------
This release includes some features requested by the user group, as well as bug-fixes:

* The performance of the Oereblex integration was improved, by using a per topic store (#993). No change in
  configuration is needed.

* A new statistics functionality was added (#987). If you wish to use this functionality, see :ref:`contrib-stats`.

* If you are using MapFish Print, you must update your configuration as described in the following section.

MapFish Print related changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In the print via MapFish Print, the table of contents page numbering was fixed (#983). The following configuration
changes are necessary:

* In your pyramid_oereb project configuration, replace the print configuration parameter ``multi_page_TOC``
  with the parameter ``compute_toc_pages``; see the standard configuration file for an example and the description.

* In your print application, update your print templates and print configuration to release v1.7.0 of pyramid_oereb_mfp.


.. _changes-version-1.6.0:

Version 1.6.0
-------------
This release includes some features requested by the user group, as well as bug-fixes,
please see the release notes for a complete list. In this page, we list the changes
which potentially affect your project configuration or custom code:

* The OEREB logo is now multilingual (#915). See standard project configuration template for how to configure it.

* Logo and symbol URLs now have file extensions (#917).
  Image types are now restricted to *PNG* and *SVG*, according to the federal specification.
  If you are using other image formats, you must convert them to one of the allowed types when migrating.

* Extract parameters are now passed to all readers and sources, to support multilingual oereblex integration (#943).
  If you have custom readers or sources (for example, to customize oereblex responses), you will need to adapt your code.

* An optional sorting of PLRs can be used via parameter ``sort_within_themes_method`` (#979).

MapFish Print related changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you are using MapFish Print, you must update your print templates and configuration to v1.6.0.
The following functionality is now available for configuration:

* You can group LegalProvisions by using the new parameter ``group_legal_provisions`` (#948).

* If you wish to keep generated PDFs on the server, use the new parameter ``pdf_archive_path`` (#982).

* If you need to keep specific parameters from your WMS URLs when printing, use the new section ``wms_url_keep_params`` (#986).

XML2PDF related changes
^^^^^^^^^^^^^^^^^^^^^^^
If you are using XML2PDF, you have the following new configuration options:

* ``verify_certificate`` (#905)

* proxy configuration (#938)


.. _changes-version-1.5.1:

Version 1.5.1
-------------
This version contains bug-fixes and provides additional functionality: the integration of the XML2PDF
service. The usage of this service is optional, if you do not use it, you do not need to change anything in your setup
(as compared to version :ref:`changes-version-1.5.0`). Significant changes:

* Ensure XML Schema compliance (#872, #891)

* Fix polygon GML rendering (#830)

* Integration of XML2PDF service (#631, #883, #887)

MapFish Print related changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you are using MapFish Print, you need to also update your print configuration when updating to pyramid_oereb version 1.5.1.
`Check the files here <https://github.com/openoereb/pyramid_oereb_mfp/releases/tag/v1.5.1>`__.


.. _changes-version-1.5.0:

Version 1.5.0
-------------
The main focus of this release is improvements for the PDF generation with MapFish Print. In addition, there are
some minor changes, bug-fixes and regular maintenance. If you are not using MapFish Print, you can upgrade to
this version without changing your project setup as compared to version :ref:`changes-version-1.4.3`.
If you are using MapFish Print, please read the following subsection carefully when upgrading your version.

MapFish Print related changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This section lists those improvements for the PDF generation (when using MapFish Print) for which a change in your
project setup is necessary:

* MapFish Print configuration and templates have been moved to their
  `own repository <https://github.com/openoereb/pyramid_oereb_mfp>`__.
  Be sure to check the version requirements stated on that project page.
* Additional URL parameters for WMS calls can now be configured (PR#831)
* Certification section can now be disabled in the configuration (PR#841)
* In some cases, the table of contents is longer than one page, however, the federal specification does not foresee
  this situation. In previous releases, this lead to wrong page numbers displayed in the table of contents.
  PR#859 provides a solution by introducing ``multi_page_TOC`` property in the ``print`` section of the
  configuration. If you set this property to ``true`` (see ``pyramid_oereb/standard/pyramid_oereb.yml.mako`` as
  an example), this will split the table of contents into separate pages: one for the available themes and another
  page for the remaining content of the table of content page. This feature is disabled by default.
* The Oereb PDF produced by MapFish Print is now PDF/A compliant; please see the following section for details.

MapFish Print PDF/A conformance
"""""""""""""""""""""""""""""""
For MapFish Print PDF files, PDF/A conformance is now enabled by default (PR#852). This is likely to break PDF printing
in existing installations. To fix your configuration and data, make the following adaptations:

* All images (like logos for canton, confederation, municipality and OEREB) must not contain any transparency. If you
  use PNG, make sure to remove the alpha channel.

* Custom formatting may not include color values with transparency. For example, change all RGBA color values to RGB.

You can disable PDF/A conformance by deleting the ``net.sf.jasperreports.export.pdfa.conformance`` property in
``print/print-apps/oereb/pdfextract.jrxml``.


.. _changes-version-1.4.3:

Version 1.4.3
-------------
This is a maintenance and bug-fix release.

* Fixed import script for federal topics (PR#821)

* Added test for ordering of non-concerned themes (PR#817)

* Fixed footer with disappearing page numbers with MapFish print 3.18 (PR#814)


.. _changes-version-1.4.2:

Version 1.4.2
-------------
This is a maintenance and bug-fix release.

* Fixed an issue by downgrading a dependency which produces wrong coordinate reprojections (PR#810). We
  strongly recommend deleting your local dependencies and re-installing them to ensure a version lower than
  2.0.0 of pyproj is installed. By the time of this release, version 1.9.6 of pyproj is the most recent
  working version.


.. _changes-version-1.4.1:

Version 1.4.1
-------------
This is a maintenance and bug-fix release.

* Fixed id types in oereblex models and model template, fixed documentation errors in standard models
  and model template (PR#807).
  We strongly recommend re-generating any custom oereblex models using the create_oereblex_model script.
  Furthermore, we suggest that you re-generate any custom non-oereblex models using the create_standard_model
  script in order to have an accurate model documentation.


.. _changes-version-1.4.0:

Version 1.4.0
-------------

* properties ``map.legend_at_web`` and ``sub_theme`` are now multilingual:
  ``legend_at_web`` now supports one link per language. The ``sub_theme`` is shown in the requested (or default)
  language.

  In the database, the field types changed from ``VARCHAR`` to ``JSON``. You need to adapt your data
  generation or existing data:

  * ``legend_at_web`` changes from ``http://your_link`` to ``{'language': 'http://your_link'}``
    if you have only one language, or
    ``{'languageA': 'http://link_A', 'languageB': 'http://link_B'}`` if you have multiple languages.

  * ``sub_theme`` changes from ``Sub theme title`` to ``{'language': 'Sub theme title'}``
    if you have only one language, or
    ``{'languageA': 'Sub theme title A', 'languageB': 'Sub theme title B'}`` if you have multiple languages.

  Language may be 'de', 'fr', 'it', 'rm' or 'en'.

  All models (standard and oereblex) have been adjusted to use ``JSONType`` instead of ``sa.String`` in each model.
  If you have custom models, adapt them accordingly. See ``pyramid_oereb/contrib/templates/plr_oereb.py.mako``
  as reference. Remember that if these custom models are oereblex models which were generated by script without
  any further customization, you can remove these from your custom and switch to the already bundled models,
  see :ref:`changes-version-1.3.1`, to simplify your upgrade (and all future upgrades).

  The extracts and mapfish print templates are not affected. They only include the ``legend_at_web`` or ``sub_theme``
  of the currently requested language.


.. _changes-version-1.3.1:

Version 1.3.1
-------------

This is a maintenance and bug-fix release. Amonst other changes, this version includes changes to the
standard models and improvements to the standard configuration:

* fix of srid usage: if you have custom models in your project, you need to update them in analogy
  to the changes in the standard models in PR#736. Please note that if these custom models are oereblex
  models which were generated by script, you can now remove your custom models and switch
  to the already bundled oereblex models (available in the contrib/oereblex/models package); if you do
  this, the necessary changes will already be included and future updates will be easier.
  Alternatively, you can re-generate models from the scripts and re-apply your customization.

* standard translations: the standard configuration now contains all official theme translations.
  If your project configuration differs from these translations, we recommend you update your configuration
  accordingly.


.. _changes-version-1.3.0:

Version 1.3.0
-------------

This version introduces an import facility for **federal data**. To support this, a new database attribute
was needed, you therefore need to apply some changes to your project if you have been using
:ref:`changes-version-1.2.3` or earlier.

Configuration
^^^^^^^^^^^^^
Add a download link in each oereb theme where you want to use the download script.
See the pyramid_oereb standard configuration file for an example. Or read optional installation hints chapter
:ref:`installation-step-sample-data`.

Models
^^^^^^
If you have custom models (for example, for oereblex), you need to add an attribute ``checksum`` of type
String to these (in class definition of *DataIntegration* model). Alternatively, you can recreate your models
using the standard scripts. This will solve it for you.

Database
^^^^^^^^
New column ``checksum`` in all oereb theme *DataIntegration* tables.

.. _changes-version-1.2.3:

Version 1.2.3
-------------

The version 1.2.3 fixes a print template bug present in :ref:`changes-version-1.2.2`. You do not need to change your configuration
or schema.

.. _changes-version-1.2.2:

Version 1.2.2
-------------

The version 1.2.2 is a bug-fix release for :ref:`changes-version-1.2.1`. You do not need to change your configuration
or schema. However, you may wish to use the new optional configuration parameter ``type_mapping`` within
``real_estate``, as this allows you to define the texts to be used for the types in the configuration, instead of
needing to have them in the data.

.. _changes-version-1.2.1:

Version 1.2.1
-------------

The version 1.2.1 is the first stable version that implements the new federal specification (published november 2017).
Because this specification contains some new attributes (including mandatory attributes), and some renaming
of attributes as compared to the previous version of the specification (implemented by pyramid_oereb
in :ref:`changes-version-1.1.0`), you need to adapt your configuration and your models if you have used the previous version.

.. _changes-new-config-options-1.2.1:

New configuration options in yml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These are the new configuration options for your project (yml file):

* within the ``plan_for_land_register`` section:

  * ``layer_index``
  * ``layer_opacity``

* ``plan_for_land_register_main_page``: new section, content like ``plan_for_land_register``

* within the ``extract`` section:

  * ``certification`` (replaces certificationText)
  * ``certification_at_web``

* within each theme, in the ``view_service`` section:

  * ``layer_index``
  * ``layer_opacity``

* within the ``print`` section:

  * ``furtherInformationText`` was removed. This information is not existing any longer regarding to changed
    federal specification for the static extract.

See the `pyramid_oereb_standard yml template <https://github.com/openoereb/pyramid_oereb/blob/v1.2.1/pyramid_oereb/standard/pyramid_oereb.yml.mako>`__
for the correct style of the configuration and an explanation of the new attributes.

.. _changes-new-config-mapfish-print-1.2.1:

MapFish Print
"""""""""""""

These are the new configuration options for the printing of your extracts:

* ``display_real_estate_subunit_of_land_register``: flag whether to display the RealEstate_SubunitOfLandRegister (Grundbuchkreis)
  in the pdf extract or not

See the ``print`` section at this place in the
`pyramid_oereb_standard yml template <https://github.com/openoereb/pyramid_oereb/blob/v1.2.1/pyramid_oereb/standard/pyramid_oereb.yml.mako#L65>`__
for the correct style of the configuration.

Database
^^^^^^^^

In the standard database schema, the following has changed:

* Primary keys in the standard tables are now of type ``VARCHAR`` (not ``INTEGER``). Foreign key types need to be adapted accordingly as well.
* In the ``document`` table of each theme (i.e. ``land_use_plans`` scheme etc.), new attribute ``document_type``.
* The ``document_type`` replaces the table ``legal_provision`` for each theme (i.e. ``land_use_plans`` scheme etc.), which no longer exists.

.. _changes-version-1.1.0:

Version 1.1.0
-------------

The stable version 1.1.0 contains a lot of changes. It can be counted as the first version to be used in
production mode. When you are updating from previous version to 1.1.0 you will have to adjust your yml file.
Description below will try to classify new options whether they are *optional* or **mandatory** to use the
new version.
Of course you also could use the way described in the ``installation-step-configuration``. But then it will
create a completely new yml but valid file. In order to do that its up to your decision: Migrate new options
to your existing configuration or migrate your custom configuration into a newly created file.

Here is a list of features this version additionally implements compared to
`1.0.1 <https://github.com/openoereb/pyramid_oereb/releases/tag/v1.0.1>`__:

.. _changes-oereb-lex:

OEREBlex
^^^^^^^^

This version includes binding/adapter to oereb lex. The code can be found
`here <https://github.com/openoereb/pyramid_oereb/blob/v1.1.0/pyramid_oereb/contrib/sources/plr_oereblex.py>`__.
This should enable you to use OEREBlex with a minimum of configuration.
See :ref:`changes-new-config-oereb-lex` for further details of configuration options.

The idea of this oereb lex adapter is to access OEREBlex documents directly via API provided by OEREBlex.
You can configure this per theme. If you have a theme which has all documents stored in OEREBlex you
will need a link to the dedicated set of documents for every public law restriction in this theme. You will
end up with an attribute in the database table for your public law restriction which contains the link.

.. note:: OREBlex uses unique ids for the document sets. To prevent from storing redundant data and for
    simplifying things we decided to not store the complete link in database attribute but the id only!

Regarding to the note above we assume you have stored the correct id of your OEREBlex document set per public
law restriction in your database table.

The next step is to define the sqlalchemy mappings. This works like normal mapping definition described here:
:ref:`configuration-adapt-models`. The difference to the standard database configuration is here:

- All document related model classes are obsolete.
- The public law restriction class gets an attribute which is called geolink.
- Since all document related mapping can be ignored the mapping is slightly shorter than standard mapping.

Below you can find an example mapping.

.. note:: Have a detailed look at the PublicLawRestriction class and its attribute geolink. The name geolink
    must exist in the class to be able to use the prepared OEREBlex adapter. If you use different name in
    your database you can map it the known way:

    `geolink = sa.Column('meine_eigene_spaltenbezeichnung', sa.Integer, nullable=True)`

.. code-block:: python

    import sqlalchemy as sa
    from pyramid_oereb.standard.models import NAMING_CONVENTION
    from pyramid_oereb import srid
    from sqlalchemy.ext.declarative import declarative_base
    from geoalchemy2.types import Geometry as GeoAlchemyGeometry
    from sqlalchemy.orm import relationship

    metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)
    Base = declarative_base()

    if not srid:
        srid = 2056


    class Availability(Base):
        """
        A simple bucket for achieving a switch per municipality. Here you can configure via the imported data if
        a public law restriction is available or not. You need to fill it with the data you provided in the
        app schemas municipality table (fosnr).
        Attributes:
            fosnr (int): The identifier of the municipality in your system (id_bfs = fosnr)
            available (bool): The switch field to configure if this plr is available for the
                municipality or not.  This field has direct influence on the applications
                behaviour. See documentation for more info.
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'availability'
        fosnr = sa.Column(sa.Integer, primary_key=True)
        available = sa.Column(sa.Boolean, nullable=False, default=False)


    class Office(Base):
        """
        The bucket to fill in all the offices you need to reference from public law restriction, document,
        geometry.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            name (dict): The multilingual name of the office.
            office_at_web (str): A web accessible url to a presentation of this office.
            uid (str): The uid of this office from https
            line1 (str): The first address line for this office.
            line2 (str): The second address line for this office.
            street (str): The streets name of the offices address.
            number (str): The number on street.
            postal_code (int): The ZIP-code.
            city (str): The name of the city.
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'office'
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        name = sa.Column(sa.String, nullable=False)
        office_at_web = sa.Column(sa.String, nullable=True)
        uid = sa.Column(sa.String(12), nullable=True)
        line1 = sa.Column(sa.String, nullable=True)
        line2 = sa.Column(sa.String, nullable=True)
        street = sa.Column(sa.String, nullable=True)
        number = sa.Column(sa.String, nullable=True)
        postal_code = sa.Column(sa.Integer, nullable=True)
        city = sa.Column(sa.String, nullable=True)


    class DataIntegration(Base):
        """
        The bucket to fill in the date when this whole schema was updated. It has a relation to the office to be
        able to find out who was the delivering instance.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            date (datetime.date): The date when this data set was delivered.
            office_id (int): A foreign key which points to the actual office instance.
            office (oereb_server.models.land_use_plans.Office):
                The actual office instance which the id points to.
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'data_integration'
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        date = sa.Column(sa.DateTime, nullable=False)
        office_id = sa.Column(sa.Integer, sa.ForeignKey(Office.id), nullable=False)
        office = relationship(Office)


    class ViewService(Base):
        """
        A view service aka WM(T)S which can deliver a cartographic representation via web.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            reference_wms (str): The actual url which leads to the desired cartographic representation.
            legend_at_web (str): A link leading to a wms describing document (png).
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'view_service'
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        reference_wms = sa.Column(sa.String, nullable=False)
        legend_at_web = sa.Column(sa.String, nullable=True)


    class LegendEntry(Base):
        """
        A class based legend system which is directly related to
        :meth:`oereb_server.models.land_use_plans.ViewService`.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            symbol (str): An image with represents the legend entry. This can be png or svg. It is string
                but BaseCode64  encoded.
            legend_text (str): Multilingual text to describe this legend entry.
            type_code (str): Type code of the public law restriction which is represented by this legend
                entry.
            type_code_list (str): List of all public law restrictions which are described through this
                legend  entry.
            topic (str): Statement to describe to which public law restriction this legend entry
                belongs.
            sub_theme (str): Description for sub topics this legend entry might belonging to.
            other_theme (str): A link to additional topics. It must be like the following patterns
                * ch.{canton}.{topic}  * fl.{topic}  * ch.{bfsnr}.{topic}  This with {canton} as
                the official two letters short version (e.g.'BE') {topic} as the name of the
                topic and {bfsnr} as the municipality id of the federal office of statistics.
            view_service_id (int): The foreign key to the view service this legend entry is related to.
            view_service (oereb_server.models.land_use_plans.ViewService):
                The dedicated relation to the view service instance from database.
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'legend_entry'
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        symbol = sa.Column(sa.String, nullable=False)
        legend_text = sa.Column(sa.String, nullable=False)
        type_code = sa.Column(sa.String(40), nullable=False)
        type_code_list = sa.Column(sa.String, nullable=False)
        topic = sa.Column(sa.String, nullable=False)
        sub_theme = sa.Column(sa.String, nullable=True)
        other_theme = sa.Column(sa.String, nullable=True)
        view_service_id = sa.Column(
            sa.Integer,
            sa.ForeignKey(ViewService.id),
            nullable=False
        )
        view_service = relationship(ViewService, backref='legends')


    class PublicLawRestriction(Base):
        """
        The container where you can fill in all your public law restrictions to the topic.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            information (dict): The multilingual textual representation of the public law restriction.
            topic (str): Category for this public law restriction (name of the topic).
            sub_theme (str): Textual explanation to subtype the topic attribute.
            other_theme (str): A link to additional topics. It must be like the following patterns
                * ch.{canton}.{topic}  * fl.{topic}  * ch.{bfsnr}.{topic}  This with {canton} as
                the official two letters short version (e.g.'BE') {topic} as the name of the
                topic and {bfsnr} as the municipality id of the federal office of statistics.
            type_code (str): Type code of the public law restriction machine readable based on the
                original data  model of this public law restriction.
            type_code_list (str): List of full range of type_codes for this public law restriction in a
                machine  readable format.
            law_status (str): The status switch if the document is legally approved or not.
            published_from (datetime.date): The date when the document should be available for
                publishing on extracts. This  directly affects the behaviour of extract
                generation.
            geolink (int): ID of the referenced documents in OEREBlex.
            geom (geoalchemy2.types.Geometry): The geometry of the public law restriction.
            geo_metadata (uri): Link to the metadata.
            basis (list of oereb_server.models.land_use_plans.PublicLawRestriction):
                Public law restricitons as basis.
            refinements (list of oereb_server.models.land_use_plans.PublicLawRestriction):
                Public law restricitons as refinements.
            view_service_id (int): The foreign key to the view service this public law restriction is
                related to.
            view_service (oereb_server.models.land_use_plans.ViewService):
                The dedicated relation to the view service instance from database.
            office_id (int): The foreign key to the office which is responsible to this public law
                restriction.
            responsible_office (oereb_server.models.land_use_plans.Office):
                The dedicated relation to the office instance from database.
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'public_law_restriction'
        id = sa.Column(sa.String, primary_key=True)
        information = sa.Column(sa.String, nullable=False)
        topic = sa.Column(sa.String, nullable=False)
        sub_theme = sa.Column(sa.String, nullable=True)
        other_theme = sa.Column(sa.String, nullable=True)
        type_code = sa.Column(sa.String(40), nullable=True)
        type_code_list = sa.Column(sa.String, nullable=True)
        law_status = sa.Column(sa.String, nullable=False)
        published_from = sa.Column(sa.Date, nullable=False)
        geolink = sa.Column(sa.Integer, nullable=True)
        view_service_id = sa.Column(
            sa.Integer,
            sa.ForeignKey(ViewService.id),
            nullable=False
        )
        view_service = relationship(
            ViewService,
            backref='public_law_restrictions'
        )
        office_id = sa.Column(
            sa.Integer,
            sa.ForeignKey(Office.id),
            nullable=False
        )
        responsible_office = relationship(Office)


    class Geometry(Base):
        """
        The dedicated model for all geometries in relation to their public law restriction.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            law_status (str): The status switch if the document is legally approved or not.
            published_from (datetime.date): The date when the document should be available for
                publishing on extracts. This  directly affects the behaviour of extract
                generation.
            geo_metadata (str): A link to the metadata which this geometry is based on which delivers
                machine  readable response format (XML).
            public_law_restriction_id (int): The foreign key to the public law restriction this geometry
                is  related to.
            public_law_restriction (pyramid_oereb.standard.models.land_use_plans
                .PublicLawRestriction): The dedicated relation to the public law restriction instance from
                database.
            office_id (int): The foreign key to the office which is responsible to this public law
                restriction.
            responsible_office (pyramid_oereb.standard.models.land_use_plans.Office):
                The dedicated relation to the office instance from database.
            geom (geoalchemy2.types.Geometry): The geometry it's self. For type information see
                geoalchemy2_.  .. _geoalchemy2:
                https://geoalchemy-2.readthedocs.io/en/0.2.4/types.html  docs dependent on the
                configured type.  This concrete one is POLYGON
        """
        __table_args__ = {'schema': 'land_use_plans'}
        __tablename__ = 'geometry'
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        law_status = sa.Column(sa.String, nullable=False)
        published_from = sa.Column(sa.Date, nullable=False)
        geo_metadata = sa.Column(sa.String, nullable=True)
        geom = sa.Column(GeoAlchemyGeometry('POLYGON', srid=srid), nullable=False)
        public_law_restriction_id = sa.Column(
            sa.Integer,
            sa.ForeignKey(PublicLawRestriction.id),
            nullable=False
        )
        public_law_restriction = relationship(
            PublicLawRestriction,
            backref='geometries'
        )
        office_id = sa.Column(
            sa.Integer,
            sa.ForeignKey(Office.id),
            nullable=False
        )
        responsible_office = relationship(Office)


    class PublicLawRestrictionBase(Base):
        """
        Meta bucket (join table) for public law restrictions which acts as a base for other public law
        restrictions.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            public_law_restriction_id (int): The foreign key to the public law restriction which bases
                on another  public law restriction.
            public_law_restriction_base_id (int): The foreign key to the public law restriction which is
                the  base for the public law restriction.
            plr (pyramid_oereb.standard.models.land_use_plans.PublicLawRestriction):
                The dedicated relation to the public law restriction (which bases on) instance from  database.
            base (pyramid_oereb.standard.models.land_use_plans.PublicLawRestriction):
                The dedicated relation to the public law restriction (which is the base) instance from database.
        """
        __tablename__ = 'public_law_restriction_base'
        __table_args__ = {'schema': 'land_use_plans'}
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        public_law_restriction_id = sa.Column(
            sa.Integer,
            sa.ForeignKey(PublicLawRestriction.id),
            nullable=False
        )
        public_law_restriction_base_id = sa.Column(
            sa.Integer,
            sa.ForeignKey(PublicLawRestriction.id),
            nullable=False
        )
        plr = relationship(
            PublicLawRestriction,
            backref='basis',
            foreign_keys=[public_law_restriction_id]
        )
        base = relationship(
            PublicLawRestriction,
            foreign_keys=[public_law_restriction_base_id]
        )


    class PublicLawRestrictionRefinement(Base):
        """
        Meta bucket (join table) for public law restrictions which acts as a refinement for other public law
        restrictions.
        Attributes:
            id (int): The identifier. This is used in the database only and must not be set manually. If
                you  don't like it - don't care about.
            public_law_restriction_id (int): The foreign key to the public law restriction which is
                refined by  another public law restriction.
            public_law_restriction_refinement_id (int): The foreign key to the public law restriction
                which is  the refinement of the public law restriction.
            plr (pyramid_oereb.standard.models.land_use_plans.PublicLawRestriction):
                The dedicated relation to the public law restriction (which refines) instance from  database.
            base (pyramid_oereb.standard.models.land_use_plans.PublicLawRestriction):
                The dedicated relation to the public law restriction (which is refined) instance from database.
        """
        __tablename__ = 'public_law_restriction_refinement'
        __table_args__ = {'schema': 'land_use_plans'}
        id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
        public_law_restriction_id = sa.Column(
            sa.Integer,
            sa.ForeignKey(PublicLawRestriction.id),
            nullable=False
        )
        public_law_restriction_refinement_id = sa.Column(
            sa.Integer,
            sa.ForeignKey(PublicLawRestriction.id),
            nullable=False
        )
        plr = relationship(
            PublicLawRestriction,
            backref='refinements',
            foreign_keys=[public_law_restriction_id]
        )
        refinement = relationship(
            PublicLawRestriction,
            foreign_keys=[public_law_restriction_refinement_id]
        )

Next step would be configuration of the theme which is same like known. Only difference will be the use of
oereb lex source. See chapter :ref:`changes-new-config-oereb-lex` to know how.


.. _changes-new-config-options:

New configuration options in yml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _changes-new-config-mapfish-print:

MapFish Print
"""""""""""""

See the `pyramid_oereb_standard.yml <https://github.com/openoereb/pyramid_oereb/blob/v1.1.0/pyramid_oereb/standard/pyramid_oereb.yml.mako#L65>`__
for the correct style of the configuration.

- improved print templates to fit federal definitions as good as possible
- improved configuration in the ``pyramid_oereb.yml`` to better support requirements of different operators (multilingual)
    - **template_name**:
        Defines the name of the mapfish print template which is used to provide static extract.
    - **headers**:
        Defines the content type which is sent to mapfish print service by mapfish print proxy.
        This must be set to `Content-Type: application/json; charset=UTF-8`
    - **furtherInformationText**:
        It must contain at least one of the following sub items which can contain a
        free text. It is used to point user to more cantonal information about the oereb. It can contain
        simple html markup. As sub item at least the configured default language must be defined: *de*, *fr*,
        *it*, *rm*
        Otherwise a '-' will be shown in resulting PDF.
    - **certificationText** :
        It must contain at least one of the following sub items which can contain a
        free text. It is used to specify cantonal information about certification. It can contain
        simple html markup. As sub item at least the configured default language must be defined: *de*, *fr*,
        *it*, *rm*
        Otherwise a '-' will be shown in resulting PDF.

Since behaviour of mapfish print service was updated you may want have a more detailed look at the docs of
this package.

.. _changes-new-config-themes:

Theme configuration
"""""""""""""""""""

Each theme configuration block included a threshold configuration like this:

.. code-block:: yaml

    thresholds:
      length:
        limit: 1.0
        # Unit used internally only until now!
        unit: 'm'
        precision: 2
      area:
        limit: 1.0
        # Unit used internally only until now!
        unit: 'm²'
        precision: 2
      percentage:
        precision: 1

Due to many code reorganisations and cleaning it turned out that this is not needed any longer. So now the
block looks ways simpler as follows:

.. code-block:: yaml

    thresholds:
      length:
        limit: 1.0
      area:
        limit: 1.0

.. _changes-new-config-oereb-lex:

OEREBlex
""""""""

We assume you already defined your model mapping definition and your data is organized like described in
chapter :ref:`changes-oereb-lex`. Then you only need to add/adjust your config in little details.

The OEREBlex configuration is done in two places:

#. dedicated configuration block for OEREBlex common config
#. inside of each theme configuration block which should use OEREBlex

Find an example configuration for OEREBlex below:

.. code-block:: yaml

    # Configuration for OEREBlex
    oereblex:
      # OEREBlex host
      host: https://oereblex.bl.ch
      # geoLink schema version
      version: 1.1.0
      # Pass schema version in URL
      pass_version: true
      # Language of returned values
      language: de
      # Value for canton attribute
      canton: BL
      # Mapping for other optional attributes
      # mapping:
      #   official_number: number
      #   abbreviation: abbreviation
      # Handle related decree also as main document
      # By default a related decree will be added as reference of the type "legal provision" to the main
      # document. Set this flag to true, if you want the related decree to be added as additional legal
      # provision directly to the public law restriction. This might have an impact on client side rendering.
      related_decree_as_main: true
      # Proxy to be used for web requests
      proxy:
        http: http://xxx:xxx@proxy.ch:8088
        https: https://xxx:xxx@proxy.ch:8088
      # auth:
      #   username: preview
      #   password: preview

.. note:: The configuration above is an example only. If you want to know more in detail what to configure
    and why please have a detailed look at the documentation of the used package
    `python_geolink_formatter <https://gf-bl.gitlab.io/python-geolink-formatter/v1.3.0/index.html>`__ and
    ``api.pyramid_oereb.contrib.sources.document.oereblexsource``.


Find an example configuration for land use plans below:

.. code-block:: yaml

    - name: plr73
      code: ch.Nutzungsplanung
      geometry_type: GEOMETRYCOLLECTION
      # Define the minmal area and length for public law restrictions that should be considered as 'true' restrictions
      # and not as calculation errors (false true's) due to topological imperfections
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Nutzungsplanung kommunal
      language: de
      federal: false
      standard: true
      source:
        class: pyramid_oereb.contrib.sources.plr_oereblex.DatabaseOEREBlexSource
        params:
          db_connection: <your db connection>
          models: <path_to_your_models>.land_use_plans
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        inKraft: inKraft
        AenderungMitVorwirkung: AenderungMitVorwirkung
        AenderungOhneVorwirkung: AenderungOhneVorwirkung
