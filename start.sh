#!/bin/bash
# Requires docker, docker-compose (v1+) : sudo apt install docker docker-compose
# Usage : `./start.sh` or `./start.sh init` to list available commands or initialize the project
set -ex

printArguments() {
    echo "Usage : sh start.sh [argument]"
    echo " init              Initialize the project from scratch (empty database)."
    echo " logs              View logs in docker container."
    echo " bash              Open a bash in docker container."
    echo " images            Rebuild images."
    echo " start|restart     Start, stop or restart docker container."
    echo " npmrunstart       Run 'npm run start' in watch mode."
    echo " npmrunbuild       Run 'npm run build' and mount the frontend in fastapi (app_spa)."
    echo " makemigration     Make a new migration with alembic."
    echo " migrate           Migrate all with alembic."
    echo " resetmigrations   Reset all alembic migrations."
    echo " fixtures          Run fixtures. Sqlalchemy and Sqlmodel are supported."
    echo " test <tname>      Run python unit and integration on test_name if provided, or on all tests."
    echo " testdebug <tname> Same as test in debug mode. See REAMDE.md for more info."
}

init() {
    docker-compose down --volumes
    docker-compose pull
    docker-compose up -d
    docker-compose exec postgres-docker bash -c "cd /home/init; ./create_db.sh"
    stop # Need to restart to create models
    start_no_logs
    resetmigrations
    fixtures
    print_url
    # npmrunbuild # If production
    logs
}

images() {
    docker-compose build
}

start() {
    docker-compose up -d
    print_url
    # npmrunstart
    logs
}

npmrunstart() {
    print_url
    docker-compose exec fastapi-docker bash -c "set -ex
        cd /frontend
        npm i
        npm run start
    "
}

npmrunbuild() {
    docker-compose exec fastapi-docker bash -c "set -ex
        cd /frontend
        npm i
        npm run build
    "
    SPA_APP="app_spa"
    SPA_DIR="frontend_static_build"
    rm -Rf "fastapi/$SPA_APP/$SPA_DIR/"
    cp -a "frontend/build/." "fastapi/$SPA_APP/$SPA_DIR/"
    echo -e "*\n!.gitignore" > fastapi/$SPA_APP/$SPA_DIR/.gitignore
    print_url
}

start_no_logs() {
    docker-compose up -d
}

print_url() {
    echo ">>> http://localhost:$NODE_JS_EXTERNAL_PORT for NodeJS"
    echo ">>> http://localhost:$FAST_API_EXTERNAL_PORT/docs for FASTAPI"
}

stop() {
    docker-compose down
}

restart() {
    stop
    start
}

logs() {
    docker-compose logs -ft
}

bash() {
    docker-compose exec fastapi-docker bash
}

makemigration() {
    MIGRATION_NAME=`date +%Y%m%d%H%M%S`
    docker-compose exec fastapi-docker bash -c "
        set +ex
        alembic revision --autogenerate -m '$MIGRATION_NAME'
        chmod -R 777 migrations_alembic
    "
}

migrate() {
    docker-compose exec fastapi-docker bash -c "alembic upgrade head"
}

fixtures() {
    fixture_filename="fixtures" # python file name
    if [ "$FAST_API_APP" = "app_sql_model" ]; then
        fixture_filename="db"
        docker-compose exec postgres-docker bash -c "psql -U $POSTGRES_USER -d $DB_NAME -c '
            DROP TABLE IF EXISTS fastapi_schema.herocitylink;
            DROP TABLE IF EXISTS fastapi_schema.city;
            DROP TABLE IF EXISTS fastapi_schema.hero;
            DROP TABLE IF EXISTS fastapi_schema.team;'"
    fi
    docker-compose exec fastapi-docker bash -c "python3 -m ${FAST_API_APP}.${fixture_filename}"
}

resetmigrations() {
    docker-compose exec postgres-docker bash -c "psql -U $POSTGRES_USER -d $DB_NAME -c 'DROP TABLE IF EXISTS fastapi_schema.alembic_version;'"
    docker-compose exec fastapi-docker bash -c "alembic stamp head"
}

testdebug() {
    PYTEST_COMMAND="python -m debugpy --wait-for-client --listen 0.0.0.0:$FAST_API_DEBUG_UNITTESTS_INTERNAL_PORT -m"
    echo ">>> Waiting for debugger to attach on port $FAST_API_DEBUG_UNITTESTS_EXTERNAL_PORT. In vscode, run the debug task 'FastAPI test."
    test
}

test() {
    PYTEST_COMMAND="$PYTEST_COMMAND pytest -v"
    if [ $# -eq 1 ]; then
        PYTEST_COMMAND="$PYTEST_COMMAND -k $1"
    fi
    docker-compose exec fastapi-docker bash -c "$PYTEST_COMMAND"
}

main() {
    if [ $# -eq 0 ]; then # No argument
        set +x
        printArguments
        exit 1
    fi

    if [ ! -f .env ]; then
        echo ".env not found : cp .env.tpl .env"
        cp .env.tpl .env
    fi
    source ./.env

    cmd="$1 ${@:2}" # $1 is the command and ${@:2} is the list of arguments
    $cmd
}

# Main entry point
main "$@"
