from app.recomendador import generar_plan_semanal
from app.utils import formatear_plan_semanal


plan = generar_plan_semanal(
    nivel="Intermedio",
    equipo="Sin equipo",
    objetivo="Condicion fisica / potencia",
    tiempo=45,
    dias=2,
    enfermedad="hipotiroidismo",
    lesion="Ninguna"
)

mensaje = formatear_plan_semanal(plan)

print(mensaje)