import pymysql

conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="210606",
    database="workflowvdai",
    autocommit=True
)
cur = conn.cursor()
cur.execute("SHOW TABLES;")
tables = cur.fetchall()
print("Tables in MySQL 'workflowvdai':", [t[0] for t in tables])

for t in [t[0] for t in tables]:
    cur.execute(f"SELECT COUNT(*) FROM {t};")
    count = cur.fetchone()[0]
    print(f"  Table '{t}': {count} rows")

conn.close()
print("✓ MySQL Connection test PASSED!")
