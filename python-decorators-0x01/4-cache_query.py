import time
import sqlite3 
import functools
from functools import wraps

# Dictionary to store cached query results
query_cache = {}

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

def cache_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from arguments
        query = kwargs.get('query', None)
        if query is None and len(args) > 1:  # First arg is conn
            query = args[1]
        
        # Check if query exists in cache
        if query in query_cache:
            print("Returning cached result for query:", query)
            return query_cache[query]
        
        # Execute and cache if not in cache
        result = func(*args, **kwargs)
        query_cache[query] = result
        print("Caching result for query:", query)
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")
print("First call result count:", len(users))

# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print("Second call result count:", len(users_again))