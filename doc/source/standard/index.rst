
Standard
========

The standard package is the part where all the database configuration is stored. It also provides really
useful functions to integrate data, as well as creation of a YAML-configuration fitting this standard
structure. In addition you will find here the hook methods which are used in several places in the
configuration and an example usage of the pyconizer package to provide legend entry icons for a dedicated
layer.

.. toctree::
   :hidden:

   sources
   models/index

Functions for creating standard environment
-------------------------------------------

.. _api-pyramid_oereb-standard-create_tables:

.. automodule:: pyramid_oereb.contrib.data_sources.create_tables
   :members:
      create_tables_from_standard_configuration

.. _api-pyramid_oereb-standard-load_legend_entries:

.. automodule:: pyramid_oereb.contrib.data_sources.standard.load_legend_entries
   :members:
      create_legend_entries_in_standard_db

Functions used as configurable hooks
------------------------------------

.. _api-pyramid_oereb-standard-hook_methods:

.. automodule:: pyramid_oereb.contrib.data_sources.standard.hook_methods
   :members:
