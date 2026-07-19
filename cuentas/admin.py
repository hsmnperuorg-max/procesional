from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import RegistroAuditoria, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil del sistema', {'fields': ('nombre', 'rol')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Perfil del sistema', {'fields': ('nombre', 'rol')}),
    )
    list_display = ('username', 'nombre', 'rol', 'is_active')


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'usuario', 'rol', 'accion', 'entidad', 'entidad_id')
    list_filter = ('accion', 'entidad', 'rol')
    search_fields = ('usuario', 'detalle', 'entidad_id')
