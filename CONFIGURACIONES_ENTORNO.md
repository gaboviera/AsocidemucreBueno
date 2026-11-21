# Historial de Configuraciones del Proyecto

Este documento resume las configuraciones realizadas en el equipo local y en el proyecto para su funcionamiento mediante contenedores y su control de versiones.

## 1. Configuración de Docker (Contenerización)
- **Dockerfile**: Se creó un archivo `Dockerfile` basado en `python:3.11-slim`. Este archivo instala las dependencias de sistema y de Python necesarias. Además, se configuró el servidor **Gunicorn** como servidor WSGI de producción para ejecutar la aplicación Flask en el puerto `5000`.
- **docker-compose.yml**: Se agregó el servicio `web` al archivo original, vinculándolo con el servicio de base de datos `db` (PostgreSQL 17). Se configuraron las variables de entorno para que el contenedor web se conecte directamente a la base de datos de Docker.
- **Codificación**: Se actualizó la codificación del archivo `requirements.txt` a `UTF-8` para evitar conflictos al instalar paquetes dentro del entorno Linux del contenedor Docker.

## 2. Restauración de Base de Datos
- **Reinicio del Volumen**: Para asegurar una base de datos limpia, se eliminó el volumen de datos de PostgreSQL creado previamente por Docker.
- **Importación de Datos**: Se utilizó el respaldo local `Asosidemucre.sql` (formato pg_dump) para restaurar la estructura y los datos iniciales dentro del contenedor de base de datos.
  - El comando usado internamente fue: `pg_restore -U postgres -d asocidemucre_db ...`

## 3. Seguridad y Control de Versiones (Git/GitHub)
- **.gitignore**: Se creó un archivo `.gitignore` estricto que previene que información sensible se envíe al repositorio. Archivos excluidos:
  - Archivos `.env`
  - Respaldo de la base de datos (`Asosidemucre.sql` y `/postgres_data`)
  - Entornos virtuales (`.venv`) y cachés de Python (`__pycache__`)
  - Carpetas de configuración de IDEs (`.vscode`, `.idea`, etc.)
- **Inicialización Git**: Se inicializó el repositorio local con `git init` y se realizó el primer commit de la base del proyecto (69 archivos).
- **Autenticación Global de GitHub**: Se configuró globalmente Git en el sistema operativo para reescribir todas las URL de `https://github.com/` e inyectar de forma transparente el Token de Acceso Personal (PAT) del usuario. El comando utilizado fue:
  ```bash
  git config --global url."https://TU_TOKEN_AQUI@github.com/".insteadOf "https://github.com/"
  ```
  - Esto significa que cualquier comando futuro hacia GitHub (ej. `git push`, `git pull`) se autenticará automáticamente sin pedir contraseñas.
- **Conexión a Remoto**: Se conectó el repositorio local con `https://github.com/gaboviera/asosidemucre.git` y se subió (`push`) la rama `master`.
