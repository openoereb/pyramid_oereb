#!/bin/bash
# wait-for-db.sh

counter=0

docker_container="$1"
pg_password="$2"
pg_user="$3"

cmd="PGPASSWORD=$pg_password exec psql -h \"\$POSTGRES_PORT_5432_TCP_ADDR\" -p \"\$POSTGRES_PORT_5432_TCP_PORT\" -U $pg_user -w -c \"\l\""

echo -n "Waiting for database to be ready"
until docker run -i --link "$docker_container":postgres --rm postgres sh -c "$cmd" > /dev/null 2>&1; do
  echo -n "."
  sleep 1
  counter=$((counter+1))
  if [ $counter -eq 60 ]
  then
    echo $'\nConnection to database failed: timeout.'
    exit 1
  fi
done

echo $'\nDatabase is ready. Continue with setup...'
