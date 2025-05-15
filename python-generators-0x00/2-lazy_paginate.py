#!/usr/bin/python3
import mysql.connector

def paginate_users(page_size, offset):
    """Fetch a page of users from the database with LIMIT/OFFSET."""
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ALX_prodev"
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM user_data LIMIT %s OFFSET %s", 
        (page_size, offset)
    )
    page = cursor.fetchall()
    cursor.close()
    connection.close()
    return page

def lazy_paginate(page_size):
    """Generator to lazily paginate users in chunks of `page_size`."""
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size