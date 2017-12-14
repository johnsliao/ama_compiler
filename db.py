import sqlite3

conn = sqlite3.connect('db.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE posts
             (date text, post_id text)''')
conn.commit()
conn.close()
