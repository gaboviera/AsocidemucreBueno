from forms import PacienteForm, CitaForm, ConsultaForm, LoginForm, RegistroForm
from psycopg2.extras import RealDictConnection 
from services.paciente_service import PacienteService
from services.cita_services import CitaService
from services.consulta_service import ConsultaService 
from services.usuario_service import UsuarioService
from services.reportes_service import ReporteService
from services.catalogos_service import MedicamentoService, EnfermedadService, EspecialidadService
import os 
from flask import Flask, render_template, redirect, request, url_for, flash, session

from dotenv import load_dotenv 
from extensions import db, migrate
from sqlalchemy import func

import models
from models import Usuario, Empleado, Paciente, Cita, Consulta, Medicamento, Enfermedad, Especialidad, IndicacionMedica
from werkzeug.security import generate_password_hash, check_password_hash
from forms import (PacienteForm, CitaForm, ConsultaForm, LoginForm, 
                   RegistroForm, MedicamentoForm, EnfermedadForm, EspecialidadForm, IndicacionForm, PublicCitaForm, RegistroCuentaPacienteForm, HorarioMedicoForm, AsignarHorarioForm)

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret")

USER = os.getenv("DB_USER", "postgres")
PASSWORD = os.getenv("DB_PASSWORD", "postgres")
HOST = os.getenv("DB_HOST", "localhost")
PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME") or "asocidemucre_db"

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 

db.init_app(app)
migrate.init_app(app, db)

# --- Formateador de fechas en español (sin depender del locale del SO) ---
DIAS_ES = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
MESES_ES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def fecha_en_espanol(fecha):
    """Devuelve una fecha formateada como 'Miércoles, 22 de Abril de 2026'."""
    dia_semana = DIAS_ES[fecha.weekday()]
    mes = MESES_ES[fecha.month - 1]
    return f"{dia_semana}, {fecha.day:02d} de {mes} de {fecha.year}"


# --- DASHBOARD / PANEL DE CONTROL ---
@app.route("/")
def index():
    if "id_usuario" in session:
        if session.get('rol') == 'Paciente':
            return redirect(url_for("mi_historial"))
        else:
            return redirect(url_for("dashboard"))
    return render_template("publico/landing.html")

@app.route("/dashboard")
def dashboard():
    if "id_usuario" not in session:
        return redirect(url_for("login"))
        
    from datetime import date
    hoy = date.today()
    
    stats = ReporteService.resumen_dashboard()
    
    citas_hoy_query = Cita.query.filter_by(fecha_cita=hoy)
    total_citas_hoy = citas_hoy_query.count() 
    pendientes_hoy = citas_hoy_query.filter_by(estado='Pendiente').count() 
    atendidas_hoy = citas_hoy_query.filter_by(estado='Atendida').count() 
    citas_canceladas = stats['citas_canceladas']
    total_pacientes = stats['total_pacientes']
    
    proximas_citas = citas_hoy_query.filter(Cita.estado != 'Cancelada').order_by(Cita.hora_cita).limit(5).all()

    return render_template("index.html", 
                           total_pacientes=total_pacientes,
                           total_citas_hoy=total_citas_hoy,
                           pendientes_hoy=pendientes_hoy,
                           atendidas_hoy=atendidas_hoy,
                           citas_canceladas=citas_canceladas,
                           citas_atendidas_general=stats['citas_atendidas'],
                           citas_pendientes_general=stats['citas_pendientes'],
                           total_citas_general=stats['total_citas_general'],
                           proximas_citas=proximas_citas,
                           hoy=hoy,
                           fecha_formateada=fecha_en_espanol(hoy))

# --- INICIO DE SESIÓN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.username.data).first()
        
        if usuario and check_password_hash(usuario.password, form.password.data): 
            session['id_usuario'] = usuario.id_usuario
            session['username'] = usuario.username
            
            if usuario.empleado_id:
                session['nombre'] = usuario.empleado_datos.nombre_completo
                session['rol'] = usuario.empleado_datos.rol_cargo
                session['empleado_id'] = usuario.empleado_datos.id_empleado
                flash(f"¡Bienvenido {session['nombre']}!", "success")
                return redirect(url_for("dashboard")) 
            elif usuario.paciente_cedula:
                session['nombre'] = f"{usuario.paciente_datos.nombres} {usuario.paciente_datos.apellidos}"
                session['rol'] = 'Paciente'
                session['paciente_cedula'] = usuario.paciente_cedula
                flash(f"¡Bienvenido {session['nombre']}!", "success")
                return redirect(url_for("mi_historial"))
        else: 
            flash("Usuario o contraseña incorrectos", "danger") 
            
    return render_template("login.html", form=form) 

# --- REGISTRO ---
@app.route("/registro", methods=["GET", "POST"])
def registro():
    form = RegistroForm()
    
    # Cargar las especialidades disponibles
    lista_especialidades = EspecialidadService.obtener_todas()
    form.especialidad_id.choices = [(0, '-- No aplica / Sin asignar --')] + [(e.id_especialidad, e.nombre) for e in lista_especialidades]
    
    if form.validate_on_submit():
        esp_val = form.especialidad_id.data if form.especialidad_id.data != 0 else None
        
        if Usuario.query.filter_by(username=form.username.data).first():
            flash("El nombre de usuario ya está en uso. Por favor elige otro.", "danger")
            return render_template("registro.html", form=form)
            
        if Empleado.query.filter_by(cedula=form.cedula.data).first():
            flash("Ya existe un empleado registrado con esa cédula.", "danger")
            return render_template("registro.html", form=form)
        
        UsuarioService.crear_empleado_y_usuario(
            cedula=form.cedula.data,
            nombre_completo=form.nombre_completo.data,
            username=form.username.data,
            password=form.password.data,
            rol_cargo=form.rol.data,
            especialidad_id=esp_val
        )
        flash("¡El empleado fue registrado con éxito!", "success")
        return redirect(url_for("registro"))
        
    return render_template("registro.html", form=form)

@app.route("/logout")
def logout():
    session.clear() 
    flash("Has cerrado sesión exitosamente", "info")
    return redirect(url_for("login"))

# --- PORTAL DEL PACIENTE (NUEVO) ---
@app.route("/registro_paciente", methods=["GET", "POST"])
def registro_paciente():
    form = RegistroCuentaPacienteForm()
    if form.validate_on_submit():
        # Validar que el paciente exista
        paciente_existe = Paciente.query.filter_by(cedula=form.cedula.data).first()
        if not paciente_existe:
            flash("Tu cédula no está registrada en nuestra clínica. Primero debes agendar una cita o comunicarte con recepción.", "danger")
            return redirect(url_for("registro_paciente"))
            
        # Validar que no tenga cuenta ya
        if Usuario.query.filter_by(paciente_cedula=form.cedula.data).first():
            flash("Ya existe una cuenta para esta cédula.", "warning")
            return redirect(url_for("login"))
            
        # Validar username
        if Usuario.query.filter_by(username=form.username.data).first():
            flash("Ese nombre de usuario ya está en uso. Elige otro.", "danger")
            return redirect(url_for("registro_paciente"))
            
        UsuarioService.crear_usuario_paciente(
            cedula_paciente=form.cedula.data,
            username=form.username.data,
            password=form.password.data
        )
        flash("¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))
        
    return render_template("publico/registro_paciente.html", form=form)

@app.route("/mi_historial")
def mi_historial():
    if "id_usuario" not in session or session.get("rol") != "Paciente":
        flash("Acceso denegado. Debes iniciar sesión como paciente.", "danger")
        return redirect(url_for("login"))
        
    cedula = session.get("paciente_cedula")
    paciente_actual = PacienteService.obtener_por_cedula(cedula)
    
    # Obtenemos sus consultas con sus indicaciones
    from services.consulta_service import ConsultaService
    notas_historial = ConsultaService.obtener_historial_paciente(cedula)
    
    return render_template("pacientes/mi_historial.html", 
                           paciente=paciente_actual, 
                           historial=notas_historial)

# --- PERSONAL CLÍNICO ---
@app.route("/personal")
def personal_clinica():
    if "id_usuario" not in session:
        return redirect(url_for("login"))
    
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    
    # Restricción: Si no es Administrador, solo puede verse a sí mismo
    empleado_id_filtro = None
    if session.get("rol") not in ["Administrador", "Administradora"]:
        empleado_id_filtro = session.get("empleado_id")
        
    personal = UsuarioService.obtener_todos_los_empleados(q=query, empleado_id=empleado_id_filtro, page=page)
        
    return render_template("personal/lista_personal.html", personal=personal, query=query)

@app.route("/personal/<int:id_empleado>/cambiar_password", methods=["POST"])
def cambiar_password_personal(id_empleado):
    if "id_usuario" not in session: return redirect(url_for("login"))
    
    # Solo administradores o el mismo empleado pueden cambiar la contraseña
    if session.get("rol") not in ["Administrador", "Administradora"] and session.get("empleado_id") != id_empleado:
        flash("No tienes permiso para cambiar esta contraseña.", "danger")
        return redirect(url_for("personal_clinica"))
        
    nueva_password = request.form.get("nueva_password")
    if nueva_password:
        usuario = Usuario.query.filter_by(empleado_id=id_empleado).first()
        if usuario:
            usuario.password = generate_password_hash(nueva_password, method='pbkdf2:sha256')
            db.session.commit()
            flash("Contraseña actualizada exitosamente.", "success")
        else:
            flash("Este empleado no tiene cuenta de usuario activa.", "warning")
            
    return redirect(request.referrer or url_for("personal_clinica"))

@app.route("/mis_horarios", methods=["GET", "POST"])
def mis_horarios():
    if "id_usuario" not in session or session.get("rol") not in ["Medico", "Médico", "Administrador"]:
        flash("Acceso denegado. Solo personal médico puede gestionar sus horarios.", "danger")
        return redirect(url_for("index"))
        
    form = HorarioMedicoForm()
    empleado_id = session.get("empleado_id")
    
    if form.validate_on_submit():
        from models import HorarioMedico
        nuevo_horario = HorarioMedico(
            empleado_id=empleado_id,
            dia_semana=form.dia_semana.data,
            hora_inicio=form.hora_inicio.data,
            hora_fin=form.hora_fin.data,
            cupos_diarios=form.cupos_diarios.data
        )
        db.session.add(nuevo_horario)
        db.session.commit()
        flash(f"Horario de {form.dia_semana.data} agregado exitosamente.", "success")
        return redirect(url_for("mis_horarios"))
        
    from models import HorarioMedico, Cita
    mis_turnos = HorarioMedico.query.filter_by(empleado_id=empleado_id).order_by(HorarioMedico.dia_semana, HorarioMedico.hora_inicio).all()
    
    from datetime import date, timedelta
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    hoy = date.today()
    proximos_cupos = {}
    
    for turno in mis_turnos:
        if turno.dia_semana in dias_semana:
            target_idx = dias_semana.index(turno.dia_semana)
            days_ahead = target_idx - hoy.weekday()
            if days_ahead < 0:
                days_ahead += 7
            proxima_fecha = hoy + timedelta(days=days_ahead)
            
            citas_agendadas = Cita.query.filter_by(
                empleado_id=empleado_id, 
                fecha_cita=proxima_fecha
            ).filter(Cita.estado != 'Cancelada').count()
            
            disponibles = turno.cupos_diarios - citas_agendadas
            proximos_cupos[turno.id_horario] = {
                'fecha': proxima_fecha.strftime('%d/%m/%Y'),
                'disponibles': disponibles
            }
            
    return render_template("personal/mis_horarios.html", form=form, horarios=mis_turnos, proximos_cupos=proximos_cupos)

@app.route("/mis_horarios/eliminar/<int:id_horario>")
def eliminar_horario(id_horario):
    if "id_usuario" not in session or session.get("rol") not in ["Medico", "Médico", "Administrador"]:
        return redirect(url_for("login"))
        
    from models import HorarioMedico
    turno = HorarioMedico.query.get_or_404(id_horario)
    
    # Validar que el turno le pertenezca a quien lo borra o que sea Administrador
    if turno.empleado_id != session.get("empleado_id") and session.get("rol") not in ["Super Admin", "Administrador", "Administradora"]:
        flash("No puedes eliminar un horario que no es tuyo.", "danger")
        return redirect(url_for("mis_horarios"))
        
    db.session.delete(turno)
    db.session.commit()
    flash("El turno ha sido eliminado.", "info")
    return redirect(request.referrer or url_for("mis_horarios"))

@app.route("/admin/asignar_horario", methods=["GET", "POST"])
def admin_asignar_horario():
    if "id_usuario" not in session or session.get("rol") not in ["Administrador", "Administradora"]:
        flash("Acceso denegado. Solo los administradores pueden asignar horarios.", "danger")
        return redirect(url_for("index"))
        
    form = AsignarHorarioForm()
    
    # Cargar los médicos disponibles
    doctores = Empleado.query.filter(Empleado.rol_cargo.in_(['Medico', 'Médico'])).all()
    form.doctor_id.choices = [(0, '-- Seleccione Médico --')] + [(d.id_empleado, f"Dr/a. {d.nombre_completo}") for d in doctores]
    
    if form.validate_on_submit():
        if form.doctor_id.data == 0:
            flash("Debes seleccionar un médico.", "warning")
            return redirect(url_for("admin_asignar_horario"))
            
        from models import HorarioMedico
        nuevo_horario = HorarioMedico(
            empleado_id=form.doctor_id.data,
            dia_semana=form.dia_semana.data,
            hora_inicio=form.hora_inicio.data,
            hora_fin=form.hora_fin.data,
            cupos_diarios=form.cupos_diarios.data
        )
        db.session.add(nuevo_horario)
        db.session.commit()
        
        # Obtener el nombre del médico para el mensaje
        medico = Empleado.query.get(form.doctor_id.data)
        flash(f"Horario asignado exitosamente al Dr/a. {medico.nombre_completo}.", "success")
        return redirect(url_for("admin_asignar_horario"))
        
    from models import HorarioMedico
    # Listar todos los horarios asignados para mostrarlos
    todos_horarios = HorarioMedico.query.join(Empleado).order_by(Empleado.nombre_completo, HorarioMedico.dia_semana, HorarioMedico.hora_inicio).all()
    
    return render_template("personal/admin_asignar_horario.html", form=form, horarios=todos_horarios)

# --- PACIENTES ---
@app.route("/pacientes")
def lista_pacientes():
    if "id_usuario" not in session:
        return redirect(url_for("login"))

    query = request.args.get("q")
    page = request.args.get("page", 1, type=int)
    
    # Eliminado el filtro de privacidad para que los médicos puedan ver y referir a todos los pacientes
    limite_medico = None
    
    if query:
        pacientes = PacienteService.buscar(query, medico_id=limite_medico, page=page)
    else:
        pacientes = PacienteService.obtener_todos(medico_id=limite_medico, page=page)

    return render_template("pacientes/lista_pacientes.html", pacientes=pacientes, query=query)

@app.route("/pacientes/nuevo", methods=["GET", "POST"])    
def nuevo_paciente():
    if "id_usuario" not in session:
        return redirect(url_for("login"))

    form = PacienteForm()
    if form.validate_on_submit():
        PacienteService.agregar_paciente(
            cedula=form.cedula.data,
            nombres=form.nombres.data,
            apellidos=form.apellidos.data,
            telefono=form.telefono.data,
            fecha_nacimiento=form.fecha_nacimiento.data
        )  
        flash("Paciente registrado con éxito.", "success")
        return redirect(url_for("lista_pacientes"))

    return render_template("pacientes/formulario_paciente.html", form=form, accion="Nuevo")

@app.route("/pacientes/editar/<string:cedula>", methods=["GET", "POST"])
def editar_paciente(cedula):
    if "id_usuario" not in session:
        return redirect(url_for("login"))

    paciente_actual = PacienteService.obtener_por_cedula(cedula)
    form = PacienteForm(obj=paciente_actual)

    if form.validate_on_submit():
        PacienteService.editar_paciente(
            cedula=cedula,
            nombres=form.nombres.data,
            apellidos=form.apellidos.data,
            telefono=form.telefono.data,
            fecha_nacimiento=form.fecha_nacimiento.data
        )
        flash(f"Datos actualizados exitosamente", "success")
        return redirect(url_for("lista_pacientes"))

    return render_template("pacientes/formulario_paciente.html", form=form, accion="Editar")

@app.route("/pacientes/eliminar/<string:cedula>")
def eliminar_paciente(cedula):
    if "id_usuario" not in session:
        return redirect(url_for("login"))
        
    if session.get("rol") != "Administrador":
        flash("Acceso denegado. Solo los administradores pueden archivar pacientes.", "danger")
        return redirect(url_for("lista_pacientes"))
    
    PacienteService.eliminar_paciente(cedula)
    flash("El paciente ha sido archivado e inactivado.", "warning")
    return redirect(url_for("lista_pacientes"))

# --- CITAS ---
@app.route("/citas")
def lista_citas():
    if "id_usuario" not in session: return redirect(url_for("login"))
    query = request.args.get("q", "")
    estado = request.args.get("estado", "")
    fecha_inicio = request.args.get("fecha_inicio", "")
    fecha_fin = request.args.get("fecha_fin", "")
    medico_id_filtro = request.args.get("medico_id", type=int)
    page = request.args.get("page", 1, type=int)
    
    # Privacidad de la agenda: si es médico, solo ve sus propias citas. Si es admin, puede usar el filtro.
    limite_medico = session['empleado_id'] if session.get('rol') in ['Medico', 'Médico'] else medico_id_filtro
    
    from models import Empleado
    doctores = Empleado.query.filter(Empleado.rol_cargo.in_(['Medico', 'Médico'])).all()
    
    if query:
        citas = CitaService.buscar(query, medico_id=limite_medico, estado=estado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, page=page)
    else:
        citas = CitaService.obtener_todas(medico_id=limite_medico, estado=estado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, page=page)
        
    return render_template("citas/lista_citas.html", citas=citas, query=query, estado=estado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, medico_id_filtro=medico_id_filtro, doctores=doctores)

@app.route("/citas/reporte_pdf")
def reporte_citas_pdf():
    if "id_usuario" not in session: return redirect(url_for("login"))
    query = request.args.get("q", "")
    estado = request.args.get("estado", "")
    fecha_inicio = request.args.get("fecha_inicio", "")
    fecha_fin = request.args.get("fecha_fin", "")
    medico_id_filtro = request.args.get("medico_id", type=int)
    
    limite_medico = session['empleado_id'] if session.get('rol') in ['Medico', 'Médico'] else medico_id_filtro
    
    if query:
        citas = CitaService.buscar(query, medico_id=limite_medico, estado=estado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, page=None)
    else:
        citas = CitaService.obtener_todas(medico_id=limite_medico, estado=estado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, page=None)
        
    return render_template("citas/reporte_pdf.html", citas=citas, query=query, estado=estado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, medico_id_filtro=medico_id_filtro)

@app.route("/citas/nueva", methods=["GET", "POST"])
def nueva_cita():
    if "id_usuario" not in session:
        return redirect(url_for("login"))

    form = CitaForm()
    
    pacientes = PacienteService.obtener_todos(page=None)
    doctores = Empleado.query.all() 
    especialidades = EspecialidadService.obtener_todas()

    form.paciente_cedula.choices = [(p.cedula, f"{p.nombres} {p.apellidos} - CI: {p.cedula}") for p in pacientes]
    form.especialidad_id.choices = [(e.id_especialidad, e.nombre) for e in especialidades]
    form.doctor_id.choices = [(d.id_empleado, f"Dr/a. {d.nombre_completo}") for d in doctores if d.rol_cargo in ["Medico", "Médico", "Administrador"]]

    if form.validate_on_submit():
        # Validar conflicto de horario para el paciente
        from models import Cita
        cita_conflicto = Cita.query.filter_by(
            pacientes_cedula=form.paciente_cedula.data,
            fecha_cita=form.fecha.data,
            hora_cita=form.hora.data
        ).filter(Cita.estado != 'Cancelada').first()
        
        if cita_conflicto:
            flash(f"El paciente ya tiene una cita agendada para el {form.fecha.data.strftime('%d/%m/%Y')} a las {form.hora.data.strftime('%H:%M')}.", "danger")
            return redirect(url_for("nueva_cita"))

        CitaService.agregar_cita(
            pacientes_cedula=form.paciente_cedula.data,
            empleado_id=form.doctor_id.data,
            especialidad_id=form.especialidad_id.data,
            fecha=form.fecha.data,
            hora=form.hora.data,
            motivo=form.motivo.data,
            estado=form.estado.data
        )
        flash("¡Anotado! Cita agregada con éxito.", "success")
        return redirect(url_for("lista_citas"))

    from models import HorarioMedico
    todos_horarios = HorarioMedico.query.all()
    
    from models import Cita
    from sqlalchemy import func
    from datetime import date
    citas_futuras = db.session.query(
        Cita.empleado_id, 
        Cita.fecha_cita, 
        func.count(Cita.id_cita)
    ).filter(
        Cita.estado != 'Cancelada',
        Cita.fecha_cita >= date.today()
    ).group_by(Cita.empleado_id, Cita.fecha_cita).all()

    ocupacion = {}
    for emp_id, fecha_cita, conteo in citas_futuras:
        emp_str = str(emp_id)
        fecha_str = fecha_cita.strftime('%Y-%m-%d')
        if emp_str not in ocupacion:
            ocupacion[emp_str] = {}
        ocupacion[emp_str][fecha_str] = conteo
        
    return render_template("citas/formulario_cita.html", form=form, accion="Agendar", doctores_brutos=doctores, horarios=todos_horarios, ocupacion=ocupacion)

@app.route("/citas/editar/<int:id>", methods=["GET", "POST"])
def editar_cita(id):
    if "id_usuario" not in session:
        return redirect(url_for("login"))

    cita_actual = CitaService.obtener_por_id(id)
    form = CitaForm(obj=cita_actual)
    
    # Pre-cargar manualmente los campos cuyos nombres en BD difieren de WTForms
    if request.method == 'GET':
        form.paciente_cedula.data = cita_actual.pacientes_cedula
        form.doctor_id.data = cita_actual.empleado_id
        form.fecha.data = cita_actual.fecha_cita
        form.hora.data = cita_actual.hora_cita

    pacientes = PacienteService.obtener_todos(page=None)
    doctores = Empleado.query.all()
    especialidades = EspecialidadService.obtener_todas()
    
    form.paciente_cedula.choices = [(p.cedula, f"{p.nombres} {p.apellidos} - CI: {p.cedula}") for p in pacientes]
    form.especialidad_id.choices = [(e.id_especialidad, e.nombre) for e in especialidades]
    form.doctor_id.choices = [(d.id_empleado, f"Dr/a. {d.nombre_completo}") for d in doctores if d.rol_cargo in ["Medico", "Médico", "Administrador"]]

    if form.validate_on_submit():
        # Validar conflicto de horario para el paciente (excluyendo esta misma cita)
        from models import Cita
        cita_conflicto = Cita.query.filter_by(
            pacientes_cedula=form.paciente_cedula.data,
            fecha_cita=form.fecha.data,
            hora_cita=form.hora.data
        ).filter(Cita.estado != 'Cancelada', Cita.id_cita != id).first()
        
        if cita_conflicto:
            flash(f"El paciente ya tiene OTRA cita agendada para el {form.fecha.data.strftime('%d/%m/%Y')} a las {form.hora.data.strftime('%H:%M')}.", "danger")
            return redirect(url_for("editar_cita", id=id))

        CitaService.editar_cita(
            id_cita=id,
            pacientes_cedula=form.paciente_cedula.data,
            empleado_id=form.doctor_id.data,
            especialidad_id=form.especialidad_id.data,
            fecha=form.fecha.data,
            hora=form.hora.data,
            motivo=form.motivo.data,
            estado=form.estado.data
        )
        flash("La cita ha sido actualizada correctamente.", "success")
        return redirect(url_for("lista_citas"))

    from models import HorarioMedico
    todos_horarios = HorarioMedico.query.all()

    from sqlalchemy import func
    from datetime import date
    citas_futuras = db.session.query(
        Cita.empleado_id, 
        Cita.fecha_cita, 
        func.count(Cita.id_cita)
    ).filter(
        Cita.estado != 'Cancelada',
        Cita.fecha_cita >= date.today()
    ).group_by(Cita.empleado_id, Cita.fecha_cita).all()

    ocupacion = {}
    for emp_id, fecha_cita, conteo in citas_futuras:
        emp_str = str(emp_id)
        fecha_str = fecha_cita.strftime('%Y-%m-%d')
        if emp_str not in ocupacion:
            ocupacion[emp_str] = {}
        ocupacion[emp_str][fecha_str] = conteo

    return render_template("citas/formulario_cita.html", form=form, accion="Editar", doctores_brutos=doctores, horarios=todos_horarios, ocupacion=ocupacion)

@app.route("/citas/eliminar/<int:id>", methods=["GET", "POST"])
def eliminar_cita(id):
    if "id_usuario" not in session: return redirect(url_for("login"))
    motivo = request.form.get('motivo_cancelacion') if request.method == "POST" else None
    CitaService.eliminar_cita(id, motivo_cancelacion=motivo)
    flash("La cita ha sido cancelada.", "info")
    return redirect(request.referrer or url_for("lista_citas"))

@app.route("/citas/<int:id_cita>/finalizar_rapido", methods=["POST"])
def finalizar_cita_rapido(id_cita):
    if "id_usuario" not in session: return redirect(url_for("login"))
    cita = Cita.query.get_or_404(id_cita)
    cita.estado = "Atendida"
    db.session.commit()
    flash("Cita marcada como Atendida (Finalizada).", "success")
    return redirect(url_for("consulta_paciente", cedula=cita.pacientes_cedula))

# --- VISTA PÚBLICA: EL PACIENTE SE AGENTA SOLO ---
@app.route("/cita_publica", methods=["GET", "POST"])
def cita_publica():
    form = PublicCitaForm()
    
    especialidades = EspecialidadService.obtener_todas()
    form.especialidad_id.choices = [(0, "-- Seleccione Servicio --")] + [(e.id_especialidad, e.nombre) for e in especialidades]
    
    doctores = Empleado.query.filter(Empleado.rol_cargo.in_(['Medico', 'Médico'])).all()
    form.doctor_id.choices = [(0, "-- Seleccione Especialista --")] + [(d.id_empleado, f"Dr/a. {d.nombre_completo}") for d in doctores]

    from models import HorarioMedico, Cita
    from sqlalchemy import func
    from datetime import date
    todos_horarios = HorarioMedico.query.all()

    citas_futuras = db.session.query(
        Cita.empleado_id, 
        Cita.fecha_cita, 
        func.count(Cita.id_cita)
    ).filter(
        Cita.estado != 'Cancelada',
        Cita.fecha_cita >= date.today()
    ).group_by(Cita.empleado_id, Cita.fecha_cita).all()

    ocupacion = {}
    for emp_id, fecha_cita, conteo in citas_futuras:
        emp_str = str(emp_id)
        fecha_str = fecha_cita.strftime('%Y-%m-%d')
        if emp_str not in ocupacion:
            ocupacion[emp_str] = {}
        ocupacion[emp_str][fecha_str] = conteo

    if form.validate_on_submit():
        # Validar horario y cupos
        
        # Mapear día de la semana (0=Monday, 6=Sunday) a nombres en español
        dias_es = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dia_str = dias_es[form.fecha.data.weekday()]
        
        horario = HorarioMedico.query.filter_by(empleado_id=form.doctor_id.data, dia_semana=dia_str).first()
        
        if not horario:
            flash(f"El médico no tiene consultas programadas los días {dia_str}. Por favor revisa su horario.", "danger")
            return render_template("publico/agendar.html", form=form, especialidades=especialidades, doctores=doctores, horarios=todos_horarios, ocupacion=ocupacion)
            
        if form.hora.data < horario.hora_inicio or form.hora.data > horario.hora_fin:
            flash(f"El médico atiende los {dia_str} de {horario.hora_inicio.strftime('%H:%M')} a {horario.hora_fin.strftime('%H:%M')}.", "warning")
            return render_template("publico/agendar.html", form=form, especialidades=especialidades, doctores=doctores, horarios=todos_horarios, ocupacion=ocupacion)
            
        # Contar citas existentes para ese doctor en ese día
        citas_dia = Cita.query.filter_by(empleado_id=form.doctor_id.data, fecha_cita=form.fecha.data).filter(Cita.estado != 'Cancelada').count()
        if citas_dia >= horario.cupos_diarios:
            flash(f"El médico ya no tiene cupos disponibles para el {form.fecha.data.strftime('%d/%m/%Y')} (Límite: {horario.cupos_diarios} pacientes). Intenta otro día.", "danger")
            return render_template("publico/agendar.html", form=form, especialidades=especialidades, doctores=doctores, horarios=todos_horarios, ocupacion=ocupacion)

        # Validar si EL PACIENTE ya tiene cita a esa misma hora
        cita_conflicto = Cita.query.filter_by(
            pacientes_cedula=form.cedula.data,
            fecha_cita=form.fecha.data,
            hora_cita=form.hora.data
        ).filter(Cita.estado != 'Cancelada').first()
        
        if cita_conflicto:
            flash(f"Ya tienes una cita agendada para el {form.fecha.data.strftime('%d/%m/%Y')} a las {form.hora.data.strftime('%H:%M')}. No puedes agendar dos citas a la misma hora.", "danger")
            return render_template("publico/agendar.html", form=form, especialidades=especialidades, doctores=doctores, horarios=todos_horarios, ocupacion=ocupacion)

        try:
            paciente = PacienteService.obtener_por_cedula(form.cedula.data)
        except:
            paciente = PacienteService.agregar_paciente(
                cedula=form.cedula.data,
                nombres=form.nombres.data,
                apellidos=form.apellidos.data,
                telefono=form.telefono.data,
                fecha_nacimiento=form.fecha_nacimiento.data
            )
        
        CitaService.agregar_cita(
            pacientes_cedula=paciente.cedula,
            empleado_id=form.doctor_id.data,
            especialidad_id=form.especialidad_id.data,
            fecha=form.fecha.data,
            hora=form.hora.data,
            motivo=form.motivo.data,
            estado='Pendiente'
        )
        
        flash("¡Tu solicitud de cita ha sido enviada! Te esperamos el día agendado.", "success")
        return redirect(url_for("cita_publica"))

    from models import HorarioMedico
    todos_horarios = HorarioMedico.query.all()
    return render_template("publico/agendar.html", form=form, especialidades=especialidades, doctores=doctores, horarios=todos_horarios, ocupacion=ocupacion)


# --- PUENTE ECOSISTEMA: ATENDER CITA DIRECTAMENTE ---
@app.route("/citas/<int:id_cita>/atender")
def pre_atender_cita(id_cita):
    if "id_usuario" not in session: return redirect(url_for("login"))
    cita_activa = CitaService.obtener_por_id(id_cita)
    # Mandamos al médico al Historial del paciente con bandera de la Cita
    return redirect(url_for("consulta_paciente", cedula=cita_activa.pacientes_cedula, origen_cita_id=id_cita))

# --- CONSULTA MEDICA (EXPEDIENTE Y RECETAS) ---
@app.route("/pacientes/<string:cedula>/consulta", methods=["GET", "POST"])
def consulta_paciente(cedula):
    if "id_usuario" not in session:
        return redirect(url_for("login"))
        
    paciente_actual = PacienteService.obtener_por_cedula(cedula)
    
    # Manejo del acto medico y diagnósticos
    form = ConsultaForm()
    
    # Cargar dropdown de enfermedades CIE
    lista_cies = EnfermedadService.obtener_todas()
    
    # Cargar dropdown para recetas en pantalla compartida
    indicador_form = IndicacionForm()
    catalogo_meds = MedicamentoService.obtener_todos()
    
    if form.validate_on_submit() and 'observaciones' in request.form:
        lista_diagnosticos = []
        if form.diagnostico_libre.data:
            diagnosticos_text = form.diagnostico_libre.data.split(',')
            for diag_item in diagnosticos_text:
                diag_item = diag_item.strip()
                if not diag_item: continue
                enf = Enfermedad.query.filter(Enfermedad.nombre.ilike(diag_item)).first()
                if not enf:
                    import uuid
                    nuevo_cod = "LIBR-" + str(uuid.uuid4()).upper()[:10]
                    enf = Enfermedad(codigo_cie=nuevo_cod, nombre=diag_item, descripcion="Guardado libremente en Consulta")
                    db.session.add(enf)
                    db.session.flush()
                lista_diagnosticos.append(enf)
            
        # Recuperar origin_cita_id de los url arguments (si vino de la Agenda)
        cita_vinculada = request.args.get("origen_cita_id")
        
        nueva_consulta = ConsultaService.agregar_consulta(
             paciente_cedula=cedula, 
             medico_id=session.get('empleado_id', 1),
             cita_id_para_cerrar=cita_vinculada,
             diagnosticos=lista_diagnosticos,
             presion_arterial=form.presion_arterial.data,
             temperatura=form.temperatura.data,
             observaciones=form.observaciones.data
        )
        
        # Procesar y guardar el Recetario (si el médico indicó medicamento y dosis)
        if hasattr(indicador_form, 'nombre_medicamento') and indicador_form.dosis.data and indicador_form.nombre_medicamento.data:
            nombre_med = indicador_form.nombre_medicamento.data
            
            # Buscar el medicamento o crearlo al vuelo si no existe
            med = Medicamento.query.filter(Medicamento.nombre_comercial.ilike(nombre_med)).first()
            if not med:
                med = Medicamento(nombre_comercial=nombre_med, compuesto="Genérico Asignado Libremente", presentacion="S/A")
                db.session.add(med)
                db.session.flush() # Obtenemos el nuevo ID temporal
                
            nueva_indicacion = IndicacionMedica(
                consulta_id=nueva_consulta.id_consulta,
                medicamento_id=med.id_medicamento,
                dosis=indicador_form.dosis.data,
                duracion_dias=indicador_form.duracion_dias.data,
                observaciones=""
            )
            db.session.add(nueva_indicacion)
            db.session.commit()
            
        flash("Nota clínica guardada exitosamente. Se ha actualizado su Agenda.", "success")
        return redirect(url_for("consulta_paciente", cedula=cedula))
        
    notas_historial = ConsultaService.obtener_historial_paciente(cedula)
    return render_template("pacientes/historial_paciente.html", 
                           paciente=paciente_actual, 
                           historial=notas_historial, 
                           form=form,
                           indicador_form=indicador_form,
                           catalogo_meds=catalogo_meds,
                           lista_cies=lista_cies)

# ========================================== #
#      CATÁLOGOS MÉDICOS (MEDICAMENTOS CIE)  #
# ========================================== #

@app.route("/medicamentos", methods=["GET", "POST"])
def cat_medicamentos():
    if "id_usuario" not in session: return redirect(url_for("login"))
    form = MedicamentoForm()
    if form.validate_on_submit():
        if session.get("rol") not in ["Administrador", "Administradora", "Medico", "Médico"]:
            flash("Acceso denegado. Solo médicos y administradores pueden añadir medicamentos.", "danger")
            return redirect(url_for("cat_medicamentos"))
            
        MedicamentoService.agregar_medicamento(form.nombre_comercial.data, form.compuesto.data, form.presentacion.data)
        flash("Fármaco incorporado al Vademécum exitosamente", "success")
        return redirect(url_for("cat_medicamentos"))
        
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    if q:
        registros = MedicamentoService.buscar_medicamento(q, page=page)
    else:
        registros = MedicamentoService.obtener_todos(page=page)
        
    return render_template("medicamentos/lista_medicamentos.html", registros=registros, form=form)

@app.route("/medicamento/editar/<int:id_med>", methods=["POST"])
def editar_medicamento(id_med):
    if "id_usuario" not in session: return redirect(url_for("login"))
    if session.get("rol") not in ["Administrador", "Administradora", "Medico", "Médico"]:
        flash("Acceso denegado. Solo médicos y administradores pueden editar.", "danger")
        return redirect(url_for("cat_medicamentos"))
        
    nombre = request.form.get("nombre")
    compuesto = request.form.get("compuesto")
    presentacion = request.form.get("presentacion")
    MedicamentoService.actualizar_medicamento(id_med, nombre, compuesto, presentacion)
    flash("Medicamento actualizado correctamente.", "success")
    return redirect(url_for("cat_medicamentos"))

@app.route("/medicamento/eliminar/<int:id_med>", methods=["POST"])
def eliminar_medicamento(id_med):
    if "id_usuario" not in session: return redirect(url_for("login"))
    if session.get("rol") not in ["Administrador", "Administradora"]:
        flash("Acceso denegado. Solo los administradores pueden eliminar.", "danger")
        return redirect(url_for("cat_medicamentos"))
        
    MedicamentoService.desactivar_medicamento(id_med)
    flash("Medicamento eliminado (soft delete) del Vademécum.", "info")
    return redirect(url_for("cat_medicamentos"))

@app.route("/enfermedades", methods=["GET", "POST"])
def cat_enfermedades():
    if "id_usuario" not in session: return redirect(url_for("login"))
    form = EnfermedadForm()
    if form.validate_on_submit():
        if session.get("rol") not in ["Administrador", "Administradora"]:
            flash("Acceso denegado. Solo los administradores pueden añadir enfermedades.", "danger")
            return redirect(url_for("cat_enfermedades"))
        EnfermedadService.registrar_cie(form.codigo_cie.data, form.nombre.data, form.descripcion.data)
        flash("Enfermedad CIE catalogada.", "success")
        return redirect(url_for("cat_enfermedades"))
        
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    if q:
        registros = EnfermedadService.buscar_cie(q, page=page)
    else:
        registros = EnfermedadService.obtener_todas(page=page)
        
    return render_template("enfermedades/lista_enfermedades.html", registros=registros, form=form)

@app.route("/enfermedad/editar/<string:codigo>", methods=["POST"])
def editar_enfermedad(codigo):
    if "id_usuario" not in session: return redirect(url_for("login"))
    if session.get("rol") not in ["Administrador", "Administradora"]:
        flash("Acceso denegado. Solo los administradores pueden editar enfermedades.", "danger")
        return redirect(url_for("cat_enfermedades"))
        
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    EnfermedadService.actualizar_cie(codigo, nombre, descripcion)
    flash(f"Enfermedad {codigo} actualizada correctamente.", "success")
    return redirect(url_for("cat_enfermedades"))

@app.route("/enfermedad/eliminar/<string:codigo>", methods=["POST"])
def eliminar_enfermedad(codigo):
    if "id_usuario" not in session: return redirect(url_for("login"))
    if session.get("rol") not in ["Administrador", "Administradora"]:
        flash("Acceso denegado. Solo los administradores pueden eliminar enfermedades.", "danger")
        return redirect(url_for("cat_enfermedades"))
        
    EnfermedadService.desactivar_cie(codigo)
    flash(f"Enfermedad {codigo} eliminada (soft delete) del catálogo.", "info")
    return redirect(url_for("cat_enfermedades"))
    
@app.route("/especialidades", methods=["GET", "POST"])
def cat_especialidades():
    if "id_usuario" not in session: return redirect(url_for("login"))
    form = EspecialidadForm()
    if form.validate_on_submit():
        if session.get("rol") not in ["Administrador", "Administradora"]:
            flash("Acceso denegado. Solo los administradores pueden añadir especialidades.", "danger")
            return redirect(url_for("cat_especialidades"))
            
        EspecialidadService.agregar(form.nombre.data, form.descripcion.data)
        flash("Especialidad técnica abierta en el sistema.", "success")
        return redirect(url_for("cat_especialidades"))
    registros = EspecialidadService.obtener_todas()
    return render_template("enfermedades/lista_especialidades.html", registros=registros, form=form)

@app.route("/especialidad/editar/<int:id_esp>", methods=["POST"])
def editar_especialidad(id_esp):
    if "id_usuario" not in session: return redirect(url_for("login"))
    if session.get("rol") not in ["Administrador", "Administradora"]:
        flash("Acceso denegado. Solo los administradores pueden editar.", "danger")
        return redirect(url_for("cat_especialidades"))
        
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    EspecialidadService.actualizar(id_esp, nombre, descripcion)
    flash("Especialidad actualizada correctamente.", "success")
    return redirect(url_for("cat_especialidades"))

@app.route("/especialidad/eliminar/<int:id_esp>", methods=["POST"])
def eliminar_especialidad(id_esp):
    if "id_usuario" not in session: return redirect(url_for("login"))
    if session.get("rol") not in ["Administrador", "Administradora"]:
        flash("Acceso denegado. Solo los administradores pueden eliminar.", "danger")
        return redirect(url_for("cat_especialidades"))
        
    EspecialidadService.desactivar(id_esp)
    flash("Especialidad eliminada (soft delete) del sistema.", "info")
    return redirect(url_for("cat_especialidades"))

# ========================================== #
# DASHBOARD: ESTADÍSTICAS Y SALIDAS (REPORTES)
# ========================================== #

@app.route("/reportes")
def dashboard_reportes():
    if "id_usuario" not in session: return redirect(url_for("login"))
    
    limite_medico = session['empleado_id'] if session.get('rol') in ['Medico', 'Médico'] else None

    # 1. Total Citas por Estado (Gráfico Circular)
    citas_query = db.session.query(Cita.estado, func.count(Cita.id_cita))
    if limite_medico:
        citas_query = citas_query.filter(Cita.empleado_id == limite_medico)
    citas_por_estado = citas_query.group_by(Cita.estado).all()
    datos_estados = {estado: count for estado, count in citas_por_estado}
    
    # 2. Top 5 Médicos con más Citas Atendidas/Pendientes
    top_medicos_query = db.session.query(
        Empleado.nombre_completo, func.count(Cita.id_cita)
    ).join(Cita, Cita.empleado_id == Empleado.id_empleado).filter(
        Cita.estado != 'Cancelada'
    )
    if limite_medico:
        top_medicos_query = top_medicos_query.filter(Cita.empleado_id == limite_medico)
    top_medicos = top_medicos_query.group_by(Empleado.nombre_completo).order_by(func.count(Cita.id_cita).desc()).limit(5).all()
    
    # 3. Top Enfermedades/Diagnósticos en Consultas Historiales
    top_enf_query = db.session.query(
        Enfermedad.nombre, func.count(models.consulta_diagnosticos.c.consulta_id)
    ).join(
        models.consulta_diagnosticos, Enfermedad.codigo_cie == models.consulta_diagnosticos.c.enfermedad_cod_cie
    )
    if limite_medico:
        top_enf_query = top_enf_query.join(Consulta, Consulta.id_consulta == models.consulta_diagnosticos.c.consulta_id).filter(Consulta.medico_id == limite_medico)
    
    top_enfermedades = top_enf_query.group_by(
        Enfermedad.nombre
    ).order_by(func.count(models.consulta_diagnosticos.c.consulta_id).desc()).limit(5).all()
    
    # Cantidades Generales (KPIs)
    if limite_medico:
        total_pacientes = Paciente.query.join(Cita).filter(Cita.empleado_id == limite_medico).distinct().count()
        total_citas = Cita.query.filter(Cita.empleado_id == limite_medico).count()
    else:
        total_pacientes = Paciente.query.count()
        total_citas = Cita.query.count()
    
    return render_template(
        "reportes/dashboard.html", 
        datos_estados=datos_estados,
        top_medicos=top_medicos,
        top_enfermedades=top_enfermedades,
        total_pacientes=total_pacientes,
        total_citas=total_citas
    )



@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('errores/404.html'), 404

@app.errorhandler(500)
def error_interno_servidor(e):
    import traceback
    return "<pre>" + traceback.format_exc() + "</pre>", 500

if __name__ == "__main__":
    app.run(debug=True, port=5005)
