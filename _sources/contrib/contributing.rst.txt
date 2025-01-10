.. _contributing:

==============================
Contributing to pyramid\_oereb
==============================

Community
=========
If you want to know more about pyramid_oereb, please get in touch with the open oereb community.
The community organises regular user group meetings. Here is an extract of points discussed at
these meetings:

User Group 29.04.20
-------------------
- `Release overview <../Usergroup20200429_dev_summary.pdf>`__


User Group 14.05.19
-------------------
- `Release overview <../Usergroup20190514_dev_summary.pdf>`__


Contributing to Documentation
=============================

.. _code_documentation_style:

Changing the documentation
--------------------------
Check out the current master of *pyramid_oereb* locally and edit the documentation source files just like you
would edit the source code of the GitHub project.

Generating the documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Run ``make doc`` to generate the documentation;
check for any warnings or errors related to your changes.

Code Documentation
~~~~~~~~~~~~~~~~~~

Some parts of the documentation are built directly from the code.
The documentation is built using `Sphinx <http://sphinx-doc.org/>`__, so the code documentation uses
`Google style docstrings
<http://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`__.

Contributing to the Code
========================

If you plan to contribute source code,
please follow the `instructions <https://github.com/openoereb/pyramid_oereb/tree/master/cla>`__ and sign the CLA.

Create a local development instance
-----------------------------------

You can checkout the current master and run *pyramid\_oereb* locally.
We recommend to use a linux system but the application is tested and
may also be used in a windows environment.

NOTE
   Use the installation instructions below for local development instances only!

...on Linux
~~~~~~~~~~~

Requirements:

-  `Git <https://git-scm.com/>`__
-  `Python <https://www.python.org/>`__
-  `Virtualenv <https://virtualenv.pypa.io/en/stable/>`__
-  `Docker <https://docker.com/>`__
-  `make <https://www.gnu.org/software/make/>`__

After installing the listed requirements, clone the repository and enter
its directory.

.. code-block:: shell

 git clone https://github.com/openoereb/pyramid_oereb.git
 cd pyramid_oereb

Build and start your local installation using ``make serve``.
To stop the server, press ``CTRL`` + ``C``.

NOTE
   You can try your oereb server as follows.
   In your browser, check the following URL (the latter two are based on sample data):

   -  http://localhost:6543/oereb/versions/json
   -  http://localhost:6543/oereb/capabilities/json
   -  http://localhost:6543/oereb/getegrid/json?EN=2608883,1261844
   -  http://localhost:6543/oereb/extract/xml?EGRID=CH113928077734

...on Windows
~~~~~~~~~~~~~

#. Creation of base directory for the project:

   .. code-block:: shell

    mkdir oereb
    cd oereb

#. Prepare it for git:

   .. code-block:: shell

    git init

#. Install the virtual environnement (supposed you already have python installed)

   .. code-block:: shell

    virtualenv --setuptools --no-site-packages .build/venv

#. Install a basic Pyramid component

   NOTE
      If you are sure about what you do, you may activate venv with

      .. code-block:: shell

       .build\venv\Scripts\activate

      to further ommit the path to your venv, but otherwise leave it and enter the complete path for each
      install command.

   .. code-block:: shell

    .build\venv\Scripts\pip install pyramid==1.7.4

#. get one level up to create the empty project

   .. code-block:: shell

    cd ..
    oereb\.build\venv\Scripts\pcreate.exe -s alchemy oereb

#. Delete unused files for this project:

   .. code-block:: shell

    cd oereb
    rm [filename]

   -  .coveragerc
   -  MANIFEST.in
   -  pytest.ini

#. Maybe create an github project with this base structure and push it but first create a .gitignore file with
   at least

   -  \*.pyc
   -  /.build

   as content - other files will follow...

   .. code-block:: shell

    git add .gitignore
    git commit -m "added .gitignore"

   Then create your git repository and add is as remote to the local directory:

   .. code-block:: shell

    git remote add upstream https://github.com/youraccount/oereb.git

#. Collect complementary files created on github such as the README.md

   .. code-block:: shell

    git fetch upstream
    git merge upstream/master

#. Add your local files and push them to the repository to get an clean initial version

   .. code-block:: shell

    git add -A
    git commit -m "commit message"
    git push upstream master

#. On windows there's a problem with the shapely dependencies, so before installing all the other
   dependencies, one should manually install shapely and psycopg2 wheels:

   .. code-block:: shell

    .build\venv\Scripts\pip install wheel [path to psycopg2-2.5.5-cp27-none-win32.whl or newer version]
    .build\venv\Scripts\pip install wheel [path to Shapely-1.5.13-cp27-none-win32.whl or newer version]

#. Then install the pyramid\_oereb egg and the dependencies

   .. code-block:: shell

    .build\venv\Scripts\pip install pyramid_oereb

   In the setup.py add "pyramid\_oereb" in the list of requirements then run

   .. code-block:: shell

    .build\venv\Scripts\pip install -e .

#. Create the standard parameters file by running:

   .. code-block:: shell

    .build\venv\Scripts\create_standard_yaml

#. Now to the configuration - you could do a commit and push on git to have a clean project before
   configuration... :)

   You want to add \*.egg-info/ in your .gitignore file first then add the new and changed files, commit

   .. code-block:: shell

    git add [files]
    git commit -m "clean unconfigured standard project"
    git push upstream [branch]

   With this proper instance we start messing around:

   Create a pyramid\_oereb.yml file in the project root folder and copy the content of
   pyramid\_oereb\_standard.yml we created before in it and adapt the necessary parameters to your
   environment - p.ex db\_connection and so on in the development.ini at the end of the
   [app:main] block add

   .. code-block:: shell

    pyramid_oereb.cfg.file = pyramid_oereb_standard.yml
    pyramid_oereb.cfg.section = pyramid_oereb

#. Install all the standard test and db scripts in the project

   .. code-block:: shell

    .build\venv\Scripts\python setup.py develop

#. Configure the database settings and install standard tables

   Make sure (eg using pgAdmin) the configured database exists and has the postgis extensions installed
   (create extension postgis). Set the db parameters in your pyramid\_oereb.yml config or use
   pyramid\_oereb\_standard.yml for your test environnement then
   .. code-block:: shell

    .build\venv\Scripts\create_main_schema_tables.exe -c pyramid_oereb_standard.yml --sql-file=sqlFile.sql
    .build\venv\Scripts\create_standard_tables.exe -c pyramid_oereb_standard.yml --sql-file=sqlFile.sql
    .build\venv\Scripts\create_oereblex_tables.exe -c pyramid_oereb_standard.yml --sql-file=sqlFile.sql

   Then load the generate sql file into your DB

#. Load sample data in the standard db or connect your own PLR database for standard sample data:

   .. code-block:: shell

    .build\venv\Scripts\python pyramid_oereb\standard\load_sample_data.py -c pyramid_oereb_standard.yml

#. Don't forget to include the configuration adding

   .. code-block:: shell

    config.include('pyramid_oereb', route_prefix='oereb')

   in \\oereb\_\_init\_\_.py just befor the line config.scan()

   For testing start the local instance with:

   .. code-block:: shell

    .build\venv\Scripts\pserve --reload development.ini

   WARNING
      On windows you may have an error message regarding 'encoding'. If that's the case, remove the --reload
      from the command

      .. code-block:: shell

       .build\venv\Scripts\pserve development.ini

Update existing pyramid\_oereb package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  Uninstall the existing package

   .. code-block:: shell

    .build\venv\Scripts\pip uninstall pyramid_oereb

-  Install the new version

   .. code-block:: shell

    .build\venv\Scripts\pip install pyramid_oereb

   If for some reasons you need the latest version from git (master),
   use

   .. code-block:: shell

    .build\venv\Scripts\pip install git+https://github.com/openoereb/pyramid_oereb.git@master#egg=pyramid_oereb

   then rebuild the app with

   .. code-block:: shell

    .build\venv\Scripts\python setup.py develop

Testing the application
-----------------------

Browser requests
~~~~~~~~~~~~~~~~

Once your application has started as describe above,
you can try your oereb server as follows.
In your browser, check the following URL:

* http://localhost:6543/oereb/versions/json
* http://localhost:6543/oereb/capabilities/json

Now try the following requests; these are based on sample data:

* http://localhost:6543/oereb/getegrid/xml?EN=2608883,1261844
* http://localhost:6543/oereb/extract/xml?EGRID=CH113928077734

Test suite
~~~~~~~~~~

To run the test suite, do ``make tests``.

NOTE
   The test suite will generate and start a test database, on port 5432. Please check whether you already have
   a database server running on this port, if so, please stop it before starting the tests.

Documentation style
-------------------
Regarding code documentation style, see :ref:`code_documentation_style`.
