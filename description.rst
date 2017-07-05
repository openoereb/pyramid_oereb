``pyramid_oereb`` (ÖREB-Server)
===============================

|Build Status|

``pyramid_oereb`` is an open-source implementation of the server side
part for the swiss `"Cadastre of Public-law Restrictions on
landownership"
(PLR-cadastre) <https://www.cadastre.ch/en/oereb.html>`__.

It is written in Python and designed as a plugin for the `Pyramid Web
Framework <http://docs.pylonsproject.org/projects/pyramid/en/latest/>`__.
This allows *pyramid\_oereb* to be included in any Pyramid web
application.

Please refer to the
`documentation <https://camptocamp.github.io/pyramid_oereb/doc/>`__ for
detailed information and instructions for installation and
configuration.

If you are interested in contributing or extending the project, take a
look at the `contribution guidelines <CONTRIBUTING.md>`__.

Changelog
=========

1.0.0-alpha.2
-------------

-  proceed with renderer for xml and json
-  add metadata for embeddable flavour
-  images accessible via URL
-  add configurable methods for processing
-  improve geometry handling
-  add documentation on https://camptocamp.github.io/pyramid\_oereb/doc/
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

.. |Build Status| image:: https://travis-ci.com/camptocamp/pyramid_oereb.svg?token=oTUZsPVUPe1BYV5bzANE&branch=master
   :target: https://travis-ci.com/camptocamp/pyramid_oereb
