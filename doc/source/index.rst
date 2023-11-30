.. OEREB documentation master file, created by
   sphinx-quickstart on Tue May  9 09:50:33 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyramid_oereb (ÖREB-Server) documentation
=========================================

.. toctree::
   :caption: Contents:
   :hidden:

   installation
   installation-dev
   makefile
   configuration
   changes
   contrib/index
   core/index
   faq

``pyramid_oereb`` is an open-source implementation of the server side
part for the swiss `"Cadastre of Public-law Restrictions on
landownership"
(PLR-cadastre) <https://www.cadastre.ch/en/oereb.html>`__.

It is written in Python and designed as a plugin for the `Pyramid Web
Framework <http://docs.pylonsproject.org/projects/pyramid/en/latest/>`__.
This allows ``pyramid_oereb`` to be included in any Pyramid web
application.

If you are planning to run an own instance of ``pyramid_oereb``, we suggest to read the sections
:ref:`installation` and :ref:`configuration` to get started.

Architecture
------------

The application is separated into different layers to provide different points to hook into it for easier
customization.

.. image:: ../images/base_architecture.png
   :scale: 20 %
   :align: center

The server provides access to the 4 services:

* GetExtractById
* GetEGRID
* GetCapabilities
* GetVersions

The server is able to use several specific external api endpoints to fetch data at runtime (e.g. ÖEREBlex or GeoAdmin
API). These need to be configured and prepared by the integrator of this package. Please read the dedicated part
of documentation.

For the moment we provide an adapter to get the PDF static extract from mapfishprint.

.. image:: ../images/overview.png
   :align: center

As mentioned above we used a layer architecture for this project. See following graphic:

.. image:: ../images/detail.png

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
