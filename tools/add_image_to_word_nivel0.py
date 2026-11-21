import sys
import subprocess
import zlib
import base64
import urllib.request
import os

def run():
    from docx import Document
    from docx.shared import Inches
    import pypandoc

    mermaid_code = """graph LR
    classDef process fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000;
    classDef entity fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000;
    classDef datastore fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000;

    Pac[Paciente]:::entity
    Med[Médico]:::entity
    PacAtendido[Paciente Atendido]:::entity

    subgraph Sistema["Sistema de Gestión de Citas Médicas Asocidemucre"]
        Admin[Administrador / Secretaria]:::entity
        P1(Registrar paciente):::process
        P2(Agendar cita médica):::process
        P3(Atender consulta médica):::process

        BD1[(BD Pacientes)]:::datastore
        BD2[(BD Citas)]:::datastore
        BD3[(BD Consultas)]:::datastore

        Admin -- "Datos del\\npaciente" --> P1
        Admin -- "Datos de\\ncita" --> P2
        
        P1 -- "Datos del\\npaciente" --> P2
        P2 -- "Datos de\\ncita" --> P3

        P1 <--> BD1
        P2 <--> BD2
        P3 <--> BD3
    end
    
    style Sistema fill:none,stroke:#000,stroke-width:2px,stroke-dasharray: 5 5,color:#000

    Pac -- "Cédula,\\nNombre,\\nApellido,\\nTeléfono,\\nFecha Nac." --> P1
    Med -- "Diagnóstico,\\nIndicaciones" --> P3
    P3 --> PacAtendido
"""

    print("Generando imagen del diagrama Nivel 0...")
    compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')

    url = f"https://kroki.io/mermaid/png/{encoded}"
    img_path = "diagrama_nivel0_temp.png"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(img_path, 'wb') as out_file:
        out_file.write(response.read())
        
    print("Imagen descargada exitosamente.")

    print("Re-creando el documento Word limpio sin el código mermaid...")
    with open("diagrama_dfd_nivel0.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    clean_content = content.split("```mermaid")[0] + content.split("```")[2]
    
    with open("diagrama_nivel0_temp.md", "w", encoding="utf-8") as f:
        f.write(clean_content)
        
    pypandoc.convert_file("diagrama_nivel0_temp.md", 'docx', outputfile="Diagrama_DFD_Nivel0.docx")
    
    print("Añadiendo imagen al documento Word...")
    doc = Document("Diagrama_DFD_Nivel0.docx")
    
    doc.add_heading('Diagrama Gráfico', level=2)
    doc.add_picture(img_path, width=Inches(6.0))
    
    doc.save("Diagrama_DFD_Nivel0.docx")
    
    if os.path.exists(img_path): os.remove(img_path)
    if os.path.exists("diagrama_nivel0_temp.md"): os.remove("diagrama_nivel0_temp.md")
    
    print("¡Documento finalizado!")

if __name__ == "__main__":
    run()
