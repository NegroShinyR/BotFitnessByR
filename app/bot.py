import os
from dotenv import load_dotenv
from pathlib import Path
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from app.recomendador import generar_plan_semanal, obtener_categoria_movimiento
from app.utils import formatear_plan_semanal, dividir_mensaje
from app.modelo_ia import predecir_con_modelos
from app.user_database import (
    usuario_existe,
    registrar_usuario,
    validar_login,
    actualizar_perfil,
    obtener_perfil,
)

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("No se encontró TELEGRAM_TOKEN en el archivo .env")


user_data_temp = {}
rutinas_temp = {}
mensajes_rutina_temp = {}
mensajes_menu_dias_temp = {}
mensajes_menu_principal_temp = {}


async def borrar_menu_principal(context, chat_id, user_id):
    mensajes = mensajes_menu_principal_temp.get(user_id, [])

    for message_id in mensajes:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            pass

    mensajes_menu_principal_temp[user_id] = []


async def borrar_menus_dias(context, chat_id, user_id):
    mensajes = mensajes_menu_dias_temp.get(user_id, [])

    for message_id in mensajes:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            pass

    mensajes_menu_dias_temp[user_id] = []


def menu_principal():
    teclado = [
        [
            InlineKeyboardButton("📅 Mi rutina", callback_data="mi_rutina"),
            InlineKeyboardButton("👤 Mi perfil", callback_data="mi_perfil"),
        ],
        [
            InlineKeyboardButton(
                "🔄 Nueva rutina semanal", callback_data="nueva_rutina"
            ),
        ],
        [
            InlineKeyboardButton("🚪 Cerrar sesión", callback_data="cerrar_sesion"),
        ],
    ]
    return InlineKeyboardMarkup(teclado)


def obtener_primer_ejercicio_del_plan(plan):
    for _, rutina in plan.items():
        for _, ejercicios in rutina.items():
            if ejercicios:
                return ejercicios[0]
    return None


async def borrar_mensajes_rutina(context, chat_id, user_id):
    mensajes = mensajes_rutina_temp.get(user_id, [])

    for message_id in mensajes:
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )
        except Exception:
            pass

    mensajes_rutina_temp[user_id] = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if usuario_existe(user_id):
        user_data_temp[user_id] = {"estado": "login_password"}

        await update.message.reply_text("Ya tienes cuenta. Ingresa tu contraseña:")
    else:
        user_data_temp[user_id] = {"estado": "registro_password"}

        await update.message.reply_text(
            "No tienes cuenta registrada. Crea una contraseña:"
        )


async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip()

    if user_id not in user_data_temp:
        user_data_temp[user_id] = {}

    datos = user_data_temp[user_id]

    # =========================
    # REGISTRO CON CONTRASEÑA
    # =========================
    if datos.get("estado") == "registro_password":
        password = texto
        nombre = update.effective_user.first_name or "Usuario"

        try:
            await update.message.delete()
        except Exception:
            pass

        registrar_usuario(
            telegram_id=user_id,
            nombre=nombre,
            password=password,
        )

        datos["estado"] = "perfil_nivel"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Cuenta creada correctamente ✅\n\n¿Cuál es tu nivel?",
            reply_markup=ReplyKeyboardMarkup(
                [["Principiante"], ["Intermedio"], ["Avanzado"]],
                resize_keyboard=True,
            ),
        )
        return

    # =========================
    # LOGIN CON CONTRASEÑA
    # =========================
    if datos.get("estado") == "login_password":
        password = texto

        try:
            await update.message.delete()
        except Exception:
            pass

        if not validar_login(user_id, password):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Contraseña incorrecta. Intenta otra vez.",
            )
            return

        perfil = obtener_perfil(user_id)

        if perfil and perfil["nivel"]:
            user_data_temp.pop(user_id, None)

            await borrar_menu_principal(context, update.effective_chat.id, user_id)

            msg_menu = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Inicio de sesión correcto ✅\n\nSelecciona una opción:",
                reply_markup=menu_principal(),
            )

            mensajes_menu_principal_temp[user_id] = [msg_menu.message_id]

            return

        datos["estado"] = "perfil_nivel"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Inicio de sesión correcto ✅\n\nTu perfil está incompleto. ¿Cuál es tu nivel?",
            reply_markup=ReplyKeyboardMarkup(
                [["Principiante"], ["Intermedio"], ["Avanzado"]],
                resize_keyboard=True,
            ),
        )
        return

    # =========================
    # PERFIL: NIVEL
    # =========================
    if "nivel" not in datos:
        datos["nivel"] = texto

        await update.message.reply_text(
            "Perfecto. Ahora dime qué equipo tienes:",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["Sin equipo"],
                    ["Peso libre"],
                    ["Ligas"],
                    ["Gimnasio / maquina"],
                    ["Calistenia / barras"],
                ],
                resize_keyboard=True,
            ),
        )
        return

    # =========================
    # PERFIL: EQUIPO
    # =========================
    if "equipo" not in datos:
        datos["equipo"] = texto

        await update.message.reply_text(
            "Ahora dime tu objetivo:",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["Condicion fisica / potencia"],
                    ["Fuerza / hipertrofia"],
                    ["Movilidad / estabilidad"],
                    ["Core / estabilidad"],
                    ["Condicion general"],
                ],
                resize_keyboard=True,
            ),
        )
        return

    # =========================
    # PERFIL: OBJETIVO
    # =========================
    if "objetivo" not in datos:
        datos["objetivo"] = texto

        await update.message.reply_text(
            "¿Cuántos minutos tienes para entrenar?",
            reply_markup=ReplyKeyboardMarkup(
                [["20"], ["30"], ["45"], ["60"]],
                resize_keyboard=True,
            ),
        )
        return

    # =========================
    # PERFIL: TIEMPO
    # =========================
    if "tiempo" not in datos:
        try:
            datos["tiempo"] = int(texto)
        except ValueError:
            await update.message.reply_text("Pon solo el número de minutos.")
            return

        await update.message.reply_text(
            "¿Cuántos días quieres entrenar?",
            reply_markup=ReplyKeyboardMarkup(
                [["2"], ["3"], ["4"], ["5"], ["6"]],
                resize_keyboard=True,
            ),
        )
        return

    # =========================
    # PERFIL: DÍAS
    # =========================
    if "dias" not in datos:
        try:
            datos["dias"] = int(texto)
        except ValueError:
            await update.message.reply_text("Pon solo el número de días.")
            return

        await update.message.reply_text("¿Cuál es tu edad?")
        return

    # =========================
    # PERFIL: EDAD
    # =========================
    if "edad" not in datos:
        try:
            datos["edad"] = int(texto)
        except ValueError:
            await update.message.reply_text("Pon solo tu edad en número.")
            return

        await update.message.reply_text("¿Cuál es tu peso en kg?")
        return

    # =========================
    # PERFIL: PESO
    # =========================
    if "peso" not in datos:
        try:
            datos["peso"] = float(texto)
        except ValueError:
            await update.message.reply_text("Pon solo tu peso en número. Ejemplo: 82")
            return

        await update.message.reply_text("¿Cuál es tu altura en cm?")
        return

    # =========================
    # PERFIL: ALTURA
    # =========================
    if "altura" not in datos:
        try:
            datos["altura"] = float(texto)
        except ValueError:
            await update.message.reply_text("Pon solo tu altura en cm. Ejemplo: 178")
            return

        await update.message.reply_text(
            "¿Tienes alguna enfermedad? Ejemplo: hipertension, asma, hipotiroidismo o Ninguna"
        )
        return

    # =========================
    # PERFIL: ENFERMEDAD
    # =========================
    if "enfermedad" not in datos:
        datos["enfermedad"] = texto

        await update.message.reply_text(
            "¿Tienes alguna lesión? Ejemplo: rodilla, espalda, hombro o Ninguna"
        )
        return

    # =========================
    # PERFIL: LESIÓN Y GUARDADO
    # =========================
    if "lesion" not in datos:
        datos["lesion"] = texto

        actualizar_perfil(
            telegram_id=user_id,
            edad=datos["edad"],
            peso=datos["peso"],
            altura=datos["altura"],
            enfermedad=datos["enfermedad"],
            lesion=datos["lesion"],
            objetivo=datos["objetivo"],
            nivel=datos["nivel"],
            equipo=datos["equipo"],
            dias=datos["dias"],
            tiempo=datos["tiempo"],
        )

        rutinas_temp.pop(user_id, None)
        
        await borrar_menus_dias(
            context,
            update.effective_chat.id,
            user_id
        )
        
        await borrar_menu_principal(
            context,
            update.effective_chat.id,
            user_id
        )

        msg_menu = await update.message.reply_text(
            "✅ Perfil actualizado correctamente.\n\nCuando quieras, presiona 📅 Mi rutina para generar/ver tu rutina.",
            reply_markup=menu_principal(),
        )

        mensajes_menu_principal_temp[user_id] = [msg_menu.message_id]

        user_data_temp.pop(user_id, None)

        return


async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "mi_perfil":
        perfil = obtener_perfil(user_id)

        if not perfil:
            await query.message.reply_text("No se encontró perfil.")
            return

        mensaje = (
            "👤 MI PERFIL\n\n"
            f"📈 Nivel: {perfil['nivel']}\n"
            f"🏋️ Equipo: {perfil['equipo']}\n"
            f"🎯 Objetivo: {perfil['objetivo']}\n"
            f"📅 Días: {perfil['dias']}\n"
            f"⏱ Tiempo: {perfil['tiempo']}\n\n"
            f"🎂 Edad: {perfil['edad']}\n"
            f"⚖️ Peso: {perfil['peso']} kg\n"
            f"📏 Altura: {perfil['altura']} cm\n"
            f"🩺 Enfermedad: {perfil['enfermedad']}\n"
            f"🦴 Lesión: {perfil['lesion']}"
        )

        teclado = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✏️ Editar perfil", callback_data="editar_perfil"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Volver al menú", callback_data="volver_menu"
                    )
                ],
            ]
        )

        await query.message.reply_text(mensaje, reply_markup=teclado)
        return

    if query.data == "editar_perfil":
        user_data_temp[user_id] = {}

        await query.message.reply_text(
            "Vamos a actualizar tu perfil.\n\n¿Cuál es tu nivel?",
            reply_markup=ReplyKeyboardMarkup(
                [["Principiante"], ["Intermedio"], ["Avanzado"]],
                resize_keyboard=True,
            ),
        )
        return

    if query.data == "mi_rutina":
        perfil = obtener_perfil(user_id)

        if not perfil:
            await query.message.reply_text("No se encontró perfil.")
            return

        plan = rutinas_temp.get(user_id)

        if not plan:
            plan = generar_plan_semanal(
                nivel=perfil["nivel"],
                equipo=perfil["equipo"],
                objetivo=perfil["objetivo"],
                tiempo=perfil["tiempo"],
                dias=perfil["dias"],
                enfermedad=perfil["enfermedad"],
                lesion=perfil["lesion"],
            )

            rutinas_temp[user_id] = plan

        teclado = []

        for dia in plan.keys():
            teclado.append(
                [
                    InlineKeyboardButton(
                        dia,
                        callback_data=f"ver_{dia}",
                    )
                ]
            )

        teclado.append(
            [
                InlineKeyboardButton(
                    "🔙 Volver al menú",
                    callback_data="volver_menu",
                )
            ]
        )

        await borrar_menus_dias(context, query.message.chat_id, user_id)

        msg_menu_dias = await query.message.reply_text(
            "📅 Selecciona el día que quieres ver:",
            reply_markup=InlineKeyboardMarkup(teclado),
        )

        mensajes_menu_dias_temp[user_id] = [msg_menu_dias.message_id]
        return

    if query.data.startswith("ver_Día"):
        plan = rutinas_temp.get(user_id)

        if not plan:
            await query.message.reply_text(
                "No hay rutina cargada. Presiona 📅 Mi rutina otra vez."
            )
            return

        dia = query.data.replace("ver_", "")

        if dia not in plan:
            await query.message.reply_text("Ese día no existe en tu rutina.")
            return

        rutina_dia = {dia: plan[dia]}

        mensaje = formatear_plan_semanal(rutina_dia)
        partes = dividir_mensaje(mensaje)

        await borrar_mensajes_rutina(
            context,
            query.message.chat_id,
            user_id,
        )

        mensajes_rutina_temp[user_id] = []

        for parte in partes:
            msg = await query.message.reply_text(parte)
            mensajes_rutina_temp[user_id].append(msg.message_id)

        msg_menu = await query.message.reply_text(
            "¿Qué quieres hacer ahora?",
            reply_markup=menu_principal(),
        )

        mensajes_rutina_temp[user_id].append(msg_menu.message_id)
        return

    if query.data == "volver_menu":
        await query.message.reply_text(
            "Menú principal:",
            reply_markup=menu_principal(),
        )
        return

    if query.data == "nueva_rutina":
        perfil = obtener_perfil(user_id)

        if not perfil:
            await query.message.reply_text("No se encontró perfil.")
            return

        chat_id = query.message.chat_id
        
        try:
            await query.message.delete()
        except Exception:
            pass

        await borrar_menu_principal(
            context,
            chat_id,
            user_id
        )

        await borrar_mensajes_rutina(context, chat_id, user_id)
        await borrar_menus_dias(context, chat_id, user_id)

        plan = generar_plan_semanal(
            nivel=perfil["nivel"],
            equipo=perfil["equipo"],
            objetivo=perfil["objetivo"],
            tiempo=perfil["tiempo"],
            dias=perfil["dias"],
            enfermedad=perfil["enfermedad"],
            lesion=perfil["lesion"],
        )

        rutinas_temp[user_id] = plan
        mensajes_rutina_temp[user_id] = []

        await query.message.reply_text(
            "🔄 Nueva rutina semanal generada correctamente.\n\nPresiona 📅 Mi rutina para verla por días.",
            reply_markup=menu_principal()
        )

        return


    if query.data == "cerrar_sesion":

        chat_id = query.message.chat_id

        try:
            await query.message.delete()
        except Exception:
            pass

        await borrar_mensajes_rutina(context, chat_id, user_id)
        await borrar_menus_dias(context, chat_id, user_id)
        await borrar_menu_principal(context, chat_id, user_id)

        user_data_temp.pop(user_id, None)
        rutinas_temp.pop(user_id, None)
        mensajes_rutina_temp.pop(user_id, None)
        mensajes_menu_dias_temp.pop(user_id, None)
        mensajes_menu_principal_temp.pop(user_id, None)

        msg_start = await context.bot.send_message(
            chat_id=chat_id,
            text="Sesión cerrada correctamente 🔒\n\nEscribe /start para volver a iniciar sesión."
        )
        return


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
    app.add_handler(CallbackQueryHandler(manejar_botones))

    print("Bot iniciado...")
    app.run_polling()


if __name__ == "__main__":
    main()
