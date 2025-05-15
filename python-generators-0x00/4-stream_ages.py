#!/usr/bin/python3
import mysql.connector

def stream_user_ages():
    """Generator to stream user ages one by one from the database."""
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ALX_prodev"
    )
    cursor = connection.cursor(cursor_class=mysql.connector.cursor.SSCursor)
    cursor.execute("SELECT age FROM user_data")
    
    try:
        for (age,) in cursor:
            yield age
    finally:
        cursor.close()
        connection.close()

def compute_average_age():
    """Compute the average age using the streaming generator."""
    total_age = 0
    count = 0
    for age in stream_user_ages():
        total_age += age
        count += 1
    return total_age / count if count else 0.0

if __name__ == "__main__":
    average_age = compute_average_age()
    print(f"Average age of users: {average_age:.2f}")