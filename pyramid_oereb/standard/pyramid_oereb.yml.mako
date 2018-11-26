# This is a example yaml configuration file for the pyramid oereb server. It contains all configuration you
# need to get an up and running server.

# The line below represents the "entry point" for the yaml configuration also called section. Keep this in
# mind for later stuff. You can change it to your favorite name.
pyramid_oereb:


  # Here you can set a central proxy which can be used in the application.
  # proxies:
    # http: http://"username":"password"@your_proxy.com:8088
    # https: https://"username":"password"@your_proxy.com:8088

  # The "language" property is a list of all languages supported by this application. It only affects the
  # output of the extract webservice. The default langage below and any language specified by a "LANG"
  # parameter in a request of an extract must be in this list to be accepted.
  language:
    - de
    - fr
    - it
    - rm

  # The language that should be used by default, if no other language is specified in the request.
  # This has to be one of the languages defined above.
  default_language: de

  # The law status translations based on the two possible codes 'inForce' and 'runningModifications'
  law_status_translations:
    in_force:
      de: in Kraft
      fr: en vigueur
      it: in vigore
      rm: en vigur
      en: in force
    running_modifications:
      de: laufende Änderungen
      fr: modification en cours
      it: modifica in corso
      rm: midada current
      en: ongoing modification

  # The "flavour" property is a list of all flavours of data extracts provided by this application.
  # For the moment this only affects the output of the capabilities webservice. In later
  # versions, this will be the place to directly influence the available output formats.
  #
  # Possible flavours are: REDUCED, FULL, EMBEDDABLE, SIGNED
  # REDUCED:    Means that depending on the cantonal implementation you may be able to select
  #             a defined combination of topics to extract (e.g. only 'federal' topics without
  #             cantonal extensions - and choosing this option, legal provisions are only output
  #             as link.
  # FULL:       Means you get all topics, whether they are defined in the 17 base topics or if they
  #             are cantonal specificities.
  #             The extract will also have the legal provisions and referenced documents
  #             included as PDF.
  # SIGNED:     Is essentially the same as FULL, but the extract is certified by the competent
  #             authority
  # EMBEDDABLE: With this flavour all images and documents are included as base64 binary
  flavour:
    - REDUCED
    - FULL
    - EMBEDDABLE

  print:
    # The pyramid renderer which is used as proxy pass through to the desired service for printable static
    # extract. Here you can define the path to the logic which prepares the output as payload for print
    # service and returns the result to the user.
    renderer: pyramid_oereb.contrib.print_proxy.mapfish_print.Renderer
    # The minimum buffer in pixel at 72 DPI between the real estate and the map's border.
    buffer: 30
    # The map size in pixel at 72 DPI (width, height), This is the defined size of a map image
    # (requested in wms urls) inside the static extract. On a pdf report, tha map size will
    # be calculated with the pdf_dpi and the pdf_map_size_millimeters below.
    basic_map_size: [493, 280]
    # The dpi used to calculate the size of the requested map (for pdf export only).
    pdf_dpi: 300
    # The map size (in millimeters) used to calculate the size of the requested map (for pdf export only).
    pdf_map_size_millimeters: [174, 99]
    # Base URL with application of the print server
    base_url: http://print:8080/print/oereb
    # Name of the print template to use
    template_name: A4 portrait
    # The headers sent to the print
    headers:
      Content-Type: application/json; charset=UTF-8
    # Whether to display the RealEstate_SubunitOfLandRegister (Grundbuchkreis) in the pdf extract or not.
    # Default to true.
    display_real_estate_subunit_of_land_register: true
    # Split themes up, so that each sub theme gets its own page
    # Disabled by default.
    split_sub_themes: false

  # The "app_schema" property contains only one sub property "name". This is directly related to the database
  # creation process, because this name is used as schema name in the target database. The app_schema holds
  # all application stuff like: addresses, municipalities, real estates, etc.
  # Please note that this is only necessary if you want to use the standard configuration. Normally you don't
  # need to adjust this. Only in the unlikely case of another schema in the same database with the same name
  # you can change it here to avoid name collision. Of course you can configure the application to load this
  # data from elsewhere.
  app_schema:
    name: pyramid_oereb_main
    models: pyramid_oereb.standard.models.main
    db_connection: &main_db_connection
      ${sqlalchemy_url}

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

  # Configuration for OEREBlex
  oereblex:
    # OEREBlex host
    host: https://oereblex.bl.ch
    # geoLink schema version
    # version: 1.1.1
    # Pass schema version in URL
    # pass_version: true
    # Language of returned values
    language: de
    # Value for canton attribute
    canton: BL
    # Mapping for other optional attributes
    mapping:
      official_number: number
      abbreviation: abbreviation
    # Handle related decree also as main document
    # By default a related decree will be added as reference of the type "legal provision" to the main
    # document. Set this flag to true, if you want the related decree to be added as additional legal
    # provision directly to the public law restriction. This might have an impact on client side rendering.
    related_decree_as_main: false
    # Proxy to be used for web requests
    # proxy:
    #   http:
    #   https:
    # Credentials for basic authentication
    # auth:
    #   username:
    #   password:

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
    # The logo representing the swiss confederation. You can use it as is because it is provided in this
    # repository, but if you need to change it for any reason: Feel free...
    confederation: ${png_root_dir}logo_confederation.png
    # The logo representing the oereb extract CI. You can use it as is because it is provided in this
    # repository, but if you need to change it for any reason: Feel free...
    oereb: ${png_root_dir}logo_oereb.png
    # The logo representing your canton. Replace with your own logo!
    canton: ${png_root_dir}logo_canton.png

  # The method used to return the logo images configured above.
  get_logo_method: pyramid_oereb.standard.hook_methods.get_logo

  # The method used to return the municipality logos.
  get_municipality_method: pyramid_oereb.standard.hook_methods.get_municipality

  # The processor of the oereb project needs access to real estate data. In the standard configuration this
  # is assumed to be read from a database. Hint: If you want to read the real estate out of an existing
  # database table to avoid imports of this data every time it gets updates, you only need to change the model
  # bound to the source. The model must implement the same field names and information as the default model
  # does.
  real_estate:
    plan_for_land_register:
      # WMS URL to query the plan for land register used for all themes pages
      reference_wms: https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default&SRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&WIDTH=493&HEIGHT=280&FORMAT=image/png&LAYERS=ch.swisstopo-vd.amtliche-vermessung
      layer_index: 0
      layer_opacity: 1.0
    plan_for_land_register_main_page:
      # WMS URL to query the plan for land register specially for static extracts overview page
      reference_wms: https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default&SRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&WIDTH=493&HEIGHT=280&FORMAT=image/png&LAYERS=ch.swisstopo-vd.amtliche-vermessung
      layer_index: 0
      layer_opacity: 1.0
    visualisation:
      method: pyramid_oereb.standard.hook_methods.produce_sld_content
      # Note: these parameters must fit to the attributes provided by the RealEstateRecord!!!!
      url_params:
        - egrid
      layer:
        name: ch.swisstopo-vd.amtliche-vermessung
      style:
        stroke_opacity: 0.6
        stroke_color: '#e60000'
        stroke_width: 5
    type_mapping:
      - mapping: RealEstate
        type: Liegenschaft
      - mapping: Distinct_and_permanent_rights.BuildingRight
        type: Baurecht
      - mapping: Distinct_and_permanent_rights.right_to_spring_water
        type: Quellenrecht
      - mapping: Distinct_and_permanent_rights.concession
        type: Konzessionsrecht
      - mapping: Distinct_and_permanent_rights.other
        type: weitere
      - mapping: Mineral_rights
        type: Bergwerk
    # The real estate must have a property source.
    source:
      # The source must have a class which represents the accessor to the source. In this example, it is a an
      # already implemented source which reads data from a database.
      class: pyramid_oereb.standard.sources.real_estate.DatabaseSource
      # The necessary parameters to use this class
      params:
        # The connection path where the database can be found
        db_connection: *main_db_connection
        # The model which maps the real estate database table.
        model: pyramid_oereb.standard.models.main.RealEstate

  # The processor of the oereb project needs access to address data. In the standard configuration, this
  # is assumed to be read from a database. Hint: If you want to read the addresses out of an existing database
  # table to avoid imports of this data every time it gets updatesi, you only need to change the model bound to
  # the source. The model must implement the same field names and information as the default model does.
  address:
    # The address must have a property source.
    source:
      # The source must have a class which represents the accessor to the source. In this example, it is an
      # already implemented source which reads data from a database.
      class: pyramid_oereb.standard.sources.address.DatabaseSource
      # The necessary parameters to use this class
      params:
        # The connection path where the database can be found
        db_connection: *main_db_connection
        # The model which maps the address database table.
        model: pyramid_oereb.standard.models.main.Address
        # Alternatively, you can use the search service of the GeoAdmin API to look up the real estate by
        # address. Replace the configuration above with the following lines:
        # class: pyramid_oereb.lib.sources.address.AddressGeoAdminSource
        # # Optional referer to use.
        # referer: http://my.referer.ch
        # params:
          # # URL of the GeoAdmin API SearchServer
          # geoadmin_search_api: https://api3.geo.admin.ch/rest/services/api/SearchServer
          # # Origins to use (should be "address" only)
          # origins: address

  # The processor of the oereb project needs access to municipality data. In the standard configuration this
  # is assumed to be read from a database. Hint: If you want to read the municipality out of an existing
  # database table to avoid imports of this data every time it gets updates, you only need to change the model
  # bound to the source. The model must implement the same field names and information as the default model
  # does.
  municipality:
    # The municipality must have a property source.
    source:
      # The source must have a class which represents the accessor to the source. In this example, it is an
      # already implemented source hich reads data from a database.
      class: pyramid_oereb.standard.sources.municipality.DatabaseSource
      # The necessary parameters to use this class
      params:
        # The connection path where the database can be found
        db_connection: *main_db_connection
        # The model which maps the municipality database table.
        model: pyramid_oereb.standard.models.main.Municipality

  # The processor of the oereb project needs access to glossary data. In the standard configuration this
  # is assumed to be read from a database. Hint: If you want to read the glossary out of an existing database
  # table to avoid imports of this data every time it gets updatesi, you only need to change the model bound to
  # the source. The model must implement the same field names and information as the default model does.
  glossary:
    # The glossary must have a property source.
    source:
      # The source must have a class which represents the accessor to the source. In this example, it is an
      # already implemented source which reads data from a database.
      class: pyramid_oereb.standard.sources.glossary.DatabaseSource
      # The necessary parameters to use this class
      params:
        # The connection path where the database can be found
        db_connection: *main_db_connection
        # The model which maps the glossary database table.
        model: pyramid_oereb.standard.models.main.Glossary

  # The processor of the oereb project needs access to exclusion of liability data. In the standard
  # configuration this is assumed to be read from a database. Hint: If you wamt to read the exclusion of
  # liability out of an existing database table to avoid imports of this data every time it gets updates, you
  # only need to change the model bound to the source. The model must implement the same field names and
  # information as the default model does.
  exclusion_of_liability:
    # The exclusion_of_liability must have a property source.
    source:
      # The source must have a class which represents the accessor to the source. In this example, it is an
      # already implemented source which reads data from a database.
      class: pyramid_oereb.standard.sources.exclusion_of_liability.DatabaseSource
      # The necessary parameters to use this class
      params:
        # The connection path where the database can be found
        db_connection: *main_db_connection
        # The model which maps the exclusion_of_liability database table.
        model: pyramid_oereb.standard.models.main.ExclusionOfLiability

  # The extract is the entry point which binds everything
  # related to data together.
  extract:
    # Information about the base data used for the extract, e.g. the used base map and its currentness.
    # This is a multilingual value. In the minimum, the value for the default language has to be defined.
    base_data:
        text:
          de: "Daten der amtlichen Vermessung. Stand der amtlichen Vermessung: {0}."
          fr: "Données de la mensuration officielle, état de la mensuration officielle: {0}."
          it: "Dati della misurazione ufficiale. Stato della misurazione ufficiale: {0}."
          rm: "Datas da la mesiraziun uffiziala. Versiun dal mesiraziun uffiziala: {0}."
        methods:
          date: pyramid_oereb.standard.hook_methods.get_surveying_data_update_date
          provider:  pyramid_oereb.standard.hook_methods.get_surveying_data_provider
      # Certification and certification_at_web must be set with your own certification information.
    certification:
        de: Referenz zur kantonsspezifischen Gesetzesgrundlage bezüglich Beglaubigungen.
        fr: Référence vers les dispositions légales cantonales concernant la certification
        it: Certificazione secondo OCRDPP art. 14
        rm: ...
    certification_at_web:
        de: https://oereb.bl.ch/certification/de
        fr: https://oereb.bl.ch/certification/fr
        it: https://oereb.bl.ch/certification/it
        rm: https://oereb.bl.ch/certification/rm
    general_information:
        de: Der Inhalt des Katasters wird als bekannt vorausgesetzt. Der Kanton --HIER MUSS DER KANTONSNAME STEHEN--- ist für die Genauigkeit und Verlässlichkeit der gesetzgebenden Dokumenten in elektronischer Form nicht haftbar. Der Auszug hat rein informativen Charakter und begründet insbesondere keine Rechten und Pflichten. Rechtsverbindlich sind diejenigen Dokumente, welche rechtskräftig verabschiedet oder veröffentlicht worden sind. Mit der Beglaubigung des Auszuges wird die Übereinstimmung des Auszuges mit dem Kataster zum Zeitpunkt des Auszuges bestätigt.
        fr: Le contenu du cadastre RDPPF est supposé connu. Le canton de ---NOM DU CANTON--- n'engage pas sa responsabilité sur l'exactitude ou la fiabilité des documents législatifs dans leur version électronique. L'extrait a un caractère informatif et ne crée aucun droit ou obligation. Les documents juridiquement contraignants sont ceux qui ont été légalement adoptés ou publiés. La certification d'un extrait confirme la concordance de cet extrait avec le cadastre RDPPF à la date d'établissement dudit extrait.
        it: Il contenuto del Catasto RDPP si considera noto. Il Canton ---NOME DEL CANTON--- non può essere ritenuto responsabile per la precisione e l'affidabilità dei documenti legislativi in formato elettronico. L'estratto ha carattere puramente informativo e non è in particolare costituti-vo di diritti e obblighi. Sono considerati giuridicamente vincolanti i documenti approvati o pubblicati passati in giudicato. Con l'autenticazione dell'estratto viene confermata la conformità dell'estratto rispetto al Catasto RDPP al momento della sua redazione.
        rm: ...


  # All PLRs which are provided by this application. This is related to all application behaviour, especially
  # the extract creation process which loops over this list.
  plrs:

    - name: plr73
      code: LandUsePlans
      geometry_type: GEOMETRYCOLLECTION
      # Define the minmal area and length for public law restrictions that should be considered as 'true' restrictions
      # and not as calculation errors (false trues) due to topological imperfections
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Nutzungsplanung
      language: de
      federal: false
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 1.0
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.land_use_plans
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr87
      code: MotorwaysProjectPlaningZones
      geometry_type: MULTIPOLYGON
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Projektierungszonen Nationalstrassen
      language: de
      federal: true
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.motorways_project_planing_zones
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr88
      code: MotorwaysBuildingLines
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Baulinien Nationalstrassen
      language: de
      federal: true
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.motorways_building_lines
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr97
      code: RailwaysBuildingLines
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Baulinien Eisenbahnanlagen
      language: de
      federal: true
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.railways_building_lines
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr96
      code: RailwaysProjectPlanningZones
      geometry_type: POLYGON
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Projektierungszonen Eisenbahnanlagen
      language: de
      federal: true
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.railways_project_planning_zones
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr103
      code: AirportsProjectPlanningZones
      geometry_type: POLYGON
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Projektierungszonen Flughafenanlagen
      language: de
      federal: true
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.airports_project_planning_zones
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr104
      code: AirportsBuildingLines
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Baulinien Flughafenanlagen
      language: de
      federal: true
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.airports_building_lines
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr108
      code: AirportsSecurityZonePlans
      geometry_type: MULTIPOLYGON
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Sicherheitszonenplan Flughafen
      language: de
      federal: true
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.airports_security_zone_plans
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications
      download: https://data.geo.admin.ch/ch.bazl.sicherheitszonenplan.oereb/data.zip

    - name: plr116
      code: ContaminatedSites
      geometry_type: GEOMETRYCOLLECTION
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Belastete Standorte
      language: de
      federal: false
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 1.0
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.contaminated_sites
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr117
      code: ContaminatedMilitarySites
      geometry_type: GEOMETRYCOLLECTION
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Belastete Standorte Militär
      language: de
      federal: true
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.contaminated_military_sites
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr118
      code: ContaminatedCivilAviationSites
      geometry_type: GEOMETRYCOLLECTION
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Belastete Standorte Zivile Flugplätze
      language: de
      federal: true
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.contaminated_civil_aviation_sites
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr119
      code: ContaminatedPublicTransportSites
      geometry_type: GEOMETRYCOLLECTION
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Belastete Standorte Öffentlicher Verkehr
      language: de
      federal: true
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 0.75
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.contaminated_public_transport_sites
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr131
      code: GroundwaterProtectionZones
      geometry_type: POLYGON
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Grundwasserschutzzonen
      language: de
      federal: false
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 1.0
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.groundwater_protection_zones
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr132
      code: GroundwaterProtectionSites
      geometry_type: POLYGON
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Grundwasserschutzareale
      language: de
      federal: false
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 1.0
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.groundwater_protection_sites
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr145
      code: NoiseSensitivityLevels
      geometry_type: POLYGON
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Lärmemfindlichkeitsstufen
      language: de
      federal: false
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 1.0
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.noise_sensitivity_levels
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr157
      code: ForestPerimeters
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Waldgrenzen
      language: de
      federal: false
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 1.0
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.forest_perimeters
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications

    - name: plr159
      code: ForestDistanceLines
      geometry_type: LINESTRING
      thresholds:
        length:
          limit: 1.0
        area:
          limit: 1.0
      text:
        de: Waldabstandslinien
      language: de
      federal: false
      standard: true
      view_service:
        layer_index: 1
        layer_opacity: 1.0
      source:
        class: pyramid_oereb.standard.sources.plr.DatabaseSource
        params:
          db_connection: *main_db_connection
          models: pyramid_oereb.standard.models.forest_distance_lines
      hooks:
        get_symbol: pyramid_oereb.standard.hook_methods.get_symbol
        get_symbol_ref: pyramid_oereb.standard.hook_methods.get_symbol_ref
      law_status:
        in_force: inForce
        running_modifications: runningModifications
