def formatear_rutina(rutina):

    mensaje = ""

    for bloque, ejercicios in rutina.items():

        mensaje += f"\n🔥 {bloque.upper()}\n"
        mensaje += "-" * 30 + "\n"

        if not ejercicios:
            mensaje += "No hay ejercicios disponibles.\n"
            continue

        for i, ejercicio in enumerate(ejercicios, start=1):

            mensaje += (
                f"\n{i}. {ejercicio['ejercicio']}\n"
            )

            mensaje += (
                f"📈 Nivel: {ejercicio['nivel_bot']}\n"
            )

            mensaje += (
                f"🏋️ Equipo: {ejercicio['equipo_bot']}\n"
            )

            mensaje += (
                f"🎯 Objetivo: {ejercicio['objetivo_bot']}\n"
            )

            mensaje += (
                f"🔁 Series: {ejercicio['series_sugeridas']}\n"
            )

            mensaje += (
                f"⏱ Reps/Tiempo: "
                f"{ejercicio['repeticiones_o_tiempo']}\n"
            )

            mensaje += (
                f"😴 Descanso: "
                f"{ejercicio['descanso_sugerido']}\n"
            )

        link = str(ejercicio.get("short_youtube_url", "")).strip()

        if link and link.lower() != "nan":
            mensaje += (
                f"🎥 Demo:\n"
                f"{link}\n"
            )

    return mensaje

def formatear_plan_semanal(plan):
    mensaje = "📅 PLAN SEMANAL DE ENTRENAMIENTO\n"

    for dia, rutina in plan.items():
        mensaje += f"\n\n====================\n"
        mensaje += f"🏋️ {dia.upper()}\n"
        mensaje += f"====================\n"

        if isinstance(rutina, dict) and "error" in rutina:
            mensaje += f"\n⚠️ {rutina['error']}\n"
            continue

        mensaje += formatear_rutina(rutina)

    return mensaje


def dividir_mensaje(texto, limite=4000):

    partes = []

    while len(texto) > limite:
        corte = texto.rfind("\n", 0, limite)

        if corte == -1:
            corte = limite

        partes.append(texto[:corte])
        texto = texto[corte:]

    partes.append(texto)

    return partes