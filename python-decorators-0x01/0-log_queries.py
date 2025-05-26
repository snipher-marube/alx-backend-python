import sqlite3
import functools

def log_queries(func):
    """Decorator that logs the SQL queries executed by the function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query form the kwargs or args
        query = kwargs.get('query', None)
        if query is None and args:
            query = args[0] if len(args) >= 1 else None

        # log the query
        print(f'Executing query: {query}')

        # call the original function
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# fetch the users while we log the query
users = fetch_all_users(query="SELECT * FROM users")

