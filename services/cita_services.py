from models import Cita, Paciente, Empleado, Especialidad
from extensions import db

class CitaService:
    @staticmethod
    def obtener_todas(medico_id=None, estado=None, fecha_inicio=None, fecha_fin=None, page=1, per_page=10):
        query = Cita.query
        if medico_id:
            query = query.filter_by(empleado_id=medico_id)
        if estado:
            query = query.filter_by(estado=estado)
        if fecha_inicio:
            query = query.filter(Cita.fecha_cita >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Cita.fecha_cita <= fecha_fin)
            
        if page:
            return query.order_by(Cita.fecha_cita.asc(), Cita.hora_cita.asc()).paginate(page=page, per_page=per_page, error_out=False)
        return query.order_by(Cita.fecha_cita.asc(), Cita.hora_cita.asc()).all()

    @staticmethod
    def buscar(q, medico_id=None, estado=None, fecha_inicio=None, fecha_fin=None, page=1, per_page=10):
        query = Cita.query.join(Paciente).join(Empleado).filter(
            (Paciente.cedula.ilike(f"%{q}%")) |
            (Paciente.nombres.ilike(f"%{q}%")) |
            (Paciente.apellidos.ilike(f"%{q}%")) |
            (Empleado.nombre_completo.ilike(f"%{q}%")) |
            (Cita.motivo.ilike(f"%{q}%")) |
            (Cita.estado.ilike(f"%{q}%"))
        )
        if medico_id:
            query = query.filter(Cita.empleado_id == medico_id)
        if estado:
            query = query.filter(Cita.estado == estado)
        if fecha_inicio:
            query = query.filter(Cita.fecha_cita >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Cita.fecha_cita <= fecha_fin)
            
        if page:
            return query.order_by(Cita.fecha_cita.asc(), Cita.hora_cita.asc()).paginate(page=page, per_page=per_page, error_out=False)
        return query.order_by(Cita.fecha_cita.asc(), Cita.hora_cita.asc()).all()

    @staticmethod
    def obtener_por_id(id_cita):
        return Cita.query.get_or_404(id_cita)

    @staticmethod 
    def agregar_cita(pacientes_cedula, empleado_id, especialidad_id, fecha, hora, motivo, estado):
        nueva_cita = Cita(
            pacientes_cedula=pacientes_cedula,
            empleado_id=empleado_id,
            especialidad_id=especialidad_id,
            fecha_cita=fecha,
            hora_cita=hora,
            motivo=motivo,
            estado=estado
        )    
        db.session.add(nueva_cita)
        db.session.commit()
        return nueva_cita
    
    @staticmethod
    def editar_cita(id_cita, pacientes_cedula, empleado_id, especialidad_id, fecha, hora, motivo, estado):
        cita = CitaService.obtener_por_id(id_cita)
        cita.pacientes_cedula = pacientes_cedula
        cita.empleado_id = empleado_id
        cita.especialidad_id = especialidad_id
        cita.fecha_cita = fecha
        cita.hora_cita = hora
        cita.motivo = motivo
        cita.estado = estado
        db.session.commit()
        return cita

    @staticmethod
    def eliminar_cita(id_cita, motivo_cancelacion=None):
        cita = CitaService.obtener_por_id(id_cita)
        cita.estado = 'Cancelada'
        if motivo_cancelacion:
            cita.motivo_cancelacion = motivo_cancelacion
        db.session.commit()
        return True
