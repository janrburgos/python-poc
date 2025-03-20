from functools import wraps
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.database import get_db


def clean_table_after_test(table_name: str):
    """Decorator to truncate a specific table after a test, even if it fails."""

    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            try:
                return test_func(*args, **kwargs)  # Run the test
            finally:
                # Cleanup runs even if test fails
                db: Session = next(get_db())
                db.execute(
                    text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
                )
                db.commit()
                db.close()

        return wrapper

    return decorator
