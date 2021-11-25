# -*- coding: utf-8 -*-
"""
This package offers access to the standard database structure. All defined sources are belonging directly to
the so called "standard configuration". Whenever you use a standard configuration for a topic (you configure
this in your YAML see: :ref:`configuration`)you can find further information here. All standard sources are
sub classes of the core source classes
(:ref:`base-sources`)
and the basic database source
(:ref:`api-pyramid_oereb-core-sources-basedatabasesource`).

All sources developed in this package are behaving the same. Besides the maybe implemented parameters for the
read method of course. The main approach is to establish a session with the configured database and query it.
If some error accrues it is closing the session correctly to be aware of hanging sessions.
"""
