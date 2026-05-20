from app.database import obtener_ejercicios


df = obtener_ejercicios()

print("\n==============================")
print(" TOTAL DE EJERCICIOS")
print("==============================")
print(len(df))


# =========================
# NIVELES
# =========================

print("\n==============================")
print(" EJERCICIOS POR NIVEL")
print("==============================")

print(
    df["nivel_bot"]
    .value_counts()
)


# =========================
# EQUIPO
# =========================

print("\n==============================")
print(" EJERCICIOS POR EQUIPO")
print("==============================")

print(
    df["equipo_bot"]
    .value_counts()
)


# =========================
# OBJETIVO
# =========================

print("\n==============================")
print(" EJERCICIOS POR OBJETIVO")
print("==============================")

print(
    df["objetivo_bot"]
    .value_counts()
)


# =========================
# BLOQUES
# =========================

print("\n==============================")
print(" EJERCICIOS POR BLOQUE")
print("==============================")

print(
    df["bloque_bot"]
    .value_counts()
)


# =========================
# COMBINACIONES IMPORTANTES
# =========================

print("\n==============================")
print(" COMBINACIONES NIVEL + EQUIPO + BLOQUE")
print("==============================")

combinaciones = (
    df.groupby(
        [
            "nivel_bot",
            "equipo_bot",
            "bloque_bot"
        ]
    )
    .size()
    .reset_index(name="cantidad")
    .sort_values("cantidad")
)

print(combinaciones)


# =========================
# DETECTAR COMBINACIONES POBRES
# =========================

print("\n==============================")
print(" COMBINACIONES CON POCOS EJERCICIOS")
print("==============================")

pocos = combinaciones[
    combinaciones["cantidad"] <= 3
]

print(pocos)


# =========================
# EJERCICIOS SIN VIDEO
# =========================

print("\n==============================")
print(" EJERCICIOS SIN VIDEO")
print("==============================")

sin_video = df[
    (
        df["short_youtube_url"].isna()
    )
    |
    (
        df["short_youtube_url"] == ""
    )
]

print(len(sin_video))


# =========================
# DUPLICADOS
# =========================

print("\n==============================")
print(" POSIBLES DUPLICADOS")
print("==============================")

duplicados = df[
    df["ejercicio"].duplicated()
]

print(duplicados[["ejercicio"]])