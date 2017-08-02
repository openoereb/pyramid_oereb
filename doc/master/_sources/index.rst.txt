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
   configuration
   standard/index
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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
