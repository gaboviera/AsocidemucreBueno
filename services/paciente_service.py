from models import Paciente # Importamos el modelo de la tabla Paciente
from extensions import db    # Importamos la conexión a la base de datos

class PacienteService:
    @staticmethod
    def obtener_todos(medico_id=None, page=1, per_page=10):
        # Trae todos los pacientes que estén activos (Borrado Lógico) y los ordena por nombre
        query = Paciente.query.filter_by(activo=True)
        if medico_id:
            from models import Cita
            query = query.join(Cita, Cita.pacientes_cedula == Paciente.cedula).filter(Cita.empleado_id == medico_id).distinct()
        if page:
            return query.order_by(Paciente.nombres).paginate(page=page, per_page=per_page, error_out=False)
        return query.order_by(Paciente.nombres).all()

    @staticmethod
    def buscar(q, medico_id=None, page=1, per_page=10):
        query = Paciente.query.filter(
            Paciente.activo == True, 
            (Paciente.cedula.ilike(f"%{q}%")) | 
            (Paciente.nombres.ilike(f"%{q}%")) | 
            (Paciente.apellidos.ilike(f"%{q}%"))
        )
        if medico_id:
            from models import Cita
            query = query.join(Cita, Cita.pacientes_cedula == Paciente.cedula).filter(Cita.empleado_id == medico_id).distinct()
        if page:
            return query.order_by(Paciente.nombres).paginate(page=page, per_page=per_page, error_out=False)
        return query.order_by(Paciente.nombres).all()

    @staticmethod
    def obtener_por_cedula(cedula):
         # Busca un paciente específico por su cédula (nueva Primary Key). 
         return Paciente.query.get_or_404(cedula)

    @staticmethod
    def agregar_paciente(cedula, nombres, apellidos, telefono, fecha_nacimiento):
        nuevo_paciente = Paciente(
            cedula=cedula,
            nombres=nombres,
            apellidos=apellidos,
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento
        )    
        db.session.add(nuevo_paciente)
        db.session.commit()
        return nuevo_paciente

    @staticmethod
    def editar_paciente(cedula, nombres, apellidos, telefono, fecha_nacimiento):
        paciente = PacienteService.obtener_por_cedula(cedula)
        paciente.nombres = nombres
        paciente.apellidos = apellidos 
        paciente.telefono = telefono
        paciente.fecha_nacimiento = fecha_nacimiento
        db.session.commit()
        return paciente

    @staticmethod
    def eliminar_paciente(cedula):
        paciente = PacienteService.obtener_por_cedula(cedula)
        paciente.activo = False  
        db.session.commit()      
        return True