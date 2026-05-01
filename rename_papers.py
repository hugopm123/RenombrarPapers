import os
import re
import argparse
import fitz  # PyMuPDF (Requiere: pip install pymupdf)

def sanitize_filename(name):
    """
    Limpia y formatea una cadena para que sea un nombre de archivo válido.
    """
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r'\s+', " ", name)
    return name.strip(" .")[:130]

def extract_title_visual(pdf_path):
    """
    Motor Visual 4.2: Extrae el título basándose en el tamaño de fuente,
    con filtros avanzados para casos rebeldes (Preprints, Escuelas, Números).
    """
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return None
        
        page = doc[0]
        blocks = page.get_text("dict")["blocks"]
        
        max_font_size = 0
        title_components = []
        
        # Filtros avanzados para eliminar ruidos específicos detectados en las pruebas
        unwanted_patterns = [
            "doi:", "http", "issn", "received", "published", "arxiv:",
            "universitat", "universidad" "politécnica", "valència", "university", 
            "faculty", "department", "copyright", "all rights", "grado",
            "escuela técnica", "superior de ingeniería", "preprint not peer", 
            "journal", "review article", "original article"
        ]

        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        size = s["size"]
                        
                        # Ignorar fragmentos irrelevantes o muy cortos (como "1 3")
                        if not text or len(text) < 4:
                            continue
                        
                        # Ignorar si coincide con patrones de ruido conocidos
                        if any(p in text.lower() for p in unwanted_patterns):
                            continue
                        
                        # Lógica de detección de fuente máxima
                        if size > max_font_size + 0.5:
                            max_font_size = size
                            title_components = [text]
                        elif abs(size - max_font_size) < 0.5:
                            title_components.append(text)
        
        doc.close()
        
        if title_components:
            full_title = " ".join(title_components)
            full_title = re.sub(r'\s+', " ", full_title).strip()
            
            return full_title if len(full_title.split()) >= 3 else None
            
    except Exception:
        pass
    return None

def process_directory(directory, dry_run=False):
    """Escanea la carpeta y aplica el renombrado visual."""
    if not os.path.exists(directory):
        print(f"Error: La ruta '{directory}' no es válida.")
        return

    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf') and not f.startswith('._')]
    
    print(f"\n{'='*50}")
    print(f" PDF VISUAL RENAMER v4.2 - ULTIMATE")
    print(f"{'='*50}")
    print(f"Analizando: {directory}")
    print(f"Archivos encontrados: {len(pdf_files)}")
    if dry_run:
        print("[AVISO] Ejecutando en MODO PRUEBA (sin cambios reales)\n")

    count = 0
    for filename in pdf_files:
        original_path = os.path.join(directory, filename)
        title = extract_title_visual(original_path)
        
        if title:
            new_filename = sanitize_filename(title) + ".pdf"
            if filename == new_filename:
                continue
            
            target_path = os.path.join(directory, new_filename)
            if os.path.exists(target_path):
                base, ext = os.path.splitext(new_filename)
                idx = 1
                while os.path.exists(os.path.join(directory, f"{base} ({idx}){ext}")):
                    idx += 1
                new_filename = f"{base} ({idx}){ext}"
                target_path = os.path.join(directory, new_filename)

            if not dry_run:
                try:
                    os.rename(original_path, target_path)
                    print(f"✓ Renombrado: '{filename}'\n  -> '{new_filename}'")
                    count += 1
                except Exception as e:
                    print(f"✗ Error con '{filename}': {e}")
            else:
                print(f"? Sugerencia: '{filename}'\n  -> '{new_filename}'")
                count += 1

    print(f"\n--- Proceso finalizado. Archivos afectados: {count} ---\n")

def main():
    parser = argparse.ArgumentParser(description="Organizador Final de Papers Académicos.")
    parser.add_argument("directorio", help="Ruta de la carpeta con PDFs")
    parser.add_argument("--test", action="store_true", help="Modo simulación")
    args = parser.parse_args()
    process_directory(args.directorio, dry_run=args.test)

if __name__ == "__main__":
    main()
