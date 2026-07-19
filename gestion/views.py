import json
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cuentas.models import registrar_auditoria
from cuentas.permisos import ROLES_ADMIN, requiere_seccion, requiere_seccion_api

from .constants import LISTA_CUADRILLAS
from .models import Cuadrilla, Evento, Homenaje, Recorrido


def _time_or_none(value):
    return value or None


# ── DASHBOARD ────────────────────────────
@requiere_seccion('dashboard')
def dashboard(request):
    recorridos = list(Recorrido.objects.all())
    rid = request.GET.get('rid') or (recorridos[0].id if recorridos else None)
    rec_actual = next((r for r in recorridos if r.id == rid), recorridos[0] if recorridos else None)
    cuadrillas = Cuadrilla.objects.filter(recorrido_id=rid).order_by('numero')
    homenajes = Homenaje.objects.filter(recorrido_id=rid).order_by('numero_cuadrilla')

    cuadrillas_map = {
        c.id: {'numero': c.numero, 'nombre': c.cuadrilla, 'estimado': c.tiempo_estimado}
        for c in cuadrillas
    }
    homenajes_map = {
        h.id: {'nombre': h.nombre, 'estimado': h.tiempo_programado}
        for h in homenajes
    }

    return render(request, 'dashboard.html', {
        'recorridos': recorridos,
        'recorrido_actual': rec_actual,
        'rid': rid,
        'hoy': date.today(),
        'cuadrillas': cuadrillas,
        'homenajes': homenajes,
        'cuadrillas_map': cuadrillas_map,
        'homenajes_map': homenajes_map,
    })


# ── RECORRIDOS ────────────────────────────
@requiere_seccion('recorridos')
def recorridos(request):
    recorridos_data = Recorrido.objects.annotate(
        n_cuadrillas=Count('cuadrillas', distinct=True),
        n_homenajes=Count('homenajes', distinct=True),
    )
    recorridos_js = [
        {k: v for k, v in {
            'id': r.id, 'nombre': r.nombre, 'fecha': r.fecha.isoformat(),
            'estado': r.estado, 'hora_salida': r.hora_salida.strftime('%H:%M') if r.hora_salida else '',
            'hora_llegada_programada': r.hora_llegada_programada.strftime('%H:%M') if r.hora_llegada_programada else '',
            'distancia_total': r.distancia_total, 'punto_inicio': r.punto_inicio,
            'secretario': r.secretario, 'pro_secretario': r.pro_secretario,
            'observaciones': r.observaciones,
        }.items()}
        for r in recorridos_data
    ]
    return render(request, 'recorridos.html', {
        'recorridos': recorridos_data,
        'recorridos_js': recorridos_js,
    })


@requiere_seccion('recorridos')
@require_POST
def editar_recorrido(request, rid):
    r = get_object_or_404(Recorrido, id=rid)
    r.nombre = request.POST.get('nombre', r.nombre)
    r.fecha = request.POST.get('fecha') or r.fecha
    r.hora_salida = _time_or_none(request.POST.get('hora_salida'))
    r.hora_llegada_programada = _time_or_none(request.POST.get('hora_llegada'))
    r.distancia_total = int(request.POST.get('distancia', 0) or 0)
    r.observaciones = request.POST.get('observaciones', '')
    r.estado = request.POST.get('estado', 'programado')
    r.punto_inicio = request.POST.get('punto_inicio', '')
    r.secretario = request.POST.get('secretario', '')
    r.pro_secretario = request.POST.get('pro_secretario', '')
    r.save()
    registrar_auditoria(request, 'editar', 'recorrido', rid, r.nombre)
    return redirect('recorridos')


@requiere_seccion('recorridos')
@require_POST
def eliminar_recorrido(request, rid):
    if request.user.rol not in ROLES_ADMIN:
        return redirect('recorridos')
    Recorrido.objects.filter(id=rid).delete()
    registrar_auditoria(request, 'eliminar', 'recorrido', rid)
    return redirect('recorridos')


@requiere_seccion('recorridos')
def nuevo_recorrido(request):
    if request.method == 'POST':
        r = Recorrido.objects.create(
            nombre=request.POST.get('nombre'),
            fecha=request.POST.get('fecha'),
            hora_salida=_time_or_none(request.POST.get('hora_salida')),
            hora_llegada_programada=_time_or_none(request.POST.get('hora_llegada')),
            distancia_total=int(request.POST.get('distancia', 0) or 0),
            observaciones=request.POST.get('observaciones', ''),
        )
        registrar_auditoria(request, 'crear', 'recorrido', r.id, r.nombre)
        return redirect('recorridos')
    return render(request, 'nuevo_recorrido.html')


# ── CUADRILLAS ────────────────────────────
@requiere_seccion('cuadrillas')
def cuadrillas(request):
    cuas = Cuadrilla.objects.select_related('recorrido').all()
    recorridos_data = Recorrido.objects.all()
    rutas = {r.id: r.ruta_coords for r in recorridos_data}
    cuas_json = [{
        'id': c.id, 'recorrido_id': c.recorrido_id, 'numero': c.numero, 'cuadrilla': c.cuadrilla,
        'tipo': c.tipo, 'hermandad_invitada': c.hermandad_invitada, 'ubicacion': c.ubicacion,
        'punto_deja': c.punto_deja, 'es_ultima': c.es_ultima, 'metraje': c.metraje,
        'tiempo_estimado': c.tiempo_estimado,
        'hora_toma': c.hora_toma.strftime('%H:%M') if c.hora_toma else '',
        'hora_deja': c.hora_deja.strftime('%H:%M') if c.hora_deja else '',
        'lat': c.lat, 'lng': c.lng,
    } for c in cuas]
    metraje_total = sum(c.metraje for c in cuas)
    con_pos_count = sum(1 for c in cuas if c.lat)

    return render(request, 'cuadrillas.html', {
        'cuadrillas': cuas,
        'cuadrillas_json': cuas_json,
        'recorridos': recorridos_data,
        'lista_cuadrillas': LISTA_CUADRILLAS,
        'rutas_json': rutas,
        'metraje_total': metraje_total,
        'con_pos_count': con_pos_count,
    })


def _cuadrilla_form_kwargs(request):
    tipo = request.POST.get('tipo', 'regular')
    hermandad = request.POST.get('hermandad_invitada', '') if tipo == 'invitados' else ''
    lat_raw = request.POST.get('lat', '').strip()
    lng_raw = request.POST.get('lng', '').strip()
    return dict(
        recorrido_id=request.POST.get('recorrido_id'),
        numero=int(request.POST.get('numero', 1) or 1),
        cuadrilla=request.POST.get('cuadrilla'),
        tipo=tipo,
        hermandad_invitada=hermandad,
        ubicacion=request.POST.get('ubicacion', ''),
        punto_deja=request.POST.get('punto_deja', ''),
        es_ultima=request.POST.get('es_ultima') == '1',
        metraje=int(request.POST.get('metraje', 0) or 0),
        tiempo_estimado=int(request.POST.get('tiempo_estimado', 0) or 0),
        hora_toma=_time_or_none(request.POST.get('hora_toma')),
        hora_deja=_time_or_none(request.POST.get('hora_deja')),
        lat=float(lat_raw) if lat_raw else None,
        lng=float(lng_raw) if lng_raw else None,
    )


@requiere_seccion('cuadrillas')
@require_POST
def nueva_cuadrilla(request):
    c = Cuadrilla.objects.create(**_cuadrilla_form_kwargs(request))
    registrar_auditoria(request, 'crear', 'cuadrilla', c.id, c.cuadrilla)
    return redirect('cuadrillas')


@requiere_seccion('cuadrillas')
@require_POST
def editar_cuadrilla(request, cid):
    c = get_object_or_404(Cuadrilla, id=cid)
    for k, v in _cuadrilla_form_kwargs(request).items():
        setattr(c, k, v)
    c.save()
    registrar_auditoria(request, 'editar', 'cuadrilla', cid, c.cuadrilla)
    return redirect('cuadrillas')


@requiere_seccion('cuadrillas')
@require_POST
def eliminar_cuadrilla(request, cid):
    Cuadrilla.objects.filter(id=cid).delete()
    registrar_auditoria(request, 'eliminar', 'cuadrilla', cid)
    return redirect('cuadrillas')


# ── HOMENAJES ────────────────────────────
@requiere_seccion('homenajes')
def homenajes(request):
    homs = Homenaje.objects.all()
    total_tiempo = sum(h.tiempo_programado for h in homs)
    homs_json = [{
        'id': h.id, 'recorrido_id': h.recorrido_id, 'numero_cuadrilla': h.numero_cuadrilla,
        'nombre': h.nombre, 'ubicacion': h.ubicacion, 'tiempo_programado': h.tiempo_programado,
        'prioridad': h.prioridad, 'cargo_a': h.cargo_a, 'observaciones': h.observaciones,
    } for h in homs]
    return render(request, 'homenajes.html', {
        'homenajes': homs,
        'homenajes_json': homs_json,
        'recorridos': Recorrido.objects.all(),
        'total_tiempo': total_tiempo,
    })


def _homenaje_form_kwargs(request):
    nc_raw = request.POST.get('numero_cuadrilla', '').strip()
    return dict(
        recorrido_id=request.POST.get('recorrido_id'),
        numero_cuadrilla=int(nc_raw) if nc_raw else None,
        nombre=request.POST.get('nombre'),
        ubicacion=request.POST.get('ubicacion', ''),
        tiempo_programado=int(request.POST.get('tiempo_programado', 10) or 10),
        prioridad=request.POST.get('prioridad', 'media'),
        cargo_a=request.POST.get('cargo_a', 'cuadrilla'),
        observaciones=request.POST.get('observaciones', ''),
    )


@requiere_seccion('homenajes')
@require_POST
def nuevo_homenaje(request):
    h = Homenaje.objects.create(**_homenaje_form_kwargs(request))
    registrar_auditoria(request, 'crear', 'homenaje', h.id, h.nombre)
    return redirect('homenajes')


@requiere_seccion('homenajes')
@require_POST
def editar_homenaje(request, hid):
    h = get_object_or_404(Homenaje, id=hid)
    for k, v in _homenaje_form_kwargs(request).items():
        setattr(h, k, v)
    h.save()
    registrar_auditoria(request, 'editar', 'homenaje', hid, h.nombre)
    return redirect('homenajes')


@requiere_seccion('homenajes')
@require_POST
def eliminar_homenaje(request, hid):
    Homenaje.objects.filter(id=hid).delete()
    registrar_auditoria(request, 'eliminar', 'homenaje', hid)
    return redirect('homenajes')


# ── TABLET ────────────────────────────────
@requiere_seccion('tablet')
def tablet(request):
    cuas = Cuadrilla.objects.all()
    homs = Homenaje.objects.all()
    cuas_json = [{'id': c.id, 'recorrido_id': c.recorrido_id, 'numero': c.numero,
                  'cuadrilla': c.cuadrilla, 'hora_toma': c.hora_toma.strftime('%H:%M') if c.hora_toma else '',
                  'hora_deja': c.hora_deja.strftime('%H:%M') if c.hora_deja else '',
                  'tiempo_estimado': c.tiempo_estimado} for c in cuas]
    homs_json = [{'id': h.id, 'recorrido_id': h.recorrido_id, 'nombre': h.nombre,
                  'tiempo_programado': h.tiempo_programado} for h in homs]
    return render(request, 'tablet.html', {
        'recorridos': Recorrido.objects.all(),
        'cuadrillas_json': cuas_json,
        'homenajes_json': homs_json,
        'hoy': date.today(),
    })


@requiere_seccion_api('tablet')
@require_POST
def api_evento(request):
    body = json.loads(request.body or '{}')
    rid = body.get('recorrido_id')
    recorrido = get_object_or_404(Recorrido, id=rid)
    tipo = body.get('tipo')
    referencia_id = body.get('referencia_id') or None

    sector_numero = None
    if tipo == 'inicio_sector':
        qs = Evento.objects.filter(tipo='inicio_sector', recorrido=recorrido)
        if referencia_id:
            qs = qs.filter(referencia_id=referencia_id)
        sector_numero = qs.count() + 1

    lat_raw, lng_raw = body.get('lat'), body.get('lng')
    evento = Evento.objects.create(
        recorrido=recorrido,
        tipo=tipo,
        referencia_id=referencia_id,
        usuario=request.user.nombre,
        lat=float(lat_raw) if lat_raw not in (None, '') else None,
        lng=float(lng_raw) if lng_raw not in (None, '') else None,
        observacion=body.get('observacion', ''),
        sector_numero=sector_numero,
    )
    return JsonResponse({'ok': True, 'evento': {
        'id': evento.id, 'tipo': evento.tipo, 'referencia_id': evento.referencia_id,
        'fecha_hora': evento.fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
        'observacion': evento.observacion,
    }})


# ── API ESTADO ────────────────────────────
def api_estado(request):
    rid = request.GET.get('rid')
    rec = Recorrido.objects.filter(id=rid).first()
    eventos = list(Evento.objects.filter(recorrido_id=rid).order_by('fecha_hora'))
    cuas = list(Cuadrilla.objects.filter(recorrido_id=rid))
    homs = list(Homenaje.objects.filter(recorrido_id=rid))

    cuadrilla_activa = None
    homenaje_activo = None
    inicio_cuadrilla_dt = None
    inicio_homenaje_dt = None
    cuadrillas_completadas = []
    tiempos_cuadrilla = []
    tiempos_homenaje = []

    for e in eventos:
        if e.tipo == 'inicio_cuadrilla':
            cuadrilla_activa = e.referencia_id
            inicio_cuadrilla_dt = e.fecha_hora
        elif e.tipo == 'fin_cuadrilla' and cuadrilla_activa:
            c = next((c for c in cuas if c.id == cuadrilla_activa), None)
            if c:
                dur_real = int((e.fecha_hora - inicio_cuadrilla_dt).total_seconds() / 60)
                tiempos_cuadrilla.append({
                    'id': c.id, 'cuadrilla': c.cuadrilla, 'numero': c.numero,
                    'tipo': c.tipo, 'hermandad_invitada': c.hermandad_invitada,
                    'estimado': c.tiempo_estimado, 'real': dur_real,
                    'diferencia': dur_real - c.tiempo_estimado,
                })
            cuadrillas_completadas.append(cuadrilla_activa)
            cuadrilla_activa = None
        elif e.tipo == 'inicio_homenaje':
            homenaje_activo = e.referencia_id
            inicio_homenaje_dt = e.fecha_hora
        elif e.tipo == 'fin_homenaje' and homenaje_activo:
            h = next((h for h in homs if h.id == homenaje_activo), None)
            if h:
                dur_real = int((e.fecha_hora - inicio_homenaje_dt).total_seconds() / 60)
                tiempos_homenaje.append({
                    'id': h.id, 'nombre': h.nombre, 'ubicacion': h.ubicacion,
                    'numero_cuadrilla': h.numero_cuadrilla, 'cargo_a': h.cargo_a,
                    'estimado': h.tiempo_programado, 'real': dur_real,
                    'diferencia': dur_real - h.tiempo_programado,
                })
            homenaje_activo = None

    atraso_institucional = 0
    for t in tiempos_homenaje:
        if t['cargo_a'] == 'institucion':
            atraso_institucional += t['diferencia']
            nc = t.get('numero_cuadrilla')
            if nc:
                for tc in tiempos_cuadrilla:
                    if tc['numero'] == nc:
                        tc['real'] -= t['real']
                        tc['diferencia'] -= t['real']
                        break

    completadas_obj = [c for c in cuas if c.id in cuadrillas_completadas]
    metros_recorridos = sum(c.metraje for c in completadas_obj)
    metros_totales = sum(c.metraje for c in cuas)
    atraso_total = sum(t['diferencia'] for t in tiempos_cuadrilla) + atraso_institucional

    fecha_rec = rec.fecha if rec else date.today()
    hora_llegada = rec.hora_llegada_programada if (rec and rec.hora_llegada_programada) else None
    if hora_llegada:
        hora_llegada_prog = datetime.combine(fecha_rec, hora_llegada)
        eta = hora_llegada_prog + timedelta(minutes=atraso_total)
        eta_str, hora_llegada_str = eta.strftime('%H:%M'), hora_llegada.strftime('%H:%M')
    else:
        eta_str, hora_llegada_str = '–', '–'

    cuadrilla_activa_obj = next((c for c in cuas if c.id == cuadrilla_activa), None)
    homenaje_activo_obj = next((h for h in homs if h.id == homenaje_activo), None)

    return JsonResponse({
        'cuadrilla_activa': {'id': cuadrilla_activa_obj.id, 'numero': cuadrilla_activa_obj.numero,
                              'cuadrilla': cuadrilla_activa_obj.cuadrilla} if cuadrilla_activa_obj else None,
        'cuadrilla_activa_inicio': inicio_cuadrilla_dt.strftime('%Y-%m-%d %H:%M:%S') if cuadrilla_activa_obj and inicio_cuadrilla_dt else None,
        'homenaje_activo': {'id': homenaje_activo_obj.id, 'nombre': homenaje_activo_obj.nombre} if homenaje_activo_obj else None,
        'metros_recorridos': metros_recorridos,
        'metros_totales': metros_totales,
        'porcentaje': round(metros_recorridos / metros_totales * 100, 1) if metros_totales else 0,
        'atraso_minutos': atraso_total,
        'atraso_institucional': atraso_institucional,
        'eta': eta_str,
        'cuadrillas_completadas': len(cuadrillas_completadas),
        'total_cuadrillas': len(cuas),
        'cuadrillas_completadas_ids': cuadrillas_completadas,
        'tiempos_cuadrilla': tiempos_cuadrilla,
        'tiempos_homenaje': tiempos_homenaje,
        'total_eventos': len(eventos),
        'hora_llegada_prog': hora_llegada_str,
    })


def api_eventos_recientes(request):
    rid = request.GET.get('rid')
    eventos = Evento.objects.filter(recorrido_id=rid).order_by('fecha_hora')[:15]
    return JsonResponse([{
        'fecha_hora': e.fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
        'tipo': e.tipo, 'usuario': e.usuario, 'observacion': e.observacion,
    } for e in eventos], safe=False)


@requiere_seccion_api('dashboard')
@require_POST
def api_reset(request):
    rid = request.GET.get('rid') or request.POST.get('rid')
    qs = Evento.objects.filter(recorrido_id=rid) if rid else Evento.objects.all()
    qs.delete()
    return JsonResponse({'ok': True})


# ── MAPA ──────────────────────────────────
@requiere_seccion('mapa')
def mapa_view(request, rid=None):
    recorridos_data = Recorrido.objects.all()
    if rid is None:
        rid = recorridos_data[0].id if recorridos_data else None
    rec = next((r for r in recorridos_data if r.id == rid), None)
    return render(request, 'mapa.html', {'recorrido': rec, 'recorridos': recorridos_data})


@requiere_seccion('recorridos')
def trazar_recorrido(request, rid):
    rec = get_object_or_404(Recorrido, id=rid)
    cuas = Cuadrilla.objects.filter(recorrido_id=rid).order_by('numero')
    cuas_json = [{'id': c.id, 'numero': c.numero, 'cuadrilla': c.cuadrilla, 'lat': c.lat, 'lng': c.lng} for c in cuas]
    return render(request, 'trazador.html', {'recorrido': rec, 'cuadrillas_json': cuas_json})


@requiere_seccion_api('recorridos')
@require_POST
def api_ruta_guardar(request):
    body = json.loads(request.body or '{}')
    rid = body.get('rid')
    coords = body.get('coords', [])
    rec = get_object_or_404(Recorrido, id=rid)
    rec.ruta_coords = coords
    rec.save(update_fields=['ruta_coords'])
    return JsonResponse({'ok': True, 'puntos': len(coords)})


def api_ruta(request, rid):
    cuas = Cuadrilla.objects.filter(recorrido_id=rid, lat__isnull=False, lng__isnull=False).order_by('numero')
    return JsonResponse({
        'rid': rid,
        'waypoints': [{'id': c.id, 'numero': c.numero, 'nombre': c.cuadrilla, 'lat': c.lat, 'lng': c.lng} for c in cuas],
    })


def api_posicion_mapa(request):
    rid = request.GET.get('rid')
    rec = Recorrido.objects.filter(id=rid).first()
    ruta_coords = rec.ruta_coords if rec else []
    cuas = list(Cuadrilla.objects.filter(recorrido_id=rid).order_by('numero'))
    eventos = Evento.objects.filter(recorrido_id=rid).order_by('fecha_hora')
    total = len(cuas)

    activa_id = None
    completadas = []
    for e in eventos:
        if e.tipo == 'inicio_cuadrilla':
            activa_id = e.referencia_id
        elif e.tipo == 'fin_cuadrilla' and activa_id:
            completadas.append(activa_id)
            activa_id = None

    n_completadas = len([c for c in cuas if c.id in completadas])
    n_ruta = len(ruta_coords)

    def closest_idx(lat, lng):
        best, best_d = 0, float('inf')
        for i, pt in enumerate(ruta_coords):
            d = (pt[0] - lat) ** 2 + (pt[1] - lng) ** 2
            if d < best_d:
                best_d, best = d, i
        return best

    segments = []
    for c in cuas:
        route_index = None
        if c.lat and c.lng and n_ruta > 1:
            route_index = closest_idx(c.lat, c.lng)
        segments.append({
            'id': c.id, 'numero': c.numero, 'nombre': c.cuadrilla,
            'lat': c.lat, 'lng': c.lng,
            'completada': c.id in completadas, 'activa': c.id == activa_id,
            'route_index': route_index,
        })

    fill_index = 0
    for seg in segments:
        if seg['completada'] and seg['route_index'] is not None:
            fill_index = seg['route_index']
    if fill_index == 0 and n_completadas > 0 and n_ruta > 1 and total > 0:
        fill_index = min(round(n_completadas / total * (n_ruta - 1)), n_ruta - 1)

    activa_obj = next((c for c in cuas if c.id == activa_id), None)

    return JsonResponse({
        'rid': rid, 'ruta_coords': ruta_coords, 'fill_index': fill_index,
        'total': total, 'n_completadas': n_completadas, 'activa_id': activa_id,
        'activa_nombre': activa_obj.cuadrilla if activa_obj else None,
        'segments': segments, 'tiene_ruta': n_ruta > 1,
    })


# ── REPORTES ──────────────────────────────
@requiere_seccion('reportes')
def reporte_toma_y_deja(request, rid):
    rec = get_object_or_404(Recorrido, id=rid)
    cuas = list(Cuadrilla.objects.filter(recorrido_id=rid).order_by('numero'))
    homs_all = list(Homenaje.objects.filter(recorrido_id=rid))
    homs_por_cuadrilla = {}
    for h in homs_all:
        if h.numero_cuadrilla:
            homs_por_cuadrilla.setdefault(int(h.numero_cuadrilla), []).append(h)

    filas = []
    for i, c in enumerate(cuas):
        punto_toma = rec.punto_inicio or 'Inicio del Recorrido Procesional' if i == 0 else (c.ubicacion or '—')
        next_c = cuas[i + 1] if i + 1 < len(cuas) else None
        if c.es_ultima and c.punto_deja:
            punto_deja = c.punto_deja
        elif next_c and next_c.ubicacion:
            punto_deja = next_c.ubicacion
        else:
            punto_deja = '—'
        homs_cua = homs_por_cuadrilla.get(c.numero, [])
        filas.append({
            'c': c, 'punto_toma': punto_toma, 'punto_deja': punto_deja,
            'total_hom': sum(h.tiempo_programado for h in homs_cua),
        })

    metraje_prom = int(sum(c.metraje for c in cuas) / len(cuas)) if cuas else 0

    return render(request, 'reporte_toma_y_deja.html', {
        'recorrido': rec, 'filas': filas, 'homenajes': homs_all,
        'metraje_prom': metraje_prom,
        'total_hom_tiempo': sum(h.tiempo_programado for h in homs_all),
    })


@requiere_seccion('reportes')
def reporte_marcaciones(request):
    cuas_all = Cuadrilla.objects.all()
    homs_all = Homenaje.objects.all()
    eventos = Evento.objects.order_by('fecha_hora')

    cua_idx = {c.id: c for c in cuas_all}
    hom_idx = {h.id: h for h in homs_all}

    PARES = {
        'inicio_cuadrilla': 'fin_cuadrilla',
        'inicio_homenaje': 'fin_homenaje',
        'inicio_cambio': 'fin_cambio',
        'inicio_sector': 'fin_sector',
    }
    # Los pendientes se guardan por (tipo_fin, referencia_id) para no cruzar
    # eventos de cuadrillas/homenajes distintos que se solapen en el tiempo.
    pendientes = {}
    registros = []
    eventos_list = list(eventos)

    for e in eventos_list:
        tipo = e.tipo
        if tipo in PARES:
            fin_tipo = PARES[tipo]
            pendientes[(fin_tipo, e.referencia_id)] = e
        elif tipo in PARES.values():
            clave = (tipo, e.referencia_id)
            inicio_e = pendientes.pop(clave, None)
            if inicio_e is None:
                # Compatibilidad: si no hay referencia (cambios sin cuadrilla), usar la más antigua sin ref.
                inicio_e = pendientes.pop((tipo, None), None)
            duracion = None
            if inicio_e:
                duracion = int((e.fecha_hora - inicio_e.fecha_hora).total_seconds() // 60)
            ref_id = e.referencia_id or (inicio_e.referencia_id if inicio_e else None)
            ref_name = ''
            estimado = None
            if ref_id in cua_idx:
                ref_name = f'#{cua_idx[ref_id].numero} — {cua_idx[ref_id].cuadrilla}'
                estimado = cua_idx[ref_id].tiempo_estimado
            elif ref_id in hom_idx:
                ref_name = hom_idx[ref_id].nombre
                estimado = hom_idx[ref_id].tiempo_programado
            sector_num = inicio_e.sector_numero if inicio_e else None
            cua_nombre = cua_numero = None
            if tipo == 'fin_sector':
                if ref_id in cua_idx:
                    cua_nombre, cua_numero = cua_idx[ref_id].cuadrilla, cua_idx[ref_id].numero
                    ref_name = f'Sector {sector_num}' if sector_num else 'Sector –'
                elif sector_num:
                    ref_name = f'Sector {sector_num}'
            diferencia = (duracion - estimado) if (duracion is not None and estimado) else None
            registros.append({
                'tipo': tipo,
                'hora_inicio': inicio_e.fecha_hora.strftime('%H:%M') if inicio_e else '–',
                'hora_fin': e.fecha_hora.strftime('%H:%M'),
                'duracion': duracion, 'ref_id': ref_id, 'ref_nombre': ref_name,
                'usuario': e.usuario, 'observacion': e.observacion,
                'sector_numero': sector_num, 'cua_nombre': cua_nombre, 'cua_numero': cua_numero,
                'estimado': estimado, 'diferencia': diferencia,
            })
        elif tipo == 'observacion':
            registros.append({
                'tipo': 'observacion', 'hora_inicio': e.fecha_hora.strftime('%H:%M'),
                'hora_fin': None, 'duracion': None, 'ref_id': None, 'ref_nombre': '',
                'usuario': e.usuario, 'observacion': e.observacion,
            })
        elif tipo == 'pausa_sector':
            ref_id = e.referencia_id
            ref_name = ''
            if ref_id in cua_idx:
                ref_name = f'#{cua_idx[ref_id].numero} — {cua_idx[ref_id].cuadrilla}'
            registros.append({
                'tipo': 'pausa_sector', 'hora_inicio': e.fecha_hora.strftime('%H:%M'),
                'hora_fin': None, 'duracion': None, 'ref_id': ref_id, 'ref_nombre': ref_name,
                'usuario': e.usuario, 'observacion': e.observacion,
            })

    TIPO_BADGE = {
        'inicio_cuadrilla': ('tb-cua', '▶ Inicio Cua.'), 'fin_cuadrilla': ('tb-cua', '⏹ Fin Cua.'),
        'inicio_homenaje': ('tb-hom', '🙏 Inicio Hom.'), 'fin_homenaje': ('tb-hom', '✓ Fin Hom.'),
        'inicio_cambio': ('tb-cam', '🔄 Inicio Cambio'), 'fin_cambio': ('tb-cam', '✓ Fin Cambio'),
        'inicio_sector': ('tb-sec', '📍 Inicio Sector'), 'fin_sector': ('tb-sec', '🏁 Fin Sector'),
        'pausa_sector': ('tb-pausa', '⏸ Pausa Sector'),
    }
    eventos_view = []
    for e in eventos_list:
        if e.referencia_id in cua_idx:
            ref_label = f'Cua. {cua_idx[e.referencia_id].numero} – {cua_idx[e.referencia_id].cuadrilla}'
        elif e.referencia_id in hom_idx:
            ref_label = hom_idx[e.referencia_id].nombre
        elif e.sector_numero:
            ref_label = f'Sector {e.sector_numero}'
        else:
            ref_label = e.referencia_id or '–'
        badge_class, badge_label = TIPO_BADGE.get(e.tipo, ('tb-obs', f'📝 {e.tipo}'))
        eventos_view.append({
            'fecha_hora': e.fecha_hora, 'ref_label': ref_label, 'usuario': e.usuario,
            'observacion': e.observacion, 'badge_class': badge_class, 'badge_label': badge_label,
        })

    return render(request, 'reporte_marcaciones.html', {
        'eventos': eventos_list, 'eventos_view': eventos_view, 'registros': registros,
        'n_cua': sum(1 for r in registros if r['tipo'] == 'fin_cuadrilla'),
        'n_hom': sum(1 for r in registros if r['tipo'] == 'fin_homenaje'),
        'n_cam': sum(1 for r in registros if r['tipo'] == 'fin_cambio'),
        'n_sec': sum(1 for r in registros if r['tipo'] == 'fin_sector'),
        'n_obs': sum(1 for e in eventos_list if e.tipo == 'observacion'),
        'n_pausas': sum(1 for e in eventos_list if e.tipo == 'pausa_sector'),
        'reg_cua': [r for r in registros if r['tipo'] == 'fin_cuadrilla'],
        'reg_hom': [r for r in registros if r['tipo'] == 'fin_homenaje'],
        'reg_cam': [r for r in registros if r['tipo'] == 'fin_cambio'],
        'reg_sec': [r for r in registros if r['tipo'] == 'fin_sector'],
        'reg_obs': [r for r in registros if r['tipo'] == 'observacion'],
        'reg_pausas': [r for r in registros if r['tipo'] == 'pausa_sector'],
    })
