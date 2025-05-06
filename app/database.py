from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os



SQLALCHEMY_DB_URL = os.getenv("DATABASE_URL")


engine = create_engine(SQLALCHEMY_DB_URL)

Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()
