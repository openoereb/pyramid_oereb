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
3.  Include the Pyramid plugin in your application. Edit the application's main method and add the following line:
    ```python
    config.include('pyramid_oereb', route_prefix='oereb')
    ```
    It is recommended to define a route prefix like "oereb" or something similar.
4.  Add your configuration as described in the following section.
5.  Restart your web server. The PLR webservice should now be available under the specified route prefix.


Configuration
-------------

To be added...


Running development version locally
-----------------------------------

You can checkout the current master and run _pyramid_oereb_ locally, but we cannot guarantee a working configuration as it is under development. We recommend to use a linux system.

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

To start a local server run `make serve`. The default route prefix is _oereb_.
