from app.database import obtener_ejercicios

df = obtener_ejercicios()

columnas = [
    "grupo_muscular",
    "patron_movimiento_1",
    "clasificacion"
]

for columna in columnas:
    print("\n==============================")
    print(f" VALORES EN: {columna.upper()}")
    print("==============================")

    if columna in df.columns:
        print(df[columna].dropna().value_counts().head(50))
    else:
        print(f"No existe la columna: {columna}")