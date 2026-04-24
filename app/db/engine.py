"""Database engine and session factory.

Centralizes DB connection setup. Other modules should import `SessionLocal`
to work with the database — never create engines themselves.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/companion.db")

# Ensure the data directory exists for SQLite file databases
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

# `echo=False` in production; set to True for debugging (prints every SQL query)
engine = create_engine(DATABASE_URL, echo=False)

# Session factory — use SessionLocal() to get a new session
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)