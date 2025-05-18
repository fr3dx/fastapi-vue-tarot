import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
from dotenv import load_dotenv

# Load environment variables from .env file.
load_dotenv()

# Database connection parameters retrieved from environment variables.
# Default values are provided for development/testing purposes.
DB_HOST = os.getenv("DB_HOST_HELPER_SCRIPTS", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "test")
DB_USER = os.getenv("DB_USER", "test")
DB_PASSWORD = os.getenv("DB_PASSWORD", "test")

# Paths
# Get the directory of the current script.
script_dir = os.path.dirname(os.path.realpath(__file__))
# Construct the path to the multi-language JSON file containing card descriptions.
json_file_path = os.path.join(script_dir, "card_descriptions_multilanguage_prod.json")

# Check if the JSON file exists. If not, print an error and exit.
if not os.path.exists(json_file_path):
    print(f"JSON file not found at: {json_file_path}")
    exit(1)

def create_database_if_not_exists():
    """
    Connects to the PostgreSQL server and creates the specified database
    if it does not already exist.
    """
    try:
        # Connect to the default 'postgres' database to check for and potentially create
        # the target database.
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname="postgres",  # Connect to 'postgres' database initially
            user=DB_USER,
            password=DB_PASSWORD
        )
        # Set isolation level to AUTOCOMMIT to allow database creation.
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Check if the target database already exists.
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (DB_NAME,))
        exists = cur.fetchone()

        # Create the database if it does not exist.
        if not exists:
            cur.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"Database '{DB_NAME}' created.")
        else:
            print(f"Database '{DB_NAME}' already exists.")

        # Close the cursor and connection.
        cur.close()
        conn.close()
    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database server: {e}")
        print("Please ensure the database server is running and the connection details in the .env file are correct.")
        exit(1)


def create_tables_and_insert_data():
    """
    Connects to the specified database, creates the necessary tables (cards,
    card_translations, users, daily_card) if they don't exist, and inserts
    card and translation data from the JSON file.
    """
    try:
        # Connect to the target database.
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        # Create 'cards' table if it does not exist.
        # Stores unique card keys.
        cur.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id SERIAL PRIMARY KEY,
            key VARCHAR(100) NOT NULL UNIQUE
        );
        """)

        # Create 'card_translations' table if it does not exist.
        # Stores translated names and descriptions for cards based on language.
        cur.execute("""
        CREATE TABLE IF NOT EXISTS card_translations (
            id SERIAL PRIMARY KEY,
            card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
            lang VARCHAR(10) NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            UNIQUE (card_id, lang) -- Ensures only one translation per card and language
        );
        """)

        # Create 'users' table if it does not exist.
        # Stores user information.
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            sub VARCHAR(255) NOT NULL UNIQUE, -- Subject identifier (e.g., from OAuth)
            email VARCHAR(255),
            name VARCHAR(255),
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(), -- Timestamp of user creation
            last_draw_date DATE, -- Date of the last card draw
            lang VARCHAR(10) NOT NULL DEFAULT 'hu' -- User's preferred language, default is Hungarian
        );
        """)

        # Create index on the 'lang' column in the 'users' table for faster lookups.
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_lang ON users(lang);
        """)

        # Create 'daily_card' table if it does not exist.
        # Stores the daily card drawn by each user.
        cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_card (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- Foreign key to users table
            card_key VARCHAR(100) NOT NULL REFERENCES cards(key) ON DELETE RESTRICT, -- Foreign key to cards table
            draw_date DATE NOT NULL DEFAULT CURRENT_DATE -- Date the card was drawn
        );
        """)

        # Create indexes for performance optimization on frequently queried columns.
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_sub ON users(sub);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_card_user_id ON daily_card(user_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_card_draw_date ON daily_card(draw_date);")

        # Read card data from the JSON file.
        with open(json_file_path, encoding="utf-8") as f:
            cards_data = json.load(f)

        # Iterate through each card in the JSON data.
        for card in cards_data:
            key = card["key"]

            # Insert the card key into the 'cards' table if it doesn't already exist.
            # ON CONFLICT (key) DO NOTHING prevents errors if the key is already present.
            cur.execute("""
                INSERT INTO cards (key)
                VALUES (%s)
                ON CONFLICT (key) DO NOTHING;
            """, (key,))
            # Retrieve the generated 'id' for the card.
            cur.execute("SELECT id FROM cards WHERE key = %s;", (key,))
            card_id = cur.fetchone()[0]

            # Process translations for the current card.
            translations = card.get("translations", {})
            for lang, trans in translations.items():
                name = trans.get("name", "")
                description = trans.get("description", "")

                # Insert or update card translations.
                # ON CONFLICT (card_id, lang) DO UPDATE SET updates
                # the name and description if a translation for the same card
                # and language already exists.
                cur.execute("""
                    INSERT INTO card_translations (card_id, lang, name, description)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (card_id, lang) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description;
                """, (card_id, lang, name, description))

        # Commit the transaction to save the changes to the database.
        conn.commit()

        # Optional: Print the data from the 'cards' and 'card_translations' tables
        # to verify insertion.
        print("Cards:")
        cur.execute("SELECT * FROM cards ORDER BY id;")
        for row in cur.fetchall():
            print(row)

        print("\nCard translations:")
        cur.execute("SELECT card_id, lang, name, description FROM card_translations ORDER BY card_id, lang;")
        for row in cur.fetchall():
            print(row)

        # Close the cursor and connection.
        cur.close()
        conn.close()

    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database or executing queries: {e}")
        print("Please ensure the database is running and accessible with the provided credentials.")
        exit(1)
    except FileNotFoundError:
        print(f"JSON file not found at: {json_file_path}")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)

# Entry point of the script.
if __name__ == "__main__":
    # First, ensure the database exists.
    create_database_if_not_exists()
    # Then, create tables and populate with data.
    create_tables_and_insert_data()
