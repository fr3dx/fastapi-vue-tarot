import os
import psycopg2
from dotenv import load_dotenv

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
    # Connect to the PostgreSQL database using psycopg2
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    table_name = 'users'  # Name of the table to inspect

    # Query the schema of the 'users' table from the information_schema.columns view
    print(f"Querying schema for the '{table_name}' table...")
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = %s;
    """, (table_name,))  # Use parameterized query to avoid SQL injection

    schema_rows = cur.fetchall()

    # Print schema information
    if schema_rows:
        print(f"\nSchema for table '{table_name}':")
        print("-" * 30)
        for row in schema_rows:
            column_name, data_type, is_nullable = row
            print(f"Column Name: {column_name}, Data Type: {data_type}, Nullable: {is_nullable}")
        print("-" * 30)
    else:
        # If no column info is found, check if the table exists at all
        cur.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);", (table_name,))
        table_exists = cur.fetchone()[0]

        if table_exists:
            print(f"The table '{table_name}' exists, but contains no columns (empty schema).")
        else:
            print(f"The table '{table_name}' does not exist.")

    # Query all data from the 'users' table
    print(f"\nQuerying data from the '{table_name}' table...")
    try:
        cur.execute(f"SELECT * FROM {table_name};")  # Directly using table name – be cautious in dynamic scenarios!
        data_rows = cur.fetchall()

        # Print the table's data
        if data_rows:
            print(f"\nData from the '{table_name}' table:")
            # Extract column names from cursor description
            col_names = [desc[0] for desc in cur.description]
            print(", ".join(col_names))  # Print column headers
            print("-" * (sum(len(name) for name in col_names) + 2 * len(col_names) - 2 if col_names else 30))  # Simple divider
            for row in data_rows:
                print(row)  # Print each row of data
        else:
            print(f"The '{table_name}' table is empty (no data).")

    except psycopg2.ProgrammingError as e:
        print(f"Error while querying data from the '{table_name}' table: {e}")
        print("Please check if the table exists and is accessible.")

except psycopg2.OperationalError as e:
    # Handle connection-related errors
    print(f"Error while connecting to the database: {e}")
except Exception as e:
    # Handle any other unexpected errors
    print(f"An unexpected error occurred: {e}")

finally:
    # Close cursor and connection if they exist
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
    print("Database connection closed.")
