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

    table_name = 'users' # Tábla neve

    # Lekérdezzük a 'users' tábla sémaját az information_schema.columns nézetből
    print(f"Lekérdezés a '{table_name}' tábla sémajához...")
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = %s;
    """, (table_name,)) # Használjunk paraméterezett lekérdezést

    schema_rows = cur.fetchall()

    # Kiírjuk a séma információkat
    if schema_rows:
        print(f"\n'{table_name}' tábla séma:")
        print("-" * 30)
        for row in schema_rows:
            column_name, data_type, is_nullable = row
            print(f"Oszlop neve: {column_name}, Adattípus: {data_type}, Nullázható: {is_nullable}")
        print("-" * 30)
    else:
        # Ellenőrizzük, hogy a tábla maga létezik-e, ha nincs oszlop infó
        cur.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);", (table_name,))
        table_exists = cur.fetchone()[0]

        if table_exists:
             print(f"A '{table_name}' tábla létezik, de nincsnek benne oszlopok (üres séma).")
        else:
             print(f"A '{table_name}' nevű tábla nem található.")


    # Lekérdezzük a 'users' tábla teljes tartalmát
    print(f"\nLekérdezés a '{table_name}' tábla adatairól...")
    try:
        cur.execute(f"SELECT * FROM {table_name};") # Közvetlen tábla nevet használunk, de óvatosan kell vele bánni dinamikus esetben!
        data_rows = cur.fetchall()

        # Kiírjuk a tábla adatait
        if data_rows:
            print(f"\nAdatok a '{table_name}' táblából:")
            # Oszlopnevek kinyerése a kurzor description-ből
            col_names = [desc[0] for desc in cur.description]
            print(", ".join(col_names)) # Kiírjuk az oszlop neveket
            print("-" * (sum(len(name) for name in col_names) + 2 * len(col_names) - 2 if col_names else 30)) # Egy egyszerű elválasztó
            for row in data_rows:
                print(row) # Kiírjuk a sorokat
        else:
            print(f"A '{table_name}' tábla üres (nincs adat).")

    except psycopg2.ProgrammingError as e:
         print(f"Hiba a '{table_name}' tábla adatainak lekérdezésekor: {e}")
         print("Ellenőrizze, hogy a tábla létezik-e és elérhető-e.")


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
