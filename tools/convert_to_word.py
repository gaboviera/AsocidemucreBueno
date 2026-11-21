import pypandoc

def convert():
    input_file = "diagrama_dfd_contextual.md"
    output_file = "Diagrama_DFD_Contextual.docx"
    
    print("Convirtiendo archivo...")
    pypandoc.convert_file(input_file, 'docx', outputfile=output_file)
    print(f"¡Convertido exitosamente a {output_file}!")

if __name__ == "__main__":
    convert()
