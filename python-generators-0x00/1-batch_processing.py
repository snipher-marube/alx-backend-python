import mysql.connector

def stream_users_in_batches(batch_size):
    """Generator to fetch user data in batches from the database."""
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ALX_prodev"
    )
    cursor = connection.cursor(cursor_class=mysql.connector.cursor.SSCursor)
    cursor.execute("SELECT * FROM user_data")
    columns = [col[0] for col in cursor.description]
    
    try:
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            batch = [dict(zip(columns, row)) for row in rows]
            yield batch
    finally:
        cursor.close()
        connection.close()

def batch_processing(batch_size):
    """Process each batch to filter users over the age of 25."""
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                yield user