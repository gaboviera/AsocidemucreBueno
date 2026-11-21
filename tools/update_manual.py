import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

doc_path = r"C:\Users\jous_\OneDrive\Documents\manual_usuario_asocidemucre.docx"

if not os.path.exists(doc_path):
    print(f"File not found: {doc_path}")
    exit(1)

document = Document(doc_path)

# Añadir el nuevo contenido al final del documento
h1 = document.add_paragraph()
r = h1.add_run('4. Gestión de Horarios por el Administrador')
r.bold = True
r.font.size = Pt(14)

p = document.add_paragraph('En la versión más reciente del sistema, los administradores tienen la capacidad de asignar y gestionar los horarios de los médicos. Esto permite centralizar la organización de los turnos en caso de ser necesario.')
p.style.font.size = Pt(11)

h2 = document.add_paragraph()
r2 = h2.add_run('Asignación de Horarios')
r2.bold = True
r2.font.size = Pt(12)
p2 = document.add_paragraph('Para asignar un horario, el administrador debe seguir estos pasos:\n')
p2.add_run('1. ').bold = True
p2.add_run('Iniciar sesión con su cuenta de Administrador.\n')
p2.add_run('2. ').bold = True
p2.add_run('Dirigirse al menú superior y desplegar la sección ').bold = False
p2.add_run('Panel de Configuración').bold = True
p2.add_run('.\n')
p2.add_run('3. ').bold = True
p2.add_run('Hacer clic en la opción ').bold = False
p2.add_run('Asignar Horarios a Médicos').bold = True
p2.add_run('.\n')
p2.add_run('4. ').bold = True
p2.add_run('En el formulario de la izquierda, seleccione al médico, el día de la semana, las horas de inicio y fin, y los cupos diarios permitidos.\n')
p2.add_run('5. ').bold = True
p2.add_run('Haga clic en "Asignar Horario". El nuevo turno aparecerá en la tabla de la derecha.')

h3 = document.add_paragraph()
r3 = h3.add_run('Eliminación de Horarios')
r3.bold = True
r3.font.size = Pt(12)
p3 = document.add_paragraph('Si es necesario cancelar o eliminar un turno previamente asignado, el administrador puede hacerlo desde la misma pantalla:\n')
p3.add_run('1. ').bold = True
p3.add_run('Busque el turno en la tabla de "Todos los Turnos Activos".\n')
p3.add_run('2. ').bold = True
p3.add_run('Haga clic en el icono de la papelera (Eliminar) en la columna de acción correspondiente a ese turno.\n')
p3.add_run('3. ').bold = True
p3.add_run('Confirme la eliminación.')

document.save(doc_path)
print("El manual de usuario ha sido actualizado correctamente.")
