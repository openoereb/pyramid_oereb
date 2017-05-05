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
This is simple: Mainly all content from the [pyramid_oereb.yaml](pyramid_oereb.yml).

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
