from models import Empleado, Usuario
from extensions import db
from werkzeug.security import generate_password_hash

class UsuarioService:
    @staticmethod
    def crear_empleado_y_usuario(cedula, nombre_completo, username, password, rol_cargo, especialidad_id=None):
        nuevo_empleado = Empleado(
            cedula=cedula,
            nombre_completo=nombre_completo,
            rol_cargo=rol_cargo,
            especialidad_id=especialidad_id
        )
        db.session.add(nuevo_empleado)
        db.session.flush() 
        
        nuevo_usuario = Usuario(
            empleado_id=nuevo_empleado.id_empleado,
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return nuevo_usuario

    @staticmethod
    def crear_usuario_paciente(cedula_paciente, username, password):
        nuevo_usuario = Usuario(
            paciente_cedula=cedula_paciente,
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return nuevo_usuario

    @staticmethod
    def obtener_todos_los_empleados(q="", empleado_id=None, page=1, per_page=10):
        query = Empleado.query
        
        if empleado_id:
            query = query.filter(Empleado.id_empleado == empleado_id)
            
        if q:
            q_lower = f"%{q.lower()}%"
            # Join with Usuario to search by username
            query = query.outerjoin(Usuario).filter(
                (Empleado.nombre_completo.ilike(q_lower)) |
                (Empleado.cedula.ilike(q_lower)) |
                (Usuario.username.ilike(q_lower))
            )
            
        return query.order_by(Empleado.nombre_completo).paginate(page=page, per_page=per_page, error_out=False)
