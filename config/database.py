import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_CONFIG = {
    "user": os.getenv("POSTGRES_USER", "psql"),
    "password": os.getenv("POSTGRES_PASSWORD", "psql"),
    "name": os.getenv("POSTGRES_DB", "rpn"),
}


class DatabaseConfig:
    DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@db/{DB_CONFIG['name']}"
    DEBUG = True


engine = create_engine(DatabaseConfig.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
