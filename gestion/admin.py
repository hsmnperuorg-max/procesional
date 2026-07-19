from django.contrib import admin

from .models import Cuadrilla, Evento, Homenaje, Recorrido

admin.site.register(Recorrido)
admin.site.register(Cuadrilla)
admin.site.register(Homenaje)
admin.site.register(Evento)
