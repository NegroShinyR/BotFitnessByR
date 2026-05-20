import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "data" / "dataset_ml.csv"
MODEL_PATH = BASE_DIR / "models" / "modelo_rutinas.pkl"


def entrenar_modelo():
    df = pd.read_csv(DATASET_PATH)

    columnas = [
        "nivel_bot",
        "equipo_bot",
        # "objetivo_bot",
        "bloque_bot",
        "grupo_muscular",
        "patron_movimiento_1",
        "clasificacion",
        "categoria_movimiento",
        "score_funcional",
    ]

    X = df[columnas].copy()

    y = df["tipo_rutina"]

    encoders = {}

    for col in X.columns:
        if col != "score_funcional":
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le
        else:
            X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    label_y = LabelEncoder()
    y = label_y.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("\nTipos de datos usados para entrenar:")
    print(X.dtypes)

    print("\nEntrenando Decision Tree...")
    dt_model = DecisionTreeClassifier(max_depth=10, random_state=42)

    dt_model.fit(X_train, y_train)

    dt_pred = dt_model.predict(X_test)

    dt_acc = accuracy_score(y_test, dt_pred)

    print(f"Accuracy Decision Tree: {dt_acc:.4f}")

    print("\nEntrenando Random Forest...")

    rf_model = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42)

    rf_model.fit(X_train, y_train)

    rf_pred = rf_model.predict(X_test)

    rf_acc = accuracy_score(y_test, rf_pred)

    print(f"Accuracy Random Forest: {rf_acc:.4f}")

    mejor_modelo = rf_model if rf_acc >= dt_acc else dt_model

    joblib.dump(
        {
            "decision_tree": dt_model,
            "random_forest": rf_model,
            "accuracy_decision_tree": dt_acc,
            "accuracy_random_forest": rf_acc,
            "encoders": encoders,
            "label_y": label_y,
            "columnas": columnas,
        },
        MODEL_PATH,
    )

    print("\nModelo guardado correctamente.")
    print(f"Ruta: {MODEL_PATH}")


if __name__ == "__main__":
    entrenar_modelo()
