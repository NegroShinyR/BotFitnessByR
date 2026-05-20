import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "fitness.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(ejercicios)")
columnas = cursor.fetchall()

print("\nCOLUMNAS DE LA TABLA ejercicios:\n")

for columna in columnas:
    print(columna[1])

conn.close()