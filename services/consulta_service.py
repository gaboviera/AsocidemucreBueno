from models import Consulta, IndicacionMedica
from extensions import db

class ConsultaService:
    @staticmethod
    def obtener_historial_paciente(paciente_cedula):
        return Consulta.query.filter_by(paciente_cedula=paciente_cedula).order_by(Consulta.fecha_registro.desc()).all()

    @staticmethod
    def agregar_consulta(paciente_cedula, medico_id, diagnosticos=None, 
                         presion_arterial=None, temperatura=None, observaciones="", cita_id_para_cerrar=None):
        nueva_consulta = Consulta(
            paciente_cedula=paciente_cedula,
            medico_id=medico_id,
            presion_arterial=presion_arterial,
            temperatura=temperatura,
            observaciones=observaciones
        )
        
        if diagnosticos:
            for diag in diagnosticos:
                nueva_consulta.diagnosticos.append(diag)
                
        db.session.add(nueva_consulta)
        
        # Cerrar el lazo del ecosistema: Si originó en una Cita, marcarla Atendida (aunque ya no se vincule en BD a la consulta)
        if cita_id_para_cerrar:
            from models import Cita
            cita_origen = Cita.query.get(cita_id_para_cerrar)
            if cita_origen:
                cita_origen.estado = "Atendida"
                
        db.session.commit()
        return nueva_consulta
