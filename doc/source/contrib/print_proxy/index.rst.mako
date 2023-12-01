.. _contrib-print-proxy:

Print Proxy
-----------

Part of ``pyramid_oereb`` plugable system is also the production of PDF files of the extracts.

It is solved via a proxy approach. The extract is passed to a service which knows how to produce a PDF
satisfying the federal specifications.

As of now ``pyramid_oereb`` offers the following print proxy:

* :ref:`contrib-print_proxy-mapfish-print`

.. toctree::
   :hidden:

   mapfish-print
