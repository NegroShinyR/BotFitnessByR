from app.database import obtener_ejercicios

df = obtener_ejercicios()

print("\nNIVELES:")
print(df["nivel_bot"].dropna().unique())

print("\nEQUIPOS:")
print(df["equipo_bot"].dropna().unique())

print("\nOBJETIVOS:")
print(df["objetivo_bot"].dropna().unique())

print("\nBLOQUES:")
print(df["bloque_bot"].dropna().unique())