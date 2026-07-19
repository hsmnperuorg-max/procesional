from functools import wraps

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

# Cada rol tiene acceso a un conjunto de "secciones" del sistema.
ROLES_PERMISOS = {
    'Super Admin':        ['dashboard', 'recorridos', 'cuadrillas', 'homenajes', 'mapa', 'reportes', 'tablet', 'usuarios', 'auditoria'],
    'Mayordomía':         ['dashboard', 'mapa'],
    'Pro Secretario':     ['recorridos', 'cuadrillas', 'homenajes'],
    'Cronometrista':      ['tablet', 'reportes'],
    'Gestor de Usuarios': ['usuarios'],
}

ROLES_ADMIN = ['Super Admin']

# Endpoint (name de urls.py) al que se redirige por defecto para cada sección
SECCION_ENDPOINT = {
    'dashboard':  'dashboard',
    'recorridos': 'recorridos',
    'cuadrillas': 'cuadrillas',
    'homenajes':  'homenajes',
    'mapa':       'mapa_view',
    'reportes':   'reporte_marcaciones',
    'tablet':     'tablet',
    'usuarios':   'usuarios',
    'auditoria':  'auditoria',
}


def tiene_acceso(rol, seccion):
    return seccion in ROLES_PERMISOS.get(rol, [])


def ruta_inicio(rol):
    permitidas = ROLES_PERMISOS.get(rol, [])
    if not permitidas:
        return reverse('login')
    return reverse(SECCION_ENDPOINT[permitidas[0]])


def requiere_seccion(seccion):
    """Protege una página: exige login y que el rol tenga acceso a la sección."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if not tiene_acceso(request.user.rol, seccion):
                messages.error(request, 'No tienes permiso para acceder a esa sección.')
                return redirect(ruta_inicio(request.user.rol))
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def requiere_seccion_api(seccion):
    """Protege un endpoint JSON: exige login y acceso a la sección, sin redirigir."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'No autorizado'}, status=401)
            if not tiene_acceso(request.user.rol, seccion):
                return JsonResponse({'error': 'Permiso denegado'}, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
