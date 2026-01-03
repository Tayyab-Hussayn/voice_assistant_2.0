#!/usr/bin/env python3

# Example file with security issues for testing
import sqlite3

# Hardcoded credentials (security issue)
password = "admin123"
api_key = "sk-1234567890abcdef"
secret = "my-secret-token"

def unsafe_query(user_input):
    # SQL injection vulnerability
    conn = sqlite3.connect('database.db')
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    cursor = conn.execute(query)
    return cursor.fetchall()

def another_unsafe_query(table_name):
    # Another SQL injection risk
    query = f"SELECT * FROM {table_name} WHERE active = 1"
    return execute(query)
