# This is a example yaml configuration file for the pyramid oereb server. It contains all configuration you
# need to get an up and running server.

# The line below represents the "entry point" for the yaml configuration also called section. Keep this in
# mind for later stuff. You can change it to your favorite name. For the moment this is enough to know.
pyramid_oereb:

  # The "language" property is a list of all languages provided by this application. In the moment this only
  # affects the output of the capabilities webservice. Whatever in later versions it will be the configuration
  # also for the translation mechanism. TODO: Add more details When this feature is fully implemented!
  language:
    - de
    - fr
    - it
    - rm

  # The language that should be used by default, if no other language is specified in the request.
  # This has to be one of the languages defined above.
  default_language: de

  # The "flavour" property is a list of all flavours provided by this application. In the moment this only
  # affects the output of the capabilities webservice. Whatever in later versions it is the place to directly
  # influence the available output formats.
  #
  # Possible flavours are: REDUCED, FULL, EMBEDDABLE, SIGNED
  # TODO: Add more details When this feature is fully implemented!
  flavour:
    - REDUCED
    - FULL
    - EMBEDDABLE

  print:
    # The buffer on the map around the parcel in percent
    buffer: 10

    # The map size in pixel at 72 DPI (width, height), This is the defined size of a map image inside the
    # static extract.
    map_size: [493, 280]

    # The print DPI
    dpi: 200

    # Base URL with application of the print server
    base_url: http://localhost:8280/print/oereb

  # The "app_schema" property contains only one sub property "name". This is directly related to the database
  # creation process. Because this name is used as schema name in the target database. The app_schema holds
  # all application stuff like: addresses, municipalities, real estates, etc.
  # Please note that this is only necessary if you want to use the standard configuration. Normally you don't
  # need to adjust this. Only in the unlikely case of another schema in the same database with the same name
  # you can change it here to avoid name collision. Of cause you can configure the application to load these
  # data from else where.
  app_schema:
    name: pyramid_oereb_main
    models: pyramid_oereb.standard.models.main
    db_connection: ${sqlalchemy_url}

  # Define the SRID which your server is representing. Note: Only one projection system is possible in the
  # application. It does not provide any reprojection nor data in different projection systems. Take care in
  # your importing process!
  srid: 2056

  # definition of the available geometry types for different checks
  geometry_types:
    point:
      types:
       - Point
       - MultiPoint
    line:
       types:
       - LineString
       - LinearRing
       - MultiLineString
    polygon:
       types:
       - Polygon
       - MultiPolygon
    collection:
        types:
        - GeometryCollection

  # Defines the information of the oereb cadastre providing authority. Please change this to your data. This
  # will be directly used for producing the extract output.
  plr_cadastre_authority:
    # The name of your Office. For instance: Amt für Geoinformation Basel-Landschaft
    name:
        en: PLR cadastre authority
        de: ÖREB-Katasteraufsichtsbehörde
    # An online link to web presentation of your office. For instance: https://www.geo.bl.ch/
    office_at_web: https://www.cadastre.ch/en/oereb.html
    # The street name of the address of your office. For instance: Mühlemattstrasse
    street: Seftigenstrasse
    # The street number of the address of your office. For instance: 36
    number: 264
    # The ZIP code of the address of your office. For instance: 4410
    postal_code: 3084
    # The city name of the address of your office. For instance: Liestal
    city: Wabern

  # The extract provides logos. Therefor you need to provide a path to these logos. Note: This must be a
  # valid absolute system path available for reading by the user running this server.
  logo:
    # The logo representing the swiss confederation (you can use it as is cause it is provided in this
    # repository). But if you need to change it for any reason: Feel free...
    confederation: ${png_root_dir}logo_confederation.png
    # The logo representing the oereb extract CI (you can use it as is cause it is provided in this
    # repository). But if you need to change it for any reason: Feel free...
    oereb: ${png_root_dir}logo_oereb.png
    # The logo representing your canton. Replace with your own logo!
    canton: ${png_root_dir}logo_canton.png

  # The method used to return the logo images configured above.
  get_logo_method: pyramid_oereb.standard.methods.get_logo

  # The method used to return the municipality logos.
  get_municipality_method: pyramid_oereb.standard.methods.get_municipality

  # The processor of the oereb project needs access to real estate data. In the standard configuration this
  # is assumed to be read from a database. Hint: If you like to read the real estate out of an existing
  # database table to avoid imports of this data every time it gets updates you only need to change the model
  # bound to the source. The model must implement the same field names and information then the default model
  # does.
  real_estate:
    view_service:
      reference_wms: https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default&SRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&WIDTH=493&HEIGHT=280&FORMAT=image/png&LAYERS=ch.swisstopo-vd.amtliche-vermessung
      legend_at_web: https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetLegendGraphic&VERSION=1.1.1&FORMAT=image/png&LAYER=ch.swisstopo-vd.amtliche-vermessung
    # The real estate must have a property source.
    source:
      # The source must have a class which represents the accessor to the source. In this case it is a source
      # already implemented which reads data from a database.
      class: pyramid_oereb.lib.sources.real_estate.RealEstateDatabaseSource
      # The configured class accepts params which are also necessary to define
      params:
        # The connection path where the database can be found
        db_connection: ${sqlalchemy_url}
        # The model which maps the real estate database table.
        model: pyramid_oereb.standard.models.main.RealEstate

  # The processor of the oereb project needs access to address data. In the standard configuration this
  # is assumed to be read from a database. Hint: If you like to read the addresses out of an existing database
  # table to avoid imports of this data every time it gets updates you only need to change the model bound to
  # the source. The model must implement the same field names and information then the default model does.
  address:
    # The address must have a property source.
    source:
      # The source must have a class which represents the accessor to the source. In this case it is a source
      # already implemented which reads data from a database.
      class: pyramid_oereb.lib.sources.address.AddressDatabaseSource
      # The configured class accepts params which are also necessary to define
      params:
        # The connection path where the database can be found
        db_connection: ${sqlalchemy_url}
        # The model which maps the address database table.
        model: pyramid_oereb.standard.models.main.Address

  # The processor of the oereb project needs access to municipality data. In the standard configuration this
  # is assumed to be read from a database. Hint: If you like to read the municipality out of an existing
  # database table to avoid imports of this data every time it gets updates you only need to change the model
  # bound to the source. The model must implement the same field names and information then the default model
  # does.
  municipality:
    # The municipality must have a property source.
    source:
      # The source must have a class which represents the accessor to the source. In this case it is a source
      # already implemented which reads data from a database.
      class: pyramid_oereb.lib.sources.municipality.MunicipalityDatabaseSource
      # The configured class accepts params which are also necessary to define
      params:
        # The connection path where the database can be found
        db_connection: ${sqlalchemy_url}
        # The model which maps the municipality database table.
        model: pyramid_oereb.standard.models.main.Municipality

  # The processor of the oereb project needs access to glossary data. In the standard configuration this
  # is assumed to be read from a database. Hint: If you like to read the glossary out of an existing database
  # table to avoid imports of this data every time it gets updates you only need to change the model bound to
  # the source. The model must implement the same field names and information then the default model does.
  glossary:
    # The glossary must have a property source.
    source:
      # The source must have a class which represents the accessor to the source. In this case it is a source
      # already implemented which reads data from a database.
      class: pyramid_oereb.lib.sources.glossary.GlossaryDatabaseSource
      # The configured class accepts params which are also necessary to define
      params:
        # The connection path where the database can be found
        db_connection: ${sqlalchemy_url}
        # The model which maps the glossary database table.
        model: pyramid_oereb.standard.models.main.Glossary

  # The processor of the oereb project needs access to exclusion of liability data. In the standard
  # configuration this is assumed to be read from a database. Hint: If you like to read the exclusion of
  # liability out of an existing database table to avoid imports of this data every time it gets updates you
  # only need to change the model bound to the source. The model must implement the same field names and
  # information then the default model does.
  exclusion_of_liability:
    # The exclusion_of_liability must have a property source.
    source:
      # The source must have a class which represents the accessor to the source. In this case it is a source
      # already implemented which reads data from a database.
      class: pyramid_oereb.lib.sources.exclusion_of_liability.ExclusionOfLiabilityDatabaseSource
      # The configured class accepts params which are also necessary to define
      params:
        # The connection path where the database can be found
        db_connection: ${sqlalchemy_url}
        # The model which maps the exclusion_of_liability database table.
        model: pyramid_oereb.standard.models.main.ExclusionOfLiability

  # The extract is more an abstract implementation of a source. It is the entry point which binds everything
  # related to data together.
  extract:
    # Information about the base data used for the extract, e.g. the used base map and its currentness.
    # This is a multlingual value. At least the set default language has to be defined.
    base_data:
        text:
          de: Daten der amtlichen Vermessung, Stand {0}.
        methods:
          date: pyramid_oereb.standard.hook_methods.get_surveying_data_update_date
          provider:  pyramid_oereb.standard.hook_methods.get_surveying_data_provider
    # The extract must have a property source.
    source:
      # The source must have a class which represents the accessor to the source. In this case it is a source
      # already implemented which reads data from a database. In this case it does not take any parameters.
      class: pyramid_oereb.lib.sources.extract.ExtractStandardDatabaseSource


  # All PLR's which are provided by this application. This is related to all application behaviour. Especially
  # the extract creation process which loops over this list.
  plrs:

    - name: plr73
      code: LandUsePlans
      geometry_type: GEOMETRYCOLLECTION
      # Define the minmal area and length for public law restrictions that should be considered as 'true' restrictions
      # and not as calculation errors (false true's) due to topological imperfections
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Nutzungsplanung
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.land_use_plans
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr87
      code: MotorwaysProjectPlaningZones
      geometry_type: MULTIPOLYGON
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Projektierungszonen Nationalstrassen
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.motorways_project_planing_zones
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr88
      code: MotorwaysBuildingLines
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Baulinien Nationalstrassen
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.motorways_building_lines
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr97
      code: RailwaysBuildingLines
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Baulinien Eisenbahnanlagen
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.railways_building_lines
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr96
      code: RailwaysProjectPlanningZones
      geometry_type: POLYGON
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Projektierungszonen Eisenbahnanlagen
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.railways_project_planning_zones
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr103
      code: AirportsProjectPlanningZones
      geometry_type: POLYGON
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Projektierungszonen Flughafenanlagen
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.airports_project_planning_zones
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr104
      code: AirportsBuildingLines
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Baulinien Flughafenanlagen
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.airports_building_lines
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr108
      code: AirportsSecurityZonePlans
      geometry_type: MULTIPOLYGON
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Sicherheitszonenplan Flughafen
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.airports_security_zone_plans
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr116
      code: ContaminatedSites
      geometry_type: GEOMETRYCOLLECTION
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Belastete Standorte
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.contaminated_sites
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr117
      code: ContaminatedMilitarySites
      geometry_type: GEOMETRYCOLLECTION
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Belastete Standorte Militär
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.contaminated_military_sites
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr118
      code: ContaminatedCivilAviationSites
      geometry_type: POLYGON
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Belastete Standorte Zivile Flugplätze
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.contaminated_civil_aviation_sites
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr119
      code: ContaminatedPublicTransportSites
      geometry_type: GEOMETRYCOLLECTION
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Belastete Standorte Öeffentlicher Verkehr
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.contaminated_public_transport_sites
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr131
      code: GroundwaterProtectionZones
      geometry_type: POLYGON
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Grundwasserschutzzonen
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.groundwater_protection_zones
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr132
      code: GroundwaterProtectionSites
      geometry_type: POLYGON
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Grundwasserschutzareale
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.groundwater_protection_sites
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr145
      code: NoiseSensitivityLevels
      geometry_type: POLYGON
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Lärmemfindlichkeitsstufen
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.noise_sensitivity_levels
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr157
      code: ForestPerimeters
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Waldgrenzen
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.forest_perimeters
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol

    - name: plr159
      code: ForestDistanceLines
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm2'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Waldabstandslinien
      language: de
      federal: true
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.forest_distance_lines
      get_symbol_method: pyramid_oereb.standard.methods.get_symbol
