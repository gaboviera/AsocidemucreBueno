from flask_sqlalchemy import SQLAlchemy # Importamos el motor para conectar Flask con bases de datos (ORM)
from flask_migrate import Migrate        # Importamos la herramienta para hacer cambios en la estructura de la base de datos

db = SQLAlchemy()  # Creamos la instancia principal de la base de datos (se usa en los modelos y servicios)
migrate = Migrate() # Creamos la instancia para manejar las migraciones (historial de cambios en las tablas)

