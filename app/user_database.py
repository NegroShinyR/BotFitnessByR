import sqlite3
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "fitness.db"


def conectar_db():
    return sqlite3.connect(DB_PATH)


def encriptar_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def crear_tablas_usuarios():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        nombre TEXT,
        password_hash TEXT NOT NULL,
        edad INTEGER,
        peso REAL,
        altura REAL,
        enfermedad TEXT,
        lesion TEXT,
        objetivo TEXT,
        nivel TEXT,
        equipo TEXT,
        dias INTEGER,
        tiempo INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial_rutinas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        rutina TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restricciones_salud (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        condicion TEXT NOT NULL,
        tipo_condicion TEXT,
        evitar_patron TEXT,
        evitar_grupo_muscular TEXT,
        evitar_clasificacion TEXT,
        evitar_palabras TEXT,
        adaptacion TEXT,
        recomendacion TEXT
    )
    """)

    conn.commit()
    conn.close()


def usuario_existe(telegram_id):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT telegram_id FROM usuarios WHERE telegram_id = ?",
        (telegram_id,)
    )

    usuario = cursor.fetchone()
    conn.close()

    return usuario is not None


def registrar_usuario(telegram_id, nombre, password):
    conn = conectar_db()
    cursor = conn.cursor()

    password_hash = encriptar_password(password)

    cursor.execute("""
    INSERT INTO usuarios (
        telegram_id,
        nombre,
        password_hash
    )
    VALUES (?, ?, ?)
    """, (telegram_id, nombre, password_hash))

    conn.commit()
    conn.close()


def validar_login(telegram_id, password):
    conn = conectar_db()
    cursor = conn.cursor()

    password_hash = encriptar_password(password)

    cursor.execute("""
    SELECT telegram_id
    FROM usuarios
    WHERE telegram_id = ?
    AND password_hash = ?
    """, (telegram_id, password_hash))

    usuario = cursor.fetchone()
    conn.close()

    return usuario is not None


def actualizar_perfil(
    telegram_id,
    edad,
    peso,
    altura,
    enfermedad,
    lesion,
    objetivo,
    nivel,
    equipo,
    dias,
    tiempo
):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE usuarios
    SET edad = ?,
        peso = ?,
        altura = ?,
        enfermedad = ?,
        lesion = ?,
        objetivo = ?,
        nivel = ?,
        equipo = ?,
        dias = ?,
        tiempo = ?
    WHERE telegram_id = ?
    """, (
        edad,
        peso,
        altura,
        enfermedad,
        lesion,
        objetivo,
        nivel,
        equipo,
        dias,
        tiempo,
        telegram_id
    ))

    conn.commit()
    conn.close()


def obtener_perfil(telegram_id):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        telegram_id,
        nombre,
        edad,
        peso,
        altura,
        enfermedad,
        lesion,
        objetivo,
        nivel,
        equipo,
        dias,
        tiempo
    FROM usuarios
    WHERE telegram_id = ?
    """, (telegram_id,))

    usuario = cursor.fetchone()
    conn.close()

    if not usuario:
        return None

    return {
        "telegram_id": usuario[0],
        "nombre": usuario[1],
        "edad": usuario[2],
        "peso": usuario[3],
        "altura": usuario[4],
        "enfermedad": usuario[5],
        "lesion": usuario[6],
        "objetivo": usuario[7],
        "nivel": usuario[8],
        "equipo": usuario[9],
        "dias": usuario[10],
        "tiempo": usuario[11],
    }
def insertar_restricciones_base():
    conn = conectar_db()
    cursor = conn.cursor()

    restricciones = [
    # =========================
    # LESIONES MECÁNICAS
    # =========================

    (
        "rodilla", "lesion", "Knee Dominant", "Quadriceps", "Plyometric",
        "jump,lunge,squat,pistol,step up,skater,split squat,knee hover,fire hydrant,copenhagen",
        "bajo_impacto",
        "Evitar saltos, sentadillas profundas y movimientos explosivos de rodilla."
    ),
    (
        "espalda", "lesion", "Hip Hinge", "Back", "Powerlifting",
        "deadlift,good morning,hinge,rollout,heavy,squat,lunge,pistol,cossack,split squat,reverse hyperextension",
        "evitar_carga_lumbar",
        "Evitar cargas pesadas, peso muerto intenso y flexión fuerte de columna."
    ),
    (
        "lumbar", "lesion", "Hip Hinge", "Back", "Powerlifting",
        "deadlift,good morning,rollout,heavy,leg raise",
        "evitar_carga_lumbar",
        "Evitar ejercicios que aumenten presión lumbar o provoquen dolor en espalda baja."
    ),
    (
        "hombro", "lesion", "Vertical Push", "Shoulders", "Olympic Weightlifting",
        "press,snatch,jerk,overhead,handstand",
        "evitar_sobrecabeza",
        "Evitar press sobre cabeza y movimientos explosivos del hombro."
    ),
    (
        "manguito rotador", "lesion", "Vertical Push", "Shoulders", "Olympic Weightlifting",
        "press,snatch,jerk,overhead,throw",
        "evitar_sobrecabeza",
        "Evitar movimientos sobre cabeza y ejercicios balísticos del hombro."
    ),
    (
        "cuello", "lesion", "Vertical Push", "Trapezius", "Olympic Weightlifting",
        "neck,shrug,overhead,headstand",
        "control_fatiga",
        "Evitar cargas sobre cabeza y movimientos bruscos del cuello."
    ),
    (
        "cadera", "lesion", "Hip Flexion", "Hip Flexors", "Plyometric",
        "pistol,cossack,deep squat,high knee",
        "progresion_gradual",
        "Evitar flexiones profundas de cadera y rangos dolorosos."
    ),
    (
        "tobillo", "lesion", "Ankle Plantar Flexion", "Calves", "Plyometric",
        "jump,hop,skater,calf raise,sprint",
        "bajo_impacto",
        "Evitar saltos, impactos repetidos y movimientos explosivos de tobillo."
    ),
    (
        "muneca", "lesion", "Wrist Extension", "Forearms", "",
        "push up,plank,handstand,burpee,crawl",
        "evitar_apoyo_muneca",
        "Evitar apoyo prolongado sobre muñecas y extensión forzada."
    ),
    (
        "codo", "lesion", "Elbow Extension", "Triceps", "",
        "dip,pushdown,tricep extension,skull crusher",
        "progresion_gradual",
        "Evitar extensiones fuertes de codo y sobrecarga directa."
    ),
    (
        "hernia", "lesion", "Hip Hinge", "Back", "Powerlifting",
        "deadlift,good morning,heavy,rollout,leg raise",
        "evitar_carga_lumbar",
        "Evitar cargas pesadas, flexión de columna y presión lumbar alta."
    ),
    (
        "ciatica", "lesion", "Hip Hinge", "Back", "Powerlifting",
        "deadlift,good morning,deep squat,leg raise",
        "evitar_carga_lumbar",
        "Evitar movimientos que irriten zona lumbar o generen dolor irradiado."
    ),

    # =========================
    # CARDIOVASCULARES
    # =========================

    (
        "hipertension", "cardiovascular", "", "", "Plyometric",
        "sprint,burpee,max effort,hiit,jump,clean,snatch,push press,high pull",
        "descanso_largo",
        "Evitar esfuerzos máximos, alta intensidad continua y descansos muy cortos."
    ),
    (
        "hipotension", "cardiovascular", "Locomotion", "", "Plyometric",
        "burpee,sprint,jump,fast transition",
        "control_fatiga",
        "Evitar cambios bruscos de posición e intensidad excesiva."
    ),
    (
        "cardiaco", "cardiovascular", "", "", "Plyometric",
        "sprint,burpee,max effort,hiit,jump,clean,snatch,push press,high pull",
        "baja_intensidad",
        "Evitar esfuerzos máximos y rutinas intensas sin supervisión."
    ),
    (
        "taquicardia", "cardiovascular", "Locomotion", "", "Plyometric",
        "sprint,burpee,hiit,max effort,jump",
        "control_fatiga",
        "Evitar ejercicios que eleven demasiado la frecuencia cardiaca."
    ),
    (
        "arritmia", "cardiovascular", "Locomotion", "", "Plyometric",
        "sprint,burpee,hiit,max effort,jump",
        "baja_intensidad",
        "Priorizar intensidad baja a moderada y descansos amplios."
    ),

    # =========================
    # METABÓLICAS / HORMONALES
    # =========================

    (
        "diabetes", "metabolica", "", "", "Plyometric",
        "max effort,sprint,burpee",
        "intensidad_moderada",
        "Priorizar intensidad moderada, hidratación y descansos controlados."
    ),
    (
        "obesidad", "metabolica", "Locomotion", "", "Plyometric",
        "jump,burpee,sprint,pistol,hop",
        "bajo_impacto",
        "Evitar impactos altos. Priorizar bajo impacto y progresión gradual."
    ),
    (
        "sobrepeso", "metabolica", "Locomotion", "", "Plyometric",
        "jump,burpee,sprint,pistol,hop",
        "bajo_impacto",
        "Priorizar ejercicios de bajo impacto y progresión gradual."
    ),
    (
        "hipotiroidismo", "metabolica", "", "", "",
        "max effort,hiit,sprint",
        "progresion_gradual",
        "Priorizar fuerza moderada, cardio progresivo y evitar fatiga extrema."
    ),
    (
        "hipertiroidismo", "metabolica", "", "", "Plyometric",
        "sprint,burpee,max effort,hiit,jump,clean,snatch,push press,high pull",
        "control_fatiga",
        "Evitar sobreentrenamiento, esfuerzos máximos y exceso cardiovascular."
    ),
    (
        "resistencia insulina", "metabolica", "", "", "Plyometric",
        "max effort,sprint,burpee",
        "intensidad_moderada",
        "Priorizar fuerza moderada, cardio controlado y progresión gradual."
    ),

    # =========================
    # RESPIRATORIAS
    # =========================

    (
        "asma", "respiratoria", "Locomotion", "", "Plyometric",
        "sprint,burpee,max effort,hiit,jump,clean,snatch,push press,high pull",
        "descanso_largo",
        "Controlar intensidad, respiración y descansos."
    ),
    (
        "bronquitis", "respiratoria", "Locomotion", "", "Plyometric",
        "burpee,sprint,hiit,jump",
        "baja_intensidad",
        "Priorizar baja intensidad y descansos amplios."
    ),
    (
        "epoc", "respiratoria", "Locomotion", "", "Plyometric",
        "burpee,sprint,hiit,jump",
        "baja_intensidad",
        "Evitar alta intensidad continua y priorizar trabajo controlado."
    ),

    # =========================
    # CRÓNICAS / FATIGA / SISTEMA NERVIOSO
    # =========================

    (
        "artritis", "cronica", "", "", "Plyometric",
        "jump,burpee,pistol,deep squat,heavy",
        "bajo_impacto",
        "Evitar impacto, cargas excesivas y rangos dolorosos."
    ),
    (
        "fibromialgia", "cronica", "", "", "Plyometric",
        "max effort,hiit,burpee,sprint",
        "progresion_gradual",
        "Priorizar intensidad baja, movilidad y progresión lenta."
    ),
    (
        "fatiga cronica", "cronica", "", "", "Plyometric",
        "max effort,hiit,sprint,burpee",
        "control_fatiga",
        "Evitar volumen excesivo y priorizar sesiones cortas."
    ),
    (
        "migraña", "neurologica", "Locomotion", "", "Plyometric",
        "burpee,sprint,hiit,jump",
        "control_fatiga",
        "Evitar cambios bruscos, alta intensidad y sobreesfuerzo."
    ),
    (
        "vertigo", "neurologica", "Rotational", "", "Plyometric",
        "spin,rotation,roll,burpee,handstand",
        "baja_intensidad",
        "Evitar giros rápidos, inversiones y cambios bruscos de posición."
    ),
    (
        "ansiedad", "neurologica", "Locomotion", "", "Plyometric",
        "max effort,hiit,sprint",
        "control_fatiga",
        "Priorizar intensidad moderada, respiración y descansos controlados."
    ),
    (
        "estres cronico", "neurologica", "", "", "Plyometric",
        "max effort,hiit,sprint",
        "control_fatiga",
        "Evitar sobreentrenamiento y priorizar movilidad/fuerza moderada."
    )
]

    for r in restricciones:
        cursor.execute("""
        INSERT INTO restricciones_salud (
            condicion,
            tipo_condicion,
            evitar_patron,
            evitar_grupo_muscular,
            evitar_clasificacion,
            evitar_palabras,
            adaptacion,
            recomendacion
        )
        SELECT ?, ?, ?, ?, ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM restricciones_salud WHERE condicion = ?
        )
        """, (*r, r[0]))

    conn.commit()
    conn.close()


def obtener_restricciones_por_condicion(condicion):
    conn = conectar_db()
    cursor = conn.cursor()

    condicion = str(condicion).lower()

    cursor.execute("""
    SELECT
        condicion,
        tipo_condicion,
        evitar_patron,
        evitar_grupo_muscular,
        evitar_clasificacion,
        evitar_palabras,
        adaptacion,
        recomendacion
    FROM restricciones_salud
    WHERE condicion LIKE ?
    """, (f"%{condicion}%",))

    datos = cursor.fetchall()
    conn.close()

    return datos