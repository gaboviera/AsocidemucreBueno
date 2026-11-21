import sys
import subprocess

def run():
    print("Añadiendo explicaciones de Entradas, Procesos y Salidas al documento...")
    from docx import Document
    from docx.shared import Pt
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

    # Abrir el documento que ya contiene la Carta Estructurada
    doc_path = "Carta_Estructurada_Asocidemucre.docx"
    doc = Document(doc_path)
    
    doc.add_heading('Análisis HIPO (Jerarquía + Entradas, Procesos y Salidas)', level=1)
    doc.add_paragraph('Es muy común acompañar la Carta Estructurada con un análisis de Entradas, Procesos y Salidas (modelo HIPO). A continuación se detalla cómo fluye la información en los módulos principales identificados en el diagrama anterior:')

    # Datos para las tablas
    modulos = [
        {
            "nombre": "1. Gestión de Pacientes",
            "entrada": "• Datos personales (Cédula, Nombre, Apellido, Fecha de Nacimiento).\n• Solicitud de actualización de datos.",
            "proceso": "• Validación de formato de cédula y existencia previa.\n• Registro del paciente en la base de datos (BD Pacientes).\n• Búsqueda y filtrado de pacientes en el sistema.",
            "salida": "• Confirmación de paciente registrado exitosamente.\n• Lista de pacientes registrados.\n• Mensajes de error en caso de duplicados."
        },
        {
            "nombre": "2. Gestión de Citas Médicas",
            "entrada": "• Cédula del paciente.\n• ID del médico especialista.\n• Fecha y hora deseada.\n• Motivo de la cita.",
            "proceso": "• Verificación de disponibilidad de horario del médico.\n• Comprobación de conflictos (paciente con otra cita a la misma hora).\n• Almacenamiento de la reserva en BD Citas.",
            "salida": "• Cita programada (Estado: Pendiente).\n• Notificación de confirmación o rechazo de horario."
        },
        {
            "nombre": "3. Consultas Clínicas",
            "entrada": "• Selección del paciente citado.\n• Signos vitales (Temperatura, Presión).\n• Diagnóstico médico (CIE).\n• Medicamentos e indicaciones.",
            "proceso": "• Actualización del estado de la cita a 'Atendida'.\n• Generación de la nota clínica en el expediente.\n• Creación de la receta médica (BD Consultas).",
            "salida": "• Historial clínico actualizado.\n• Receta médica generada para el paciente."
        },
        {
            "nombre": "4. Personal Médico / Dashboard",
            "entrada": "• Datos del nuevo empleado/médico.\n• Días y horas de turnos.\n• Criterios de búsqueda para reportes.",
            "proceso": "• Creación de credenciales de acceso (Usuarios).\n• Asignación de cupos diarios por horario.\n• Cálculo de estadísticas (citas atendidas vs canceladas).",
            "salida": "• Médico registrado con acceso al sistema.\n• Agenda disponible para que los pacientes reserven.\n• Gráficos estadísticos en el panel de control."
        }
    ]

    for mod in modulos:
        doc.add_heading(mod["nombre"], level=2)
        
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        
        # Header
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'ENTRADAS'
        hdr_cells[1].text = 'PROCESOS'
        hdr_cells[2].text = 'SALIDAS'
        
        # Poner en negrita el header
        for cell in hdr_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                
        # Fila de datos
        row_cells = table.add_row().cells
        row_cells[0].text = mod["entrada"]
        row_cells[1].text = mod["proceso"]
        row_cells[2].text = mod["salida"]
        
        doc.add_paragraph("") # Espacio en blanco

    doc.save("Carta_Estructurada_y_IPO.docx")
    print("¡Documento generado con éxito: Carta_Estructurada_y_IPO.docx!")

if __name__ == "__main__":
    run()
