from models import Medicamento, Enfermedad, Especialidad
from extensions import db

class MedicamentoService:
    @staticmethod
    def obtener_todos(page=1, per_page=10):
        return Medicamento.query.filter_by(activo=True).order_by(Medicamento.nombre_comercial).paginate(page=page, per_page=per_page, error_out=False)
        
    @staticmethod
    def buscar_medicamento(busqueda, page=1, per_page=10):
        return Medicamento.query.filter(
            Medicamento.activo == True,
            ((Medicamento.nombre_comercial.ilike(f"%{busqueda}%")) | 
            (Medicamento.compuesto.ilike(f"%{busqueda}%")) |
            (Medicamento.presentacion.ilike(f"%{busqueda}%")))
        ).order_by(Medicamento.nombre_comercial).paginate(page=page, per_page=per_page, error_out=False)
        
    @staticmethod
    def agregar_medicamento(nombre, compuesto, presentacion):
        med = Medicamento(nombre_comercial=nombre, compuesto=compuesto, presentacion=presentacion)
        db.session.add(med)
        db.session.commit()
        return med

    @staticmethod
    def actualizar_medicamento(id_med, nombre, compuesto, presentacion):
        med = Medicamento.query.get(id_med)
        if med:
            med.nombre_comercial = nombre
            med.compuesto = compuesto
            med.presentacion = presentacion
            db.session.commit()
        return med

    @staticmethod
    def desactivar_medicamento(id_med):
        med = Medicamento.query.get(id_med)
        if med:
            med.activo = False
            db.session.commit()
        return med

class EnfermedadService:
    @staticmethod
    def obtener_todas(page=1, per_page=10):
        return Enfermedad.query.filter_by(activo=True).order_by(Enfermedad.codigo_cie).paginate(page=page, per_page=per_page, error_out=False)
        
    @staticmethod
    def buscar_cie(busqueda, page=1, per_page=10):
        return Enfermedad.query.filter(
            Enfermedad.activo == True,
            ((Enfermedad.codigo_cie.ilike(f"%{busqueda}%")) | 
            (Enfermedad.nombre.ilike(f"%{busqueda}%")))
        ).order_by(Enfermedad.codigo_cie).paginate(page=page, per_page=per_page, error_out=False)
        
    @staticmethod
    def registrar_cie(codigo, nombre, descripcion):
        enf = Enfermedad(codigo_cie=codigo.upper(), nombre=nombre, descripcion=descripcion)
        db.session.add(enf)
        db.session.commit()
        return enf

    @staticmethod
    def actualizar_cie(codigo, nombre, descripcion):
        enf = Enfermedad.query.get(codigo.upper())
        if enf:
            enf.nombre = nombre
            enf.descripcion = descripcion
            db.session.commit()
        return enf

    @staticmethod
    def desactivar_cie(codigo):
        enf = Enfermedad.query.get(codigo.upper())
        if enf:
            enf.activo = False
            db.session.commit()
        return enf

class EspecialidadService:
    @staticmethod
    def obtener_todas():
        return Especialidad.query.filter_by(activo=True).order_by(Especialidad.nombre).all()
    
    @staticmethod
    def agregar(nombre, descripcion):
        esp = Especialidad(nombre=nombre, descripcion=descripcion)
        db.session.add(esp)
        db.session.commit()
        return esp

    @staticmethod
    def actualizar(id_esp, nombre, descripcion):
        esp = Especialidad.query.get(id_esp)
        if esp:
            esp.nombre = nombre
            esp.descripcion = descripcion
            db.session.commit()
        return esp

    @staticmethod
    def desactivar(id_esp):
        esp = Especialidad.query.get(id_esp)
        if esp:
            esp.activo = False
            db.session.commit()
        return esp
