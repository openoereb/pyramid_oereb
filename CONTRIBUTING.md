Contributing to pyramid_oereb
=============================


> **Table of contents**
>
> - [Create a local development instance](#create-a-local-development-instance)
>     - [...on Linux](#on-linux)
>     - [...on Windows](#on-windows)
>         - [Update existing pyramid_oereb package](#update-existing-pyramid_oereb-package)
> - [Documentation style](#documentation-style)



Create a local development instance
-----------------------------------

You can checkout the current master and run _pyramid_oereb_ locally, but we cannot guarantee a working
configuration as it is under development. We recommend to use a linux system but the application is tested
and may also be used in a windows environment.

> **NOTE:** Use the installation instructions below for local development instances only!

### ...on Linux

Requirements:
-   git
-   python
-   virutalenv
-   docker
-   make

After installing the listed requirements, clone the repository and enter its directory.
```
git clone https://github.com/camptocamp/pyramid_oereb.git
cd pyramid_oereb
```

You can set up the virtual environment using `make install` and run the unit tests using `make checks`.

Create an empty database using docker.
```
docker run --name postgis-oereb -e POSTGRES_PASSWORD=password --net host -d mdillon/postgis:9.4-alpine
```
Now you can use `docker container start/stop/restart postgis-oereb` to control your database. Ensure the database is running.

Create your configuration file and load the sample data.
```
.venv/bin/create_standard_yaml
.venv/bin/create_standard_tables -c pyramid_oereb_standard.yml
.venv/bin/load_standard_sample_data -c pyramid_oereb_standard.yml
```

To start a local server run `make serve`. It should be available unter http://localhost:6543/oereb/, e.g.
http://localhost:6543/oereb/versions. To stop the server, press `CTRL` + `C`.

> **NOTE:** The sample extract can be called for the EGRID "CH113928077734", e.g. http://localhost:6543/oereb/extract/reduced/json/CH113928077734.

### ...on Windows

1. Creation of base directory for the project:
```
mkdir oereb
cd oereb
```

2. Prepare it for git:
```
git init
```

3. Install the virtual environnement (supposed you already have python installed)
```
virtualenv --setuptools --no-site-packages .build/venv
```

4. Install a basic Pyramid component*

(* if you are sure about what you do, you may activate venv with
```
.build\venv\Scripts\activate
```
to further ommit the path to your venv, but
otherwise leave it and enter the complete path for each install command)
```
.build\venv\Scripts\pip install pyramid==1.7.4
```

5. get one level up to create the empty project
```
cd ..
oereb\.build\venv\Scripts\pcreate.exe -s alchemy oereb
```

6. Delete unused files for this project:
```
cd oereb
rm [filename]
```
- .coveragerc
- MANIFEST.in
- pytest.ini

7. Maybe create an github project with this base structure and push it
but first create a .gitignore file with at least
- *.pyc
- /.build
as content - other files will follow...
```
git add .gitignore
git commit -m "added .gitignore"
```

then create your git repository and add is as remote to the local directory:
```
git remote add upstream https://github.com/youraccount/oereb.git
```

8. collect complementary files created on github such as the README.md
```
git fetch upstream
git merge upstream/master
```

9. Add your local files and push them to the repository to get an clean initial version
```
git add -A
git commit -m "commit message"
git push upstream master
```

10. On windows there's a problem with the shapely dependencies, so before installing
all the other dependencies, one should manually install shapely and psycopg2 wheels:
```
.build\venv\Scripts\pip install wheel [path to psycopg2-2.5.5-cp27-none-win32.whl or newer version]
.build\venv\Scripts\pip install wheel [path to Shapely-1.5.13-cp27-none-win32.whl or newer version]
```

11. Then install the pyramid_oereb egg and the dependencies
```
.build\venv\Scripts\pip install pyramid_oereb
```
In the setup.py add "pyramid_oereb" in the list of requirements then run
```
.build\venv\Scripts\pip install -e .
```
12. Create the standard parameters file by running:
```
.build\venv\Scripts\create_standard_yaml
```

13. Now to the configuration - you could do a commit and push on git to have a clean project before configuration... :)
you want to add *.egg-info/ in your .gitignore file first then add the new and changed files, commit
```
git add [files]
git commit -m "clean unconfigured standard project"
git push upstream [branch]
```

With this proper instance we start messing around:
Create a pyramid_oereb.yml file in the project root folder and copy
the content of pyramid_oereb_standard.yml we created before in it
and adapt the necessary parameters to your environnement - p.ex db_connection and so on
in the development.ini and production.ini at the end of the
[app:main] block add
```
pyramid_oereb.cfg.file = pyramid_oereb_standard.yml
pyramid_oereb.cfg.section = pyramid_oereb
```

14. Install all the standard test and db scripts in the project
```
.build\venv\Scripts\python setup.py develop
```

15. Configure the database settings and install standard tables
Make sure (eg using pgAdmin) the configured database exists and has the postgis extensions installed (create extension postgis)
Set the db parameters in your pyramid_oereb.yml config or use pyramid_oereb_standard.yml for your test environnement then
```
.build\venv\Scripts\create_standard_tables.exe -c pyramid_oereb_standard.yml
```

16. Load sample data in the standard db or connect your own PLR database
for standard sample data:
```
.build\venv\Scripts\load_standard_sample_data.exe -c pyramid_oereb_standard.yml
```

17. Don't forget to include the configuration adding
```
config.include('pyramid_oereb', route_prefix='oereb')
```
in \oereb\__init__.py just befor the line config.scan()

For testing start the local instance with:
```
.build\venv\Scripts\pserve --reload development.ini
```
!! ATTENTION, on windows you may have an error message regarding 'encoding'
if that's the case, remove the --reload from the command:
```
.build\venv\Scripts\pserve development.ini
```

And call a sample extract: http://localhost:6543/oereb/extract/embeddable/json/CH113928077734
or at least
http://localhost:6543/oereb/versions.json


#### Update existing pyramid_oereb package
- Uninstall the existing package
```
.build\venv\Scripts\pip uninstall pyramid_oereb
```
- Install the new version
```
.build\venv\Scripts\pip install pyramid_oereb
```
If for some reasons you need the latest version from git (master), use
```
.build\venv\Scripts\pip install git+https://github.com/camptocamp/pyramid_oereb.git@master#egg=pyramid_oereb
```
then rebuild the app with
```
.build\venv\Scripts\python setup.py develop
```


Documentation style
-------------------

The documentation is built using [Sphinx](http://sphinx-doc.org/). You have to use [Google style docstrings](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for documenting the code.
