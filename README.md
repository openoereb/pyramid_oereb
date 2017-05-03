pyramid_oereb (ÖREB-Server)
===========================
[![Build Status](https://travis-ci.com/camptocamp/pyramid_oereb.svg?token=oTUZsPVUPe1BYV5bzANE&branch=master)](https://travis-ci.com/camptocamp/pyramid_oereb)

_pyramid_oereb_ is an open-source implementation of the server side part for the swiss ["Cadastre of Public-law Restrictions on landownership" (PLR-cadastre)](https://www.cadastre.ch/en/oereb.html).

It is written in Python and designed as a plugin for the [Pyramid Web Framework](http://docs.pylonsproject.org/projects/pyramid/en/latest/). This allows _pyramid_oereb_ to be included in any Pyramid web application.


Basic idea
----------

You are looking at a highly configurable piece of software. To get the right understanding of the server it 
is highly recommended to read this part carefully.

Since the confederations definitions and the specifications for the extract of OEREB data are really straight 
 we had very narrow margins to develop the code. Using this pyramid plugin you will get a running server 
 instance which is able to provide the services with output satisfying the specification of the confederation.
 But to get this extract you need to bind the data to this server. And this is basically what you need to 
 configure.

For configuration we use the YAML system. It is a handy way to separate config in a human and machine 
readable way in text files. 

![Screenshot](doc/images/configuration_workflow.png)


Installation
------------

**Note:** Installing _pyramid_oereb_ requires a running Pyramid web application.

1.  If not already existent, set up a Pyramid web application.
2.  Install the Python package _pyramid_oereb_ in the Python environment of your application.
    ```
    pip install pyramid_oereb
    ```
3.  Include the Pyramid plugin in your application. Edit the application's main method and add the following line:
    ```python
    config.include('pyramid_oereb', route_prefix='oereb')
    ```
    It is recommended to define a route prefix like "oereb" or something similar (You are free to choose 
    whatever prefix you like).
4.  Add your configuration as described in the following section.
5.  Restart your web server. The PLR webservice should now be available under the specified route prefix.


Configuration
-------------

To be added...


Running development version locally
-----------------------------------

You can checkout the current master and run _pyramid_oereb_ locally, but we cannot guarantee a working configuration as it is under development. We recommend to use a linux system but the application is tested and may also be used in a windows environment.

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

To start a local server run `make serve`. It should be available unter http://localhost:6543/oereb/, e.g. http://localhost:6543/oereb/versions. To stop the server, press `CTRL + C`.
