.. _changes:

Changes/Hints for migration
===========================

This section will give you hints how to handle version migration. Since the project moves forward it will
introduce differences in the yml configuration file. So it would not be enough to simply install newest
version. Often a version upgrade changes or add parameters which are used.

.. _changes-version-1.1.0:

Version 1.1.0
-------------

The stable version 1.1.0 contains a lot of changes. It can be counted as the first version to be used in
production mode. When you are updating from previous version to 1.1.0 you will have to adjust your yml file.
Description below will try to classify new options whether they are *optional* or **mandatory** to use the
new version.
Of course you also could use the way described in the ``installation-step-configuration``. But then it will
create a completely new yml but valid file. In order to that its up to your decision: Migrate new options to
your existing configuration or migrate your custom configuration into a newly created file.

Here is a list of features this version additionally implements compared to
`1.0.1 <https://github.com/camptocamp/pyramid_oereb/releases/tag/v1.0.1>`__:

New configuration options in yml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mapfish print
"""""""""""""

See the `pyramid_oereb_standard.yml <https://github.com/camptocamp/pyramid_oereb/blob/v1.1.0/pyramid_oereb/standard/pyramid_oereb.yml.mako#L65>`__
for the correct style of the configuration.

- improved print templates to fit federal definitions as good as possible
- improved configuration in the ``pyramid_oere.yml`` to better support requirements of different operators (multilingual)
    - **template_name**:
        Defines the name of the mapfish print template which is used to provide static extract.
    - **headers**:
        Defines the content type which is sent to mapfish print service by mapfish print proxy.
        This should be set to = `Content-Type: application/json; charset=UTF-8`
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

Theme configuration
"""""""""""""""""""

Each theme configuration block included a threshold configuration like this:

.. code-block:: yml

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

.. code-block:: yml

    thresholds:
      length:
        limit: 1.0
      area:
        limit: 1.0
