import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="1234",
        port="5432"
    )
    cur = conn.cursor()

    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("✅ Connected to PostgreSQL!")
    print("PostgreSQL version:", version[0])

    cur.close()
    conn.close()

except psycopg2.Error as e:
    print("Failed to connect to PostgreSQL.")
    print("Error:", e)
