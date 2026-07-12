# Sistema de Control Procesional – Señor de los Milagros

Sistema integral para planificar, registrar y monitorear en tiempo real
los recorridos procesionales de la Hermandad del Señor de los Milagros de Nazarenas.

---

## REQUISITOS

- Python 3.8 o superior
- VS Code (recomendado)
- Conexión a internet (solo para íconos Font Awesome)

---

## INSTALACIÓN PASO A PASO

### 1. Abrir VS Code en esta carpeta
Abre VS Code y luego: Archivo → Abrir Carpeta → selecciona esta carpeta.

### 2. Abrir la Terminal en VS Code
Menú → Terminal → Nueva Terminal

### 3. Instalar Flask
```
pip install flask
```

### 4. Ejecutar la aplicación
```
python app.py
```

### 5. Abrir en el navegador
```
http://localhost:5000
```

---

## USUARIOS DE PRUEBA

| Usuario      | Contraseña | Rol                    |
|--------------|------------|------------------------|
| admin        | admin123   | Administrador General  |
| cronometro1  | cron123    | Cronometrista          |
| director     | dir123     | Director de Recorrido  |

---

## MÓDULOS DEL SISTEMA

| Ruta         | Descripción                                      |
|--------------|--------------------------------------------------|
| /login       | Inicio de sesión                                 |
| /dashboard   | Centro de control ejecutivo en tiempo real       |
| /recorridos  | Gestión de recorridos procesionales              |
| /cuadrillas  | Configuración de cuadrillas y tiempos            |
| /homenajes   | Gestión de homenajes programados                 |
| /tablet      | Interfaz de campo para cronometristas            |

---

## CÓMO HACER UNA DEMO EN VIVO

1. Abre dos pestañas del navegador:
   - Pestaña 1: http://localhost:5000/dashboard (dashboard ejecutivo)
   - Pestaña 2: http://localhost:5000/tablet (tablet de campo)

2. En la pestaña TABLET:
   - Selecciona la Cuadrilla Nº 1
   - Presiona "INICIO CUADRILLA"
   - Verás el dashboard actualizarse automáticamente en 3 segundos

3. Para reiniciar la demo:
   - En el dashboard, presiona el botón "Reset Demo"

---

## ESTRUCTURA DE ARCHIVOS

```
procesional/
├── app.py                  ← Servidor principal Flask
├── requirements.txt        ← Dependencias Python
├── README.md               ← Este archivo
├── data/                   ← Base de datos (archivos JSON)
│   ├── recorridos.json
│   ├── cuadrillas.json
│   ├── homenajes.json
│   ├── eventos.json
│   └── usuarios.json
├── templates/              ← Páginas HTML
│   ├── base.html           ← Layout base con navbar
│   ├── login.html
│   ├── dashboard.html
│   ├── tablet.html
│   ├── recorridos.html
│   ├── nuevo_recorrido.html
│   ├── cuadrillas.html
│   └── homenajes.html
└── static/
    ├── css/main.css        ← Estilos (morado nazareno + dorado)
    └── js/main.js
```

---

## DATOS PRE-CARGADOS

Al ejecutar por primera vez se crean automáticamente:
- 2 recorridos procesionales (2024)
- 10 cuadrillas del Primer Recorrido
- 5 homenajes programados
- 3 usuarios de prueba

Para reiniciar los datos, elimina los archivos dentro de la carpeta `data/`
y vuelve a ejecutar `python app.py`.
