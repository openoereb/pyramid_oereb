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
% if print_backend == 'XML2PDF':
    # Configuration for XML2PDF print service
    renderer: pyramid_oereb.contrib.print_proxy.xml_2_pdf.Renderer
    # Define whether all geometry data must be included when sending the data to the print service
    with_geometry: True
    # Base URL with application of the print server
    base_url: https://oereb-dev.gis-daten.ch/oereb/report/create
    token: 24ba4328-a306-4832-905d-b979388d4cab
    use_wms: "true"
    validate: "false"
    # The following parameters are currently not used by xml2pdf, but might be in the future (see issue #873)
    buffer: 10
    basic_map_size: [493, 280]
    pdf_dpi: 300
    pdf_map_size_millimeters: [174, 99]
% else:
    # Configuration for MapFish-Print print service
    renderer: pyramid_oereb.contrib.print_proxy.mapfish_print.Renderer
    # Define whether all geometry data must be included when sending the data to the print service
    with_geometry: False
    # Set an archive path to keep a copy of each generated pdf.
    # pdf_archive_path: /tmp
    # The minimum buffer in pixel at 72 DPI between the real estate and the map's border. If your print
    # system draws a margin around the feature (the real estate), you have to set your buffer
    # here accordingly.
    buffer: 10
    # The map size in pixel at 72 DPI (width, height), This is the defined size of a map image
    # (requested in wms urls) inside the static extract. On a pdf report, tha map size will
    # be calculated with the pdf_dpi and the pdf_map_size_millimeters below.
    basic_map_size: [493, 280]
    # The dpi used to calculate the size of the requested map (for pdf export only).
    pdf_dpi: 300
    # The map size (in millimeters) used to calculate the size of the requested map (for pdf export only).
    pdf_map_size_millimeters: [174, 99]
    # Base URL with application of the print server
    base_url: http://{PRINT_SERVICE_HOST}:{PRINT_SERVICE_PORT}/print/oereb
    # Name of the print tempate to use
    template_name: A4 portrait
    # The headers send to the print
    headers:
      Content-Type: application/json; charset=UTF-8
    # Whether to display the RealEstate_SubunitOfLandRegister (Grundbuchkreis) in the pdf extract or not.
    # Default to true.
    display_real_estate_subunit_of_land_register: true
    # Whether to display the Certification section in the pdf extract or not.
    # Default to true
    display_certification: true
    # Split themes up, so that each sub theme gets its own page
    # Disabled by default.
    split_sub_themes: false
    # Group elements of "LegalProvision" and "Hints" with the same "Title.Text" together yes/no
    # Disabled by default.
    group_legal_provisions: false
    # Will make an estimation of the total length of the Table of Content (TOC) and control that the page
    # numbering in the output pdf is consistent with TOC numbering. If it is known that the TOC is very long and
    # could run over more than one page, it is preferred to set this to true. The drawback is that it might need
    # more time to generate the PDF. If set to false, it will assume that only one TOC page exists, and this can
    # lead to wrong numbering in the TOC.
    compute_toc_pages: true
    # Specify any additional URL parameters that the print shall use for WMS calls
    wms_url_params:
      TRANSPARENT: 'true'
    # If you want the print to keep some custom URL parameters directly from the reference_wms you have defined,
    # then use the configuration option wms_url_keep_params.
    # In wms_url_keep_params, you can list which URL parameter values should be read from the reference_wms
    # and used by the print.
    # wms_url_keep_params:
    #   - ogcserver
% endif

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

  # Configuration option for full extract: apply SLD on land register WMS (defaults to true)
  full_extract_use_sld: true

  # Configuration for OEREBlex
  oereblex:
    # OEREBlex host
    host: https://oereblex.bl.ch
    # Default language of returned values
    language: de
    # Value for canton attribute
    canton: BL
    # Mapping for other optional attributes
    mapping:
      municipality: subtype
      official_number: number
      abbreviation: abbreviation
    # Handle related decree also as main document
    # By default a related decree will be added as reference of the type "legal provision" to the main
    # document. Set this flag to true, if you want the related decree to be added as additional legal
    # provision directly to the public law restriction. This might have an impact on client side rendering.
    related_decree_as_main: false
    # Same as related_decree_as_main but for related notice document.
    related_notice_as_main: false
    # Proxy to be used for web requests
    # proxy:
    #   http:
    #   https:
    # Credentials for basic authentication
    # auth:
    #   username:
    #   password:
    # Enable/disable XML validation
    validation: true
    # Additional URL parameters to pass, depending on the PLR theme
    # url_param_config:
    # - code: ForestPerimeters
    #   url_param: 'oereb_id=5'

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
    oereb:
        de: ${png_root_dir}logo_oereb_de.png
        fr: ${png_root_dir}logo_oereb_fr.png
        it: ${png_root_dir}logo_oereb_it.png
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
      # The source must have a class which represents the accessor to the source. In this example, it is an
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
  # table to avoid imports of this data every time it gets updates, you only need to change the model bound to
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
      # already implemented source which reads data from a database.
      class: pyramid_oereb.standard.sources.municipality.DatabaseSource
      # The necessary parameters to use this class
      params:
        # The connection path where the database can be found
        db_connection: *main_db_connection
        # The model which maps the municipality database table.
        model: pyramid_oereb.standard.models.main.Municipality

  # The processor of the oereb project needs access to glossary data. In the standard configuration this
  # is assumed to be read from a database. Hint: If you want to read the glossary out of an existing database
  # table to avoid imports of this data every time it gets updates, you only need to change the model bound to
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
  # configuration this is assumed to be read from a database. Hint: If you want to read the exclusion of
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
    sort_within_themes_method: pyramid_oereb.standard.hook_methods.plr_sort_within_themes
    # Example of a specific sorting method:
    # sort_within_themes_method: pyramid_oereb.contrib.plr_sort_within_themes_by_type_code

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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Nutzungsplanung (kantonal/kommunal)
        fr: Plans d'affectation (cantonaux/communaux)
        it: Piani di utilizzazione (cantonali/comunali)
        rm: Planisaziun d'utilisaziun (chantunal/communal)
        en: Land-use planning (cantonal / municipal)
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Projektierungszonen Nationalstrassen
        fr: Zones réservées des routes nationales
        it: Zone riservate per le strade nazionali
        rm: Zonas projectaziun per las vias naziunalas
        en: Reserved zones for motorways
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Baulinien Nationalstrassen
        fr: Alignements des routes nationales
        it: Allineamenti per le strade nazionali
        rm: Lingias da construcziun per las vias naziunalas
        en: Building lines for motorways
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Baulinien Eisenbahnanlagen
        fr: Alignements des installations ferroviaires
        it: Allineamenti per gli impianti ferroviari
        rm: Lingias da construcziun per implants da viafier
        en: Building lines of the railways installations
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Projektierungszonen Eisenbahnanlagen
        fr: Zones réservées des installations ferroviaires
        it: Zone riservate per gli impianti ferroviari
        rm: Zonas projectaziun per implants da viafier
        en: Reserved zones of the railways installations
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Projektierungszonen Flughafenanlagen
        fr: Zones réservées des installations aéroportuaires
        it: Zone riservate per gli impianti aeroportuali
        rm: Zonas projectaziun per implants d'eroports
        en: Reserved zones of the airport installations
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Baulinien Flughafenanlagen
        fr: Alignements des installations aéroportuaires
        it: Allineamenti per gli impianti aeroportuali
        rm: Lingias da construcziun per implants d'eroports
        en: Building lines of the airport installations
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Sicherheitszonenplan
        fr: Plan de la zone de sécurité
        it: Piano delle zone di sicurezza
        rm: Plan da zonas da segirezza
        en: Safety zone plan
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Kataster der belasteten Standorte
        fr: Cadastre des sites pollués
        it: Catasto dei siti inquinati
        rm: Cataster dals lieus contaminads
        en: Register of polluted sites
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Kataster der belasteten Standorte im Bereich des Militärs
        fr: Cadastre des sites pollués - domaine militaire
        it: Catasto dei siti inquinati nel settore militare
        rm: Cataster dals lieus contaminads en il sectur da l'armada
        en: Register of polluted sites in the area of army
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Kataster der belasteten Standorte im Bereich der zivilen Flugplätze
        fr: Cadastre des sites pollués - domaine des aérodromes civils
        it: Catasto dei siti inquinati nel settore degli aeroporti civili
        rm: Cataster dals lieus contaminads en il sectur da las plazzas aviaticas civilas
        en: Cadastre of polluted sites on civil aerodromes
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Kataster der belasteten Standorte im Bereich des öffentlichen Verkehrs
        fr: Cadastre des sites pollués - domaine des transports publics
        it: Catasto dei siti inquinati nel settore dei trasporti pubblici
        rm: Cataster dals lieus contaminads en il sectur dal traffic public
        en: Register of polluted sites in the area of public transport
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
      # Example of how sub_themes sorting can be activated (uncomment to enable):
      #sub_themes:
      #  sorter:
      #    module: pyramid_oereb.contrib.print_proxy.sub_themes.sorting
      #    class_name: ListSort
      #    params:
      #      list:
      #        - SubTheme3
      #        - SubTheme2
      #        - SubTheme1

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
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Grundwasserschutzzonen
        fr: Zones de protection des eaux souterraines
        it: Zone di protezione delle acque sotterranee
        rm: Zona da protecziun da l'aua sutterrana
        en: Groundwater protection zone
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Grundwasserschutzareale
        fr: Périmètres de protection des eaux souterraines
        it: Aree di protezione delle acque sotterranee
        rm: Areal da protecziun da l'aua sutterrana
        en: Groundwater protection areas
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Lärmempfindlichkeitsstufen (in Nutzungszonen)
        fr: Degré de sensibilité au bruit (dans les zones d'affectation)
        it: Gradi di sensibilità al rumore (in zone d'utilizzazione)
        rm: Grad da sensibilitad da canera (en zona d'utilisaziun)
        en: Noise sensitivity level (in land-use zones)
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Statische Waldgrenzen
        fr: Limites forestières statiques
        it: Margini statici della foresta
        rm: Cunfin static dal guaud
        en: Static forest perimeter
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
          unit: 'm'
          precision: 2
        area:
          limit: 1.0
          unit: 'm²'
          precision: 2
        percentage:
          precision: 1
      text:
        de: Waldabstandslinien
        fr: Distances par rapport à la forêt
        it: Linee di distanza dalle foreste
        rm: Lingias da distanza dal guaud
        en: Forest distance lines
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
