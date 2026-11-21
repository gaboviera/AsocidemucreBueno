from models import HistorialClinico # Importamos el modelo de Historia Clínica
from extensions import db             # Base de datos
from datetime import datetime        # Para manejar fechas y horas exactas

class HistorialService:
    @staticmethod
    def obtener_historial_paciente(paciente_id):
        # Buscamos todas las notas médicas registradas para una paciente específica
        # .order_by(...desc()) asegura que la consulta médica más reciente salga de primera en la lista
        return HistorialClinico.query.filter_by(pacientes_id_paciente=paciente_id).order_by(HistorialClinico.fecha_registro.desc()).all()

    @staticmethod 
    def agregar_nota(paciente_id, observaciones):
        # Crea una nueva entrada en el historial clínico ginecológico
        nueva_nota = HistorialClinico(
            pacientes_id_paciente=paciente_id, # ID de la paciente dueña del expediente
            observaciones=observaciones,       # Lo que el médico escribió (diagnóstico, tratamiento)
            fecha_registro=datetime.now()      # Captura la hora y fecha del servidor en este instante
        )
        db.session.add(nueva_nota) # Encola la nota para guardar
        db.session.commit()        # Guarda permanentemente en PostgreSQL
        return nueva_nota

    @staticmethod
    def eliminar_nota(id_historial):
        # Si por algún error se debe borrar una nota (requiere ID único)
        nota = HistorialClinico.query.get_or_404(id_historial)
        db.session.delete(nota) # Elimina físicamente el registro (Hard Delete)
        db.session.commit()     # Confirma la eliminación

