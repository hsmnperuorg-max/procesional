from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Extiende el usuario de Django: `username`/`password` cumplen el rol de
    login que en el sistema original se llamaba `usuario`; se agrega `nombre`
    (nombre completo a mostrar) y `rol` (perfil de permisos)."""

    ROL_SUPER_ADMIN = 'Super Admin'
    ROL_MAYORDOMIA = 'Mayordomía'
    ROL_PRO_SECRETARIO = 'Pro Secretario'
    ROL_CRONOMETRISTA = 'Cronometrista'
    ROL_GESTOR_USUARIOS = 'Gestor de Usuarios'
    ROLES = [
        (ROL_SUPER_ADMIN, ROL_SUPER_ADMIN),
        (ROL_MAYORDOMIA, ROL_MAYORDOMIA),
        (ROL_PRO_SECRETARIO, ROL_PRO_SECRETARIO),
        (ROL_CRONOMETRISTA, ROL_CRONOMETRISTA),
        (ROL_GESTOR_USUARIOS, ROL_GESTOR_USUARIOS),
    ]

    nombre = models.CharField(max_length=150)
    rol = models.CharField(max_length=30, choices=ROLES)

    def __str__(self):
        return f'{self.nombre} ({self.rol})'


class RegistroAuditoria(models.Model):
    usuario = models.CharField(max_length=150)
    rol = models.CharField(max_length=30, blank=True)
    accion = models.CharField(max_length=20)      # crear | editar | eliminar | login | logout
    entidad = models.CharField(max_length=30)      # recorrido | cuadrilla | homenaje | usuario | sesion
    entidad_id = models.CharField(max_length=40, blank=True)
    detalle = models.CharField(max_length=255, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_hora']

    def __str__(self):
        return f'{self.fecha_hora:%Y-%m-%d %H:%M} · {self.usuario} · {self.accion} {self.entidad}'


def registrar_auditoria(request, accion, entidad, entidad_id='', detalle=''):
    """Deja constancia de una acción administrativa (alta/baja/edición/sesión)."""
    if not request.user.is_authenticated:
        return
    RegistroAuditoria.objects.create(
        usuario=request.user.nombre,
        rol=request.user.rol,
        accion=accion,
        entidad=entidad,
        entidad_id=str(entidad_id or ''),
        detalle=detalle,
    )
