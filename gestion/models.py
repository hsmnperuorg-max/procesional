import uuid

from django.db import models


def nuevo_id_recorrido():
    return f'rec-{uuid.uuid4().hex[:8]}'


def nuevo_id_cuadrilla():
    return f'cua-{uuid.uuid4().hex[:8]}'


def nuevo_id_homenaje():
    return f'hom-{uuid.uuid4().hex[:8]}'


def nuevo_id_evento():
    return uuid.uuid4().hex[:8]


class Recorrido(models.Model):
    ESTADOS = [
        ('programado', 'Programado'),
        ('en_curso', 'En curso'),
        ('completado', 'Completado'),
    ]

    id = models.CharField(max_length=20, primary_key=True, default=nuevo_id_recorrido, editable=False)
    nombre = models.CharField(max_length=200)
    fecha = models.DateField()
    hora_salida = models.TimeField(null=True, blank=True)
    hora_llegada_programada = models.TimeField(null=True, blank=True)
    distancia_total = models.IntegerField(default=0)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='programado')
    color = models.CharField(max_length=10, default='#6E1E91')
    ruta_coords = models.JSONField(default=list, blank=True)
    punto_inicio = models.CharField(max_length=255, blank=True)
    secretario = models.CharField(max_length=150, blank=True)
    pro_secretario = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['fecha', 'hora_salida']

    def __str__(self):
        return self.nombre


class Cuadrilla(models.Model):
    TIPOS = [
        ('regular', 'Regular'),
        ('honorarios', 'Hermanos Honorarios'),
        ('invitados', 'Invitados'),
        ('directorio_general', 'Directorio General'),
        ('capataces', 'Capataces'),
        ('dirigentes', 'Dirigentes'),
        ('adjuntos', 'Adjuntos'),
    ]

    id = models.CharField(max_length=20, primary_key=True, default=nuevo_id_cuadrilla, editable=False)
    recorrido = models.ForeignKey(Recorrido, on_delete=models.CASCADE, related_name='cuadrillas')
    numero = models.IntegerField()
    cuadrilla = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='regular')
    hermandad_invitada = models.CharField(max_length=200, blank=True)
    ubicacion = models.CharField(max_length=255, blank=True)
    punto_deja = models.CharField(max_length=255, blank=True)
    es_ultima = models.BooleanField(default=False)
    metraje = models.IntegerField(default=0)
    tiempo_estimado = models.IntegerField(default=0)
    hora_toma = models.TimeField(null=True, blank=True)
    hora_deja = models.TimeField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['numero']

    def __str__(self):
        return f'#{self.numero} {self.cuadrilla}'


class Homenaje(models.Model):
    PRIORIDADES = [('alta', 'Alta'), ('media', 'Media'), ('baja', 'Baja')]
    CARGOS = [('cuadrilla', 'Cuadrilla'), ('institucion', 'Institución')]

    id = models.CharField(max_length=20, primary_key=True, default=nuevo_id_homenaje, editable=False)
    recorrido = models.ForeignKey(Recorrido, on_delete=models.CASCADE, related_name='homenajes')
    numero_cuadrilla = models.IntegerField(null=True, blank=True)
    nombre = models.CharField(max_length=200)
    ubicacion = models.CharField(max_length=255, blank=True)
    tiempo_programado = models.IntegerField(default=10)
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    cargo_a = models.CharField(max_length=15, choices=CARGOS, default='cuadrilla')
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['numero_cuadrilla']

    def __str__(self):
        return self.nombre


class Evento(models.Model):
    TIPOS = [
        ('inicio_cuadrilla', 'Inicio cuadrilla'),
        ('fin_cuadrilla', 'Fin cuadrilla'),
        ('inicio_homenaje', 'Inicio homenaje'),
        ('fin_homenaje', 'Fin homenaje'),
        ('inicio_cambio', 'Inicio cambio'),
        ('fin_cambio', 'Fin cambio'),
        ('inicio_sector', 'Inicio sector'),
        ('fin_sector', 'Fin sector'),
        ('pausa_sector', 'Pausa sector'),
        ('observacion', 'Observación'),
    ]

    id = models.CharField(max_length=12, primary_key=True, default=nuevo_id_evento, editable=False)
    recorrido = models.ForeignKey(Recorrido, on_delete=models.CASCADE, related_name='eventos')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    referencia_id = models.CharField(max_length=20, blank=True, null=True)
    usuario = models.CharField(max_length=150, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    observacion = models.TextField(blank=True)
    sector_numero = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['fecha_hora']

    def __str__(self):
        return f'{self.tipo} · {self.fecha_hora:%Y-%m-%d %H:%M:%S}'
