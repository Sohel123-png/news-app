import psycopg2

def connect_to_db():
    """Connects to the PostgreSQL database and returns the connection object."""
    try:
        conn = psycopg2.connect(
            dbname="fitgent_db",
            user="postgres",  # Replace with your PostgreSQL username if different
            password="",  # Replace with your PostgreSQL password if you set one
            host="localhost",
            port="5432"
        )
        print("Successfully connected to the database!")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

if __name__ == '__main__':
    conn = connect_to_db()
    if conn:
        # Example: You can perform database operations here
        # For now, just close the connection
        conn.close()
        print("Database connection closed.")
