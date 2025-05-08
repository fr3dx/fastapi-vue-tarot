import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Database connection settings loaded from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "test")
DB_USER = os.getenv("DB_USER", "test")
DB_PASSWORD = os.getenv("DB_PASSWORD", "test")

# Connect to the PostgreSQL database using psycopg2
conn = None
cur = None
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    # Lekérdezzük a 'user' tábla sémaját az information_schema.columns nézetből
    print("Lekérdezés a 'user' tábla sémajához...")
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'users';
    """)

    schema_rows = cur.fetchall()

    # Kiírjuk a séma információkat
    if schema_rows:
        print("\n'user' tábla séma:")
        print("-" * 30)
        for row in schema_rows:
            column_name, data_type, is_nullable = row
            print(f"Oszlop neve: {column_name}, Adattípus: {data_type}, Nullázható: {is_nullable}")
        print("-" * 30)
    else:
        print("A 'user' nevű tábla nem található, vagy nincsnek benne oszlopok.")

    # Ha továbbra is le szeretnéd kérdezni a user tábla adatait,
    # a korábbi SELECT * FROM user; lekérdezést is itt végezheted el.
    # print("\nLekérdezés a 'user' tábla adatairól...")
    # try:
    #     cur.execute("SELECT * FROM user;")
    #     data_rows = cur.fetchall()
    #     if data_rows:
    #         print("\nAdatok a 'user' táblából:")
    #         for row in data_rows:
    #             print(row)
    #     else:
    #         print("A 'user' tábla üres.")
    # except psycopg2.ProgrammingError as e:
    #      print(f"Hiba a 'user' tábla adatainak lekérdezésekor: {e}")


except psycopg2.OperationalError as e:
    print(f"Hiba az adatbázishoz való csatlakozáskor: {e}")
except Exception as e:
    print(f"Váratlan hiba történt: {e}")

finally:
    # Bezárjuk a kurzort és a kapcsolatot, ha léteznek
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
    print("Adatbázis kapcsolat bezárva.")
