pyramid_oereb (ÖREB-Server)
===========================
[![Build Status](https://travis-ci.com/camptocamp/pyramid_oereb.svg?token=oTUZsPVUPe1BYV5bzANE&branch=master)](https://travis-ci.com/camptocamp/pyramid_oereb)

_pyramid_oereb_ is an open-source implementation of the server side part for the swiss ["Cadastre of Public-law Restrictions on landownership" (PLR-cadastre)](https://www.cadastre.ch/en/oereb.html).

It is written in Python and designed as a plugin for the [Pyramid Web Framework](http://docs.pylonsproject.org/projects/pyramid/en/latest/). This allows _pyramid_oereb_ to be included in any Pyramid web application.

Installation
------------

**Note:** Installing _pyramid_oereb_ requires a running Pyramid web application.

1.  If not already existent, set up a Pyramid web application.
2.  Install the Python package _pyramid_oereb_ in the Python environment of your application.
    ```
    pip install pyramid_oereb
    ```
3.  Include the Pyramid plugin in your application. Edit the application's main method and add the following
line:
    ```python
    config.include('pyramid_oereb', route_prefix='oereb')
    ```
    It is recommended to define a route prefix like "oereb" or something similar (You are free to choose
    whatever prefix you like).
4.  Add your configuration as described in the following section.
5.  Restart your web server. The PLR webservice should now be available under the specified route prefix.


Configuration
-------------

### Basic idea

You are looking at a highly configurable piece of software. To get the right understanding of the server it
is recommended to read this part carefully.

Since the confederations definition and the specification for the extract of OEREB data is really straight
 we had very narrow margins to develop the code. Using this pyramid plugin you will get a running server
 instance which is able to provide the services with output satisfying the specification of the confederation.
 But to get this extract you need to bind the data to this server. And this is basically what you need to
 configure.

For configuration we use the [YAML](http://www.yaml.org/spec/1.2/spec.html) system. It is a handy way to
separate config in a human and machine readable way in text files.

So the first goal for configuration is to have such a YAML file. To point out which way you should go please
follow this workflow sheet:

![Screenshot](doc/images/configuration_workflow.png)

After you know now what way you want to go you are probably curious what you add as configuration content.
This is simple: Mainly all content from the [pyramid_oereb.yaml](https://github.com/camptocamp/pyramid_oereb/blob/master/pyramid_oereb/standard/pyramid_oereb.yml).

It contains the basic configuration which can be used as a start point.

### The structure

When you open the [pyramid_oereb.yaml](pyramid_oereb.yml) you see "pyramid_oreb" in the first line. This is
the section. This is the entry point of the configuration. When ever you copy this config content to a own
config file, take care that this section needs to be at the most left (without spaces in front). This ensures
that it will be available by the oereb application.

For further information read the comments inside this file attentively.

Running development version locally and standalone
--------------------------------------------------

You can checkout the current master and run _pyramid_oereb_ locally, but we cannot guarantee a working
configuration as it is under development. We recommend to use a linux system but the application is tested
and may also be used in a windows environment.

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

To start a local server run `make serve`. It should be available unter http://localhost:6543/oereb/, e.g.
http://localhost:6543/oereb/versions. To stop the server, press `CTRL + C`.

Running development version on a up and running already existing pyramid_server
-------------------------------------------------------------------------------

Before you start whith the following instructions you should think about creating a branch of your applications code to not mess things up.

1. In the setup.py add "pyramid_oereb" in the list of requirements (often a python list stored in the variable "requires")
2. If you are using virtual environment enable it:
```source <path_to_your_venv>/bin/activate```
3. run the following command (This will install all new requirements):
```pip install -e.```
3. Now you have installed the pyramid oereb package
4. In the root folder of your pyramid app (the one where the setup.py is stored too) run the command: ```create_standard_yaml```
5. You got a configuration file which contains all standard things (a yaml, and two logo png files). **IMPORTANT:** There are several places where database connections are defined. They all are defined like this: ```db_connection: postgresql://postgres:password@localhost/pyramid_oereb```, you **MUST** adapt this to your database configuration. Note that the database you specify here must exist and it must be able to handle spacial data (postgis,...). **This connections are used later to create/drop standard tables and fill database with standard data.** HINT: Use *find and replace* of your favorite editor and replace all connection definitions. In addition to the database connection you can find a line with the content: ```canton: YOUR_LOGO_HERE!```. Place a png file representing your cantonal logo in this folder and replace 'YOUR_LOGO_HERE!' with the name of your logo.
6. Open the development.ini file and add two lines to the end of the "[app:main]" block
```
pyramid_oereb.cfg.file = pyramid_oereb_standard.yml
pyramid_oereb.cfg.section = pyramid_oereb
```
7. Do the same in the production.ini file
8. In the __init__ file of your application inside of the main method add this line just before the config.scan() call.
```
config.include('pyramid_oereb', route_prefix='oereb')
```
9. execute the command in the folder where you created the pyramid_oereb.yml to make sure having a clean database for start (this should only influence the pyramid_oereb related data):
```
drop_standard_tables -c pyramid_oereb_standard.yml
```
10. execute the command in the folder where you created the pyramid_oereb.yaml:
```
create_standard_tables -c pyramid_oereb_standard.yml
```
11. execute the command in the folder where you created the pyramid_oereb.yaml (this will create a test data set):
```
load_standard_sample_data -c pyramid_oereb_standard.yml
```
12. Check with a tool of your choise that the structure was created successfully in you desired database. You should find 17 database schemas named (snake_case) by their code attribute from the yml file. Plus one schema called "pyramid_oereb_main" containing the app global stuff (addresses, municipalities, etc.). At least these tables need to be filled up with your data with a tool of your choise).
13. Start your pyramid application.
14. Point your browser to: <your pyramid applications root url>/oereb/extract/embeddable/json/CH113928077734

WINDOWS: Getting a development version running with a clean and basic pyramid app as base
-------------------------------------------------------------------------------
1.Creation of base directory for the project: oereb
cd oereb

2. prepare it for git
git init

3. Install the virtual environnement (supposed you already have python installed)
virtualenv --setuptools --no-site-packages .build/venv

4. Install a basic Pyramid component*
(* if you are sure about what you do, you may activate venv with
.build\venv\Scripts\activate to further ommit the path to your venv, but
otherwise leave it and enter the complete path for each install command)
.build\venv\Scripts\pip install pyramid==1.7.4

5. get one level up to create the empty project
cd ..
oereb\.build\venv\Scripts\pcreate.exe -s alchemy oereb

6. Delete unused files for this project:
 cd oereb
- .coveragerc
- MANIFEST.in
- pytest.ini

7. Maybe create an github project with this base structure and push it
but first create a .gitignore file with at least
*.pyc
/.build
as content - other files will follow...
git add .gitignore
git commit -m "added .gitignore"

then create your git repository and add is as remote to the local directory:
git remote add upstream https://github.com/youraccount/oereb.git

8. collect complementary files created on github such as the README.md
git fetch upstream
git merge upstream/master

9. Add your local files and push them to the repository to get an clean initial version
git add -A
git commit -m "commit message"
git push upstream master

10. On windows there's a problem with the shapely dependencies, so before installing
all the other dependencies, one should manually install shapely and psycopg2 wheels:
.build\venv\Scripts\pip install wheel [path to psycopg2-2.5.5-cp27-none-win32.whl or newer version]
.build\venv\Scripts\pip install wheel [path to Shapely-1.5.13-cp27-none-win32.whl or newer version]

11. Then install the pyramid_oereb egg and the dependencies
.build\venv\Scripts\pip install pyramid_oereb
In the setup.py add "pyramid_oereb" in the list of requirements then run
.build\venv\Scripts\pip install -e .

12. Create the standard parameters file by running:
.build\venv\Scripts\create_standard_yaml

13. Now to the configuration - you could do a commit and push on git to have a clean project before configuration... :)
you want to add *.egg-info/ in your .gitignore file first then add the new and changed files, commit
git add [files]
git commit -m "clean unconfigured standard project"
git push upstream [branch]
With this proper instance we start messing around:
Create a pyramid_oereb.yml file in the project root folder copy the content of pyramid_oereb_standard.yml in it
and adapt the necessary parameters to your environnement - p.ex db_connection and so on
in the development.ini and production.ini at the end of the [app:main] block add 
pyramid_oereb.cfg.file = pyramid_oereb_standard.yml
pyramid_oereb.cfg.section = pyramid_oereb

14. Install all the standard test and db scripts in the project
.build\venv\Scripts\python setup.py develop

15. Configure the database settings and install standard tables
Make sure (eg using pgAdmin) the configured database exists and has the postgis extensions installed (create extension postgis)
Set the db parameters in your pyramid_oereb.yml config or use pyramid_oereb_standard.yml for your test environnement then
.build\venv\Scripts\create_standard_tables.exe -c pyramid_oereb_standard.yml

16. Load sample data in the standard db or connect your own PLR database
for standard sample data:
.build\venv\Scripts\load_standard_sample_data.exe -c pyramid_oereb_standard.yml

17. Don't forget to include the configuration adding
config.include('pyramid_oereb', route_prefix='oereb')
in \oereb\__init__.py just befor the line config.scan()

For testing start the local instance with:
.build\venv\Scripts\pserve --reload development.ini
!! ATTENTION, on windows you may have an error message regarding 'encoding'
if that's the case, remove the --reload from the command:
.build\venv\Scripts\pserve development.ini

And call a sample extract: http://localhost:6543/oereb/extract/embeddable/json/CH113928077734
or at least
http://localhost:6543/oereb/versions.json


Update existing pyramid_oereb egg
- Uninstall the existing egg
.build\venv\Scripts\pip uninstall pyramid_oereb
- Install the new version
.build\venv\Scripts\pip install pyramid_oereb
	If for some reasons you need the latest version from git (master), use
.build\venv\Scripts\pip install git+https://github.com/camptocamp/pyramid_oereb.git@master#egg=pyramid_oereb
then rebuild the app with
.build\venv\Scripts\python setup.py develop

External link
-------------

- [Documentation](https://camptocamp.github.io/pyramid_oereb/doc/)
