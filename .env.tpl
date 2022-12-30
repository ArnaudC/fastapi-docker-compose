# Container registry where docker images are stored (here, gitlab)
REGISTRY=registry.gitlab.com
# Base path of the container registry for this project (no ending /)
REGISTRY_BASE_PATH=registry.gitlab.com/icm-institute/dsi/dev/docker-compose/fast-api-docker-compose
# Developer's gitlab username
REGISTRY_USER=username
# Developer's personal access token, with "write_registry" scope (https://gitlab.com/-/profile/personal_access_tokens)
REGISTRY_PASSWORD=secret_change_me
# The branch in the project you should use for development (develop, except in Quickstart: django-base-3.x)
DEV_BRANCH=develop

# Postgres and ./db/init/create_db.sh
PG_VERSION=15
PGHOST=localhost
PGPORT=5432
POSTGRES_DOCKER_PORT=50317
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_NAME=fastapi_db
DB_SCHEMA=fastapi_schema
DB_OWNER=fastapi_owner
DB_OWNER_PASS=fastapi_owner_password
DB_APP=fastapi_app
DB_APP_PASS=fastapi_app_password
DB_READ=fastapi_read
DB_READ_PASS=fastapi_read_password
FAST_API_SQLALCHEMY_DATABASE_URL=postgresql://${DB_APP}:${DB_APP_PASS}@postgres-docker:${PGPORT}/${DB_NAME}

# Frontend
NODE_JS_EXTERNAL_PORT=3000
NODE_JS_INTERNAL_PORT=3000

# Fast API
FAST_API_EXTERNAL_PORT=53187
FAST_API_INTERNAL_PORT=8000
FAST_API_DEBUG_PORT_INTERNAL=5678
FAST_API_DEBUG_PORT_EXTERNAL=42645
FAST_API_DEBUG_UNITTESTS_INTERNAL_PORT=5679
FAST_API_DEBUG_UNITTESTS_EXTERNAL_PORT=31424
REACT_APP_DEV_FASTAPI_URL=http://localhost:$FAST_API_EXTERNAL_PORT
FAST_API_FILE_FUNC=.main:app
MIGRATION_ALEMBIC_MODEL=app_sql_alchemy.models
# Supported apps : [app_basic, app_graphql, app_spa, app_sql_alchemy, app_sql_model, app_structured]
FAST_API_APP=app_sql_alchemy
