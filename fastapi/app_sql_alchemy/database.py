import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData


# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"  # Use sqlite to debug without database
SQLALCHEMY_DATABASE_URL = os.environ['FAST_API_SQLALCHEMY_DATABASE_URL']  # postgresql://fastapi_app:fastapi_app_password@postgres-docker:5432/fastapi_db

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(metadata=MetaData(schema=os.environ["DB_SCHEMA"]))
