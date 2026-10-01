import psycopg2

try:
    conn = psycopg2.connect(
        dbname="marketing_hw2",
        user="rishpa",
        password="Rishpa@123",
        host="localhost",
        port="5432"
    )

    print("Successfully connected to the database!")

    conn.close()

except Exception as e:
    print("Connection failed:")
    print(e)