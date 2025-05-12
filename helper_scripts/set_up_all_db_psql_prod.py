import os
import psycopg2
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Paths
script_dir = os.path.dirname(os.path.realpath(__file__))
json_file_path = os.path.join(script_dir, "card_descriptions_prod.json")

# Check if the JSON file exists
if not os.path.exists(json_file_path):
    print(f"JSON file not found at: {json_file_path}")
    exit(1)

# Environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "test")
DB_USER = os.getenv("DB_USER", "test")
DB_PASSWORD = os.getenv("DB_PASSWORD", "test")

# Connect to database
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = conn.cursor()

# === Create tables in correct order ===
cur.execute("""
CREATE TABLE IF NOT EXISTS card_descriptions (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    sub VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255),
    name VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    last_draw_date DATE
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS daily_card (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_key VARCHAR(100) NOT NULL REFERENCES card_descriptions(key) ON DELETE RESTRICT,
    draw_date DATE NOT NULL DEFAULT CURRENT_DATE
);
""")

# === Create indexes ===
cur.execute("CREATE INDEX IF NOT EXISTS idx_users_sub ON users(sub);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_card_user_id ON daily_card(user_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_card_draw_date ON daily_card(draw_date);")

# === Insert card descriptions from JSON ===
with open(json_file_path, encoding="utf-8") as f:
    sample_data = json.load(f)

for item in sample_data:
    key = item["key"]
    description = item["description"]
    cur.execute("""
        INSERT INTO card_descriptions (key, description)
        VALUES (%s, %s)
        ON CONFLICT (key) DO UPDATE SET description = EXCLUDED.description;
    """, (key, description))

conn.commit()

# === Query and print all card descriptions ===
cur.execute("SELECT * FROM card_descriptions ORDER BY id;")
rows = cur.fetchall()
for row in rows:
    print(row)

# Cleanup
cur.close()
conn.close()
