from app.user_database import (
    registrar_usuario,
    usuario_existe,
    validar_login,
    obtener_perfil,
    actualizar_perfil
)

telegram_id = 123456

if not usuario_existe(telegram_id):

    registrar_usuario(
        telegram_id=telegram_id,
        nombre="Rogelio",
        password="1234"
    )

    print("Usuario registrado.")

else:
    print("El usuario ya existe.")

login = validar_login(
    telegram_id,
    "1234"
)

print("Login correcto:", login)

actualizar_perfil(
    telegram_id=telegram_id,
    edad=24,
    peso=82,
    altura=178,
    enfermedad="Ninguna",
    lesion="Rodilla",
    objetivo="Condicion fisica / potencia",
    nivel="Intermedio",
    equipo="Peso libre",
    dias=4,
    tiempo=60
)

perfil = obtener_perfil(telegram_id)

print("\nPERFIL:")
print(perfil)