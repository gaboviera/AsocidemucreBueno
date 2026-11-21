import sys
import subprocess
import zlib
import base64
import urllib.request
import os

def run():
    print("Instalando dependencias necesarias...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "pypandoc"])
    
    from docx import Document
    from docx.shared import Inches
    import pypandoc

    mermaid_code = """graph TD
    classDef process fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000;
    classDef entity fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000;
    
    P[Paciente]:::entity
    M[Médico]:::entity
    A[Administrador / Secretaria]:::entity

    S(0. Sistema Web Asocidemucre):::process

    P -- "Solicita Cita / Datos de registro" --> S
    S -- "Confirmación de cita / Historial Médico" --> P

    M -- "Diagnósticos / Recetas / Horarios" --> S
    S -- "Agenda diaria / Expedientes de pacientes" --> M

    A -- "Altas de personal / Solicitud de reportes" --> S
    S -- "Reportes y Estadísticas / Dashboard" --> A
"""

    print("Generando imagen del diagrama...")
    # Comprimir usando zlib para la API de Kroki
    compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')

    url = f"https://kroki.io/mermaid/png/{encoded}"
    img_path = "diagrama_temporal.png"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(img_path, 'wb') as out_file:
        out_file.write(response.read())
        
    print("Imagen descargada exitosamente.")

    print("Re-creando el documento Word limpio sin el código mermaid...")
    # Vamos a limpiar el markdown para que no muestre el código en el docx final
    with open("diagrama_dfd_contextual.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Quitar el bloque mermaid del texto
    clean_content = content.split("```mermaid")[0] + content.split("```")[2]
    
    with open("diagrama_temp.md", "w", encoding="utf-8") as f:
        f.write(clean_content)
        
    pypandoc.convert_file("diagrama_temp.md", 'docx', outputfile="Diagrama_DFD_Contextual.docx")
    
    print("Añadiendo imagen al documento Word...")
    doc = Document("Diagrama_DFD_Contextual.docx")
    
    # Insertar la imagen al final del documento (o buscar dónde insertarla)
    doc.add_heading('Diagrama Gráfico', level=2)
    doc.add_picture(img_path, width=Inches(6.0))
    
    doc.save("Diagrama_DFD_Contextual.docx")
    
    # Limpiar temporales
    if os.path.exists(img_path): os.remove(img_path)
    if os.path.exists("diagrama_temp.md"): os.remove("diagrama_temp.md")
    
    print("¡Documento finalizado con imagen insertada!")

if __name__ == "__main__":
    run()
