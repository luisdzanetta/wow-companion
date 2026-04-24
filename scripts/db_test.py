"""Quick sanity check: open a connection, list tables (should be empty)."""

from sqlalchemy import inspect

from app.db.engine import engine

if __name__ == "__main__":
    print(f"Database URL: {engine.url}")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if tables:
        print(f"Tables found: {tables}")
    else:
        print("No tables yet (expected — we haven't created any).")

    print(f"Database file exists at: data/companion.db")