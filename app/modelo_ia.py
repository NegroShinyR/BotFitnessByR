from pathlib import Path
import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "modelo_rutinas.pkl"


def cargar_modelo():
    return joblib.load(MODEL_PATH)


def preparar_datos(datos, paquete):
    encoders = paquete["encoders"]
    columnas = paquete["columnas"]

    df = pd.DataFrame([datos])

    for col in columnas:
        if col not in df.columns:
            df[col] = "Sin dato"

    df = df[columnas]

    for col in df.columns:
        if col in encoders:
            le = encoders[col]
            valor = str(df.loc[0, col])

            if valor not in le.classes_:
                valor = le.classes_[0]

            df[col] = le.transform([valor])
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def predecir_con_modelos(datos):
    paquete = cargar_modelo()

    df = preparar_datos(datos, paquete)

    label_y = paquete["label_y"]

    dt_pred = paquete["decision_tree"].predict(df)[0]
    rf_pred = paquete["random_forest"].predict(df)[0]

    resultado_dt = label_y.inverse_transform([dt_pred])[0]
    resultado_rf = label_y.inverse_transform([rf_pred])[0]

    return {
        "decision_tree": resultado_dt,
        "random_forest": resultado_rf,
        "accuracy_decision_tree": paquete["accuracy_decision_tree"],
        "accuracy_random_forest": paquete["accuracy_random_forest"]
    }


def predecir_tipo_rutina(datos):
    resultados = predecir_con_modelos(datos)
    return resultados["random_forest"]