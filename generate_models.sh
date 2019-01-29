#!/bin/bash

if [ -z "VENV_BIN" ]
then
    echo "VENV_BIN not defined"
    exit 1
fi

if [ -z "MODEL_SCRIPT" ]
then
    echo "MODEL_SCRIPT not defined"
    exit 1
fi

if [ -z "MODEL_PATH" ]
then
    echo "MODEL_PATH not defined"
    exit 1
fi

if [ -z "MODEL_PK_TYPE_IS_STRING" ]
then
    echo "MODEL_PK_TYPE_IS_STRING not defined"
    exit 1
fi

$($VENV_BIN/$MODEL_SCRIPT -c LandUsePlans -g GEOMETRYCOLLECTION -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c MotorwaysProjectPlaningZones -g MULTIPOLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c MotorwaysBuildingLines -g LINESTRING -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c RailwaysBuildingLines -g LINESTRING -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c RailwaysProjectPlanningZones -g POLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c AirportsProjectPlanningZones -g POLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c AirportsBuildingLines -g LINESTRING -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c AirportsSecurityZonePlans -g MULTIPOLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ContaminatedSites -g GEOMETRYCOLLECTION -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ContaminatedMilitarySites -g GEOMETRYCOLLECTION -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ContaminatedCivilAviationSites -g GEOMETRYCOLLECTION -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ContaminatedPublicTransportSites -g GEOMETRYCOLLECTION -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c GroundwaterProtectionZones -g POLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c GroundwaterProtectionSites -g POLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c NoiseSensitivityLevels -g POLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ForestPerimeters -g LINESTRING -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ForestDistanceLines -g LINESTRING -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)

echo "models using '$MODEL_SCRIPT' created in $MODEL_PATH"
