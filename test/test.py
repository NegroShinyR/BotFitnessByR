from app.recomendador import generar_plan_semanal
from app.utils import formatear_plan_semanal


plan = generar_plan_semanal(
    nivel="Principiante",
    equipo="Sin equipo",
    objetivo="Condicion fisica / potencia",
    tiempo=30,
    dias=3
)

mensaje = formatear_plan_semanal(plan)

print(mensaje)