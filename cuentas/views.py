from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import RegistroAuditoria, Usuario, registrar_auditoria
from .permisos import ROLES_PERMISOS, requiere_seccion, ruta_inicio


def login_view(request):
    error = None
    if request.method == 'POST':
        usuario = request.POST.get('usuario', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=usuario, password=password)
        if user is not None:
            auth_login(request, user)
            registrar_auditoria(request, 'login', 'sesion', detalle=f'Inicio de sesión: {usuario}')
            return redirect(ruta_inicio(user.rol))
        error = 'Usuario o contraseña incorrectos'
    return render(request, 'login.html', {'error': error})


def logout_view(request):
    if request.user.is_authenticated:
        registrar_auditoria(request, 'logout', 'sesion', detalle=f'Cierre de sesión: {request.user.username}')
    auth_logout(request)
    return redirect('login')


def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return redirect(ruta_inicio(request.user.rol))


@requiere_seccion('usuarios')
def usuarios(request):
    lista = [
        {'id': u.id, 'nombre': u.nombre, 'usuario': u.username, 'rol': u.rol}
        for u in Usuario.objects.all().order_by('nombre')
    ]
    return render(request, 'usuarios.html', {
        'usuarios': lista,
        'roles': list(ROLES_PERMISOS.keys()),
    })


@requiere_seccion('usuarios')
def nuevo_usuario(request):
    nombre = request.POST.get('nombre', '').strip()
    usuario_ = request.POST.get('usuario', '').strip()
    password = request.POST.get('password', '').strip()
    rol = request.POST.get('rol', '')
    if not nombre or not usuario_ or not password or rol not in ROLES_PERMISOS:
        messages.error(request, 'Todos los campos son obligatorios y el rol debe ser válido.')
        return redirect('usuarios')
    if rol == Usuario.ROL_SUPER_ADMIN and request.user.rol != Usuario.ROL_SUPER_ADMIN:
        messages.error(request, 'Solo un Super Admin puede asignar el rol de Super Admin.')
        return redirect('usuarios')
    if Usuario.objects.filter(username=usuario_).exists():
        messages.error(request, f'Ya existe un usuario con el nombre de acceso "{usuario_}".')
        return redirect('usuarios')
    nuevo = Usuario.objects.create_user(username=usuario_, password=password, nombre=nombre, rol=rol)
    registrar_auditoria(request, 'crear', 'usuario', nuevo.id, f'{usuario_} ({rol})')
    messages.success(request, f'Usuario "{usuario_}" creado correctamente.')
    return redirect('usuarios')


@requiere_seccion('usuarios')
def editar_usuario(request, uid):
    nombre = request.POST.get('nombre', '').strip()
    usuario_ = request.POST.get('usuario', '').strip()
    password = request.POST.get('password', '').strip()
    rol = request.POST.get('rol', '')
    if not nombre or not usuario_ or rol not in ROLES_PERMISOS:
        messages.error(request, 'Todos los campos son obligatorios y el rol debe ser válido.')
        return redirect('usuarios')
    if Usuario.objects.filter(username=usuario_).exclude(id=uid).exists():
        messages.error(request, f'Ya existe un usuario con el nombre de acceso "{usuario_}".')
        return redirect('usuarios')
    u = Usuario.objects.filter(id=uid).first()
    if u:
        u.nombre = nombre
        u.username = usuario_
        u.rol = rol
        if password:
            u.set_password(password)
        u.save()
        registrar_auditoria(request, 'editar', 'usuario', uid, f'{usuario_} ({rol})')
        if request.user.id == u.id:
            auth_login(request, u)  # refresca la sesión con los datos nuevos
    messages.success(request, 'Usuario actualizado correctamente.')
    return redirect('usuarios')


@requiere_seccion('usuarios')
def eliminar_usuario(request, uid):
    if str(uid) == str(request.user.id):
        messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('usuarios')
    objetivo = Usuario.objects.filter(id=uid).first()
    if objetivo and objetivo.rol == Usuario.ROL_SUPER_ADMIN:
        otros_admins = Usuario.objects.filter(rol=Usuario.ROL_SUPER_ADMIN).exclude(id=uid)
        if not otros_admins.exists():
            messages.error(request, 'No puedes eliminar al único Super Admin del sistema.')
            return redirect('usuarios')
    if objetivo:
        registrar_auditoria(request, 'eliminar', 'usuario', uid, objetivo.username)
        objetivo.delete()
    messages.success(request, 'Usuario eliminado.')
    return redirect('usuarios')


@requiere_seccion('auditoria')
def auditoria(request):
    registros = RegistroAuditoria.objects.all()
    usuario_f = request.GET.get('usuario', '').strip()
    accion_f = request.GET.get('accion', '').strip()
    entidad_f = request.GET.get('entidad', '').strip()
    desde_f = request.GET.get('desde', '').strip()
    hasta_f = request.GET.get('hasta', '').strip()
    if usuario_f:
        registros = registros.filter(usuario__icontains=usuario_f)
    if accion_f:
        registros = registros.filter(accion=accion_f)
    if entidad_f:
        registros = registros.filter(entidad=entidad_f)
    if desde_f:
        registros = registros.filter(fecha_hora__date__gte=desde_f)
    if hasta_f:
        registros = registros.filter(fecha_hora__date__lte=hasta_f)

    return render(request, 'auditoria.html', {
        'registros': registros[:500],
        'acciones': RegistroAuditoria.objects.order_by().values_list('accion', flat=True).distinct(),
        'entidades': RegistroAuditoria.objects.order_by().values_list('entidad', flat=True).distinct(),
        'filtros': {
            'usuario': usuario_f, 'accion': accion_f, 'entidad': entidad_f,
            'desde': desde_f, 'hasta': hasta_f,
        },
    })
