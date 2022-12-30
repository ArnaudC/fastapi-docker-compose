set -x
set -e

if [ "$#" -ne 1 ]; then
    echo "Expected dump name in the first argument."
fi

RESTORE_FILE=$1

echo "Restoring $RESTORE_FILE into $DB_HOST:$DB_PORT/$DB_NAME"

PGPASSWORD="$POSTGRES_PASSWORD" psql $PCONN -U "$POSTGRES_USER" -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$DB_NAME';" postgres
PGPASSWORD="$DB_OWNER_PASS" psql $PCONN -U "$DB_OWNER" -c "drop database if exists $DB_NAME;" postgres
PGPASSWORD="$DB_OWNER_PASS" psql $PCONN  -U "$DB_OWNER" -c "create database $DB_NAME with encoding='utf8' template=template0;" postgres
PGPASSWORD="$DB_OWNER_PASS" psql $PCONN -U "$DB_OWNER" --set ON_ERROR_STOP=on "$DB_NAME" < "$RESTORE_FILE"

if [ $? -eq 0 ]; then
    echo -e "==> Dump restored.\n"
else
    echo -e "\e[1;31mERROR: \e[0m\e[31m A problem occured during the restore of the dump to $DB_URL\e[0m"
fi
