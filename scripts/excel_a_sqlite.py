import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL_PATH = BASE_DIR / "data" / "Base_Estructurada_Chatbot_Normalizada.xlsx"
DB_PATH = BASE_DIR / "data" / "fitness.db"

def convertir_excel_a_sqlite():
    df = pd.read_excel(EXCEL_PATH, sheet_name="Dataset_Modelo")

    # Limpieza básica
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("ejercicios", conn, if_exists="replace", index=False)
    conn.close()

    print("Base de datos creada correctamente.")
    print(f"Registros guardados: {len(df)}")
    print(f"Ruta: {DB_PATH}")

if __name__ == "__main__":
    convertir_excel_a_sqlite()