from django.db import migrations


USUARIOS_DEMO = [
    {"usuario": "admin", "nombre": "Administrador General", "password": "admin123",
     "rol": "Super Admin", "is_staff": True, "is_superuser": True},
    {"usuario": "cronometro1", "nombre": "Juan Ríos", "password": "cron123",
     "rol": "Cronometrista"},
    {"usuario": "secretario1", "nombre": "Carlos Mendoza", "password": "sec123",
     "rol": "Pro Secretario"},
    {"usuario": "mayordomo1", "nombre": "Mayordomía", "password": "mayor123",
     "rol": "Mayordomía"},
]


def seed_usuarios(apps, schema_editor):
    Usuario = apps.get_model('cuentas', 'Usuario')
    from django.contrib.auth.hashers import make_password
    for u in USUARIOS_DEMO:
        if Usuario.objects.filter(username=u['usuario']).exists():
            continue
        Usuario.objects.create(
            username=u['usuario'],
            nombre=u['nombre'],
            rol=u['rol'],
            password=make_password(u['password']),
            is_staff=u.get('is_staff', False),
            is_superuser=u.get('is_superuser', False),
        )


def eliminar_usuarios(apps, schema_editor):
    Usuario = apps.get_model('cuentas', 'Usuario')
    Usuario.objects.filter(username__in=[u['usuario'] for u in USUARIOS_DEMO]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_usuarios, eliminar_usuarios),
    ]
