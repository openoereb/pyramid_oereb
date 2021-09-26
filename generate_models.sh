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
$($VENV_BIN/$MODEL_SCRIPT -c ch.ProjektierungszonenNationalstrassen -g MULTIPOLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.BaulinienNationalstrassen -g LINESTRING -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.BaulinienEisenbahnanlagen -g LINESTRING -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.ProjektierungszonenEisenbahnanlagen -g POLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.ProjektierungszonenFlughafenanlagen -g POLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.BaulinienFlughafenanlagen -g LINESTRING -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.Sicherheitszonenplan -g MULTIPOLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ContaminatedSites -g GEOMETRYCOLLECTION -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.BelasteteStandorteMilitaer -g GEOMETRYCOLLECTION -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.BelasteteStandorteZivileFlugplaetze -g GEOMETRYCOLLECTION -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.BelasteteStandorteOeffentlicherVerkehr -g GEOMETRYCOLLECTION -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.Grundwasserschutzzonen -g POLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.Grundwasserschutzareale -g POLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c NoiseSensitivityLevels -g POLYGON -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.StatischeWaldgrenzen -g LINESTRING -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)
$($VENV_BIN/$MODEL_SCRIPT -c ch.Waldabstandslinien -g LINESTRING -p $MODEL_PATH -k $MODEL_PK_TYPE_IS_STRING)

echo "models using '$MODEL_SCRIPT' created in $MODEL_PATH"
