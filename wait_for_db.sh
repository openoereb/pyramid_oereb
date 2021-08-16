#!/bin/sh
# wait_for_db.sh

until psql -h $PGHOST -U $PGUSER -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo 'Database is ready. Continue with setup...'

exec $@
