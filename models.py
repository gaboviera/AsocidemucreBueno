from extensions import db
from datetime import datetime


# CATÁLOGOS SATÉLITES: DOMINIO CLÍNICO


class Especialidad(db.Model):
    __tablename__ = "especialidades"
    id_especialidad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, server_default='true')
    
    empleados = db.relationship("Empleado", backref="especialidad_rel", lazy=True)
    citas = db.relationship("Cita", backref="especialidad_solicitada", lazy=True)
    
class Enfermedad(db.Model):
    __tablename__ = "enfermedades"
    codigo_cie = db.Column(db.String(20), primary_key=True) # Codigo de clasificacion internacional
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, server_default='true')

    def __init__(self, codigo_cie, nombre, descripcion=None, activo=True, **kwargs):
        super(Enfermedad, self).__init__(**kwargs)
        self.codigo_cie = codigo_cie
        self.nombre = nombre
        self.descripcion = descripcion
        self.activo = activo

class Medicamento(db.Model):
    __tablename__ = "medicamentos"
    id_medicamento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_comercial = db.Column(db.String(150), nullable=False)
    compuesto = db.Column(db.String(150), nullable=False)
    presentacion = db.Column(db.String(100), nullable=False) # ej: Pastillas 500mg, Jarabe
    activo = db.Column(db.Boolean, default=True, server_default='true')
    
    indicaciones = db.relationship("IndicacionMedica", backref="remedio", lazy=True)

    def __init__(self, nombre_comercial, compuesto, presentacion, activo=True, **kwargs):
        super(Medicamento, self).__init__(**kwargs)
        self.nombre_comercial = nombre_comercial
        self.compuesto = compuesto
        self.presentacion = presentacion
        self.activo = activo

# RECURSOS HUMANOS: EMPLEADO Y ACCESO


class Empleado(db.Model):
    __tablename__ = "empleados"
    id_empleado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cedula = db.Column(db.String(15), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    rol_cargo = db.Column(db.String(40), nullable=False) # e.g., Medico, Enfermero, Secretaria
    telefono = db.Column(db.String(20), nullable=True)
    
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidades.id_especialidad'), nullable=True)
    
    usuarios = db.relationship("Usuario", backref="empleado_datos", uselist=False) # One to one
    horarios = db.relationship("HorarioMedico", backref="medico", lazy=True)
    citas_asignadas = db.relationship("Cita", backref="medico_asignado", lazy=True)
    consultas_atendidas = db.relationship("Consulta", backref="medico_tratante", lazy=True)

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id_empleado'), unique=True, nullable=True)
    paciente_cedula = db.Column(db.String(15), db.ForeignKey('pacientes.cedula'), unique=True, nullable=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, default=True, server_default='true')
    
    paciente_datos = db.relationship("Paciente", backref=db.backref("usuario", uselist=False))

class HorarioMedico(db.Model):
    __tablename__ = "horarios_medicos"
    id_horario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id_empleado'), nullable=False)
    dia_semana = db.Column(db.String(15), nullable=False) # Lunes, Martes, etc.
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    cupos_diarios = db.Column(db.Integer, nullable=False, default=10)

    def __init__(self, empleado_id, dia_semana, hora_inicio, hora_fin, cupos_diarios=10, **kwargs):
        super(HorarioMedico, self).__init__(**kwargs)
        self.empleado_id = empleado_id
        self.dia_semana = dia_semana
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.cupos_diarios = cupos_diarios


# GESTIÓN CLÍNICA: PACIENTE, CITAS, CONSULTA


class Paciente(db.Model):
    __tablename__ = "pacientes"
    cedula = db.Column(db.String(15), primary_key=True) # Cedula como PK!
    nombres = db.Column(db.String(60), nullable=False)
    apellidos = db.Column(db.String(60), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True, server_default='true')

    citas = db.relationship("Cita", backref="paciente_rel", lazy=True)
    consultas = db.relationship('Consulta', backref='paciente_rel', lazy=True)

class Cita(db.Model):
    __tablename__ = "citas"
    id_cita = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pacientes_cedula = db.Column(db.String(15), db.ForeignKey('pacientes.cedula'), nullable=False)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id_empleado'), nullable=False) # A que medico va
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidades.id_especialidad'), nullable=True)
    
    fecha_cita = db.Column(db.Date, nullable=False)
    hora_cita = db.Column(db.Time, nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(30), nullable=False) # Pendiente, Atendida, Cancelada
    motivo_cancelacion = db.Column(db.String(255), nullable=True) # Razón por la que se canceló

# Tabla asociativa Muchos a Muchos para Consultas y Diagnósticos (Enfermedades)
consulta_diagnosticos = db.Table('consulta_diagnosticos',
    db.Column('consulta_id', db.Integer, db.ForeignKey('consultas.id_consulta'), primary_key=True),
    db.Column('enfermedad_cod_cie', db.String(20), db.ForeignKey('enfermedades.codigo_cie'), primary_key=True)
)

class Consulta(db.Model):
    """Representa el acto médico, evolución del antiguo HistorialClinico"""
    __tablename__ = "consultas"
    id_consulta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paciente_cedula = db.Column(db.String(15), db.ForeignKey('pacientes.cedula'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('empleados.id_empleado'), nullable=False)
    
    # Eliminamos el enfermedad_cod_cie directo y lo volvemos Many-To-Many
    diagnosticos = db.relationship('Enfermedad', secondary=consulta_diagnosticos, lazy='subquery',
        backref=db.backref('consultas_relacionadas', lazy=True))
    
    presion_arterial = db.Column(db.String(15), nullable=True)
    temperatura = db.Column(db.Float, nullable=True)
    observaciones = db.Column(db.Text, nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    indicaciones = db.relationship("IndicacionMedica", backref="consulta_perteneciente", lazy=True)

    def __init__(self, paciente_cedula, medico_id, observaciones="", presion_arterial=None, temperatura=None, **kwargs):
        super(Consulta, self).__init__(**kwargs)
        self.paciente_cedula = paciente_cedula
        self.medico_id = medico_id
        self.observaciones = observaciones
        self.presion_arterial = presion_arterial
        self.temperatura = temperatura

class IndicacionMedica(db.Model):
    """Las indicaciones y récipe prescrito durante una consulta."""
    __tablename__ = "indicaciones_medicas"
    id_indicacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id_consulta'), nullable=False)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamentos.id_medicamento'), nullable=False)
    
    dosis = db.Column(db.String(100), nullable=False) # Ej: 1 cada 8 horas
    duracion_dias = db.Column(db.Integer, nullable=True) # Ej: 7 dias
    observaciones = db.Column(db.String(255), nullable=True)

    def __init__(self, consulta_id, medicamento_id, dosis, duracion_dias=None, observaciones=None, **kwargs):
        super(IndicacionMedica, self).__init__(**kwargs)
        self.consulta_id = consulta_id
        self.medicamento_id = medicamento_id
        self.dosis = dosis
        self.duracion_dias = duracion_dias
        self.observaciones = observaciones
