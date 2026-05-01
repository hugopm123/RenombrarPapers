import streamlit as st
import os
import re
import fitz  # PyMuPDF
from pathlib import Path
import pandas as pd
import io
import zipfile

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="PDF Paper Renamer - Online",
    page_icon="📚",
    layout="wide"
)

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DEL MOTOR VISUAL ---

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r'\s+', " ", name)
    return name.strip(" .")[:130]

def extract_title_from_bytes(pdf_bytes):
    """Extrae el título de un PDF cargado en memoria."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if len(doc) == 0: return None
        page = doc[0]
        blocks = page.get_text("dict")["blocks"]
        max_font_size = 0
        title_parts = []
        
        unwanted = [
            "doi:", "http", "issn", "received", "published", "arxiv:",
            "universitat", "politécnica", "valència", "university", 
            "faculty", "department", "copyright", "all rights", "grado",
            "escuela técnica", "superior de ingeniería", "preprint not peer", 
            "journal", "review article", "original article", "universidad"
        ]

        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        size = s["size"]
                        if not text or len(text) < 4: continue
                        if any(p in text.lower() for p in unwanted): continue
                        
                        if size > max_font_size + 0.5:
                            max_font_size = size
                            title_parts = [text]
                        elif abs(size - max_font_size) < 0.5:
                            title_parts.append(text)
        doc.close()
        if title_parts:
            full_title = " ".join(title_parts)
            full_title = re.sub(r'\s+', " ", full_title).strip()
            return full_title if len(full_title.split()) >= 2 else None
    except:
        pass
    return None

# --- INTERFAZ ---

st.title("📚 PDF Paper Renamer Online")
st.markdown("Sube tus archivos (PDF o ZIP) y deja que se organicen por ti.")

uploaded_files = st.file_uploader("Arrastra aquí tus archivos PDF o ZIP", type=["pdf", "zip"], accept_multiple_files=True)

if uploaded_files:
    results = []
    all_processed_files = [] # Para guardar (bytes, nombre_nuevo)
    
    with st.status("Procesando archivos...", expanded=True) as status:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            
            if file_name.lower().endswith(".zip"):
                # Caso: Archivo ZIP
                with zipfile.ZipFile(uploaded_file) as z:
                    for zname in z.namelist():
                        if zname.lower().endswith(".pdf") and not zname.startswith("__MACOSX"):
                            pdf_bytes = z.read(zname)
                            title = extract_title_from_bytes(pdf_bytes)
                            
                            original_base = os.path.basename(zname)
                            if title:
                                new_name = sanitize_filename(title) + ".pdf"
                            else:
                                new_name = "Manual - " + original_base
                            
                            results.append({
                                "Fuente": f"ZIP: {file_name}",
                                "Nombre Original": original_base,
                                "Nombre Sugerido": new_name
                            })
                            all_processed_files.append((pdf_bytes, new_name))
            else:
                # Caso: Archivo PDF suelto
                pdf_bytes = uploaded_file.read()
                title = extract_title_visual = extract_title_from_bytes(pdf_bytes)
                
                if title:
                    new_name = sanitize_filename(title) + ".pdf"
                else:
                    new_name = "Manual - " + file_name
                
                results.append({
                    "Fuente": "PDF Suelto",
                    "Nombre Original": file_name,
                    "Nombre Sugerido": new_name
                })
                all_processed_files.append((pdf_bytes, new_name))
                
        status.update(label="Procesamiento completado", state="complete")

    if results:
        st.write(f"### 📋 Archivos detectados: {len(results)}")
        df = pd.DataFrame(results)
        st.write("### Vista Previa de Renombrado")
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True)

        # Crear ZIP para descarga
        if st.button("🚀 Generar y Descargar Archivos Renombrados", use_container_width=True):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i, row in edited_df.iterrows():
                    original_bytes = all_processed_files[i][0]
                    final_name = row["Nombre Sugerido"]
                    
                    # Limpieza extra del nombre por si el usuario lo editó mal
                    final_name = sanitize_filename(final_name.replace(".pdf", "")) + ".pdf"
                    
                    zf.writestr(final_name, original_bytes)
            
            st.success("¡ZIP generado con éxito!")
            st.download_button(
                label="⬇️ Descargar todo en un ZIP",
                data=zip_buffer.getvalue(),
                file_name="papers_renombrados_pro.zip",
                mime="application/zip",
                use_container_width=True
            )
    else:
        st.info("No se encontraron archivos PDF válidos.")

st.sidebar.markdown("""
### ¿Cómo funciona?
1. **Sube**: Puedes subir archivos PDF individuales o un archivo **ZIP** lleno de papers.
2. **Auto-Extracción**: El sistema detectará automáticamente todos los PDFs dentro de tus ZIPs.
3. **Revisa**: Corrige nombres en la tabla.
4. **Descarga**: Obtén un nuevo ZIP perfectamente organizado.
""")
