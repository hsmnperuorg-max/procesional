from django.db import migrations

RECORRIDOS = [
    {"id": "rec-001", "nombre": "Primer Recorrido Procesional 2024", "fecha": "2024-10-18",
     "hora_salida": "08:00", "hora_llegada_programada": "22:00", "distancia_total": 4800,
     "observaciones": "Recorrido tradicional por el Centro Histórico de Lima",
     "estado": "programado", "color": "#6E1E91"},
    {"id": "rec-002", "nombre": "Segundo Recorrido Procesional 2024", "fecha": "2024-10-19",
     "hora_salida": "08:00", "hora_llegada_programada": "21:30", "distancia_total": 4200,
     "observaciones": "", "estado": "programado", "color": "#4B1462"},
]

CUADRILLAS = [
    {"id": "cua-01", "recorrido_id": "rec-001", "numero": 1, "cuadrilla": "Cuadrilla 1", "metraje": 320, "tiempo_estimado": 45, "hora_toma": "08:00", "hora_deja": "08:45"},
    {"id": "cua-02", "recorrido_id": "rec-001", "numero": 2, "cuadrilla": "Cuadrilla 2", "metraje": 310, "tiempo_estimado": 43, "hora_toma": "08:50", "hora_deja": "09:33"},
    {"id": "cua-03", "recorrido_id": "rec-001", "numero": 3, "cuadrilla": "Cuadrilla 3", "metraje": 330, "tiempo_estimado": 46, "hora_toma": "09:38", "hora_deja": "10:24"},
    {"id": "cua-04", "recorrido_id": "rec-001", "numero": 4, "cuadrilla": "Cuadrilla 4", "metraje": 300, "tiempo_estimado": 42, "hora_toma": "10:29", "hora_deja": "11:11"},
    {"id": "cua-05", "recorrido_id": "rec-001", "numero": 5, "cuadrilla": "Cuadrilla 5", "metraje": 340, "tiempo_estimado": 47, "hora_toma": "11:16", "hora_deja": "12:03"},
    {"id": "cua-06", "recorrido_id": "rec-001", "numero": 6, "cuadrilla": "Cuadrilla 6", "metraje": 290, "tiempo_estimado": 41, "hora_toma": "12:08", "hora_deja": "12:49"},
    {"id": "cua-07", "recorrido_id": "rec-001", "numero": 7, "cuadrilla": "Cuadrilla 7", "metraje": 315, "tiempo_estimado": 44, "hora_toma": "12:54", "hora_deja": "13:38"},
    {"id": "cua-08", "recorrido_id": "rec-001", "numero": 8, "cuadrilla": "Cuadrilla 8", "metraje": 325, "tiempo_estimado": 45, "hora_toma": "13:43", "hora_deja": "14:28"},
    {"id": "cua-09", "recorrido_id": "rec-001", "numero": 9, "cuadrilla": "Cuadrilla 9", "metraje": 305, "tiempo_estimado": 43, "hora_toma": "14:33", "hora_deja": "15:16"},
    {"id": "cua-10", "recorrido_id": "rec-001", "numero": 10, "cuadrilla": "Cuadrilla 10", "metraje": 335, "tiempo_estimado": 47, "hora_toma": "15:21", "hora_deja": "16:08"},
    {"id": "cua-11", "recorrido_id": "rec-001", "numero": 11, "cuadrilla": "Cuadrilla 11", "metraje": 310, "tiempo_estimado": 43, "hora_toma": "16:13", "hora_deja": "16:56"},
    {"id": "cua-12", "recorrido_id": "rec-001", "numero": 12, "cuadrilla": "Cuadrilla 12", "metraje": 320, "tiempo_estimado": 45, "hora_toma": "17:01", "hora_deja": "17:46"},
    {"id": "cua-13", "recorrido_id": "rec-001", "numero": 13, "cuadrilla": "Cuadrilla 13", "metraje": 300, "tiempo_estimado": 42, "hora_toma": "17:51", "hora_deja": "18:33"},
    {"id": "cua-14", "recorrido_id": "rec-001", "numero": 14, "cuadrilla": "Cuadrilla 14", "metraje": 330, "tiempo_estimado": 46, "hora_toma": "18:38", "hora_deja": "19:24"},
    {"id": "cua-15", "recorrido_id": "rec-001", "numero": 15, "cuadrilla": "Cuadrilla 15", "metraje": 315, "tiempo_estimado": 44, "hora_toma": "19:29", "hora_deja": "20:13"},
    {"id": "cua-16", "recorrido_id": "rec-001", "numero": 16, "cuadrilla": "Cuadrilla 16", "metraje": 295, "tiempo_estimado": 41, "hora_toma": "20:18", "hora_deja": "20:59"},
    {"id": "cua-17", "recorrido_id": "rec-001", "numero": 17, "cuadrilla": "Cuadrilla 17", "metraje": 325, "tiempo_estimado": 45, "hora_toma": "21:04", "hora_deja": "21:49"},
    {"id": "cua-18", "recorrido_id": "rec-001", "numero": 18, "cuadrilla": "Cuadrilla 18", "metraje": 310, "tiempo_estimado": 43, "hora_toma": "21:54", "hora_deja": "22:37"},
    {"id": "cua-19", "recorrido_id": "rec-001", "numero": 19, "cuadrilla": "Cuadrilla 19", "metraje": 320, "tiempo_estimado": 45, "hora_toma": "22:42", "hora_deja": "23:27"},
    {"id": "cua-20", "recorrido_id": "rec-001", "numero": 20, "cuadrilla": "Cuadrilla 20", "metraje": 305, "tiempo_estimado": 43, "hora_toma": "23:32", "hora_deja": "00:15"},
    {"id": "cua-hh", "recorrido_id": "rec-001", "numero": 21, "cuadrilla": "Hermanos Honorarios", "tipo": "honorarios", "metraje": 280, "tiempo_estimado": 40, "hora_toma": "00:20", "hora_deja": "01:00"},
]

HOMENAJES = [
    {"id": "hom-01", "recorrido_id": "rec-001", "nombre": "Homenaje Palacio de Gobierno", "ubicacion": "Jr. de la Unión cdra. 1", "tiempo_programado": 15, "prioridad": "alta", "cargo_a": "institucion", "observaciones": "Presencia de autoridades"},
    {"id": "hom-02", "recorrido_id": "rec-001", "nombre": "Homenaje Municipalidad de Lima", "ubicacion": "Jr. de la Unión cdra. 2", "tiempo_programado": 10, "prioridad": "alta", "cargo_a": "institucion", "observaciones": ""},
    {"id": "hom-03", "recorrido_id": "rec-001", "nombre": "Homenaje Iglesia San Pedro", "ubicacion": "Jr. Ucayali cdra. 4", "tiempo_programado": 20, "prioridad": "alta", "cargo_a": "cuadrilla", "observaciones": "Misa cantada"},
    {"id": "hom-04", "recorrido_id": "rec-001", "nombre": "Homenaje Club Nacional", "ubicacion": "Jr. de la Unión cdra. 8", "tiempo_programado": 12, "prioridad": "media", "cargo_a": "cuadrilla", "observaciones": ""},
    {"id": "hom-05", "recorrido_id": "rec-001", "nombre": "Homenaje Casa de la Literatura", "ubicacion": "Jr. Áncash cdra. 2", "tiempo_programado": 8, "prioridad": "baja", "cargo_a": "cuadrilla", "observaciones": ""},
]


def seed_datos(apps, schema_editor):
    Recorrido = apps.get_model('gestion', 'Recorrido')
    Cuadrilla = apps.get_model('gestion', 'Cuadrilla')
    Homenaje = apps.get_model('gestion', 'Homenaje')

    if Recorrido.objects.exists():
        return

    for r in RECORRIDOS:
        Recorrido.objects.create(**r)
    for c in CUADRILLAS:
        Cuadrilla.objects.create(**c)
    for h in HOMENAJES:
        Homenaje.objects.create(**h)


def eliminar_datos(apps, schema_editor):
    Recorrido = apps.get_model('gestion', 'Recorrido')
    Recorrido.objects.filter(id__in=[r['id'] for r in RECORRIDOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_datos, eliminar_datos),
    ]
