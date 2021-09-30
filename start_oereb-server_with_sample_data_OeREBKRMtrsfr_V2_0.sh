#!/bin/bash

docker-compose exec oereb-db psql -U postgres -c "DROP DATABASE oereb_fed_test;"
docker-compose exec oereb-db psql -U postgres -c "CREATE DATABASE oereb_fed_test WITH TEMPLATE template_postgis"
docker-compose exec oereb-db psql -U postgres -d oereb_fed_test -f /restore/oereb_fed_test.sql

docker-compose exec oereb-server make clean-all
docker-compose exec oereb-server make prepare_fed_data
jq -s '.[0] + .[1]' sample_data/ch.themes.json sample_data_OeREBKRMtrsfr_V2_0/themes.json > ch.themes.json
sudo mv ch.themes.json sample_data/.
docker-compose exec oereb-server make serve-dev