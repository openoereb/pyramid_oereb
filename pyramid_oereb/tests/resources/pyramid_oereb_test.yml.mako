pyramid_oereb:

  language:
    - de
    - fr
    - it
    - rm

  default_language: de

  flavour:
    - REDUCED
    - FULL
    - EMBEDDABLE

  app_schema:
    name: pyramid_oereb_main
    models: pyramid_oereb.standard.models.main
    db_connection: ${sqlalchemy_url}

  srid: 2056

  plr_cadastre_authority:
    name: PLR cadastre authority
    office_at_web: https://www.cadastre.ch/en/oereb.html
    street: Seftigenstrasse
    number: 264
    postal_code: 3084
    city: Wabern

  # The extract provides logos. Therefor you need to provide a path to these logos. Note: This must be a
  # valid absolute system path available for reading by the user running this server.
  logo:
    # The logo representing the swiss confederation (you can use it as is cause it is provided in this
    # repository). But if you need to change it for any reason: Feel free...
    confederation: pyramid_oereb/standard/logo_confederation.png
    # The logo representing the oereb extract CI (you can use it as is cause it is provided in this
    # repository). But if you need to change it for any reason: Feel free...
    oereb: pyramid_oereb/standard/logo_oereb.png
    # The logo representing your canton. This must be configured!
    canton: pyramid_oereb/standard/logo_sample.png

  real_estate:
    source:
      class: pyramid_oereb.lib.sources.real_estate.RealEstateDatabaseSource
      params:
        db_connection: ${sqlalchemy_url}
        model: pyramid_oereb.standard.models.main.RealEstate

  address:
    source:
      class: pyramid_oereb.lib.sources.address.AddressDatabaseSource
      params:
        db_connection: ${sqlalchemy_url}
        model: pyramid_oereb.standard.models.main.Address

  municipality:
    source:
      class: pyramid_oereb.lib.sources.municipality.MunicipalityDatabaseSource
      params:
        db_connection: ${sqlalchemy_url}
        model: pyramid_oereb.standard.models.main.Municipality

  glossary:
    source:
      class: pyramid_oereb.lib.sources.glossary.GlossaryDatabaseSource
      params:
        db_connection: ${sqlalchemy_url}
        model: pyramid_oereb.standard.models.main.Glossary

  exclusion_of_liability:
    source:
      class: pyramid_oereb.lib.sources.exclusion_of_liability.ExclusionOfLiabilityDatabaseSource
      params:
        db_connection: ${sqlalchemy_url}
        model: pyramid_oereb.standard.models.main.ExclusionOfLiability

  plr_limits:
    point_type: Point, MultiPoint
    line_types: LineString, LinearRing, MultiLineString
    polygon_types: Polygon, MultiPolygon
    min_length: 1.0
    min_area: 1.0

  extract:
    source:
      class: pyramid_oereb.lib.sources.extract.ExtractStandardDatabaseSource

  plr_limits:
    point_types: [Point, MultiPoint]
    line_types: [LineString, LinearRing, MultiLineString]
    polygon_types: [Polygon, MultiPolygon]
    min_length: 1.0
    min_area: 1.0

  plrs:

    - name: plr73
      code: LandUsePlans
      geometry_type: LINESTRING
      text:
        de: Nutzungsplanung
      language: de
      standard: true
      source:
        class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
        params:
          db_connection: ${sqlalchemy_url}
          models: pyramid_oereb.standard.models.land_use_plans

    - name: plr87
      code: MotorwaysProjectPlaningZones
      geometry_type: LINESTRING
      text:
        de: Projektierungszonen Nationalstrassen
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.motorways_project_planing_zones

    - name: plr88
      code: MotorwaysBuildingLines
      geometry_type: LINESTRING
      text:
        de: Baulinien Nationalstrassen
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.motorways_building_lines

    - name: plr97
      code: RailwaysBuildingLines
      geometry_type: LINESTRING
      text:
        de: Baulinien Eisenbahnanlagen
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.railways_building_lines

    - name: plr96
      code: RailwaysProjectPlanningZones
      geometry_type: POLYGON
      text:
        de: Projektierungszonen Eisenbahnanlagen
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.railways_project_planning_zones

    - name: plr103
      code: AirportsProjectPlanningZones
      geometry_type: POLYGON
      text:
        de: Projektierungszonen Flughafenanlagen
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.airports_project_planning_zones

    - name: plr104
      code: AirportsBuildingLines
      geometry_type: POLYGON
      text:
        de: Baulinien Flughafenanlagen
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.airports_building_lines

    - name: plr108
      code: AirportsSecurityZonePlans
      geometry_type: POLYGON
      text:
        de: Sicherheitszonenplan Flughafen
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.airports_security_zone_plans

    - name: plr116
      code: ContaminatedSites
      geometry_type: POLYGON
      text:
        de: Belastete Standorte
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.contaminated_sites

    - name: plr117
      code: ContaminatedMilitarySites
      geometry_type: POLYGON
      text:
        de: Belastete Standorte Militär
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.contaminated_military_sites

    - name: plr118
      code: ContaminatedCivilAviationSites
      geometry_type: POLYGON
      text:
        de: Belastete Standorte Zivile Flugplätze
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.contaminated_civil_aviation_sites

    - name: plr119
      code: ContaminatedPublicTransportSites
      geometry_type: POLYGON
      text:
        de: Belastete Standorte Öeffentlicher Verkehr
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.contaminated_public_transport_sites

    - name: plr131
      code: GroundwaterProtectionZones
      geometry_type: POLYGON
      text:
        de: Grundwasserschutzzonen
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.groundwater_protection_zones

    - name: plr132
      code: GroundwaterProtectionSites
      geometry_type: POLYGON
      text:
        de: Grundwasserschutzareale
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.groundwater_protection_sites

    - name: plr145
      code: NoiseSensitivityLevels
      geometry_type: POLYGON
      text:
        de: Lärmemfindlichkeitsstufen
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.noise_sensitivity_levels

    - name: plr157
      code: ForestPerimeters
      geometry_type: POLYGON
      text:
        de: Waldgrenzen
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.forest_perimeters

    - name: plr159
      code: ForestDistanceLines
      geometry_type: POLYGON
      text:
        de: Waldabstandslinien
      language: de
      standard: true
      source:
         class: pyramid_oereb.lib.sources.plr.PlrStandardDatabaseSource
         params:
           db_connection: ${sqlalchemy_url}
           models: pyramid_oereb.standard.models.forest_distance_lines
