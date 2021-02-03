===============================
``pyramid_oereb`` (ÖREB-Server)
===============================

|Build Status| |Requirements Status|

``pyramid_oereb`` is an open-source implementation of the server side part for the swiss `"Cadastre of
Public-law Restrictions on landownership" (PLR-cadastre) <https://www.cadastre.ch/en/oereb.html>`__.

It is written in Python and designed as a plugin for the `Pyramid Web Framework
<http://docs.pylonsproject.org/projects/pyramid/en/latest/>`__. This allows ``pyramid_oereb`` to be
included in any Pyramid web application.

Please refer to the `documentation <https://openoereb.github.io/pyramid_oereb/doc/>`__ for detailed
information and instructions for installation and configuration.

If you are interested in contributing or extending the project, take a look at the
`contribution page <https://openoereb.github.io/pyramid_oereb/doc/contrib/>`__.

.. |Build Status| image:: https://travis-ci.org/openoereb/pyramid_oereb.svg?branch=master
   :target: https://travis-ci.org/openoereb/pyramid_oereb
   :alt: Build Status

.. |Requirements Status| image:: https://requires.io/github/openoereb/pyramid_oereb/requirements.svg?branch=master
   :target: https://requires.io/github/openoereb/pyramid_oereb/requirements/?branch=master
   :alt: Requirements Status

Local testing (quick preview)
=============================

Run dev server
--------------

Following packages are required: ``python3-venv`` ``postgresql-client`` ``libpq-dev``

Run:

.. code-block:: bash

  git clone git@github.com:openoereb/pyramid_oereb.git
  cd pyramid_oereb
  make serve

JSON reduced extract is accessible at: http://localhost:6543/oereb/extract/reduced/json/CH113928077734.

Run tests
---------

To check your code, run `make checks`. It will run style checks and tests. It's also possible to
run sub-target independently:

- `make checks-style` to run only style-related checks (linting, attributes).
- `make tests` to run tests. Python 3.7 is used by default. But you can run tests with another version by
  running: `PYTHON_TEST_VERSION=python3.x make tests`. You can also set this variable in the Makefile.

After running tests, the coverage is available in the folder `coverage_report`.
