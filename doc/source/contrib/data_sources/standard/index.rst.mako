.. _contrib-data-sources-standard:

Standard
^^^^^^^^

The standard data source is a binding to a database following the definitions of
`OeREBKRMkvs_V2_0 <http://models.geo.admin.ch/V_D/OeREB/OeREBKRMkvs_V2_0.ili>`__
and `OeREBKRMtrsfr_V2_0 <http://models.geo.admin.ch/V_D/OeREB/OeREBKRMtrsfr_V2_0.ili>`__
but adds some magic sugar for convenience.

Exemplary schema of a standard database:

 .. image:: ../../../../images/standard_database_schema_example.png
   :scale: 20 %
   :align: center

This structure is defined as models for SQL-Alchemy ORM and as a fitting set of
DataBaseSource-Adapters to hook it into the core of ``pyramid_oereb``. The models
defined in this contribution package describing 2 different structures. The ``main``
definitions are used by ``pyramid_oereb`` application itself and contain the application
configuration as suggested in
`OeREBKRMkvs_V2_0 <http://models.geo.admin.ch/V_D/OeREB/OeREBKRMkvs_V2_0.ili>`__.
The ``theme`` definitions define a single ÖREB-Theme as it is suggested by
`OeREBKRMtrsfr_V2_0 <http://models.geo.admin.ch/V_D/OeREB/OeREBKRMtrsfr_V2_0.ili>`__.
Please be aware that for performance reasons the schematic mapping of SQL-Alchemy ORM
definitions and the linked INTERLIS models is not 1:1.

The definition of main and theme schema share some classes. These are provided via
factory methods at modul level. These methods can be found here :ref:`contrib-data-sources-standard-models`

* :ref:`contrib-data-sources-standard-models`
* :ref:`contrib-data-sources-standard-models-main`
* :ref:`contrib-data-sources-standard-models-theme`
* :ref:`contrib-data-sources-standard-sources`


.. toctree::
   :hidden:

   models
   models-main
   models-theme
   sources
