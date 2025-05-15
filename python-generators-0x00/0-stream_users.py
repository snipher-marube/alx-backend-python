import mysql.connector

def stream_users():
    """Generator function to stream user_data rows one by one."""
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ALX_prodev"
    )
    cursor = connection.cursor(cursor_class=mysql.connector.cursor.SSCursor)
    
    try:
        cursor.execute("SELECT * FROM user_data")
        columns = [col[0] for col in cursor.description]
        
        for row in cursor:
            yield dict(zip(columns, row))
    finally:
        cursor.close()
        connection.close()