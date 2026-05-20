from app.modelo_ia import predecir_con_modelos


datos = {
    "nivel_bot": "Intermedio",
    "equipo_bot": "Peso libre",
    "bloque_bot": "Principal",
    "grupo_muscular": "Quadriceps",
    "patron_movimiento_1": "Knee Dominant",
    "clasificacion": "Bodybuilding",
    "categoria_movimiento": "Pierna",
    "score_funcional": 3
}

resultado = predecir_con_modelos(datos)

print("Decision Tree:", resultado["decision_tree"])
print("Random Forest:", resultado["random_forest"])
print("Accuracy Decision Tree:", resultado["accuracy_decision_tree"])
print("Accuracy Random Forest:", resultado["accuracy_random_forest"])