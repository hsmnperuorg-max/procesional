# Sistema de Control Procesional – Señor de los Milagros

Sistema integral para planificar, registrar y monitorear en tiempo real
los recorridos procesionales de la Hermandad del Señor de los Milagros de Nazarenas.

Construido en **Django** + **PostgreSQL**, listo para desplegarse en **Render** o en
cualquier **VPS** con Docker.

---

## REQUISITOS

- Python 3.11+ (probado con 3.13)
- PostgreSQL (local, Docker, o un proveedor externo como Neon)
- Conexión a internet (Font Awesome y Leaflet se cargan desde CDN)

---

## INSTALACIÓN LOCAL (sin Docker)

### 1. Crear entorno virtual e instalar dependencias
```
python -m venv venv
venv\Scripts\activate          (Windows)
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Copiar `.env.example` a `.env` y completar `DATABASE_URL` con tu Postgres local
(`DB_SSLMODE=disable` si tu Postgres local no usa SSL).

### 3. Migrar la base de datos (crea también los datos de demo)
```
python manage.py migrate
```

### 4. Ejecutar la aplicación
```
python manage.py runserver
```

### 5. Abrir en el navegador
```
http://localhost:8000
```

---

## INSTALACIÓN CON DOCKER (VPS propio)

```
cp .env.example .env   # completar DB_NAME / DB_USER / DB_PASSWORD y SECRET_KEY
docker compose up --build
```

Esto levanta 3 contenedores: `db` (Postgres), `web` (Django + gunicorn) y `nginx`
(proxy inverso en el puerto 80). Las migraciones y `collectstatic` corren
automáticamente al iniciar el contenedor `web` (ver `entrypoint.sh`).

---

## DESPLIEGUE EN RENDER

El repo incluye `render.yaml` (blueprint) y el mismo `Dockerfile` usado para el VPS.
En Render: New → Blueprint → seleccionar este repo. Completar manualmente en el
dashboard las variables marcadas `sync: false` (`DATABASE_URL` de tu Postgres,
por ejemplo Neon, con `sslmode=require`).

---

## USUARIOS DE PRUEBA

Se crean automáticamente al correr `migrate` (contraseñas ya hasheadas en la base):

| Usuario      | Contraseña | Rol                    |
|--------------|------------|------------------------|
| admin        | admin123   | Super Admin            |
| cronometro1  | cron123    | Cronometrista          |
| secretario1  | sec123     | Pro Secretario         |
| mayordomo1   | mayor123   | Mayordomía             |

**Cambiar estas contraseñas antes de usar el sistema en producción real.**

---

## MÓDULOS DEL SISTEMA

| Ruta                | Descripción                                      |
|----------------------|--------------------------------------------------|
| /login               | Inicio de sesión                                 |
| /dashboard           | Centro de control ejecutivo en tiempo real       |
| /recorridos          | Gestión de recorridos procesionales              |
| /cuadrillas          | Configuración de cuadrillas y tiempos            |
| /homenajes           | Gestión de homenajes programados                 |
| /tablet              | Interfaz de campo para cronometristas            |
| /mapa                | Seguimiento en vivo sobre el mapa                |
| /reporte/marcaciones | Reporte imprimible de todos los eventos          |
| /usuarios            | Gestión de usuarios y roles                      |
| /auditoria           | Historial de acciones (solo Super Admin)         |

---

## ESTRUCTURA DE ARCHIVOS

```
procesional/
├── config/                 ← Proyecto Django (settings, urls, wsgi)
├── cuentas/                ← Usuarios, roles/permisos y auditoría
├── gestion/                ← Recorridos, cuadrillas, homenajes, eventos, reportes
├── templates/              ← Plantillas Django (una por pantalla)
├── static/
│   ├── css/main.css        ← Estilos (morado nazareno + dorado)
│   └── js/main.js
├── requirements.txt
├── Dockerfile / entrypoint.sh / docker-compose.yml / nginx.conf
├── render.yaml
└── .env.example
```

---

## DATOS PRE-CARGADOS

La migración de datos (`gestion/migrations/0002_seed_datos.py` y
`cuentas/migrations/0002_seed_usuarios.py`) crea, la primera vez:
- 2 recorridos procesionales de ejemplo
- 21 cuadrillas del Primer Recorrido
- 5 homenajes programados
- 4 usuarios de prueba (ver tabla arriba)

Todo se guarda en PostgreSQL real (no hay archivos JSON ni datos en disco).
