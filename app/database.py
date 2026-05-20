import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "fitness.db"


def conectar_db():
    return sqlite3.connect(DB_PATH)


def obtener_ejercicios():
    conn = conectar_db()

    query = """
    SELECT *
    FROM ejercicios
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def filtrar_ejercicios(
    nivel=None,
    equipo=None,
    grupo_muscular=None
):
    conn = conectar_db()

    query = """
    SELECT *
    FROM ejercicios
    WHERE 1=1
    """

    params = []

    if nivel:
        query += " AND nivel_bot = ?"
        params.append(nivel)

    if equipo:
        query += " AND equipo_bot = ?"
        params.append(equipo)

    if grupo_muscular:
        query += " AND grupo_muscular = ?"
        params.append(grupo_muscular)

    df = pd.read_sql_query(query, conn, params=params)

    conn.close()

    return df