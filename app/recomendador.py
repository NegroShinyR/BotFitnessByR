import random
from app.database import obtener_ejercicios
from app.user_database import obtener_restricciones_por_condicion


def filtrar_base(df, nivel, equipo, objetivo=None):

    df_filtrado = df.copy()

    if nivel:
        df_filtrado = df_filtrado[df_filtrado["nivel_bot"] == nivel]

    # Filtro por equipo, primero exacto
    if equipo:
        df_equipo_exacto = df_filtrado[df_filtrado["equipo_bot"] == equipo]

        # Si hay suficientes ejercicios exactos, se queda solo con esos
        if len(df_equipo_exacto) >= 20:
            df_filtrado = df_equipo_exacto

        else:
            equipos_fallback = {
                "Gimnasio / maquina": [
                    "Gimnasio / maquina",
                    "Peso libre",
                    "Accesorios funcionales",
                ],
                "Sin equipo": ["Sin equipo", "Calistenia / barras"],
                "Ligas": ["Ligas", "Accesorios funcionales", "Peso libre"],
                "Calistenia / barras": ["Calistenia / barras", "Sin equipo"],
                "Peso libre": ["Peso libre", "Accesorios funcionales"],
            }

            lista_equipos = equipos_fallback.get(equipo, [equipo])

            df_filtrado = df_filtrado[df_filtrado["equipo_bot"].isin(lista_equipos)]

    # Filtro por objetivo, solo si no deja muy pocos
    if objetivo:
        df_objetivo = df_filtrado[
            df_filtrado["objetivo_bot"]
            .astype(str)
            .str.contains(objetivo, case=False, na=False)
        ]

        if len(df_objetivo) >= 15:
            df_filtrado = df_objetivo

    return df_filtrado


def limpiar_nombre(nombre):

    palabras_ignorar = {
        # implementos
        "bodyweight",
        "dumbbell",
        "kettlebell",
        "barbell",
        "plate",
        "cable",
        "sandbag",
        "slam",
        "battle",
        "rope",
        "macebell",
        "clubbell",
        "bulgarian",
        "bag",
        "stability",
        "ball",
        "ring",
        "suspension",
        # posiciones
        "single",
        "double",
        "alternating",
        "assisted",
        "supported",
        "kneeling",
        "standing",
        "seated",
        "low",
        "high",
        "front",
        "side",
        "reverse",
        "bent",
        "knee",
        "arm",
        "leg",
        "half",
        "tall",
        "incline",
        "decline",
        "floor",
        "prone",
        "supine",
        "ipsilateral",
        "contralateral",
        # agarres / detalles
        "crush",
        "grip",
        "bottoms",
        "up",
        "overhead",
        "front",
        "rack",
        "bear",
        "hug",
        "suitcase",
        "waiter",
        # conectores
        "to",
        "and",
        "with",
        # MUY IMPORTANTES PARA NORMALIZAR
        "flutter",
        "hold",
        "tuck",
    }

    nombre = str(nombre).lower()

    palabras = nombre.split()

    palabras_limpias = [
        palabra for palabra in palabras if palabra not in palabras_ignorar
    ]

    return " ".join(palabras_limpias)

    palabras = str(nombre).lower().replace("-", " ").split()

    palabras_clave = [
        palabra for palabra in palabras if palabra not in palabras_ignorar
    ]

    return " ".join(palabras_clave)


def obtener_categoria_movimiento(ejercicio):
    patron = str(ejercicio.get("patron_movimiento_1", "")).lower()
    musculo = str(ejercicio.get("grupo_muscular", "")).lower()
    clasificacion = str(ejercicio.get("clasificacion", "")).lower()

    if "knee dominant" in patron or musculo in ["quadriceps", "glutes", "calves"]:
        return "Pierna"

    if "hip hinge" in patron or "hip extension" in patron or musculo in ["hamstrings"]:
        return "Cadera"

    if "push" in patron or musculo in ["chest", "shoulders", "triceps"]:
        return "Empuje"

    if "pull" in patron or musculo in ["back", "biceps", "trapezius"]:
        return "Jalón"

    if (
        "anti" in patron
        or "spinal" in patron
        or "isometric" in patron
        or musculo in ["abdominals", "hip flexors"]
    ):
        return "Core"

    if "rotational" in patron:
        return "Rotación"

    if "carry" in patron:
        return "Carga"

    if (
        "locomotion" in patron
        or "plyometric" in clasificacion
        or "ballistics" in clasificacion
    ):
        return "Condición"

    if "mobility" in clasificacion or "balance" in clasificacion:
        return "Movilidad"

    return "General"


def obtener_familia_movimiento(nombre):
    nombre = str(nombre).lower()

    familias = {
        "lunge_split_step": ["lunge", "split squat", "step up", "curtsy", "cossack"],
        "squat": ["squat", "pistol", "cyclist", "sissy"],
        "push_press": ["press", "push up", "thruster", "jerk"],
        "pull_row": ["row", "pull up", "face pull", "pulldown"],
        "hinge_deadlift": ["deadlift", "hinge", "romanian"],
        "core_plank_hollow": [
            "plank",
            "hollow",
            "sit up",
            "rollout",
            "dead bug",
            "l sit",
            "flutter",
            "dragon flag",
            "toe touch",
            "leg raise",
            "v up",
            "crunch",
            "bicycle",
            "hanging knee",
            "hanging leg",
            "sit through",
            "bear crawl",
        ],
        "carry_march": ["carry", "march", "walk"],
        "clean_snatch": ["clean", "snatch"],
        "swing_rotation": [
            "swing",
            "rotation",
            "rotational",
            "around the world",
            "mill",
            "360",
        ],
        "jump_plyo": ["jump", "plyometric", "burpee", "mountain climber"],
    }

    for familia, palabras in familias.items():
        for palabra in palabras:
            if palabra in nombre:
                return familia

    return "general"


def calcular_score_funcional(ejercicio):
    score = 0

    nombre = str(ejercicio.get("ejercicio", "")).lower()
    clasificacion = str(ejercicio.get("clasificacion", "")).lower()
    patron = str(ejercicio.get("patron_movimiento_1", "")).lower()
    musculo = str(ejercicio.get("grupo_muscular", "")).lower()
    objetivo = str(ejercicio.get("objetivo_bot", "")).lower()

    # Ejercicios más funcionales
    if "ballistics" in clasificacion:
        score += 3

    if "plyometric" in clasificacion:
        score += 3

    if "calisthenics" in clasificacion:
        score += 2

    if "balance" in clasificacion:
        score += 1

    if "mobility" in clasificacion:
        score += 1

    # Patrones compuestos / funcionales
    if any(
        p in patron
        for p in [
            "knee dominant",
            "hip hinge",
            "locomotion",
            "loaded carry",
            "rotational",
        ]
    ):
        score += 2

    if any(
        p in patron
        for p in [
            "horizontal push",
            "vertical push",
            "horizontal pull",
            "vertical pull",
        ]
    ):
        score += 2

    # Objetivos funcionales
    if "condicion" in objetivo:
        score += 2

    if "core" in objetivo:
        score += 0

    # Penalizar ejercicios muy aislados
    palabras_aisladas = [
        "curl",
        "tricep extension",
        "pushdown",
        "skull crusher",
        "chest fly",
        "calf raise",
        "leg extension",
        "hamstring curl",
    ]
    palabras_sobreusadas = ["hollow", "flutter", "l sit", "dragon flag", "toe touch"]

    if any(palabra in nombre for palabra in palabras_aisladas):
        score -= 3

    if any(palabra in nombre for palabra in palabras_sobreusadas):
        score -= 5

    # Penalizar bodybuilding aislado
    if "bodybuilding" in clasificacion:
        score -= 1

    # Premiar ejercicios con video
    link = str(ejercicio.get("short_youtube_url", "")).strip()

    if link and link.lower() != "nan":
        score += 1

    return score


def seleccionar_con_variedad(df, bloque, cantidad):
    bloque_df = df[
        df["bloque_bot"].astype(str).str.contains(bloque, case=False, na=False)
    ].copy()

    if bloque_df.empty:
        return []

    if "score_funcional" not in bloque_df.columns:
        bloque_df["score_funcional"] = bloque_df.apply(
            calcular_score_funcional,
            axis=1
    )

    bloque_df = bloque_df.sort_values(by="score_funcional", ascending=False)

    # Mantener solo los mejores ejercicios
    top_n = min(len(bloque_df), 80)

    bloque_df = bloque_df.head(top_n)

    # Random controlado dentro de los mejores
    bloque_df = bloque_df.sample(frac=1).reset_index(drop=True)

    seleccionados = []

    patrones_usados = set()
    musculos_usados = set()
    nombres_base_usados = set()
    conteo_equipos = {}
    conteo_palabras_clave = {}
    conteo_categorias = {}
    conteo_familias = {}

    palabras_movimiento = [
        "clean",
        "snatch",
        "thruster",
        "carry",
        "press",
        "lunge",
        "squat",
        "plank",
        "row",
        "deadlift",
        "bridge",
        "jump",
    ]

    max_por_equipo = 3
    max_por_palabra = 2

    for _, ejercicio in bloque_df.iterrows():
        nombre = ejercicio.get("ejercicio", "")
        nombre_base = limpiar_nombre(nombre)
        patron = ejercicio.get("patron_movimiento_1", "")
        musculo = ejercicio.get("grupo_muscular", "")
        equipo = ejercicio.get("equipo_bot", "")
        categoria_movimiento = obtener_categoria_movimiento(ejercicio)
        nombre_lower = str(nombre).lower()
        familia_movimiento = obtener_familia_movimiento(nombre)

        if nombre_base in nombres_base_usados:
            continue

        if conteo_categorias.get(categoria_movimiento, 0) >= 2:
            continue

        if conteo_familias.get(familia_movimiento, 0) >= 1:
            continue

        if conteo_equipos.get(equipo, 0) >= max_por_equipo:
            continue

        palabra_detectada = None

        for palabra in palabras_movimiento:
            if palabra in nombre_lower:
                palabra_detectada = palabra
                break

        if palabra_detectada:
            if conteo_palabras_clave.get(palabra_detectada, 0) >= max_por_palabra:
                continue

        if patron in patrones_usados and len(patrones_usados) < cantidad:
            continue

        if musculo in musculos_usados and len(musculos_usados) < cantidad:
            continue

        seleccionados.append(ejercicio.to_dict())

        nombres_base_usados.add(nombre_base)
        patrones_usados.add(patron)
        musculos_usados.add(musculo)

        conteo_equipos[equipo] = conteo_equipos.get(equipo, 0) + 1

        conteo_categorias[categoria_movimiento] = (
            conteo_categorias.get(categoria_movimiento, 0) + 1
        )

        if palabra_detectada:
            conteo_palabras_clave[palabra_detectada] = (
                conteo_palabras_clave.get(palabra_detectada, 0) + 1
            )

        if len(seleccionados) >= cantidad:
            break

    # Relleno menos estricto si faltan ejercicios
    if len(seleccionados) < cantidad:
        faltantes = cantidad - len(seleccionados)

        for _, ejercicio in bloque_df.iterrows():
            nombre = ejercicio.get("ejercicio", "")
            nombre_base = limpiar_nombre(nombre)

            if nombre_base in nombres_base_usados:
                continue

            seleccionados.append(ejercicio.to_dict())
            nombres_base_usados.add(nombre_base)

            if len(seleccionados) >= cantidad:
                break

    return seleccionados


def generar_rutina_inteligente(
    nivel, equipo, objetivo, tiempo=30, enfermedad=None, lesion=None
):
    df = obtener_ejercicios()

    df = aplicar_adaptaciones_salud(df, enfermedad=enfermedad, lesion=lesion)

    df = aplicar_restricciones_salud(df, enfermedad=enfermedad, lesion=lesion)

    df_base = filtrar_base(df=df, nivel=nivel, equipo=equipo, objetivo=objetivo)

    if df_base.empty:
        df_base = filtrar_base(df=df, nivel=nivel, equipo=equipo, objetivo=None)

    if df_base.empty:
        df_base = filtrar_base(df=df, nivel=nivel, equipo=None, objetivo=objetivo)

    if df_base.empty:
        return {"error": "No se encontraron ejercicios con esos filtros."}

    if tiempo <= 20:
        principal = 3
        tecnica = 1
        calentamiento = 2
    elif tiempo <= 40:
        principal = 5
        tecnica = 2
        calentamiento = 2
    else:
        principal = 6
        tecnica = 3
        calentamiento = 3

    rutina = {
        "Calentamiento": seleccionar_con_variedad(
            df[df["nivel_bot"] == nivel], "Calentamiento", calentamiento
        ),
        "Bloque principal": seleccionar_con_variedad(
            filtrar_base(df=df, nivel=nivel, equipo=equipo, objetivo=objetivo),
            "Principal",
            principal,
        ),
        "Técnica / movilidad": seleccionar_con_variedad(
            df[
                df["nivel_bot"] == nivel
            ],
            "Calentamiento",
            tecnica
        ),
    }

    return rutina


def generar_plan_semanal(
    nivel, equipo, objetivo, tiempo=30, dias=3, enfermedad=None, lesion=None
):
    plan = {}

    for dia in range(1, dias + 1):
        rutina = generar_rutina_inteligente(
            nivel=nivel,
            equipo=equipo,
            objetivo=objetivo,
            tiempo=tiempo,
            enfermedad=enfermedad,
            lesion=lesion,
        )
        plan[f"Día {dia}"] = rutina

    return plan


def aplicar_restricciones_salud(df, enfermedad=None, lesion=None):
    condiciones = []

    if enfermedad and str(enfermedad).lower() != "ninguna":
        condiciones.append(enfermedad)

    if lesion and str(lesion).lower() != "ninguna":
        condiciones.append(lesion)

    df_filtrado = df.copy()

    for condicion in condiciones:
        restricciones = obtener_restricciones_por_condicion(condicion)

        for restriccion in restricciones:
            (
                _,
                tipo_condicion,
                evitar_patron,
                evitar_grupo,
                evitar_clasificacion,
                evitar_palabras,
                adaptacion,
                _,
            ) = restriccion

            if evitar_patron:
                df_filtrado = df_filtrado[
                    df_filtrado["patron_movimiento_1"] != evitar_patron
                ]

            if evitar_grupo:
                df_filtrado = df_filtrado[df_filtrado["grupo_muscular"] != evitar_grupo]

            if evitar_clasificacion:
                df_filtrado = df_filtrado[
                    df_filtrado["clasificacion"] != evitar_clasificacion
                ]
            if evitar_palabras:

                palabras = [p.strip().lower() for p in evitar_palabras.split(",")]

                df_filtrado = df_filtrado[
                    ~df_filtrado["ejercicio"]
                    .astype(str)
                    .str.lower()
                    .apply(lambda nombre: any(p in nombre for p in palabras))
                ]

    return df_filtrado


def aplicar_adaptaciones_salud(df, enfermedad=None, lesion=None):

    condiciones = []

    if enfermedad and str(enfermedad).lower() != "ninguna":
        condiciones.append(enfermedad)

    if lesion and str(lesion).lower() != "ninguna":
        condiciones.append(lesion)

    df = df.copy()
    if "score_funcional" not in df.columns:
        df["score_funcional"] = df.apply(calcular_score_funcional, axis=1)

    for condicion in condiciones:

        restricciones = obtener_restricciones_por_condicion(condicion)

        for restriccion in restricciones:

            (
                _,
                tipo_condicion,
                evitar_patron,
                evitar_grupo,
                evitar_clasificacion,
                evitar_palabras,
                adaptacion,
                _,
            ) = restriccion

            # =========================
            # BAJO IMPACTO
            # =========================

            if adaptacion == "bajo_impacto":

                print("Aplicando adaptación: BAJO IMPACTO")

                # penalizar plyometrics
                df.loc[
                    df["clasificacion"]
                    .astype(str)
                    .str.contains("Plyometric", case=False, na=False),
                    "score_funcional",
                ] -= 20

                # eliminar ejercicios explosivos
                df = df[
                    ~df["ejercicio"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        "jump|burpee|sprint|plyometric|pistol|skater|hop|duck walk|reverse nordic|copenhagen", na=False
                    )
                ]

                # bajar ejercicios funcionales agresivos
                df.loc[
                    df["ejercicio"]
                    .astype(str)
                    .str.contains(
                        "kettlebell|clubbell|macebell|swing|snatch|clean|gunslinger|overhead|russian step up",
                        case=False,
                        na=False,
                    ),
                    "score_funcional",
                ] -= 20

                # subir ejercicios seguros
                df.loc[
                    df["objetivo_bot"]
                    .astype(str)
                    .str.contains("Movilidad|Core|Estabilidad", case=False, na=False),
                    "score_funcional",
                ] += 10

            # =========================
            # DESCANSO LARGO
            # =========================

            if adaptacion == "descanso_largo":

                print("Aplicando adaptación: DESCANSO LARGO")

                # bajar intensidad
                df.loc[
                    df["ejercicio"]
                    .astype(str)
                    .str.contains(
                        "burpee|sprint|hiit|clean|snatch|push press|high pull",
                        case=False,
                        na=False,
                    ),
                    "score_funcional",
                ] -= 20

                # eliminar ejercicios extremos
                df = df[
                    ~df["ejercicio"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        "burpee|sprint|hiit|max effort|jump|snatch|clean|high pull|push press",
                        na=False,
                    )
                ]

                # subir estabilidad/movilidad
                df.loc[
                    df["bloque_bot"]
                    .astype(str)
                    .str.contains("Movilidad|Core|Estabilidad", case=False, na=False),
                    "score_funcional",
                ] += 10

            # =========================
            # EVITAR CARGA LUMBAR
            # =========================

            if adaptacion == "evitar_carga_lumbar":

                print("Aplicando adaptación: EVITAR CARGA LUMBAR")

                # penalizar hip hinge
                df.loc[
                    df["patron_movimiento_1"]
                    .astype(str)
                    .str.contains("Hip Hinge", case=False, na=False),
                    "score_funcional",
                ] -= 20

                # eliminar ejercicios peligrosos
                df = df[
                    ~df["ejercicio"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        "deadlift|good morning|rollout|leg raise|heavy|hinge", na=False
                    )
                ]

                # subir estabilidad/core
                df.loc[
                    df["objetivo_bot"]
                    .astype(str)
                    .str.contains("Movilidad|Core|Estabilidad", case=False, na=False),
                    "score_funcional",
                ] += 10

            # =========================
            # CONTROL FATIGA
            # =========================

            if adaptacion == "control_fatiga":

                print("Aplicando adaptación: CONTROL FATIGA")

                # bajar ballistic y plyometric
                df.loc[
                    df["clasificacion"]
                    .astype(str)
                    .str.contains("Ballistics|Plyometric", case=False, na=False),
                    "score_funcional",
                ] -= 15

                # eliminar ejercicios agresivos
                df = df[
                    ~df["ejercicio"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        "burpee|sprint|hiit|max effort|snatch|clean|high pull|jump|swing|macebell|clubbell",
                        na=False,
                    )
                ]

                # bajar ejercicios funcionales agresivos
                df.loc[
                    df["ejercicio"]
                    .astype(str)
                    .str.contains(
                        "kettlebell|clubbell|macebell|swing|overhead|plyometric",
                        case=False,
                        na=False,
                    ),
                    "score_funcional",
                ] -= 15

                # subir estabilidad
                df.loc[
                    df["objetivo_bot"]
                    .astype(str)
                    .str.contains("Movilidad|Core|Estabilidad", case=False, na=False),
                    "score_funcional",
                ] += 10

            # =========================
            # PROGRESIÓN GRADUAL
            # =========================

            if adaptacion == "progresion_gradual":

                print("Aplicando adaptación: PROGRESIÓN GRADUAL")

                # bajar ejercicios avanzados
                df.loc[
                    df["nivel_bot"]
                    .astype(str)
                    .str.contains("Avanzado", case=False, na=False),
                    "score_funcional",
                ] -= 15

                # eliminar ejercicios agresivos
                df = df[
                    ~df["ejercicio"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        "max effort|hiit|sprint|burpee|snatch|clean|jump", na=False
                    )
                ]

                # subir ejercicios seguros
                df.loc[
                    df["objetivo_bot"]
                    .astype(str)
                    .str.contains("Movilidad|Core|Estabilidad", case=False, na=False),
                    "score_funcional",
                ] += 10
    return df
