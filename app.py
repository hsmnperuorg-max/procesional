from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime, timedelta
import json, os, uuid

app = Flask(__name__)
app.secret_key = 'hermandad-nazarenas-2024'

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_data(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_posicion():
    path = os.path.join(DATA_DIR, 'posicion.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_posicion(data):
    path = os.path.join(DATA_DIR, 'posicion.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Waypoints de los recorridos (coordenadas Lima Centro, aproximadas)
WAYPOINTS_RECORRIDOS = {
    "rec-001": [
        {"lat": -12.0358, "lng": -77.0245, "nombre": "Inicio – Santuario del Carmen"},
        {"lat": -12.0358, "lng": -77.0285, "nombre": "Jr. Huánuco (tramo medio)"},
        {"lat": -12.0358, "lng": -77.0340, "nombre": "Jr. Huánuco / Av. Abancay"},
        {"lat": -12.0390, "lng": -77.0258, "nombre": "Av. Miguel Grau"},
        {"lat": -12.0415, "lng": -77.0268, "nombre": "Av. Miguel Grau / Av. Nicolás de Piérola"},
        {"lat": -12.0435, "lng": -77.0295, "nombre": "Av. Nicolás de Piérola"},
        {"lat": -12.0445, "lng": -77.0315, "nombre": "Jr. Andahuaylas"},
        {"lat": -12.0445, "lng": -77.0335, "nombre": "Jr. Andahuaylas / Jr. Inambari"},
        {"lat": -12.0464, "lng": -77.0310, "nombre": "Jr. Inambari"},
        {"lat": -12.0480, "lng": -77.0292, "nombre": "Av. Abancay"},
        {"lat": -12.0506, "lng": -77.0292, "nombre": "Av. Abancay / Jr. Leticia"},
        {"lat": -12.0510, "lng": -77.0306, "nombre": "Jr. Leticia"},
        {"lat": -12.0522, "lng": -77.0318, "nombre": "Jr. Miguel Aljovin"},
        {"lat": -12.0535, "lng": -77.0320, "nombre": "Av. Paseo de la República"},
        {"lat": -12.0540, "lng": -77.0345, "nombre": "Jr. Carabaya"},
        {"lat": -12.0548, "lng": -77.0365, "nombre": "Plaza San Martín"},
        {"lat": -12.0558, "lng": -77.0395, "nombre": "Av. Nicolás de Piérola (oeste)"},
        {"lat": -12.0558, "lng": -77.0415, "nombre": "Av. Nicolás de Piérola / Av. Tacna"},
        {"lat": -12.0510, "lng": -77.0385, "nombre": "Av. Tacna (subiendo)"},
        {"lat": -12.0480, "lng": -77.0385, "nombre": "Av. Tacna"},
        {"lat": -12.0474, "lng": -77.0385, "nombre": "Av. Tacna / Jr. Huancavelica"},
        {"lat": -12.0474, "lng": -77.0397, "nombre": "Llegada – Iglesia de Las Nazarenas"},
    ],
    "rec-002": [
        {"lat": -12.0474, "lng": -77.0409, "nombre": "Inicio – Monasterio de Nazarenas"},
        {"lat": -12.0455, "lng": -77.0409, "nombre": "Jr. Chancay"},
        {"lat": -12.0436, "lng": -77.0409, "nombre": "Jr. Chancay / Jr. Ica"},
        {"lat": -12.0418, "lng": -77.0409, "nombre": "Jr. Chancay (norte)"},
        {"lat": -12.0393, "lng": -77.0409, "nombre": "Jr. Chancay / Jr. C. Superunda"},
        {"lat": -12.0393, "lng": -77.0385, "nombre": "Jr. C. Superunda / Av. Tacna"},
        {"lat": -12.0418, "lng": -77.0385, "nombre": "Av. Tacna"},
        {"lat": -12.0436, "lng": -77.0385, "nombre": "Av. Tacna / Jr. Ica"},
        {"lat": -12.0460, "lng": -77.0385, "nombre": "Av. Tacna (bajando)"},
        {"lat": -12.0489, "lng": -77.0385, "nombre": "Av. Tacna / Av. Emancipación"},
        {"lat": -12.0489, "lng": -77.0409, "nombre": "Av. Emancipación"},
        {"lat": -12.0474, "lng": -77.0409, "nombre": "Llegada – Monasterio de Nazarenas"},
    ],
}

# Lista oficial de cuadrillas disponibles
LISTA_CUADRILLAS = [
    "Cuadrilla 1", "Cuadrilla 2", "Cuadrilla 3", "Cuadrilla 4", "Cuadrilla 5",
    "Cuadrilla 6", "Cuadrilla 7", "Cuadrilla 8", "Cuadrilla 9", "Cuadrilla 10",
    "Cuadrilla 11", "Cuadrilla 12", "Cuadrilla 13", "Cuadrilla 14", "Cuadrilla 15",
    "Cuadrilla 16", "Cuadrilla 17", "Cuadrilla 18", "Cuadrilla 19", "Cuadrilla 20",
    "Hermanos Honorarios", "Invitados"
]

def init_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(os.path.join(DATA_DIR, 'recorridos.json')):
        recorridos = [
            {"id": "rec-001", "nombre": "Primer Recorrido Procesional 2024",  "fecha": "2024-10-18", "hora_salida": "08:00", "hora_llegada_programada": "22:00", "distancia_total": 4800, "observaciones": "Recorrido tradicional por el Centro Histórico de Lima", "estado": "programado", "color": "#6E1E91"},
            {"id": "rec-002", "nombre": "Segundo Recorrido Procesional 2024", "fecha": "2024-10-19", "hora_salida": "08:00", "hora_llegada_programada": "21:30", "distancia_total": 4200, "observaciones": "", "estado": "programado", "color": "#4B1462"},
        ]
        save_data('recorridos.json', recorridos)

    if not os.path.exists(os.path.join(DATA_DIR, 'cuadrillas.json')):
        cuadrillas = [
            {"id": "cua-01", "recorrido_id": "rec-001", "numero": 1,  "cuadrilla": "Cuadrilla 1",        "tipo": "regular",    "hermandad_invitada": "", "metraje": 320, "tiempo_estimado": 45, "hora_toma": "08:00", "hora_deja": "08:45"},
            {"id": "cua-02", "recorrido_id": "rec-001", "numero": 2,  "cuadrilla": "Cuadrilla 2",        "tipo": "regular",    "hermandad_invitada": "", "metraje": 310, "tiempo_estimado": 43, "hora_toma": "08:50", "hora_deja": "09:33"},
            {"id": "cua-03", "recorrido_id": "rec-001", "numero": 3,  "cuadrilla": "Cuadrilla 3",        "tipo": "regular",    "hermandad_invitada": "", "metraje": 330, "tiempo_estimado": 46, "hora_toma": "09:38", "hora_deja": "10:24"},
            {"id": "cua-04", "recorrido_id": "rec-001", "numero": 4,  "cuadrilla": "Cuadrilla 4",        "tipo": "regular",    "hermandad_invitada": "", "metraje": 300, "tiempo_estimado": 42, "hora_toma": "10:29", "hora_deja": "11:11"},
            {"id": "cua-05", "recorrido_id": "rec-001", "numero": 5,  "cuadrilla": "Cuadrilla 5",        "tipo": "regular",    "hermandad_invitada": "", "metraje": 340, "tiempo_estimado": 47, "hora_toma": "11:16", "hora_deja": "12:03"},
            {"id": "cua-06", "recorrido_id": "rec-001", "numero": 6,  "cuadrilla": "Cuadrilla 6",        "tipo": "regular",    "hermandad_invitada": "", "metraje": 290, "tiempo_estimado": 41, "hora_toma": "12:08", "hora_deja": "12:49"},
            {"id": "cua-07", "recorrido_id": "rec-001", "numero": 7,  "cuadrilla": "Cuadrilla 7",        "tipo": "regular",    "hermandad_invitada": "", "metraje": 315, "tiempo_estimado": 44, "hora_toma": "12:54", "hora_deja": "13:38"},
            {"id": "cua-08", "recorrido_id": "rec-001", "numero": 8,  "cuadrilla": "Cuadrilla 8",        "tipo": "regular",    "hermandad_invitada": "", "metraje": 325, "tiempo_estimado": 45, "hora_toma": "13:43", "hora_deja": "14:28"},
            {"id": "cua-09", "recorrido_id": "rec-001", "numero": 9,  "cuadrilla": "Cuadrilla 9",        "tipo": "regular",    "hermandad_invitada": "", "metraje": 305, "tiempo_estimado": 43, "hora_toma": "14:33", "hora_deja": "15:16"},
            {"id": "cua-10", "recorrido_id": "rec-001", "numero": 10, "cuadrilla": "Cuadrilla 10",       "tipo": "regular",    "hermandad_invitada": "", "metraje": 335, "tiempo_estimado": 47, "hora_toma": "15:21", "hora_deja": "16:08"},
            {"id": "cua-11", "recorrido_id": "rec-001", "numero": 11, "cuadrilla": "Cuadrilla 11",       "tipo": "regular",    "hermandad_invitada": "", "metraje": 310, "tiempo_estimado": 43, "hora_toma": "16:13", "hora_deja": "16:56"},
            {"id": "cua-12", "recorrido_id": "rec-001", "numero": 12, "cuadrilla": "Cuadrilla 12",       "tipo": "regular",    "hermandad_invitada": "", "metraje": 320, "tiempo_estimado": 45, "hora_toma": "17:01", "hora_deja": "17:46"},
            {"id": "cua-13", "recorrido_id": "rec-001", "numero": 13, "cuadrilla": "Cuadrilla 13",       "tipo": "regular",    "hermandad_invitada": "", "metraje": 300, "tiempo_estimado": 42, "hora_toma": "17:51", "hora_deja": "18:33"},
            {"id": "cua-14", "recorrido_id": "rec-001", "numero": 14, "cuadrilla": "Cuadrilla 14",       "tipo": "regular",    "hermandad_invitada": "", "metraje": 330, "tiempo_estimado": 46, "hora_toma": "18:38", "hora_deja": "19:24"},
            {"id": "cua-15", "recorrido_id": "rec-001", "numero": 15, "cuadrilla": "Cuadrilla 15",       "tipo": "regular",    "hermandad_invitada": "", "metraje": 315, "tiempo_estimado": 44, "hora_toma": "19:29", "hora_deja": "20:13"},
            {"id": "cua-16", "recorrido_id": "rec-001", "numero": 16, "cuadrilla": "Cuadrilla 16",       "tipo": "regular",    "hermandad_invitada": "", "metraje": 295, "tiempo_estimado": 41, "hora_toma": "20:18", "hora_deja": "20:59"},
            {"id": "cua-17", "recorrido_id": "rec-001", "numero": 17, "cuadrilla": "Cuadrilla 17",       "tipo": "regular",    "hermandad_invitada": "", "metraje": 325, "tiempo_estimado": 45, "hora_toma": "21:04", "hora_deja": "21:49"},
            {"id": "cua-18", "recorrido_id": "rec-001", "numero": 18, "cuadrilla": "Cuadrilla 18",       "tipo": "regular",    "hermandad_invitada": "", "metraje": 310, "tiempo_estimado": 43, "hora_toma": "21:54", "hora_deja": "22:37"},
            {"id": "cua-19", "recorrido_id": "rec-001", "numero": 19, "cuadrilla": "Cuadrilla 19",       "tipo": "regular",    "hermandad_invitada": "", "metraje": 320, "tiempo_estimado": 45, "hora_toma": "22:42", "hora_deja": "23:27"},
            {"id": "cua-20", "recorrido_id": "rec-001", "numero": 20, "cuadrilla": "Cuadrilla 20",       "tipo": "regular",    "hermandad_invitada": "", "metraje": 305, "tiempo_estimado": 43, "hora_toma": "23:32", "hora_deja": "00:15"},
            {"id": "cua-hh", "recorrido_id": "rec-001", "numero": 21, "cuadrilla": "Hermanos Honorarios","tipo": "honorarios", "hermandad_invitada": "", "metraje": 280, "tiempo_estimado": 40, "hora_toma": "00:20", "hora_deja": "01:00"},
        ]
        save_data('cuadrillas.json', cuadrillas)

    if not os.path.exists(os.path.join(DATA_DIR, 'homenajes.json')):
        homenajes = [
            {"id": "hom-01", "recorrido_id": "rec-001", "nombre": "Homenaje Palacio de Gobierno",   "ubicacion": "Jr. de la Unión cdra. 1",  "tiempo_programado": 15, "prioridad": "alta",  "cargo_a": "institucion", "observaciones": "Presencia de autoridades"},
            {"id": "hom-02", "recorrido_id": "rec-001", "nombre": "Homenaje Municipalidad de Lima",  "ubicacion": "Jr. de la Unión cdra. 2",  "tiempo_programado": 10, "prioridad": "alta",  "cargo_a": "institucion", "observaciones": ""},
            {"id": "hom-03", "recorrido_id": "rec-001", "nombre": "Homenaje Iglesia San Pedro",      "ubicacion": "Jr. Ucayali cdra. 4",      "tiempo_programado": 20, "prioridad": "alta",  "cargo_a": "cuadrilla",   "observaciones": "Misa cantada"},
            {"id": "hom-04", "recorrido_id": "rec-001", "nombre": "Homenaje Club Nacional",          "ubicacion": "Jr. de la Unión cdra. 8",  "tiempo_programado": 12, "prioridad": "media", "cargo_a": "cuadrilla",   "observaciones": ""},
            {"id": "hom-05", "recorrido_id": "rec-001", "nombre": "Homenaje Casa de la Literatura",  "ubicacion": "Jr. Áncash cdra. 2",       "tiempo_programado": 8,  "prioridad": "baja",  "cargo_a": "cuadrilla",   "observaciones": ""},
        ]
        save_data('homenajes.json', homenajes)

    if not os.path.exists(os.path.join(DATA_DIR, 'eventos.json')):
        save_data('eventos.json', [])

    if not os.path.exists(os.path.join(DATA_DIR, 'posicion.json')):
        save_posicion({})

    # Agregar waypoints a recorridos existentes si no los tienen
    recorridos = load_data('recorridos.json')
    changed = False
    for r in recorridos:
        if 'waypoints' not in r and r['id'] in WAYPOINTS_RECORRIDOS:
            r['waypoints'] = WAYPOINTS_RECORRIDOS[r['id']]
            changed = True
    if changed:
        save_data('recorridos.json', recorridos)

    if not os.path.exists(os.path.join(DATA_DIR, 'usuarios.json')):
        usuarios = [
            {"id": "usr-001", "nombre": "Administrador General", "usuario": "admin",       "password": "admin123", "rol": "Administrador General"},
            {"id": "usr-002", "nombre": "Juan Ríos",             "usuario": "cronometro1", "password": "cron123",  "rol": "Cronometrista"},
            {"id": "usr-003", "nombre": "Carlos Mendoza",        "usuario": "director",    "password": "dir123",   "rol": "Director de Recorrido"},
        ]
        save_data('usuarios.json', usuarios)

init_data()

# ── AUTH ──────────────────────────────────
@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        usuarios = load_data('usuarios.json')
        user = next((u for u in usuarios if u['usuario'] == usuario and u['password'] == password), None)
        if user:
            session['usuario'] = user
            return redirect(url_for('dashboard'))
        error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── DASHBOARD ────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    from datetime import date
    recorridos = load_data('recorridos.json')
    rid = request.args.get('rid', recorridos[0]['id'] if recorridos else 'rec-001')
    rec_actual = next((r for r in recorridos if r['id'] == rid), recorridos[0] if recorridos else None)
    cuadrillas = sorted(
        [c for c in load_data('cuadrillas.json') if c.get('recorrido_id') == rid],
        key=lambda c: c.get('numero', 0)
    )
    homenajes = sorted(
        [h for h in load_data('homenajes.json') if h.get('recorrido_id') == rid],
        key=lambda h: h.get('numero_cuadrilla') or 0
    )
    return render_template('dashboard.html',
        recorridos=recorridos,
        recorrido_actual=rec_actual,
        rid=rid,
        hoy=date.today().isoformat(),
        eventos=load_data('eventos.json'),
        cuadrillas=cuadrillas,
        homenajes=homenajes,
        usuario=session['usuario'])

ROLES_ADMIN = ['Administrador General', 'Super Admin']

# ── RECORRIDOS ────────────────────────────
@app.route('/recorridos')
def recorridos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    recorridos_data = load_data('recorridos.json')
    cuadrillas_data = load_data('cuadrillas.json')
    homenajes_data  = load_data('homenajes.json')
    cuas_por_rec = {}
    for c in cuadrillas_data:
        rid = c.get('recorrido_id', '')
        cuas_por_rec[rid] = cuas_por_rec.get(rid, 0) + 1
    homs_por_rec = {}
    for h in homenajes_data:
        rid = h.get('recorrido_id', '')
        homs_por_rec[rid] = homs_por_rec.get(rid, 0) + 1
    # Strip heavy ruta_coords before sending to JS (the template still gets full recorridos)
    recorridos_js = [{k: v for k, v in r.items() if k != 'ruta_coords'} for r in recorridos_data]
    return render_template('recorridos.html',
        recorridos=recorridos_data,
        recorridos_js=recorridos_js,
        cuas_por_rec=cuas_por_rec,
        homs_por_rec=homs_por_rec,
        usuario=session['usuario'])

@app.route('/recorridos/editar/<rid>', methods=['POST'])
def editar_recorrido(rid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    data = load_data('recorridos.json')
    for r in data:
        if r['id'] == rid:
            r['nombre']                  = request.form.get('nombre')
            r['fecha']                   = request.form.get('fecha')
            r['hora_salida']             = request.form.get('hora_salida')
            r['hora_llegada_programada'] = request.form.get('hora_llegada')
            r['distancia_total']         = int(request.form.get('distancia', 0))
            r['observaciones']           = request.form.get('observaciones', '')
            r['estado']                  = request.form.get('estado', 'programado')
            r['punto_inicio']            = request.form.get('punto_inicio', '')
            r['secretario']              = request.form.get('secretario', '')
            r['pro_secretario']          = request.form.get('pro_secretario', '')
            break
    save_data('recorridos.json', data)
    return redirect(url_for('recorridos'))

@app.route('/recorridos/eliminar/<rid>', methods=['POST'])
def eliminar_recorrido(rid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if session['usuario'].get('rol') not in ROLES_ADMIN:
        return redirect(url_for('recorridos'))
    save_data('recorridos.json',  [r for r in load_data('recorridos.json')  if r['id'] != rid])
    save_data('cuadrillas.json',  [c for c in load_data('cuadrillas.json')  if c.get('recorrido_id') != rid])
    save_data('homenajes.json',   [h for h in load_data('homenajes.json')   if h.get('recorrido_id') != rid])
    save_data('eventos.json',     [e for e in load_data('eventos.json')      if e.get('recorrido_id') != rid])
    return redirect(url_for('recorridos'))

@app.route('/recorridos/nuevo', methods=['GET', 'POST'])
def nuevo_recorrido():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = load_data('recorridos.json')
        data.append({
            "id": f"rec-{str(uuid.uuid4())[:8]}",
            "nombre": request.form.get('nombre'),
            "fecha": request.form.get('fecha'),
            "hora_salida": request.form.get('hora_salida'),
            "hora_llegada_programada": request.form.get('hora_llegada'),
            "distancia_total": int(request.form.get('distancia', 0)),
            "observaciones": request.form.get('observaciones', ''),
            "estado": "programado",
            "color": "#6E1E91"
        })
        save_data('recorridos.json', data)
        return redirect(url_for('recorridos'))
    return render_template('nuevo_recorrido.html', usuario=session['usuario'])

# ── CUADRILLAS ────────────────────────────
@app.route('/cuadrillas')
def cuadrillas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    recorridos_data = load_data('recorridos.json')
    rutas = {r['id']: r.get('ruta_coords', []) for r in recorridos_data}
    return render_template('cuadrillas.html',
        cuadrillas=load_data('cuadrillas.json'),
        recorridos=recorridos_data,
        lista_cuadrillas=LISTA_CUADRILLAS,
        rutas_json=rutas,
        usuario=session['usuario'])

@app.route('/cuadrillas/nueva', methods=['POST'])
def nueva_cuadrilla():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    data = load_data('cuadrillas.json')
    tipo = request.form.get('tipo', 'regular')
    hermandad = request.form.get('hermandad_invitada', '') if tipo == 'invitados' else ''
    lat_raw = request.form.get('lat', '').strip()
    lng_raw = request.form.get('lng', '').strip()
    data.append({
        "id": f"cua-{str(uuid.uuid4())[:8]}",
        "recorrido_id": request.form.get('recorrido_id'),
        "numero": int(request.form.get('numero', 1)),
        "cuadrilla": request.form.get('cuadrilla'),
        "tipo": tipo,
        "hermandad_invitada": hermandad,
        "ubicacion": request.form.get('ubicacion', ''),
        "punto_deja": request.form.get('punto_deja', ''),
        "es_ultima": request.form.get('es_ultima') == '1',
        "metraje": int(request.form.get('metraje', 0)),
        "tiempo_estimado": int(request.form.get('tiempo_estimado', 0)),
        "hora_toma": request.form.get('hora_toma'),
        "hora_deja": request.form.get('hora_deja'),
        "lat": float(lat_raw) if lat_raw else None,
        "lng": float(lng_raw) if lng_raw else None,
    })
    save_data('cuadrillas.json', data)
    return redirect(url_for('cuadrillas'))

@app.route('/cuadrillas/editar/<cid>', methods=['POST'])
def editar_cuadrilla(cid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    data = load_data('cuadrillas.json')
    tipo = request.form.get('tipo', 'regular')
    hermandad = request.form.get('hermandad_invitada', '') if tipo == 'invitados' else ''
    for c in data:
        if c['id'] == cid:
            c['recorrido_id'] = request.form.get('recorrido_id')
            c['numero'] = int(request.form.get('numero', 1))
            c['cuadrilla'] = request.form.get('cuadrilla')
            c['tipo'] = tipo
            c['hermandad_invitada'] = hermandad
            c['ubicacion']   = request.form.get('ubicacion', '')
            c['punto_deja']  = request.form.get('punto_deja', '')
            c['es_ultima']   = request.form.get('es_ultima') == '1'
            c['metraje']     = int(request.form.get('metraje', 0))
            c['tiempo_estimado'] = int(request.form.get('tiempo_estimado', 0))
            c['hora_toma'] = request.form.get('hora_toma')
            c['hora_deja'] = request.form.get('hora_deja')
            lat_raw = request.form.get('lat', '').strip()
            lng_raw = request.form.get('lng', '').strip()
            c['lat'] = float(lat_raw) if lat_raw else None
            c['lng'] = float(lng_raw) if lng_raw else None
            break
    save_data('cuadrillas.json', data)
    return redirect(url_for('cuadrillas'))

@app.route('/cuadrillas/eliminar/<cid>', methods=['POST'])
def eliminar_cuadrilla(cid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    data = [c for c in load_data('cuadrillas.json') if c['id'] != cid]
    save_data('cuadrillas.json', data)
    return redirect(url_for('cuadrillas'))

# ── HOMENAJES ────────────────────────────
@app.route('/homenajes')
def homenajes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('homenajes.html',
        homenajes=load_data('homenajes.json'),
        recorridos=load_data('recorridos.json'),
        usuario=session['usuario'])

@app.route('/homenajes/editar/<hid>', methods=['POST'])
def editar_homenaje(hid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    data = load_data('homenajes.json')
    for h in data:
        if h['id'] == hid:
            nc_raw = request.form.get('numero_cuadrilla', '').strip()
            h['recorrido_id']      = request.form.get('recorrido_id')
            h['numero_cuadrilla']  = int(nc_raw) if nc_raw else None
            h['nombre']            = request.form.get('nombre')
            h['ubicacion']         = request.form.get('ubicacion', '')
            h['tiempo_programado'] = int(request.form.get('tiempo_programado', 10))
            h['prioridad']         = request.form.get('prioridad', 'media')
            h['cargo_a']           = request.form.get('cargo_a', 'cuadrilla')
            h['observaciones']     = request.form.get('observaciones', '')
            break
    save_data('homenajes.json', data)
    return redirect(url_for('homenajes'))

@app.route('/homenajes/eliminar/<hid>', methods=['POST'])
def eliminar_homenaje(hid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    data = [h for h in load_data('homenajes.json') if h['id'] != hid]
    save_data('homenajes.json', data)
    return redirect(url_for('homenajes'))

@app.route('/homenajes/nuevo', methods=['POST'])
def nuevo_homenaje():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    data = load_data('homenajes.json')
    nc_raw = request.form.get('numero_cuadrilla', '').strip()
    data.append({
        "id": f"hom-{str(uuid.uuid4())[:8]}",
        "recorrido_id": request.form.get('recorrido_id'),
        "numero_cuadrilla": int(nc_raw) if nc_raw else None,
        "nombre": request.form.get('nombre'),
        "ubicacion": request.form.get('ubicacion'),
        "tiempo_programado": int(request.form.get('tiempo_programado', 10)),
        "prioridad": request.form.get('prioridad', 'media'),
        "cargo_a": request.form.get('cargo_a', 'cuadrilla'),
        "observaciones": request.form.get('observaciones', ''),
    })
    save_data('homenajes.json', data)
    return redirect(url_for('homenajes'))

# ── TABLET ────────────────────────────────
@app.route('/tablet')
def tablet():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    from datetime import date
    return render_template('tablet.html',
        recorridos=load_data('recorridos.json'),
        cuadrillas=load_data('cuadrillas.json'),
        homenajes=load_data('homenajes.json'),
        eventos=load_data('eventos.json')[-20:],
        hoy=date.today().isoformat(),
        usuario=session['usuario'])

@app.route('/api/evento', methods=['POST'])
def registrar_evento():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    body = request.get_json()
    eventos = load_data('eventos.json')
    rid = body.get('recorrido_id', 'rec-001')
    evento = {
        "id": str(uuid.uuid4())[:8],
        "tipo": body.get('tipo'),
        "referencia_id": body.get('referencia_id'),
        "recorrido_id": rid,
        "usuario": session['usuario']['nombre'],
        "fecha_hora": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "lat": body.get('lat'),
        "lng": body.get('lng'),
        "observacion": body.get('observacion', ''),
    }
    if body.get('tipo') == 'inicio_sector':
        cua_id = body.get('referencia_id', '')
        if cua_id:
            # Contar sectores previos de ESTA cuadrilla en este recorrido
            sector_num = sum(
                1 for e in eventos
                if e.get('tipo') == 'inicio_sector'
                and e.get('referencia_id') == cua_id
                and e.get('recorrido_id') == rid
            ) + 1
        else:
            # Sin cuadrilla: numeración global del recorrido
            sector_num = sum(
                1 for e in eventos
                if e.get('tipo') == 'inicio_sector'
                and e.get('recorrido_id') == rid
            ) + 1
        evento['sector_numero'] = sector_num
    eventos.append(evento)
    save_data('eventos.json', eventos)
    return jsonify({'ok': True, 'evento': evento})

# ── API ESTADO ────────────────────────────
@app.route('/api/estado')
def api_estado():
    rid = request.args.get('rid', 'rec-001')
    recorridos = load_data('recorridos.json')
    rec = next((r for r in recorridos if r['id'] == rid), None)
    todos_eventos = load_data('eventos.json')
    eventos = [e for e in todos_eventos if e.get('recorrido_id', rid) == rid]
    cuadrillas = [c for c in load_data('cuadrillas.json') if c.get('recorrido_id') == rid]
    homenajes = [h for h in load_data('homenajes.json') if h.get('recorrido_id') == rid]

    cuadrilla_activa = None
    homenaje_activo = None
    inicio_cuadrilla_dt = None
    inicio_homenaje_dt = None
    cuadrillas_completadas = []
    tiempos_cuadrilla = []
    tiempos_homenaje = []

    for e in eventos:
        if e['tipo'] == 'inicio_cuadrilla':
            cuadrilla_activa = e.get('referencia_id')
            inicio_cuadrilla_dt = e['fecha_hora']
        elif e['tipo'] == 'fin_cuadrilla' and cuadrilla_activa:
            c = next((c for c in cuadrillas if c['id'] == cuadrilla_activa), None)
            if c:
                inicio = datetime.strptime(inicio_cuadrilla_dt, '%Y-%m-%d %H:%M:%S')
                fin = datetime.strptime(e['fecha_hora'], '%Y-%m-%d %H:%M:%S')
                dur_real = int((fin - inicio).total_seconds() / 60)
                tiempos_cuadrilla.append({
                    'id': c['id'], 'cuadrilla': c['cuadrilla'], 'numero': c['numero'],
                    'tipo': c.get('tipo','regular'),
                    'hermandad_invitada': c.get('hermandad_invitada',''),
                    'estimado': c['tiempo_estimado'], 'real': dur_real,
                    'diferencia': dur_real - c['tiempo_estimado']
                })
            cuadrillas_completadas.append(cuadrilla_activa)
            cuadrilla_activa = None
        elif e['tipo'] == 'inicio_homenaje':
            homenaje_activo = e.get('referencia_id')
            inicio_homenaje_dt = e['fecha_hora']
        elif e['tipo'] == 'fin_homenaje' and homenaje_activo:
            h = next((hh for hh in homenajes if hh['id'] == homenaje_activo), None)
            if h:
                inicio = datetime.strptime(inicio_homenaje_dt, '%Y-%m-%d %H:%M:%S')
                fin = datetime.strptime(e['fecha_hora'], '%Y-%m-%d %H:%M:%S')
                dur_real = int((fin - inicio).total_seconds() / 60)
                tiempos_homenaje.append({
                    'id': h['id'], 'nombre': h['nombre'],
                    'ubicacion': h.get('ubicacion', ''),
                    'numero_cuadrilla': h.get('numero_cuadrilla'),
                    'cargo_a': h.get('cargo_a', 'cuadrilla'),
                    'estimado': h['tiempo_programado'], 'real': dur_real,
                    'diferencia': dur_real - h['tiempo_programado'],
                })
            homenaje_activo = None

    # Homenajes cargados a "institución" no penalizan a la cuadrilla durante la que
    # ocurrieron: se descuentan de su tiempo real y pasan a un atraso institucional aparte.
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

    completadas_obj = [c for c in cuadrillas if c['id'] in cuadrillas_completadas]
    metros_recorridos = sum(c['metraje'] for c in completadas_obj)
    metros_totales = sum(c['metraje'] for c in cuadrillas)
    atraso_total = sum(t['diferencia'] for t in tiempos_cuadrilla) + atraso_institucional

    fecha_rec = rec['fecha'] if rec else '2024-10-18'
    hora_llegada_str = rec.get('hora_llegada_programada', '22:00') if rec else '22:00'
    hora_llegada_prog = datetime.strptime(f"{fecha_rec} {hora_llegada_str}:00", '%Y-%m-%d %H:%M:%S')
    eta = hora_llegada_prog + timedelta(minutes=atraso_total)

    cuadrilla_activa_obj = next((c for c in cuadrillas if c['id'] == cuadrilla_activa), None)
    homenaje_activo_obj = next((h for h in homenajes if h['id'] == homenaje_activo), None)

    return jsonify({
        'cuadrilla_activa': cuadrilla_activa_obj,
        'cuadrilla_activa_inicio': inicio_cuadrilla_dt if cuadrilla_activa_obj else None,
        'homenaje_activo': homenaje_activo_obj,
        'homenaje_activo_inicio': inicio_homenaje_dt if homenaje_activo_obj else None,
        'metros_recorridos': metros_recorridos,
        'metros_totales': metros_totales,
        'porcentaje': round(metros_recorridos / metros_totales * 100, 1) if metros_totales else 0,
        'atraso_minutos': atraso_total,
        'atraso_institucional': atraso_institucional,
        'eta': eta.strftime('%H:%M'),
        'cuadrillas_completadas': len(cuadrillas_completadas),
        'total_cuadrillas': len(cuadrillas),
        'cuadrillas_completadas_ids': cuadrillas_completadas,
        'tiempos_cuadrilla': tiempos_cuadrilla,
        'tiempos_homenaje': tiempos_homenaje,
        'total_eventos': len(eventos),
        'hora_llegada_prog': hora_llegada_str,
    })

@app.route('/api/eventos_recientes')
def api_eventos_recientes():
    rid = request.args.get('rid', 'rec-001')
    todos = load_data('eventos.json')
    filtrados = [e for e in todos if e.get('recorrido_id', rid) == rid]
    return jsonify(filtrados[-15:])

@app.route('/api/reset', methods=['POST'])
def reset_eventos():
    save_data('eventos.json', [])
    return jsonify({'ok': True})

# ── MAPA ──────────────────────────────────
@app.route('/mapa')
@app.route('/mapa/<rid>')
def mapa_view(rid=None):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    recorridos = load_data('recorridos.json')
    if rid is None:
        rid = recorridos[0]['id'] if recorridos else 'rec-001'
    rec = next((r for r in recorridos if r['id'] == rid), None)
    return render_template('mapa.html',
        recorrido=rec,
        recorridos=recorridos,
        usuario=session['usuario'])

@app.route('/api/posicion')
def api_posicion_get():
    rid = request.args.get('rid', 'rec-001')
    recorridos = load_data('recorridos.json')
    rec = next((r for r in recorridos if r['id'] == rid), None)
    waypoints = rec.get('waypoints', []) if rec else []
    posicion = load_posicion()
    wp_actual = posicion.get(rid, 0)
    wp_actual = max(0, min(wp_actual, len(waypoints) - 1)) if waypoints else 0
    return jsonify({
        'rid': rid,
        'wp_actual': wp_actual,
        'total': len(waypoints),
        'waypoint': waypoints[wp_actual] if waypoints else None,
        'waypoints': waypoints,
    })

@app.route('/api/posicion', methods=['POST'])
def api_posicion_set():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    body = request.get_json()
    rid = body.get('rid', 'rec-001')
    recorridos = load_data('recorridos.json')
    rec = next((r for r in recorridos if r['id'] == rid), None)
    waypoints = rec.get('waypoints', []) if rec else []
    posicion = load_posicion()
    wp_actual = posicion.get(rid, 0)
    if 'wp' in body:
        wp_actual = int(body['wp'])
    elif body.get('accion') == 'avanzar':
        wp_actual += 1
    elif body.get('accion') == 'retroceder':
        wp_actual -= 1
    wp_actual = max(0, min(wp_actual, len(waypoints) - 1)) if waypoints else 0
    posicion[rid] = wp_actual
    save_posicion(posicion)
    return jsonify({'ok': True, 'wp': wp_actual, 'waypoint': waypoints[wp_actual] if waypoints else None})

@app.route('/recorridos/trazar/<rid>')
def trazar_recorrido(rid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    recorridos = load_data('recorridos.json')
    rec = next((r for r in recorridos if r['id'] == rid), None)
    if not rec:
        return redirect(url_for('recorridos'))
    cuadrillas = sorted(
        [c for c in load_data('cuadrillas.json') if c.get('recorrido_id') == rid],
        key=lambda c: c.get('numero', 0)
    )
    return render_template('trazador.html', recorrido=rec, cuadrillas=cuadrillas, usuario=session['usuario'])

@app.route('/api/ruta/guardar', methods=['POST'])
def guardar_ruta():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    body = request.get_json()
    rid    = body.get('rid')
    coords = body.get('coords', [])
    recorridos = load_data('recorridos.json')
    for r in recorridos:
        if r['id'] == rid:
            r['ruta_coords'] = coords
            break
    save_data('recorridos.json', recorridos)
    return jsonify({'ok': True, 'puntos': len(coords)})

@app.route('/api/ruta/<rid>')
def api_ruta(rid):
    cuas = sorted(
        [c for c in load_data('cuadrillas.json')
         if c.get('recorrido_id') == rid and c.get('lat') and c.get('lng')],
        key=lambda c: c.get('numero', 0)
    )
    return jsonify({
        'rid': rid,
        'waypoints': [{'id': c['id'], 'numero': c['numero'], 'nombre': c['cuadrilla'],
                        'lat': c['lat'], 'lng': c['lng']} for c in cuas]
    })

@app.route('/api/posicion_mapa')
def api_posicion_mapa():
    rid = request.args.get('rid', 'rec-001')
    eventos    = load_data('eventos.json')
    cuas_all   = load_data('cuadrillas.json')
    recorridos = load_data('recorridos.json')

    rec = next((r for r in recorridos if r['id'] == rid), None)
    ruta_coords = rec.get('ruta_coords', []) if rec else []

    cuas = sorted(
        [c for c in cuas_all if c.get('recorrido_id') == rid],
        key=lambda c: c.get('numero', 0)
    )
    total = len(cuas)

    activa_id   = None
    completadas = []
    for e in eventos:
        if e['tipo'] == 'inicio_cuadrilla':
            activa_id = e['referencia_id']
        elif e['tipo'] == 'fin_cuadrilla' and activa_id:
            completadas.append(activa_id)
            activa_id = None

    n_completadas = len([c for c in cuas if c['id'] in completadas])
    n_ruta = len(ruta_coords)

    # Snap a lat/lng point to the nearest index in ruta_coords
    def closest_idx(lat, lng):
        best, best_d = 0, float('inf')
        for i, pt in enumerate(ruta_coords):
            d = (pt[0] - lat) ** 2 + (pt[1] - lng) ** 2
            if d < best_d:
                best_d, best = d, i
        return best

    # Build segment list for all cuadrillas (ordered by numero)
    segments = []
    for c in cuas:
        route_index = None
        if c.get('lat') and c.get('lng') and n_ruta > 1:
            route_index = closest_idx(c['lat'], c['lng'])
        segments.append({
            'id':          c['id'],
            'numero':      c['numero'],
            'nombre':      c['cuadrilla'],
            'lat':         c.get('lat'),
            'lng':         c.get('lng'),
            'completada':  c['id'] in completadas,
            'activa':      c['id'] == activa_id,
            'route_index': route_index,
        })

    # fill_index: snap to the route_index of the last completed cuadrilla
    fill_index = 0
    for seg in segments:
        if seg['completada'] and seg['route_index'] is not None:
            fill_index = seg['route_index']
    # Fallback: proportional if cuadrillas have no lat/lng but some completed
    if fill_index == 0 and n_completadas > 0 and n_ruta > 1 and total > 0:
        fill_index = min(round(n_completadas / total * (n_ruta - 1)), n_ruta - 1)

    activa_obj = next((c for c in cuas if c['id'] == activa_id), None)

    return jsonify({
        'rid':           rid,
        'ruta_coords':   ruta_coords,
        'fill_index':    fill_index,
        'total':         total,
        'n_completadas': n_completadas,
        'activa_id':     activa_id,
        'activa_nombre': activa_obj['cuadrilla'] if activa_obj else None,
        'segments':      segments,
        'tiene_ruta':    n_ruta > 1,
    })

@app.route('/api/posicion/reset', methods=['POST'])
def api_posicion_reset():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    body = request.get_json()
    rid = body.get('rid', 'rec-001')
    posicion = load_posicion()
    posicion[rid] = 0
    save_posicion(posicion)
    return jsonify({'ok': True})

# ── REPORTES ──────────────────────────────
@app.route('/reporte/toma-y-deja/<rid>')
def reporte_toma_y_deja(rid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    recorridos = load_data('recorridos.json')
    rec = next((r for r in recorridos if r['id'] == rid), None)
    if not rec:
        return redirect(url_for('lista_recorridos'))
    cuadrillas = sorted(
        [c for c in load_data('cuadrillas.json') if c.get('recorrido_id') == rid],
        key=lambda c: c.get('numero', 0)
    )
    homs_all = [h for h in load_data('homenajes.json') if h.get('recorrido_id') == rid]
    homs_por_cuadrilla = {}
    for h in homs_all:
        nc = h.get('numero_cuadrilla')
        if nc:
            homs_por_cuadrilla.setdefault(int(nc), []).append(h)
    return render_template('reporte_toma_y_deja.html',
        recorrido=rec,
        cuadrillas=cuadrillas,
        homenajes=homs_all,
        homs_por_cuadrilla=homs_por_cuadrilla,
        usuario=session['usuario'])

@app.route('/reporte/marcaciones')
def reporte_marcaciones():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    recorridos = load_data('recorridos.json')
    cuas_all   = load_data('cuadrillas.json')
    homs_all   = load_data('homenajes.json')
    eventos    = load_data('eventos.json')

    # Index de cuadrillas y homenajes por id
    cua_idx = {c['id']: c for c in cuas_all}
    hom_idx = {h['id']: h for h in homs_all}

    # Calcular duraciones: emparejar inicio con fin
    from datetime import datetime
    def parse_dt(s):
        try:
            return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
        except Exception:
            return None

    PARES = {
        'inicio_cuadrilla': 'fin_cuadrilla',
        'inicio_homenaje':  'fin_homenaje',
        'inicio_cambio':    'fin_cambio',
        'inicio_sector':    'fin_sector',
    }
    pendientes = {}   # tipo_fin -> (evento_inicio, ref_id)
    registros  = []   # final list

    for e in eventos:
        tipo = e.get('tipo', '')
        # es un "inicio" → guardar pendiente
        if tipo in PARES:
            fin_tipo = PARES[tipo]
            pendientes[fin_tipo] = e
        # es un "fin" → emparejar
        elif tipo in PARES.values():
            inicio_e = pendientes.pop(tipo, None)
            duracion = None
            if inicio_e:
                t0 = parse_dt(inicio_e.get('fecha_hora', ''))
                t1 = parse_dt(e.get('fecha_hora', ''))
                if t0 and t1:
                    duracion = int((t1 - t0).total_seconds() // 60)
            ref_id   = e.get('referencia_id') or (inicio_e.get('referencia_id') if inicio_e else None)
            ref_name = ''
            if ref_id in cua_idx:
                ref_name = f"Cuadrilla {cua_idx[ref_id]['numero']} – {cua_idx[ref_id]['cuadrilla']}"
            elif ref_id in hom_idx:
                ref_name = hom_idx[ref_id]['nombre']
            sector_num = inicio_e.get('sector_numero') if inicio_e else None
            cua_nombre = None
            cua_numero = None
            if tipo == 'fin_sector':
                if ref_id in cua_idx:
                    cua_nombre = cua_idx[ref_id]['cuadrilla']
                    cua_numero = cua_idx[ref_id]['numero']
                    ref_name = f"Sector {sector_num}" if sector_num else "Sector –"
                elif sector_num:
                    ref_name = f"Sector {sector_num}"
            registros.append({
                'tipo':          tipo,
                'tipo_inicio':   tipo,
                'hora_inicio':   inicio_e['fecha_hora'].split(' ')[1][:5] if inicio_e else '–',
                'hora_fin':      e['fecha_hora'].split(' ')[1][:5],
                'duracion':      duracion,
                'ref_id':        ref_id,
                'ref_nombre':    ref_name,
                'usuario':       e.get('usuario', ''),
                'observacion':   e.get('observacion', ''),
                'sector_numero': sector_num,
                'cua_nombre':    cua_nombre,
                'cua_numero':    cua_numero,
            })
        elif tipo == 'observacion':
            registros.append({
                'tipo':       'observacion',
                'hora_inicio': e['fecha_hora'].split(' ')[1][:5],
                'hora_fin':    None,
                'duracion':    None,
                'ref_id':      None,
                'ref_nombre':  '',
                'usuario':     e.get('usuario', ''),
                'observacion': e.get('observacion', ''),
            })

    return render_template('reporte_marcaciones.html',
        eventos=eventos,
        registros=registros,
        recorridos=recorridos,
        cua_idx=cua_idx,
        hom_idx=hom_idx,
        usuario=session['usuario'])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
