import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

print("=== USERS ===")
for row in cur.execute("SELECT * FROM users"):
    print(row)

print("\n=== POSTS ===")
for row in cur.execute("SELECT * FROM posts"):
    print(row)

conn.close()
