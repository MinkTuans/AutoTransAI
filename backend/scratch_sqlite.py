import sqlite3

conn = sqlite3.connect('C:/Hack/AutoTransAI/data/workflow.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
