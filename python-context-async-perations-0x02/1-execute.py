import sqlite3

class ExecuteQuery:
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        # Open connection and execute query
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up resources
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        # Return False to propagate exceptions, True to suppress them
        return False

# Example usage
if __name__ == "__main__":
    # Using the context manager with the specified query and parameter
    with ExecuteQuery(
        "example.db", 
        "SELECT * FROM users WHERE age > ?", 
        (25,)
    ) as results:
        print("Users over 25:")
        for row in results:
            print(row)