
Standard
========

The standard package is the part where all the database configuration is stored. It also provides really
useful functions to integrate data, as well as creation of a YAML-configuration fitting this standard
structure. In addition you will find here the hook methods which are used in several places in the
configuration and an example usage of the pyconizer package to provide legend entry icons for a dedicated
layer.

.. toctree::

   sources

Functions for creating standard environment
-------------------------------------------

.. _api-pyramid_oereb-standard:

.. automodule:: pyramid_oereb.standard
   :members:
      create_tables_from_standard_configuration,
      drop_tables_from_standard_configuration,
      _create_standard_yaml_config_

.. _api-pyramid_oereb-standard-create_tables:

.. automodule:: pyramid_oereb.standard.create_tables
   :members:
      _create_theme_tables

Functions for filling standard environment with data
----------------------------------------------------

.. _api-pyramid_oereb-standard-load_sample_data:

.. automodule:: pyramid_oereb.standard.load_sample_data
   :members:
      SampleData

.. _api-pyramid_oereb-standard-load_legend_entries:

.. automodule:: pyramid_oereb.standard.load_legend_entries
   :members:
      create_legend_entries_in_standard_db

Functions used as configurable hooks
------------------------------------

.. _api-pyramid_oereb-standard-hook_methods:

.. automodule:: pyramid_oereb.standard.hook_methods
   :members:
