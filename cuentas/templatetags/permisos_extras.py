import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe

from cuentas.permisos import tiene_acceso as _tiene_acceso

register = template.Library()


@register.filter(name='tiene_acceso')
def tiene_acceso(rol, seccion):
    return _tiene_acceso(rol, seccion)


@register.filter(name='tojson')
def tojson(value):
    return mark_safe(json.dumps(value, cls=DjangoJSONEncoder))
