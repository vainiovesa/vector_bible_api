import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base


load_dotenv()


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB]):
    not_found = []
    for var in ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB"]:
        if not os.getenv(var):
            not_found.append(var)
    raise ValueError(f"Environment variables not found: {', '.join(not_found)}")

DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
DB_URL += f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
DB_URL += "?client_encoding=utf8"


engine = create_engine(DB_URL)
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()


def create_tables():
    import models
    with sessionlocal.begin() as session:
        session.execute(text("CREATE EXTENSION IF NOT EXISTS vector CASCADE"))
    Base.metadata.create_all(engine)


def drop_tables():
    import models
    Base.metadata.drop_all(engine)
    with sessionlocal.begin() as session:
        session.execute(text("DROP EXTENSION IF EXISTS vector CASCADE"))
