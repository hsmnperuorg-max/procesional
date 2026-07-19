from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('usuarios', views.usuarios, name='usuarios'),
    path('usuarios/nuevo', views.nuevo_usuario, name='nuevo_usuario'),
    path('usuarios/editar/<str:uid>', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<str:uid>', views.eliminar_usuario, name='eliminar_usuario'),
    path('auditoria', views.auditoria, name='auditoria'),
]
