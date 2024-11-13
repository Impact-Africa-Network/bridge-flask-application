import sqlite3

conn = sqlite3.connect('notes.sqlite')

cursor =  conn.cursor()


sql_query = """
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        detail TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

cursor.execute(sql_query)