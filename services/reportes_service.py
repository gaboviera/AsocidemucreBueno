from models import Cita, Consulta, Paciente
from extensions import db
from sqlalchemy import func

class ReporteService:
    @staticmethod
    def resumen_dashboard():
        total_pacientes = Paciente.query.filter_by(activo=True).count()
        
        # Agrupa citas por estado
        citas_est = db.session.query(Cita.estado, func.count(Cita.id_cita)).group_by(Cita.estado).all()
        citas_map = dict(citas_est)
        
        atendidas = citas_map.get('Atendida', 0)
        pendientes = citas_map.get('Pendiente', 0)
        canceladas = citas_map.get('Cancelada', 0)
        
        return {
            "total_pacientes": total_pacientes,
            "citas_atendidas": atendidas,
            "citas_pendientes": pendientes,
            "citas_canceladas": canceladas,
            "total_citas_general": atendidas + pendientes + canceladas
        }
