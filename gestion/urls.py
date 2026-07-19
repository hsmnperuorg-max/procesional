from django.urls import path

from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),

    path('recorridos', views.recorridos, name='recorridos'),
    path('recorridos/nuevo', views.nuevo_recorrido, name='nuevo_recorrido'),
    path('recorridos/editar/<str:rid>', views.editar_recorrido, name='editar_recorrido'),
    path('recorridos/eliminar/<str:rid>', views.eliminar_recorrido, name='eliminar_recorrido'),
    path('recorridos/trazar/<str:rid>', views.trazar_recorrido, name='trazar_recorrido'),

    path('cuadrillas', views.cuadrillas, name='cuadrillas'),
    path('cuadrillas/nueva', views.nueva_cuadrilla, name='nueva_cuadrilla'),
    path('cuadrillas/editar/<str:cid>', views.editar_cuadrilla, name='editar_cuadrilla'),
    path('cuadrillas/eliminar/<str:cid>', views.eliminar_cuadrilla, name='eliminar_cuadrilla'),

    path('homenajes', views.homenajes, name='homenajes'),
    path('homenajes/nuevo', views.nuevo_homenaje, name='nuevo_homenaje'),
    path('homenajes/editar/<str:hid>', views.editar_homenaje, name='editar_homenaje'),
    path('homenajes/eliminar/<str:hid>', views.eliminar_homenaje, name='eliminar_homenaje'),

    path('tablet', views.tablet, name='tablet'),

    path('mapa', views.mapa_view, name='mapa_view'),
    path('mapa/<str:rid>', views.mapa_view, name='mapa_view_rid'),

    path('reporte/marcaciones', views.reporte_marcaciones, name='reporte_marcaciones'),
    path('reporte/toma-y-deja/<str:rid>', views.reporte_toma_y_deja, name='reporte_toma_y_deja'),

    path('api/evento', views.api_evento, name='api_evento'),
    path('api/estado', views.api_estado, name='api_estado'),
    path('api/eventos_recientes', views.api_eventos_recientes, name='api_eventos_recientes'),
    path('api/reset', views.api_reset, name='api_reset'),
    path('api/posicion_mapa', views.api_posicion_mapa, name='api_posicion_mapa'),
    path('api/ruta/guardar', views.api_ruta_guardar, name='api_ruta_guardar'),
    path('api/ruta/<str:rid>', views.api_ruta, name='api_ruta'),
]
