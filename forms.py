from wtforms import validators
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, TimeField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Optional

# --- FORMULARIO DE ACCESO (LOGIN) ---
class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(message="El usuario es obligatorio")])
    password = PasswordField("Contraseña", validators=[DataRequired(message="La contraseña es obligatoria")])
    submit = SubmitField("Iniciar Sesión")

# --- FORMULARIO DE REGISTRO DE TRABAJADORES ---
class RegistroForm(FlaskForm):
    cedula = StringField("Cedula", validators=[DataRequired(message="Obligatorio")])
    nombre_completo = StringField("Nombre Completo", validators=[DataRequired(message="Obligatorio")])
    username = StringField("Usuario", validators=[DataRequired(message="Obligatorio")])
    password = PasswordField("Contraseña", validators=[DataRequired(message="Obligatorio")])
    rol = StringField("Rol", validators=[DataRequired(message="Obligatorio")])
    especialidad_id = SelectField("Especialidad Clínica (Solo Médicos)", coerce=int, validators=[Optional()])
    submit = SubmitField("Registrar Usuario")

# --- FORMULARIO PARA DATOS DEL PACIENTE ---
class PacienteForm(FlaskForm):
    cedula = StringField("Cédula", validators=[DataRequired(message="La cédula es obligatoria")])
    nombres = StringField("Nombres", validators=[DataRequired(message="Los nombres son obligatorios")])
    apellidos = StringField("Apellidos", validators=[DataRequired(message="Los apellidos son obligatorios")])
    telefono = StringField("Teléfono", validators=[Optional()])
    fecha_nacimiento = DateField("Fecha de Nacimiento", format='%Y-%m-%d', validators=[DataRequired(message="La fecha es obligatoria")])
    submit = SubmitField("Guardar Paciente")

# --- FORMULARIO PARA AGENDAR CITAS MÉDICAS ---
class CitaForm(FlaskForm):
    paciente_cedula = SelectField("Seleccione la Paciente", coerce=str, validators=[DataRequired(message="Obligatorio")])
    especialidad_id = SelectField("Departamento Especializado", coerce=int, validators=[DataRequired(message="Seleccione un área")])
    doctor_id = SelectField("Médico que Atenderá", coerce=int, validators=[DataRequired(message="Obligatorio")])
    fecha = DateField("Día de la Cita", format='%Y-%m-%d', validators=[DataRequired(message="Obligatorio")])
    hora = TimeField("Hora de la Cita", format='%H:%M', validators=[DataRequired(message="Obligatorio")])
    motivo = TextAreaField("Motivo de la Cita", validators=[DataRequired(message="Escriba un motivo de consulta breve")], render_kw={"placeholder": "Ej. Control prenatal, Citología, Revisión de mamas, Eco transvaginal..."})
    estado = SelectField("Estado de Cita", choices=[
        ('Pendiente', 'Pendiente'), 
        ('Atendida', 'Atendida'), 
        ('Cancelada', 'Cancelada')
    ], validators=[DataRequired(message="Obligatorio")])
    submit = SubmitField("Agendar Cita Médica")

# --- NÚCLEO CLÍNICO: FORMULARIOS DE CONSULTA ---
class ConsultaForm(FlaskForm):
    presion_arterial = StringField("Tensión Arterial (mmHg)", validators=[Optional()], render_kw={"placeholder": "120/80"})
    temperatura = FloatField("Temperatura Corporal (°C)", validators=[Optional()], render_kw={"placeholder": "37.5"})
    
    diagnostico_libre = StringField("Diagnósticos (Separe con comas si son varios)", validators=[Optional()], render_kw={"placeholder": "Ej: Hipertensión, Diabetes...", "list": "catalogo_cie_datalist", "autocomplete": "off"})
    
    observaciones = TextAreaField("Evolución Médica:", 
                                  validators=[DataRequired(message="Debe escribir alguna observación clínica")],
                                  render_kw={"rows": 5, "placeholder": "Ej. FUM, Métodos anticonceptivos, ecos, resultados de Papanicolaou, embarazo..."})
    submit = SubmitField("Guardar Evolución Médica")

class IndicacionForm(FlaskForm):
    nombre_medicamento = StringField("Medicamento a Recetar", validators=[DataRequired()], render_kw={"placeholder": "Buscar o escribir medicamento...", "list": "catalogo_meds_datalist", "autocomplete": "off"})
    dosis = StringField("Dosis e Instrucción", validators=[DataRequired()], render_kw={"placeholder": "Ej. Tomar 1 cápsula cada 8 horas"})
    duracion_dias = IntegerField("Duración Tratamiento (Días)", validators=[Optional()], render_kw={"placeholder": "Ej. 7"})
    observaciones = StringField("Comentario Opcional", validators=[Optional()])
    submit = SubmitField("Añadir Farmaco a Receta")

# --- CATÁLOGOS SATÉLITES: FORMULARIOS BASE ---
class MedicamentoForm(FlaskForm):
    nombre_comercial = StringField("Nombre Comercial del Fármaco", validators=[DataRequired()])
    compuesto = StringField("Principio Activo (Compuesto)", validators=[DataRequired()])
    presentacion = StringField("Presentación (Ej. Cajas, Miligramos)", validators=[DataRequired()], render_kw={"placeholder": "Ampolla 10mg, Pastillas..."})
    submit = SubmitField("Añadir a Inventario")

class EnfermedadForm(FlaskForm):
    codigo_cie = StringField("Código Internacional CIE-10", validators=[DataRequired()], render_kw={"placeholder": "Ej. O00 o D06"})
    nombre = StringField("Nombre del Diagnóstico", validators=[DataRequired()])
    descripcion = TextAreaField("Descripción Informativa", validators=[Optional()], render_kw={"rows": 2})
    submit = SubmitField("Añadir Diagnóstico al Registro")

class EspecialidadForm(FlaskForm):
    nombre = StringField("Nombre de Especialidad Médica", validators=[DataRequired()])
    descripcion = TextAreaField("Descripción de Funciones", validators=[Optional()], render_kw={"rows": 2})
    submit = SubmitField("Guardar Departamento / Especialidad")

# --- FORMULARIO PÚBLICO: PARA QUE EL PACIENTE SE AUTOGESTIONE ---
class PublicCitaForm(FlaskForm):
    # Datos Personales
    cedula = StringField("Cédula de Identidad", validators=[DataRequired(message="La cédula es indispensable")])
    nombres = StringField("Tus Nombres", validators=[DataRequired(message="Escribe tus nombres")])
    apellidos = StringField("Tus Apellidos", validators=[DataRequired(message="Escribe tus apellidos")])
    telefono = StringField("Teléfono de Contacto", validators=[DataRequired(message="Necesitamos contactarte")])
    fecha_nacimiento = DateField("Fecha de Nacimiento", format='%Y-%m-%d', validators=[DataRequired(message="Dato requerido para tu historia")])
    
    # Datos de la Cita
    especialidad_id = SelectField("¿Qué servicio buscas?", coerce=int, validators=[DataRequired(message="Selecciona una especialidad")])
    doctor_id = SelectField("Selecciona el Especialista", coerce=int, validators=[DataRequired(message="Elige a tu médico")])
    fecha = DateField("Día Preferido", format='%Y-%m-%d', validators=[DataRequired(message="¿Qué día vendrás?")])
    hora = TimeField("Hora Tentativa", format='%H:%M', validators=[DataRequired(message="¿A qué hora?")])
    motivo = TextAreaField("¿Qué malestar o consulta presentas?", validators=[DataRequired(message="Dinos brevemente el motivo")], render_kw={"placeholder": "Descríbenos brevemente el motivo de tu consulta..."})
    
    submit = SubmitField("Confirmar mi Solicitud de Cita")

# --- FORMULARIO PARA CREAR CUENTA DE PACIENTE ---
class RegistroCuentaPacienteForm(FlaskForm):
    cedula = StringField("Cédula de Identidad", validators=[DataRequired(message="Necesario para asociar tu historial")])
    username = StringField("Nombre de Usuario", validators=[DataRequired(message="Obligatorio")])
    password = PasswordField("Contraseña", validators=[DataRequired(message="Obligatorio")])
    submit = SubmitField("Crear mi Cuenta de Paciente")

# --- FORMULARIO PARA CONFIGURAR HORARIOS DEL MÉDICO ---
class HorarioMedicoForm(FlaskForm):
    dia_semana = SelectField("Día de la Semana", choices=[
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo')
    ], validators=[DataRequired(message="Selecciona el día")])
    hora_inicio = TimeField("Hora de Inicio", format='%H:%M', validators=[DataRequired(message="Obligatorio")])
    hora_fin = TimeField("Hora de Fin", format='%H:%M', validators=[DataRequired(message="Obligatorio")])
    cupos_diarios = IntegerField("Cupos Máximos (Pacientes al día)", validators=[DataRequired(message="Define el límite de pacientes")])
    submit = SubmitField("Guardar Horario")


# --- FORMULARIO PARA QUE EL ADMIN ASIGNE HORARIOS ---
class AsignarHorarioForm(FlaskForm):
    doctor_id = SelectField("Médico que Atenderá", coerce=int, validators=[DataRequired(message="Obligatorio")])
    dia_semana = SelectField("Día de la Semana", choices=[
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo')
    ], validators=[DataRequired(message="Selecciona el día")])
    hora_inicio = TimeField("Hora de Inicio", format='%H:%M', validators=[DataRequired(message="Obligatorio")])
    hora_fin = TimeField("Hora de Fin", format='%H:%M', validators=[DataRequired(message="Obligatorio")])
    cupos_diarios = IntegerField("Cupos Máximos (Pacientes al día)", validators=[DataRequired(message="Define el límite de pacientes")])
    submit = SubmitField("Asignar Horario")
