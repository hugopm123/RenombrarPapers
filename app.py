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
st.markdown("Sube tus archivos y deja que el motor visual los organice por ti.")

# Selector de archivos
uploaded_files = st.file_uploader("Arrastra aquí tus archivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.write(f"### 📋 Archivos detectados: {len(uploaded_files)}")
    
    results = []
    processed_files = [] # Para guardar (bytes, nombre_nuevo)
    
    with st.status("Analizando archivos...", expanded=True) as status:
        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.read()
            title = extract_title_from_bytes(file_bytes)
            
            original_name = uploaded_file.name
            if title:
                new_name = sanitize_filename(title) + ".pdf"
            else:
                new_name = "No se pudo identificar - " + original_name
            
            results.append({
                "Nombre Original": original_name,
                "Nombre Sugerido": new_name
            })
            
            processed_files.append((file_bytes, new_name))
        status.update(label="Análisis completado", state="complete")

    # Mostrar tabla previa editable
    df = pd.DataFrame(results)
    st.write("### Vista Previa de Renombrado")
    edited_df = st.data_editor(df, use_container_width=True, hide_index=True)

    # Crear ZIP para descarga
    if st.button("🚀 Generar y Descargar Archivos Renombrados", use_container_width=True):
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for i, row in edited_df.iterrows():
                # Buscar los bytes originales
                original_bytes = processed_files[i][0]
                final_name = row["Nombre Sugerido"]
                
                # Manejo de nombres duplicados dentro del ZIP
                zf.writestr(final_name, original_bytes)
        
        st.success("¡ZIP generado con éxito!")
        st.download_button(
            label="⬇️ Descargar todo en un ZIP",
            data=zip_buffer.getvalue(),
            file_name="papers_renombrados.zip",
            mime="application/zip",
            use_container_width=True
        )

st.sidebar.markdown("""
### ¿Cómo funciona?
1. **Sube**: Arrastra tus PDFs.
2. **Revisa**: Edita los nombres si es necesario en la tabla.
3. **Descarga**: Obtén un archivo ZIP con todos tus PDFs renombrados.

*Tus archivos se procesan en memoria y no se guardan en el servidor.*
""")
