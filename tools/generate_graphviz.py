import sys
import subprocess
import zlib
import base64
import urllib.request
import os

def run():
    print("Iniciando generación con Graphviz...")
    from docx import Document
    from docx.shared import Inches
    import pypandoc

    graphviz_code = """digraph G {
    rankdir=LR;
    splines=ortho;
    nodesep=0.8;
    ranksep=1.0;
    fontname="Comic Sans MS";
    
    node [fontname="Comic Sans MS", style="filled", fillcolor="white", penwidth=2, fontsize=12];
    edge [fontname="Comic Sans MS", penwidth=2, color="black", fontsize=10];

    Paciente [shape=box];
    Medico [shape=box, label="Médico"];
    PacienteAtendido [shape=box, label="Paciente\nAtendido"];

    subgraph cluster_sistema {
        label="Sistema de Gestión de Citas Médicas\nAsocidemucre";
        style=dashed;
        penwidth=2;
        color=black;
        fontname="Comic Sans MS";
        fontsize=14;
        
        Admin [shape=box, label="Administrador /\nSecretaria"];
        
        P1 [shape=box, style="rounded,filled", label="Registrar\npaciente"];
        P2 [shape=box, style="rounded,filled", label="Agendar\ncita médica"];
        P3 [shape=box, style="rounded,filled", label="Atender\nconsulta\nmédica"];
        
        BD1 [shape=none, margin=0, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4"><TR><TD SIDES="TB" BORDER="2">BD Pacientes</TD></TR></TABLE>>];
        BD2 [shape=none, margin=0, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4"><TR><TD SIDES="TB" BORDER="2">BD Citas</TD></TR></TABLE>>];
        BD3 [shape=none, margin=0, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4"><TR><TD SIDES="TB" BORDER="2">BD Consultas</TD></TR></TABLE>>];

        Admin -> P1 [label="Datos del\\npaciente"];
        Admin -> P2 [label="Datos de\\ncita"];
        
        P1 -> P2 [label="Datos del\\npaciente"];
        P2 -> P3 [label="Datos de\\ncita"];
        
        P1 -> BD1 [dir=both];
        P2 -> BD2 [dir=both];
        P3 -> BD3 [dir=both];
        
        { rank=same; P1; P2; P3 }
    }

    Paciente -> P1 [label="Cédula,\\nNombre,\\nApellido,\\nTeléfono,\\nFecha Nac."];
    
    P3 -> Medico [dir=back, label="Diagnóstico,\\nIndicaciones"];
    P3 -> PacienteAtendido;
}
"""

    print("Comprimiendo y codificando código Graphviz...")
    compressed = zlib.compress(graphviz_code.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')

    # Kroki usa el endpoint /graphviz/png/
    url = f"https://kroki.io/graphviz/png/{encoded}"
    img_path = "diagrama_graphviz_temp.png"
    
    print(f"Descargando imagen desde {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(img_path, 'wb') as out_file:
        out_file.write(response.read())
        
    print("Imagen descargada exitosamente.")

    print("Re-creando el documento Word limpio sin el código fuente...")
    with open("diagrama_dfd_nivel0.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Quitar el bloque mermaid del markdown
    clean_content = content.split("```mermaid")[0] + content.split("```")[2]
    
    with open("diagrama_nivel0_temp.md", "w", encoding="utf-8") as f:
        f.write(clean_content)
        
    pypandoc.convert_file("diagrama_nivel0_temp.md", 'docx', outputfile="Diagrama_DFD_Nivel0_Exacto.docx")
    
    print("Añadiendo la nueva imagen al documento Word...")
    doc = Document("Diagrama_DFD_Nivel0_Exacto.docx")
    
    doc.add_heading('Diagrama Gráfico (Formato Exacto)', level=2)
    doc.add_picture(img_path, width=Inches(6.5))
    
    doc.save("Diagrama_DFD_Nivel0_Exacto.docx")
    
    if os.path.exists(img_path): os.remove(img_path)
    if os.path.exists("diagrama_nivel0_temp.md"): os.remove("diagrama_nivel0_temp.md")
    
    print("¡Documento finalizado con éxito!")

if __name__ == "__main__":
    run()
