import sys
import subprocess
import zlib
import base64
import urllib.request
import os
from docx import Document
from docx.shared import Inches

def run():
    print("Iniciando generación de Carta Estructurada con Graphviz...")

    graphviz_code = """digraph G {
    splines=ortho;
    nodesep=0.4;
    ranksep=0.8;
    
    // Configuración general para imitar el estilo azul de la imagen
    node [
        shape=box, 
        style="filled,rounded", 
        fillcolor="#f2f7fc", 
        color="#4b8bce", 
        penwidth=3, 
        fontname="Arial", 
        fontsize=12,
        margin="0.2,0.1"
    ];
    edge [color="#4b8bce", penwidth=3, dir=none];

    Sistema [label="Sistema\\nAsocidemucre", fontsize=14, margin="0.3,0.2"];

    Pacientes [label="Pacientes"];
    Citas [label="Citas Médicas"];
    Consultas [label="Consultas\\nClínicas"];
    Personal [label="Personal\\nMédico"];

    Sistema -> {Pacientes, Citas, Consultas, Personal};

    P1 [label="Registrar"];
    P2 [label="Modificar"];
    P3 [label="Consultar"];
    Pacientes -> {P1, P2, P3};

    C1 [label="Agendar"];
    C2 [label="Modificar"];
    C3 [label="Cancelar"];
    Citas -> {C1, C2, C3};

    Co1 [label="Atender\\nConsulta"];
    Co2 [label="Ver\\nHistorial"];
    Consultas -> {Co1, Co2};

    Pe1 [label="Registrar"];
    Pe2 [label="Asignar\\nHorario"];
    Personal -> {Pe1, Pe2};
}
"""

    print("Comprimiendo y codificando código Graphviz...")
    compressed = zlib.compress(graphviz_code.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')

    url = f"https://kroki.io/graphviz/png/{encoded}"
    img_path = "carta_estructurada_temp.png"
    
    print(f"Descargando imagen desde Kroki...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(img_path, 'wb') as out_file:
        out_file.write(response.read())
        
    print("Imagen descargada exitosamente.")

    print("Creando el documento Word...")
    doc = Document()
    doc.add_heading('Carta Estructurada - Asocidemucre', level=1)
    
    p = doc.add_paragraph('A continuación se presenta la Carta Estructurada del sistema, la cual ilustra la jerarquía de los módulos principales (Pacientes, Citas, Consultas y Personal Médico) y sus respectivas funciones, basándose en la arquitectura del proyecto.')
    
    doc.add_picture(img_path, width=Inches(6.5))
    
    output_docx = "Carta_Estructurada_Asocidemucre.docx"
    doc.save(output_docx)
    
    if os.path.exists(img_path): os.remove(img_path)
    
    print(f"¡Documento finalizado con éxito: {output_docx}!")

if __name__ == "__main__":
    run()
