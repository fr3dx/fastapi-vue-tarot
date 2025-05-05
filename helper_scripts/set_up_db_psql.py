import os
import psycopg2
import json
from dotenv import load_dotenv

# Load environment variables from a .env file
# This helps securely store the database connection details (host, port, user, password)
load_dotenv()

# Determine the directory of the Python script to make sure the JSON file is always found relative to the script location
script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the current directory of the Python script
json_file_path = os.path.join(script_dir, "card_descriptions.json")  # Get the full path to the JSON file

# Check if the JSON file exists at the specified location
if not os.path.exists(json_file_path):
    print(f"JSON file not found at: {json_file_path}")  # If the file doesn't exist, print an error message
    exit(1)  # Exit the program as we cannot load data without the JSON file

# Database connection settings loaded from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")  # Database host (default: localhost)
DB_PORT = os.getenv("DB_PORT", "5432")  # Database port (default: 5432)
DB_NAME = os.getenv("DB_NAME", "test")  # Database name (default: test)
DB_USER = os.getenv("DB_USER", "test")  # Database user (default: test)
DB_PASSWORD = os.getenv("DB_PASSWORD", "test")  # Database password (default: test)

# Connect to the PostgreSQL database using psycopg2
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# Create a cursor object to perform database operations
cur = conn.cursor()

# Create the card_descriptions table if it doesn't exist
# The table has three fields: id, key, and description
# 'id' is an auto-incrementing unique identifier
cur.execute("""
CREATE TABLE IF NOT EXISTS card_descriptions (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    description TEXT NOT NULL
);
""")

# Open and read the JSON file containing the card descriptions
with open(json_file_path, encoding="utf-8") as f:
    sample_data = json.load(f)  # Load the JSON data into a Python list of dictionaries

# Insert the data from the JSON file into the database
# Use "ON CONFLICT" to handle cases where the key already exists and update the description if necessary
for item in sample_data:
    key = item["key"]
    description = item["description"]
    cur.execute("""
    INSERT INTO card_descriptions (key, description)
    VALUES (%s, %s)
    ON CONFLICT (key) DO UPDATE SET description = EXCLUDED.description;
    """, (key, description))

# Commit the changes to the database
conn.commit()

# Query the database to retrieve all rows from the card_descriptions table
cur.execute("SELECT * FROM card_descriptions;")
rows = cur.fetchall()

# Print the results from the database
for row in rows:
    print(row)

# Close the cursor and the database connection to clean up
cur.close()
conn.close()
