.. _contrib-data-sources:

Data Sources
------------

``pyramid_oereb`` provides a plugable system to offer an extendable system. The most
interesting part of that is probably the extension of what data sources should be
connected to the core system of ``pyramid_oereb``.

As of now ``pyramid_oereb`` offers the following data sources (db structures) you can store
your data to:

* :ref:`contrib-data-sources-standard`
* oereblex
* interlis 2.3



In addition there is a source to use with the address localisation:

* swisstopo

.. toctree::
   :hidden:

   standard/index
   oereblex/index
   interlis_2_3/index
   swisstopo/index
