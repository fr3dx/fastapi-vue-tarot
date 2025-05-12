import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime  # We'll use datetime for the timestamp

# Load environment variables from a .env file
load_dotenv()

# Retrieve database connection settings from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "test")
DB_USER = os.getenv("DB_USER", "test")
DB_PASSWORD = os.getenv("DB_PASSWORD", "test")

conn = None
cur = None

try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    # Define the name of the table
    table_name = "users"

    # Check if the table exists and drop it if it does
    print(f"Checking if the '{table_name}' table exists...")
    cur.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');")
    table_exists = cur.fetchone()[0]

    if table_exists:
        print(f"The '{table_name}' table exists. Dropping it...")
        cur.execute(f"DROP TABLE {table_name};")
        conn.commit()
        print(f"The '{table_name}' table was successfully dropped.")
    else:
        print(f"The '{table_name}' table does not exist. No need to drop.")

    # Create the 'users' table with the specified schema
    print(f"Creating the '{table_name}' table with the specified schema...")
    cur.execute(f"""
    CREATE TABLE {table_name} (
        id SERIAL PRIMARY KEY,
        sub VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255),
        email VARCHAR(255),
        last_draw_date DATE,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    print(f"The '{table_name}' table was successfully created.")

    # Optionally, retrieve and display the schema of the newly created table
    print(f"\nVerifying the schema of the newly created '{table_name}' table:")
    cur.execute(f"""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = '{table_name}';
    """)
    schema_rows = cur.fetchall()

    if schema_rows:
        print("-" * 50)
        print("Column Name | Data Type | Nullable | Default Value")
        print("-" * 50)
        for row in schema_rows:
            column_name, data_type, is_nullable, column_default = row
            print(f"{column_name:<12} | {data_type:<10} | {is_nullable:<10} | {column_default}")
        print("-" * 50)
    else:
        print(f"No column information found for the '{table_name}' table.")

except psycopg2.OperationalError as e:
    # Handle operational errors (e.g. connection issues)
    print(f"Error while connecting to the database or performing an operation: {e}")
    if conn:
        conn.rollback()  # Rollback in case of error
except Exception as e:
    # Handle any other unexpected errors
    print(f"An unexpected error occurred: {e}")
    if conn:
        conn.rollback()  # Rollback in case of error

finally:
    # Close cursor and connection if they exist
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
    print("Database connection closed.")
