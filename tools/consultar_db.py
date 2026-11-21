from app import app # Importamos nuestra aplicación Flask principal
from models import Usuario, Paciente # Importamos los modelos de las tablas que queremos espiar

def consultar_base_de_datos():
    # 'with app.app_context()' es necesario para que Flask nos deje hablar con la base de datos de manera externa
    with app.app_context():
        # Consulta todos los usuarios (doctores, admins, secretarias) en una lista
        usuarios = Usuario.query.all()
        # Consulta todos los pacientes registrados en una lista
        pacientes = Paciente.query.all()

        print("\n===============================")
        print("  USUARIOS (Doctores/Secretarias) ")
        print("===============================")
        if not usuarios:
            print("No hay usuarios registrados.")
        for u in usuarios:
            # Imprime cada usuario detalladamente en la consola (terminal)
            print(f"ID: {u.id_usuario} | Rol: {u.rol} | Usuario: {u.username} | Nombre Completo: {u.nombre_completo}")

        print("\n===============================")
        print("        PACIENTES REGISTRADAS     ")
        print("===============================")
        if not pacientes:
            print("No hay pacientes registradas.")
        for p in pacientes:
            # Imprime cada paciente registrado con su cédula y nombre
            print(f"ID: {p.id_paciente} | Cédula: {p.cedula} | Nombres: {p.nombres} {p.apellidos} | Teléfono: {p.telefono or 'N/A'}")
            
        print("\n===============================\n")

# Si ejecutamos este archivo directamente en la terminal: 'python consultar_db.py'
if __name__ == "__main__":
    consultar_base_de_datos() # Llama a la función mágica para ver los datos

