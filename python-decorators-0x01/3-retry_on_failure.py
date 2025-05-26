import time
import sqlite3
import functools
from functools import wraps

def with_db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            if 'conn' not in kwargs and not (len(args) > 0 and isinstance(args[0], sqlite3.Connection)):
                kwargs['conn'] = conn
            return func(*args, **kwargs)
        finally:
            conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
                    last_exception = e
                    if attempt < retries - 1:  # Don't sleep on last attempt
                        time.sleep(delay)
                    continue
                except Exception as e:
                    # Re-raise non-retryable exceptions immediately
                    raise e
            raise Exception(f"Failed after {retries} attempts") from last_exception
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users)