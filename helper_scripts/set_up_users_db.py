import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime # Szükségünk lesz a datetime-ra a timestamp-hez

# Load environment variables from a .env file
load_dotenv()

# Database connection settings loaded from environment variables
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

    # Tábla nevének definiálása
    table_name = "users"

    # Ellenőrizzük, hogy a tábla létezik-e és eldobjuk, ha igen
    print(f"Ellenőrzés, hogy a '{table_name}' tábla létezik-e...")
    cur.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');")
    table_exists = cur.fetchone()[0]

    if table_exists:
        print(f"A '{table_name}' tábla létezik. Eldobjuk...")
        cur.execute(f"DROP TABLE {table_name};")
        conn.commit()
        print(f"A '{table_name}' tábla sikeresen eldobva.")
    else:
        print(f"A '{table_name}' tábla nem létezik. Nem szükséges eldobni.")

    # Létrehozzuk a 'users' táblát a megadott séma alapján
    print(f"Létrehozzuk a '{table_name}' táblát a megadott séma alapján...")
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
    print(f"A '{table_name}' tábla sikeresen létrehozva.")

    # Opcionálisan lekérdezhetjük az újonnan létrehozott tábla sémaját ellenőrzésképpen
    print(f"\nEllenőrizzük az újonnan létrehozott '{table_name}' tábla sémáját:")
    cur.execute(f"""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = '{table_name}';
    """)
    schema_rows = cur.fetchall()

    if schema_rows:
        print("-" * 50)
        print("Oszlop neve | Adattípus | Nullázható | Alapértelmezett érték")
        print("-" * 50)
        for row in schema_rows:
            column_name, data_type, is_nullable, column_default = row
            print(f"{column_name:<12} | {data_type:<10} | {is_nullable:<10} | {column_default}")
        print("-" * 50)
    else:
        print(f"Nem található oszlopinformáció a '{table_name}' táblához.")


except psycopg2.OperationalError as e:
    print(f"Hiba az adatbázishoz való csatlakozáskor vagy művelet közben: {e}")
    if conn:
        conn.rollback() # Visszagörgetés hiba esetén
except Exception as e:
    print(f"Váratlan hiba történt: {e}")
    if conn:
        conn.rollback() # Visszagörgetés hiba esetén

finally:
    # Bezárjuk a kurzort és a kapcsolatot, ha léteznek
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
    print("Adatbázis kapcsolat bezárva.")
