# Guía de Desarrollo por Fases: Asocidemucre (Flask + PostgreSQL)

Esta guía detalla el orden lógico de implementación fase por fase para construir o replicar desde cero la arquitectura de este proyecto médico (`AsocidemucreBueno`), incluyendo los comandos necesarios.

---

## FASE 1: Preparación del Entorno y Dependencias
**Objetivo:** Configurar el entorno de trabajo e instalar las librerías base.

1. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install Flask Flask-SQLAlchemy Flask-Migrate psycopg2-binary python-dotenv Flask-WTF Werkzeug gunicorn
   ```
2. **Generar archivo de dependencias:**
   ```bash
   pip freeze > requirements.txt
   ```
3. **Crear archivo `.env`:**
   ```env
   DB_USER=postgres
   DB_PASSWORD=admin
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=asocidemucre_db
   SECRET_KEY=tu_clave_super_secreta
   ```

---

## FASE 2: Configuración de Base de Datos y Extensiones
**Objetivo:** Configurar las extensiones principales (`db` y `migrate`) fuera de `app.py` para evitar dependencias circulares.

1. **Crear archivo `extensions.py`:**
   - Instanciar SQLAlchemy (`db = SQLAlchemy()`).
   - Instanciar Migrate (`migrate = Migrate()`).
2. **Crear archivo base `app.py`:**
   - Cargar variables con `load_dotenv()`.
   - Configurar la URL de la base de datos usando las variables del `.env`.
   - Inicializar la app: `db.init_app(app)` y `migrate.init_app(app, db)`.

---

## FASE 3: Definición de Modelos (Capa de Datos)
**Objetivo:** Traducir las entidades del dominio (Pacientes, Citas, Usuarios, Empleados) a tablas.

1. **Crear archivo `models.py`:**
   - Importar `db` desde `extensions`.
   - Crear las clases heredando de `db.Model`.
   - *Entidades clave:* `Usuario`, `Empleado`, `Paciente`, `Cita`, `Consulta`, `Medicamento`, `Enfermedad`, `Especialidad`.
2. **Inicializar Alembic (Migraciones):**
   ```bash
   flask db init
   ```
3. **Generar y aplicar la primera migración:**
   ```bash
   flask db migrate -m "Creación inicial de tablas"
   flask db upgrade
   ```

---

## FASE 4: Capa de Formularios (WTForms)
**Objetivo:** Crear formularios seguros para validación de datos (Backend/Frontend).

1. **Crear archivo `forms.py`:**
   - Crear clases de formulario heredando de `FlaskForm`.
   - *Formularios:* `LoginForm`, `RegistroForm`, `PacienteForm`, `CitaForm`, etc.
   - Usar validadores como `DataRequired`, `Length`, `Optional`.

---

## FASE 5: Capa de Servicios (Lógica de Negocio)
**Objetivo:** Separar las reglas de negocio y las consultas a la base de datos fuera de las rutas de `app.py`.

1. **Crear directorio `services/`:**
   - `usuario_service.py`: Lógica de autenticación, creación de usuarios, hasheo de contraseñas.
   - `paciente_service.py`: CRUD de pacientes (buscar, crear, editar, eliminar lógicamente).
   - `cita_services.py`: Lógica para agendar citas, validación de conflictos de horarios.
   - `consulta_service.py` y `catalogos_service.py` para el manejo de historiales, enfermedades y medicamentos.

---

## FASE 6: Rutas y Controladores (`app.py`)
**Objetivo:** Definir las URLs (Endpoints) y conectar las vistas con los servicios.

1. **Modificar `app.py`:**
   - Implementar manejo de sesión (`session['id_usuario']`, `session['rol']`).
   - Crear rutas principales protegidas por inicio de sesión:
     - `@app.route('/dashboard')`
     - `@app.route('/pacientes')`
     - `@app.route('/citas')`
   - Conectar peticiones `GET`/`POST` con los servicios.
   - Integrar mensajes de retroalimentación usando `flash("Mensaje", "success")`.

---

## FASE 7: Plantillas e Interfaz (Frontend)
**Objetivo:** Crear la interfaz HTML utilizando Jinja2.

1. **Estructura en `templates/`:**
   - `base.html`: Plantilla maestra con la barra de navegación lateral y el `<head>` (con Tailwind/Bootstrap o CSS crudo).
   - `index.html`: Dashboard principal heredando de `base.html`.
   - `login.html`: Pantalla de inicio de sesión.
   - Carpetas por módulo: `pacientes/`, `citas/`, `enfermedades/`.
   - `_paginacion.html`: Componente reutilizable para la paginación de tablas.

---

## FASE 8: Dockerización y Despliegue
**Objetivo:** Empaquetar la aplicación para que corra en cualquier lugar sin instalar dependencias globales.

1. **Crear `Dockerfile`:**
   - Instalar python-slim, dependencias del sistema y librerías de Python.
   - Configurar `gunicorn` para servir Flask de manera concurrente: `CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]`
2. **Configurar `docker-compose.yml`:**
   - Servicio `db`: Contenedor oficial de PostgreSQL.
   - Servicio `web`: Construcción desde el Dockerfile vinculando el puerto 5000.
3. **Comandos de ejecución en Docker:**
   ```bash
   # Construir y levantar contenedores
   docker-compose up --build -d
   ```
4. **Restaurar respaldo local al contenedor (Opcional si migras bases de datos):**
   ```bash
   docker exec -i asocidemucre_db_container pg_restore -U postgres -d asocidemucre_db -O -x --clean < Asosidemucre.sql
   ```
