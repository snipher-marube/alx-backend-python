#!/usr/bin/python3
from seed import paginate_users

def lazy_paginate(page_size):
    """Generator to lazily paginate through user_data in chunks of page_size."""
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size