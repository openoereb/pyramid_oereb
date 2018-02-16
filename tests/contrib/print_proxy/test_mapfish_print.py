# -*- coding: utf-8 -*-
import pytest
from pyramid_oereb.contrib.print_proxy.mapfish_print import Renderer
from tests.renderer import DummyRenderInfo


@pytest.fixture()
def coordinates():
    return [(((2608901.529, 1261990.655), (2608898.665, 1261991.598), (2608895.798, 1261992.53),
              (2608892.928, 1261993.452), (2608890.054, 1261994.363), (2608880.256, 1261996.496),
              (2608873.932, 1261998.379), (2608867.594, 1262000.213), (2608861.242, 1262001.998),
              (2608854.876, 1262003.733), (2608848.497, 1262005.419), (2608844.698, 1262006.399),
              (2608796.844, 1261780.919), (2608799.632, 1261780.327), (2608782.789, 1261700.967),
              (2608782.961, 1261700.722), (2608783.177, 1261700.516), (2608783.43, 1261700.357),
              (2608783.71, 1261700.251), (2608784.005, 1261700.202), (2608855.37, 1261693.184),
              (2608870.718, 1261765.538), (2608943.776, 1261750.037), (2608952.331, 1261796.603),
              (2608961.92, 1261847.725), (2608969.845, 1261889.377), (2608975.711, 1261920.203),
              (2608913.546, 1261933.412), (2608912.328, 1261934.762), (2608911.162, 1261936.157),
              (2608910.049, 1261937.595), (2608908.991, 1261939.073), (2608907.988, 1261940.59),
              (2608907.043, 1261942.144), (2608906.157, 1261943.731), (2608905.331, 1261945.351),
              (2608904.566, 1261947.0), (2608903.863, 1261948.677), (2608903.223, 1261950.379),
              (2608902.648, 1261952.104), (2608909.114, 1261982.572), (2608909.22, 1261983.241),
              (2608909.256, 1261983.918), (2608909.221, 1261984.594), (2608909.115, 1261985.263),
              (2608908.941, 1261985.918), (2608908.699, 1261986.551), (2608908.393, 1261987.155),
              (2608908.026, 1261987.724), (2608907.601, 1261988.252), (2608907.124, 1261988.733),
              (2608901.529, 1261990.655)), )]


@pytest.fixture()
def symbol_ref_base():
    return 'http://localhost:6543/oereb/image/symbol/'


@pytest.fixture()
def symbol_ref_1():
    return symbol_ref_base() + 'ContaminatedPublicTransportSites/StaoTyp1'


@pytest.fixture()
def symbol_ref_2():
    return symbol_ref_base() + 'ContaminatedPublicTransportSites/StaoTyp2'


@pytest.fixture()
def symbol_ref_3():
    return symbol_ref_base() + 'ContaminatedPublicTransportSites/StaoTyp3'


@pytest.fixture()
def responsible_office_web():
    return 'http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html'


@pytest.fixture()
def bav_pdf():
    return 'https://www.bav.admin.ch/dam/bav/de/dokumente/das-bav/finanzierung/faktenblatt_fernverkehr' +\
        '_konzessionierung.pdf.download.pdf/d_Faktenblatt_Fernverkehr_und_Konzessionierung%20.pdf'


@pytest.fixture()
def reference_wms_start():
    return 'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default&SRS=EPSG' +\
        '%3A2056&BBOX=2608548.9505454544%2C1261661.8624999998%2C2609209.5494545456%2C1262037.7205&W' +\
        'IDTH=2055.1181102362207&HEIGHT=1169.291338582677&FORMAT=image%2Fpng'


@pytest.fixture()
def legend_web():
    return 'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetLegendGraphic&VERSION=1.1.1&FORMAT=image/png' +\
        '&LAYER=ch.bav.kataster-belasteter-standorte-oev.oereb'


@pytest.fixture()
def extract():
    return {
        'CreationDate': '2018-01-09T13:54:59',
        'isReduced': True,
        'ExtractIdentifier': 'c0c62a19-1cfb-4c69-864e-1e5e77f0e494',
        'BaseData': [{
            'Language': 'de',
            'Text': 'Daten der amtlichen Vermessung, Stand 09.01.2018.'
        }],
        'PLRCadastreAuthority': {
            'Name': [{
                'Language': 'de',
                'Text': 'ÖREB-Katasteraufsichtsbehörde'
            }],
            'OfficeAtWeb': 'https://www.cadastre.ch/en/oereb.html',
            'Street': 'Seftigenstrasse',
            'Number': 264,
            'PostalCode': 3084,
            'City': 'Wabern'
        },
        'RealEstate': {
            'Type': 'Liegenschaft',
            'Canton': 'BL',
            'Municipality': 'Oberwil (BL)',
            'FosNr': 2771,
            'LandRegistryArea': 35121,
            'PlanForLandRegister': {
                'ReferenceWMS': reference_wms_start() + '&LAYERS=ch.swisstopo-vd.amtliche-vermessung'
            },
            'Limit': {
                'coordinates': coordinates(),
                'crs': 'EPSG:2056'
            },
            'Number': '70',
            'IdentDN': 'BL0200002771',
            'EGRID': 'CH113928077734',
            'RestrictionOnLandownership': [{
                'Information': [{
                    'Language': 'de',
                    'Text': 'Belastet, untersuchungsbedürftig'
                }],
                'Theme': {
                    'Code': 'ContaminatedPublicTransportSites',
                    'Text': {
                        'Language': 'de',
                        'Text': 'Belastete Standorte Öffentlicher Verkehr'
                    }
                },
                'Lawstatus': {
                    'Code': 'inForce',
                    'Text': {
                        'Language': 'de',
                        'Text': 'in Kraft'
                    }
                },
                'ResponsibleOffice': {
                    'Name': [{
                        'Language': 'de',
                        'Text': 'Bundesamt für Verkehr BAV'
                    }],
                    'OfficeAtWeb': 'http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html'
                },
                'Map': {
                    'ReferenceWMS': reference_wms_start() +
                    '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb',
                    'LegendAtWeb': legend_web()
                },
                'SymbolRef': symbol_ref_2(),
                'Area': 7824,
                'TypeCode': 'StaoTyp2',
                'TypeCodelist': '',
                'PartInPercent': 22.3,
                'LegalProvisions': [{
                    'Lawstatus': {
                        'Code': 'inForce',
                        'Text': {
                            'Language': 'de',
                            'Text': 'in Kraft'
                        }
                    },
                    'TextAtWeb': [{
                        'Language': 'de',
                        'Text': bav_pdf()
                    }],
                    'Title': [{
                        'Language': 'de',
                        'Text': 'B61001'
                    }],
                    'ResponsibleOffice': {
                        'Name': [{
                            'Language': 'de',
                            'Text': 'Bundesamt für Verkehr BAV'
                        }],
                        'OfficeAtWeb': responsible_office_web()
                    },
                    'OfficialNumber': '',
                    'Canton': 'BL',
                    'Reference': [{
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_01.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Umweltschutzgesetz'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'USG'
                        }],
                        'OfficialNumber': 'SR 814.01',
                        'Canton': ''
                    }, {
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_680.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Altlasten-Verordnung'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'AltlV'
                        }],
                        'OfficialNumber': 'SR 814.680',
                        'Canton': ''
                    }]
                }]
            }, {
                'Information': [{
                    'Language': 'de',
                    'Text': 'Belastet, untersuchungsbedürftig'
                }],
                'Theme': {
                    'Code': 'ContaminatedPublicTransportSites',
                    'Text': {
                        'Language': 'de',
                        'Text': 'Belastete Standorte Öffentlicher Verkehr'
                    }
                },
                'Lawstatus': {
                    'Code': 'inForce',
                    'Text': {
                        'Language': 'de',
                        'Text': 'in Kraft'
                    }
                },
                'ResponsibleOffice': {
                    'Name': [{
                        'Language': 'de',
                        'Text': 'Bundesamt für Verkehr BAV'
                    }],
                    'OfficeAtWeb': responsible_office_web()
                },
                'Map': {
                    'ReferenceWMS': reference_wms_start() +
                    '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb',
                    'LegendAtWeb': legend_web()
                },
                'SymbolRef': symbol_ref_2(),
                'Area': 3608,
                'TypeCode': 'StaoTyp2',
                'TypeCodelist': '',
                'PartInPercent': 10.3,
                'LegalProvisions': [{
                    'Lawstatus': {
                        'Code': 'inForce',
                        'Text': {
                            'Language': 'de',
                            'Text': 'in Kraft'
                        }
                    },
                    'TextAtWeb': [{
                        'Language': 'de',
                        'Text': bav_pdf()
                    }],
                    'Title': [{
                        'Language': 'de',
                        'Text': 'B61001'
                    }],
                    'ResponsibleOffice': {
                        'Name': [{
                            'Language': 'de',
                            'Text': 'Bundesamt für Verkehr BAV'
                        }],
                        'OfficeAtWeb': responsible_office_web()
                    },
                    'OfficialNumber': '',
                    'Canton': 'BL',
                    'Reference': [{
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_01.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Umweltschutzgesetz'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'USG'
                        }],
                        'OfficialNumber': 'SR 814.01',
                        'Canton': ''
                    }, {
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_680.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Altlasten-Verordnung'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'AltlV'
                        }],
                        'OfficialNumber': 'SR 814.680',
                        'Canton': ''
                    }]
                }]
            }, {
                'Information': [{
                    'Language': 'de',
                    'Text': 'Belastet, überwachungsbedürftig'
                }],
                'Theme': {
                    'Code': 'ContaminatedPublicTransportSites',
                    'Text': {
                        'Language': 'de',
                        'Text': 'Belastete Standorte Öffentlicher Verkehr'
                    }
                },
                'Lawstatus': {
                    'Code': 'inForce',
                    'Text': {
                        'Language': 'de',
                        'Text': 'in Kraft'
                    }
                },
                'ResponsibleOffice': {
                    'Name': [{
                        'Language': 'de',
                        'Text': 'Bundesamt für Verkehr BAV'
                    }],
                    'OfficeAtWeb': 'http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html'
                },
                'Map': {
                    'ReferenceWMS': reference_wms_start() +
                    '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb',
                    'LegendAtWeb': legend_web()
                },
                'SymbolRef': symbol_ref_3(),
                'Length': 101,
                'TypeCode': 'StaoTyp3',
                'TypeCodelist': '',
                'LegalProvisions': [{
                    'Lawstatus': {
                        'Code': 'inForce',
                        'Text': {
                            'Language': 'de',
                            'Text': 'in Kraft'
                        }
                    },
                    'TextAtWeb': [{
                        'Language': 'de',
                        'Text': bav_pdf()
                    }],
                    'Title': [{
                        'Language': 'de',
                        'Text': 'B61001'
                    }],
                    'ResponsibleOffice': {
                        'Name': [{
                            'Language': 'de',
                            'Text': 'Bundesamt für Verkehr BAV'
                        }],
                        'OfficeAtWeb': responsible_office_web()
                    },
                    'OfficialNumber': '',
                    'Canton': 'BL',
                    'Reference': [{
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_01.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Umweltschutzgesetz'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'USG'
                        }],
                        'OfficialNumber': 'SR 814.01',
                        'Canton': ''
                    }, {
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_680.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Altlasten-Verordnung'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'AltlV'
                        }],
                        'OfficialNumber': 'SR 814.680',
                        'Canton': ''
                    }]
                }]
            }, {
                'Information': [{
                    'Language': 'de',
                    'Text': 'Belastet, überwachungsbedürftig'
                }],
                'Theme': {
                    'Code': 'ContaminatedPublicTransportSites',
                    'Text': {
                        'Language': 'de',
                        'Text': 'Belastete Standorte Öffentlicher Verkehr'
                    }
                },
                'Lawstatus': {
                    'Code': 'inForce',
                    'Text': {
                        'Language': 'de',
                        'Text': 'in Kraft'
                    }
                },
                'ResponsibleOffice': {
                    'Name': [{
                        'Language': 'de',
                        'Text': 'Bundesamt für Verkehr BAV'
                    }],
                    'OfficeAtWeb': responsible_office_web()
                },
                'Map': {
                    'ReferenceWMS': reference_wms_start() +
                    '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb',
                    'LegendAtWeb': legend_web()
                },
                'SymbolRef': symbol_ref_3(),
                'Length': 63,
                'TypeCode': 'StaoTyp3',
                'TypeCodelist': '',
                'LegalProvisions': [{
                    'Lawstatus': {
                        'Code': 'inForce',
                        'Text': {
                            'Language': 'de',
                            'Text': 'in Kraft'
                        }
                    },
                    'TextAtWeb': [{
                        'Language': 'de',
                        'Text': bav_pdf()
                    }],
                    'Title': [{
                        'Language': 'de',
                        'Text': 'B61001'
                    }],
                    'ResponsibleOffice': {
                        'Name': [{
                            'Language': 'de',
                            'Text': 'Bundesamt für Verkehr BAV'
                        }],
                        'OfficeAtWeb': responsible_office_web()
                    },
                    'OfficialNumber': '',
                    'Canton': 'BL',
                    'Reference': [{
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_01.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Umweltschutzgesetz'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'USG'
                        }],
                        'OfficialNumber': 'SR 814.01',
                        'Canton': ''
                    }, {
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_680.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Altlasten-Verordnung'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'AltlV'
                        }],
                        'OfficialNumber': 'SR 814.680',
                        'Canton': ''
                    }]
                }]
            }, {
                'Information': [{
                    'Language': 'de',
                    'Text': 'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
                }],
                'Theme': {
                    'Code': 'ContaminatedPublicTransportSites',
                    'Text': {
                        'Language': 'de',
                        'Text': 'Belastete Standorte Öffentlicher Verkehr'
                    }
                },
                'Lawstatus': {
                    'Code': 'inForce',
                    'Text': {
                        'Language': 'de',
                        'Text': 'in Kraft'
                    }
                },
                'ResponsibleOffice': {
                    'Name': [{
                        'Language': 'de',
                        'Text': 'Bundesamt für Verkehr BAV'
                    }],
                    'OfficeAtWeb': responsible_office_web()
                },
                'Map': {
                    'ReferenceWMS': reference_wms_start() +
                    '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb',
                    'LegendAtWeb': legend_web()
                },
                'SymbolRef': symbol_ref_1(),
                'TypeCode': 'StaoTyp1',
                'TypeCodelist': '',
                'LegalProvisions': [{
                    'Lawstatus': {
                        'Code': 'inForce',
                        'Text': {
                            'Language': 'de',
                            'Text': 'in Kraft'
                        }
                    },
                    'TextAtWeb': [{
                        'Language': 'de',
                        'Text': bav_pdf()
                    }],
                    'Title': [{
                        'Language': 'de',
                        'Text': 'B61001'
                    }],
                    'ResponsibleOffice': {
                        'Name': [{
                            'Language': 'de',
                            'Text': 'Bundesamt für Verkehr BAV'
                        }],
                        'OfficeAtWeb': responsible_office_web()
                    },
                    'OfficialNumber': '',
                    'Canton': 'BL',
                    'Reference': [{
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_01.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Umweltschutzgesetz'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'USG'
                        }],
                        'OfficialNumber': 'SR 814.01',
                        'Canton': ''
                    }, {
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_680.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Altlasten-Verordnung'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'AltlV'
                        }],
                        'OfficialNumber': 'SR 814.680',
                        'Canton': ''
                    }]
                }]
            }, {
                'Information': [{
                    'Language': 'de',
                    'Text': 'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
                }],
                'Theme': {
                    'Code': 'GroundwaterProtectionZones',
                    'Text': {
                        'Language': 'de',
                        'Text': 'Grundwasserschutzzonen'
                    }
                },
                'Lawstatus': {
                    'Code': 'inForce',
                    'Text': {
                        'Language': 'de',
                        'Text': 'in Kraft'
                    }
                },
                'ResponsibleOffice': {
                    'Name': [{
                        'Language': 'de',
                        'Text': 'Bundesamt für Verkehr BAV'
                    }],
                    'OfficeAtWeb': responsible_office_web()
                },
                'Map': {
                    'ReferenceWMS': reference_wms_start() +
                    '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb',
                    'LegendAtWeb': legend_web()
                },
                'SymbolRef': 'http://localhost:6543/oereb/image/symbol/GroundwaterProtectionZones/StaoTyp2',
                'Area': 7824,
                'TypeCode': 'StaoTyp2',
                'TypeCodelist': '',
                'PartInPercent': 22.3,
                'LegalProvisions': [{
                    'Lawstatus': {
                        'Code': 'inForce',
                        'Text': {
                            'Language': 'de',
                            'Text': 'in Kraft'
                        }
                    },
                    'TextAtWeb': [{
                        'Language': 'de',
                        'Text': bav_pdf()
                    }],
                    'Title': [{
                        'Language': 'de',
                        'Text': 'B61001'
                    }],
                    'ResponsibleOffice': {
                        'Name': [{
                            'Language': 'de',
                            'Text': 'Bundesamt für Verkehr BAV'
                        }],
                        'OfficeAtWeb': responsible_office_web()
                    },
                    'OfficialNumber': '',
                    'Canton': 'BL',
                    'Reference': [{
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_01.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Umweltschutzgesetz'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'USG'
                        }],
                        'OfficialNumber': 'SR 814.01',
                        'Canton': ''
                    }, {
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_680.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Altlasten-Verordnung'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'AltlV'
                        }],
                        'OfficialNumber': 'SR 814.680',
                        'Canton': ''
                    }]
                }]
            }, {
                'Information': [{
                    'Language': 'de',
                    'Text': 'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
                }],
                'Theme': {
                    'Code': 'ForestPerimeters',
                    'Text': {
                        'Language': 'de',
                        'Text': 'Waldgrenzen'
                    }
                },
                'Lawstatus': {
                    'Code': 'inForce',
                    'Text': {
                        'Language': 'de',
                        'Text': 'in Kraft'
                    }
                },
                'ResponsibleOffice': {
                    'Name': [{
                        'Language': 'de',
                        'Text': 'Bundesamt für Verkehr BAV'
                    }],
                    'OfficeAtWeb': responsible_office_web()
                },
                'Map': {
                    'ReferenceWMS': reference_wms_start() +
                    '&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb',
                    'LegendAtWeb': legend_web()
                },
                'SymbolRef': 'http://localhost:6543/oereb/image/symbol/ForestPerimeters/StaoTyp3',
                'Length': 101,
                'TypeCode': 'StaoTyp3',
                'TypeCodelist': '',
                'LegalProvisions': [{
                    'Lawstatus': {
                        'Code': 'inForce',
                        'Text': {
                            'Language': 'de',
                            'Text': 'in Kraft'
                        }
                    },
                    'TextAtWeb': [{
                        'Language': 'de',
                        'Text': bav_pdf()
                    }],
                    'Title': [{
                        'Language': 'de',
                        'Text': 'B61001'
                    }],
                    'ResponsibleOffice': {
                        'Name': [{
                            'Language': 'de',
                            'Text': 'Bundesamt für Verkehr BAV'
                        }],
                        'OfficeAtWeb': responsible_office_web()
                    },
                    'OfficialNumber': '',
                    'Canton': 'BL',
                    'Reference': [{
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_01.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Umweltschutzgesetz'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'USG'
                        }],
                        'OfficialNumber': 'SR 814.01',
                        'Canton': ''
                    }, {
                        'Lawstatus': {
                            'Code': 'inForce',
                            'Text': {
                                'Language': 'de',
                                'Text': 'in Kraft'
                            }
                        },
                        'TextAtWeb': [{
                            'Language': 'de',
                            'Text': 'http://www.admin.ch/ch/d/sr/c814_680.html'
                        }],
                        'Title': [{
                            'Language': 'de',
                            'Text': 'Altlasten-Verordnung'
                        }],
                        'ResponsibleOffice': {
                            'Name': [{
                                'Language': 'de',
                                'Text': 'Bundesamt für Verkehr BAV'
                            }],
                            'OfficeAtWeb': responsible_office_web()
                        },
                        'Abbrevation': [{
                            'Language': 'de',
                            'Text': 'AltlV'
                        }],
                        'OfficialNumber': 'SR 814.680',
                        'Canton': ''
                    }]
                }]
            }]
        },
        'ConcernedTheme': [{
            'Code': 'ContaminatedPublicTransportSites',
            'Text': {
                'Language': 'de',
                'Text': 'Belastete Standorte Öffentlicher Verkehr'
            }
        }, {
            'Code': 'GroundwaterProtectionZones',
            'Text': {
                'Language': 'de',
                'Text': 'Grundwasserschutzzonen'
            }
        }, {
            'Code': 'ForestPerimeters',
            'Text': {
                'Language': 'de',
                'Text': 'Waldgrenzen'
            }
        }],
        'NotConcernedTheme': [{
            'Code': 'LandUsePlans',
            'Text': {
                'Language': 'de',
                'Text': 'Nutzungsplanung'
            }
        }, {
            'Code': 'MotorwaysProjectPlaningZones',
            'Text': {
                'Language': 'de',
                'Text': 'Projektierungszonen Nationalstrassen'
            }
        }, {
            'Code': 'MotorwaysBuildingLines',
            'Text': {
                'Language': 'de',
                'Text': 'Baulinien Nationalstrassen'
            }
        }, {
            'Code': 'RailwaysBuildingLines',
            'Text': {
                'Language': 'de',
                'Text': 'Baulinien Eisenbahnanlagen'
            }
        }, {
            'Code': 'RailwaysProjectPlanningZones',
            'Text': {
                'Language': 'de',
                'Text': 'Projektierungszonen Eisenbahnanlagen'
            }
        }, {
            'Code': 'AirportsProjectPlanningZones',
            'Text': {
                'Language': 'de',
                'Text': 'Projektierungszonen Flughafenanlagen'
            }
        }, {
            'Code': 'AirportsBuildingLines',
            'Text': {
                'Language': 'de',
                'Text': 'Baulinien Flughafenanlagen'
            }
        }, {
            'Code': 'AirportsSecurityZonePlans',
            'Text': {
                'Language': 'de',
                'Text': 'Sicherheitszonenplan Flughafen'
            }
        }, {
            'Code': 'ContaminatedSites',
            'Text': {
                'Language': 'de',
                'Text': 'Belastete Standorte'
            }
        }, {
            'Code': 'ContaminatedMilitarySites',
            'Text': {
                'Language': 'de',
                'Text': 'Belastete Standorte Militär'
            }
        }, {
            'Code': 'ContaminatedCivilAviationSites',
            'Text': {
                'Language': 'de',
                'Text': 'Belastete Standorte Zivile Flugplätze'
            }
        }, {
            'Code': 'GroundwaterProtectionSites',
            'Text': {
                'Language': 'de',
                'Text': 'Grundwasserschutzareale'
            }
        }, {
            'Code': 'NoiseSensitivityLevels',
            'Text': {
                'Language': 'de',
                'Text': 'Lärmemfindlichkeitsstufen'
            }
        }, {
            'Code': 'ForestDistanceLines',
            'Text': {
                'Language': 'de',
                'Text': 'Waldabstandslinien'
            }
        }],
        'ThemeWithoutData': [],
        'LogoPLRCadastreRef': 'http://localhost:6543/oereb/image/logo/oereb',
        'FederalLogoRef': 'http://localhost:6543/oereb/image/logo/confederation',
        'CantonalLogoRef': 'http://localhost:6543/oereb/image/logo/canton',
        'MunicipalityLogoRef': 'http://localhost:6543/oereb/image/municipality/2771',
        'Glossary': [{
            'Title': [{
                'Language': 'de',
                'Text': 'ÖREB'
            }],
            'Content': [{
                'Language': 'de',
                'Text': 'Öffentlich-rechtliche Eigentumsbeschränkung'
            }]
        }, {
            'Title': [{
                'Language': 'de',
                'Text': None
            }],
            'Content': [{
                'Language': 'de',
                'Text': None
            }]
        }]
    }


@pytest.fixture()
def geometry():
    return {
        'type': 'MultiPolygon',
        'coordinates': coordinates()
    }


@pytest.fixture()
def expected_printable_extract():
    return {
        'CreationDate': '09.01.2018',
        'isReduced': True,
        'ExtractIdentifier': 'c0c62a19-1cfb-4c69-864e-1e5e77f0e494',
        'Footer': '09.01.2018   13:54:59   c0c62a19-1cfb-4c69-864e-1e5e77f0e494',
        'BaseData': 'Daten der amtlichen Vermessung, Stand 09.01.2018.',
        'ConcernedTheme': [{
            'Code': 'ContaminatedPublicTransportSites',
            'Text': 'Belastete Standorte Öffentlicher Verkehr'
        }, {
            'Code': 'GroundwaterProtectionZones',
            'Text': 'Grundwasserschutzzonen'
        }, {
            'Code': 'ForestPerimeters',
            'Text': 'Waldgrenzen'
        }],
        'NotConcernedTheme': [{
            'Code': 'LandUsePlans',
            'Text': 'Nutzungsplanung'
        }, {
            'Code': 'MotorwaysProjectPlaningZones',
            'Text': 'Projektierungszonen Nationalstrassen'
        }, {
            'Code': 'MotorwaysBuildingLines',
            'Text': 'Baulinien Nationalstrassen'
        }, {
            'Code': 'RailwaysBuildingLines',
            'Text': 'Baulinien Eisenbahnanlagen'
        }, {
            'Code': 'RailwaysProjectPlanningZones',
            'Text': 'Projektierungszonen Eisenbahnanlagen'
        }, {
            'Code': 'AirportsProjectPlanningZones',
            'Text': 'Projektierungszonen Flughafenanlagen'
        }, {
            'Code': 'AirportsBuildingLines',
            'Text': 'Baulinien Flughafenanlagen'
        }, {
            'Code': 'AirportsSecurityZonePlans',
            'Text': 'Sicherheitszonenplan Flughafen'
        }, {
            'Code': 'ContaminatedSites',
            'Text': 'Belastete Standorte'
        }, {
            'Code': 'ContaminatedMilitarySites',
            'Text': 'Belastete Standorte Militär'
        }, {
            'Code': 'ContaminatedCivilAviationSites',
            'Text': 'Belastete Standorte Zivile Flugplätze'
        }, {
            'Code': 'GroundwaterProtectionSites',
            'Text': 'Grundwasserschutzareale'
        }, {
            'Code': 'NoiseSensitivityLevels',
            'Text': 'Lärmemfindlichkeitsstufen'
        }, {
            'Code': 'ForestDistanceLines',
            'Text': 'Waldabstandslinien'
        }],
        'ThemeWithoutData': [],
        'LogoPLRCadastreRef': 'http://localhost:6543/oereb/image/logo/oereb',
        'FederalLogoRef': 'http://localhost:6543/oereb/image/logo/confederation',
        'CantonalLogoRef': 'http://localhost:6543/oereb/image/logo/canton',
        'MunicipalityLogoRef': 'http://localhost:6543/oereb/image/municipality/2771',
        'Glossary': [{
            'Title': 'ÖREB',
            'Content': 'Öffentlich-rechtliche Eigentumsbeschränkung'
        }, {
            'Title': None,
            'Content': None
        }],
        'PLRCadastreAuthority_Name': 'ÖREB-Katasteraufsichtsbehörde',
        'PLRCadastreAuthority_OfficeAtWeb': 'https://www.cadastre.ch/en/oereb.html',
        'PLRCadastreAuthority_Street': 'Seftigenstrasse',
        'PLRCadastreAuthority_Number': 264,
        'PLRCadastreAuthority_PostalCode': 3084,
        'PLRCadastreAuthority_City': 'Wabern',
        'RealEstate_Type': 'Liegenschaft',
        'RealEstate_Canton': 'BL',
        'RealEstate_Municipality': 'Oberwil (BL)',
        'RealEstate_FosNr': 2771,
        'RealEstate_LandRegistryArea': '35121 m²',
        'RealEstate_Number': '70',
        'RealEstate_IdentDN': 'BL0200002771',
        'RealEstate_EGRID': 'CH113928077734',
        'RealEstate_RestrictionOnLandownership': [{
            'Lawstatus_Code': 'inForce',
            'Lawstatus_Text': 'in Kraft',
            'Theme_Code': 'ContaminatedPublicTransportSites',
            'Theme_Text': 'Belastete Standorte Öffentlicher Verkehr',
            'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb': responsible_office_web(),
            'baseLayers': {
                'layers': [{
                    'type': 'wms',
                    'opacity': 1,
                    'styles': 'default',
                    'baseURL': 'https://wms.geo.admin.ch/',
                    'layers': ['ch.bav.kataster-belasteter-standorte-oev.oereb'],
                    'imageFormat': 'image/png',
                    'customParams': {
                        'TRANSPARENT': 'true'
                    }
                }, {
                    'type': 'wms',
                    'styles': 'default',
                    'opacity': 1,
                    'baseURL': 'https://wms.geo.admin.ch/',
                    'layers': ['ch.swisstopo-vd.amtliche-vermessung'],
                    'imageFormat': 'image/png',
                    'customParams': {
                        'TRANSPARENT': 'true'
                    }
                }]
            },
            'legend': legend_web(),
            'OtherLegend': [],
            'LegalProvisions': [{
                'TextAtWeb': bav_pdf(),
                'Title': 'B61001',
                'OfficialNumber': '',
                'Canton': 'BL',
                'Lawstatus_Code': 'inForce',
                'Lawstatus_Text': 'in Kraft',
                'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
                'ResponsibleOffice_OfficeAtWeb': responsible_office_web()
            }],
            'Reference': [{
                'TextAtWeb': 'http://www.admin.ch/ch/d/sr/c814_01.html',
                'Title': 'Umweltschutzgesetz',
                'Abbrevation': 'USG',
                'OfficialNumber': 'SR 814.01',
                'Canton': '',
                'Lawstatus_Code': 'inForce',
                'Lawstatus_Text': 'in Kraft',
                'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
                'ResponsibleOffice_OfficeAtWeb': responsible_office_web()
            }, {
                'TextAtWeb': 'http://www.admin.ch/ch/d/sr/c814_680.html',
                'Title': 'Altlasten-Verordnung',
                'Abbrevation': 'AltlV',
                'OfficialNumber': 'SR 814.680',
                'Canton': '',
                'Lawstatus_Code': 'inForce',
                'Lawstatus_Text': 'in Kraft',
                'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
                'ResponsibleOffice_OfficeAtWeb': responsible_office_web()
            }],
            'Article': [],
            'Legend': expected_legend_plr1(),
            'Information': '',
            'SymbolRef': '',
            'TypeCode': ''
        }, {
            'Lawstatus_Code': 'inForce',
            'Lawstatus_Text': 'in Kraft',
            'Theme_Code': 'GroundwaterProtectionZones',
            'Theme_Text': 'Grundwasserschutzzonen',
            'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb': responsible_office_web(),
            'baseLayers': {
                'layers': [{
                    'type': 'wms',
                    'opacity': 1,
                    'styles': 'default',
                    'baseURL': 'https://wms.geo.admin.ch/',
                    'layers': ['ch.bav.kataster-belasteter-standorte-oev.oereb'],
                    'imageFormat': 'image/png',
                    'customParams': {
                        'TRANSPARENT': 'true'
                    }
                }, {
                    'type': 'wms',
                    'styles': 'default',
                    'opacity': 1,
                    'baseURL': 'https://wms.geo.admin.ch/',
                    'layers': ['ch.swisstopo-vd.amtliche-vermessung'],
                    'imageFormat': 'image/png',
                    'customParams': {
                        'TRANSPARENT': 'true'
                    }
                }]
            },
            'legend': legend_web(),
            'OtherLegend': [],
            'LegalProvisions': [{
                'TextAtWeb': bav_pdf(),
                'Title': 'B61001',
                'OfficialNumber': '',
                'Canton': 'BL',
                'Lawstatus_Code': 'inForce',
                'Lawstatus_Text': 'in Kraft',
                'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
                'ResponsibleOffice_OfficeAtWeb': responsible_office_web()
            }],
            'Reference': [{
                'TextAtWeb': 'http://www.admin.ch/ch/d/sr/c814_01.html',
                'Title': 'Umweltschutzgesetz',
                'Abbrevation': 'USG',
                'OfficialNumber': 'SR 814.01',
                'Canton': '',
                'Lawstatus_Code': 'inForce',
                'Lawstatus_Text': 'in Kraft',
                'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
                'ResponsibleOffice_OfficeAtWeb': responsible_office_web()
            }, {
                'TextAtWeb': 'http://www.admin.ch/ch/d/sr/c814_680.html',
                'Title': 'Altlasten-Verordnung',
                'Abbrevation': 'AltlV',
                'OfficialNumber': 'SR 814.680',
                'Canton': '',
                'Lawstatus_Code': 'inForce',
                'Lawstatus_Text': 'in Kraft',
                'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
                'ResponsibleOffice_OfficeAtWeb': responsible_office_web()
            }],
            'Article': [],
            'Geom_Type': 'Area',
            'Legend': [{
                'TypeCode': 'StaoTyp2',
                'Geom_Type': 'Area',
                'TypeCodelist': '',
                'Area': '7824 m²',
                'PartInPercent': '22.3%',
                'SymbolRef': 'http://localhost:6543/oereb/image/symbol/GroundwaterProtectionZones/StaoTyp2',
                'Information': 'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
            }],
            'Information': '',
            'SymbolRef': '',
            'TypeCode': ''
        }, {
            'Lawstatus_Code': 'inForce',
            'Lawstatus_Text': 'in Kraft',
            'Theme_Code': 'ForestPerimeters',
            'Theme_Text': 'Waldgrenzen',
            'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb': responsible_office_web(),
            'baseLayers': {
                'layers': [{
                    'type': 'wms',
                    'opacity': 1,
                    'styles': 'default',
                    'baseURL': 'https://wms.geo.admin.ch/',
                    'layers': ['ch.bav.kataster-belasteter-standorte-oev.oereb'],
                    'imageFormat': 'image/png',
                    'customParams': {
                        'TRANSPARENT': 'true'
                    }
                }, {
                    'type': 'wms',
                    'styles': 'default',
                    'opacity': 1,
                    'baseURL': 'https://wms.geo.admin.ch/',
                    'layers': ['ch.swisstopo-vd.amtliche-vermessung'],
                    'imageFormat': 'image/png',
                    'customParams': {
                        'TRANSPARENT': 'true'
                    }
                }]
            },
            'legend': legend_web(),
            'OtherLegend': [],
            'LegalProvisions': [{
                'TextAtWeb': bav_pdf(),
                'Title': 'B61001',
                'OfficialNumber': '',
                'Canton': 'BL',
                'Lawstatus_Code': 'inForce',
                'Lawstatus_Text': 'in Kraft',
                'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
                'ResponsibleOffice_OfficeAtWeb': responsible_office_web()
            }],
            'Reference': [{
                'TextAtWeb': 'http://www.admin.ch/ch/d/sr/c814_01.html',
                'Title': 'Umweltschutzgesetz',
                'Abbrevation': 'USG',
                'OfficialNumber': 'SR 814.01',
                'Canton': '',
                'Lawstatus_Code': 'inForce',
                'Lawstatus_Text': 'in Kraft',
                'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
                'ResponsibleOffice_OfficeAtWeb': responsible_office_web()
            }, {
                'TextAtWeb': 'http://www.admin.ch/ch/d/sr/c814_680.html',
                'Title': 'Altlasten-Verordnung',
                'Abbrevation': 'AltlV',
                'OfficialNumber': 'SR 814.680',
                'Canton': '',
                'Lawstatus_Code': 'inForce',
                'Lawstatus_Text': 'in Kraft',
                'ResponsibleOffice_Name': 'Bundesamt für Verkehr BAV',
                'ResponsibleOffice_OfficeAtWeb': responsible_office_web()
            }],
            'Article': [],
            'Geom_Type': 'Length',
            'Legend': [{
                'TypeCode': 'StaoTyp3',
                'Geom_Type': 'Length',
                'TypeCodelist': '',
                'Length': '101 m',
                'SymbolRef': 'http://localhost:6543/oereb/image/symbol/ForestPerimeters/StaoTyp3',
                'Information': 'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
            }],
            'Information': '',
            'SymbolRef': '',
            'TypeCode': ''
        }],
        'baseLayers': {
            'layers': [{
                'type': 'wms',
                'styles': 'default',
                'opacity': 1,
                'baseURL': 'https://wms.geo.admin.ch/',
                'layers': ['ch.swisstopo-vd.amtliche-vermessung'],
                'imageFormat': 'image/png',
                'customParams': {
                    'TRANSPARENT': 'true'
                }
            }]
        },
        'legend': '',
        'features': {
            'features': {
                'type': 'FeatureCollection',
                'features': [{
                    'type': 'Feature',
                    'geometry': geometry(),
                    'properties': {}
                }]
            }
        }
    }


@pytest.fixture()
def expected_legend_plr1():
    return [{
        'TypeCode': 'StaoTyp1',
        'Geom_Type': 'Point',
        'TypeCodelist': '',
        'SymbolRef': 'http://localhost:6543/oereb/image/symbol/ContaminatedPublicTransportSites/StaoTyp1',
        'Information': 'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
    }, {
        'TypeCode': 'StaoTyp2',
        'Geom_Type': 'Area',
        'TypeCodelist': '',
        'Area': '11432 m²',
        'PartInPercent': '32.6%',
        'SymbolRef': 'http://localhost:6543/oereb/image/symbol/ContaminatedPublicTransportSites/StaoTyp2',
        'Information': 'Belastet, untersuchungsbedürftig'
    }, {
        'TypeCode': 'StaoTyp3',
        'Geom_Type': 'Length',
        'TypeCodelist': '',
        'Length': '164 m',
        'SymbolRef': 'http://localhost:6543/oereb/image/symbol/ContaminatedPublicTransportSites/StaoTyp3',
        'Information': 'Belastet, überwachungsbedürftig'
    }]


def test_legend():
    renderer = Renderer(DummyRenderInfo())
    pdf_to_join = set()
    printable_extract = extract()
    renderer.convert_to_printable_extract(printable_extract, geometry(), pdf_to_join)
    first_plr = printable_extract.get('RealEstate_RestrictionOnLandownership')[0]
    assert isinstance(first_plr, dict)
    first_legend = first_plr.get('Legend')
    assert first_legend == expected_legend_plr1()


def test_mapfish_print_entire_extract():
    renderer = Renderer(DummyRenderInfo())
    pdf_to_join = set()
    printable_extract = extract()
    renderer.convert_to_printable_extract(printable_extract, geometry(), pdf_to_join)
    assert printable_extract == expected_printable_extract()
