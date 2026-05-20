import pandas as pd
from pathlib import Path

from app.database import obtener_ejercicios
from app.recomendador import calcular_score_funcional, obtener_categoria_movimiento


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "data" / "dataset_ml.csv"


def crear_tipo_rutina(row):
    objetivo = str(row["objetivo_bot"]).lower()
    clasificacion = str(row["clasificacion"]).lower()
    patron = str(row["patron_movimiento_1"]).lower()
    musculo = str(row["grupo_muscular"]).lower()

    if "condicion" in objetivo or "ballistics" in clasificacion or "plyometric" in clasificacion:
        return "potencia_funcional"

    if "movilidad" in objetivo or "mobility" in clasificacion or "balance" in clasificacion:
        return "movilidad_estabilidad"

    if "core" in objetivo or musculo in ["abdominals", "hip flexors"]:
        return "core_estabilidad"

    if "fuerza" in objetivo or "bodybuilding" in clasificacion:
        return "fuerza_hipertrofia"

    if "locomotion" in patron or "carry" in patron:
        return "condicion_general"

    return "general"


def preparar_dataset():
    df = obtener_ejercicios()

    columnas_necesarias = [
        "nivel_bot",
        "equipo_bot",
        "objetivo_bot",
        "bloque_bot",
        "grupo_muscular",
        "patron_movimiento_1",
        "clasificacion",
        "short_youtube_url",
        "ejercicio",
    ]

    df = df[columnas_necesarias].copy()

    df = df.fillna("Sin dato")

    df["categoria_movimiento"] = df.apply(
        obtener_categoria_movimiento,
        axis=1
    )

    df["score_funcional"] = df.apply(
        calcular_score_funcional,
        axis=1
    )

    df["tipo_rutina"] = df.apply(
        crear_tipo_rutina,
        axis=1
    )

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("Dataset ML generado correctamente.")
    print(f"Ruta: {OUTPUT_PATH}")
    print(f"Registros: {len(df)}")
    print("\nTipos de rutina:")
    print(df["tipo_rutina"].value_counts())


if __name__ == "__main__":
    preparar_dataset()