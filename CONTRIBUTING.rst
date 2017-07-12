Contributing to pyramid\_oereb
==============================

.. contents::

Create a local development instance
-----------------------------------

You can checkout the current master and run *pyramid\_oereb* locally, but we cannot guarantee a working
configuration as it is under development. We recommend to use a linux system but the application is tested and
may also be used in a windows environment.

NOTE
   Use the installation instructions below for local development instances only!

...on Linux
~~~~~~~~~~~

Requirements:

-  `Git <https://git-scm.com/>`__
-  `Python <https://www.python.org/>`__
-  `Virutalenv <https://virtualenv.pypa.io/en/stable/>`__
-  `Docker <https://docker.com/>`__
-  `make <https://www.gnu.org/software/make/>`__

After installing the listed requirements, clone the repository and enter
its directory.

.. code-block:: shell

 git clone https://github.com/camptocamp/pyramid_oereb.git
 cd pyramid_oereb

You can set up the virtual environment using ``make install`` and run the unit tests using ``make checks``.

Create an empty database using docker.

.. code-block:: shell

 docker run --name postgis-oereb -e POSTGRES_PASSWORD=password -e POSTGRES_DB=pyramid_oereb \
 --net host -d mdillon/postgis:9.4-alpine

Now you can use ``docker container start/stop/restart postgis-oereb`` to control your database. Ensure the
database is running.

Create your configuration file and load the sample data.

.. code-block:: shell

 .venv/bin/create_standard_yaml
 .venv/bin/create_standard_tables -c pyramid_oereb_standard.yml
 .venv/bin/load_standard_sample_data -c pyramid_oereb_standard.yml

To start a local server run ``make serve``. It should be available unter http://localhost:6543/oereb/. To stop
the server, press ``CTRL`` + ``C``.

NOTE
   These sample requests should work, if you have loaded thesample data:

   -  http://localhost:6543/oereb/versions
   -  http://localhost:6543/oereb/capabilities
   -  http://localhost:6543/oereb/getegrid?XY=2608883,1261844
   -  http://localhost:6543/oereb/extract/reduced/xml/CH113928077734

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
   environnement - p.ex db\_connection and so on in the development.ini and production.ini at the end of the
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

    .build\venv\Scripts\create_standard_tables.exe -c pyramid_oereb_standard.yml

#. Load sample data in the standard db or connect your own PLR database for standard sample data:

   .. code-block:: shell

    .build\venv\Scripts\load_standard_sample_data.exe -c pyramid_oereb_standard.yml

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

   Call a sample extract: http://localhost:6543/oereb/extract/embeddable/json/CH113928077734

   Or at least http://localhost:6543/oereb/versions.json

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

    .build\venv\Scripts\pip install git+https://github.com/camptocamp/pyramid_oereb.git@master#egg=pyramid_oereb

   then rebuild the app with

   .. code-block:: shell

    .build\venv\Scripts\python setup.py develop

Documentation style
-------------------

The documentation is built using `Sphinx <http://sphinx-doc.org/>`__. You have to use `Google style docstrings
<http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`__ for documenting the code.
