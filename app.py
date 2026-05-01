import streamlit as st
import os
import re
import fitz  # PyMuPDF
from pathlib import Path
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="PDF Paper Renamer - Interactive Pro",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        border-radius: 5px;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #262730;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DEL MOTOR VISUAL ---

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r'\s+', " ", name)
    return name.strip(" .")[:130]

def extract_title_visual(pdf_path):
    try:
        doc = fitz.open(pdf_path)
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

# --- INTERFAZ STREAMLIT ---

st.title("📚 PDF Paper Renamer Pro")
st.markdown("Organiza tu biblioteca académica con control total.")

# Inicializar estado
if "df_suggestions" not in st.session_state:
    st.session_state.df_suggestions = None

with st.container():
    col1, col2 = st.columns([4, 1])
    with col1:
        directory = st.text_input("Ruta de la carpeta:", value="", placeholder="Ej: /Documents/Papers/V1")
    with col2:
        st.write("") # Espaciador
        st.write("") 
        if st.button("🔍 Analizar Carpeta", use_container_width=True):
            if os.path.exists(directory):
                files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf') and not f.startswith('._')]
                
                results = []
                progress_bar = st.progress(0)
                
                for i, filename in enumerate(files):
                    title = extract_title_visual(os.path.join(directory, filename))
                    if title:
                        new_name = sanitize_filename(title) + ".pdf"
                        if filename != new_name:
                            results.append({
                                "Aceptar": True,
                                "Nombre Actual": filename,
                                "Nombre Sugerido": new_name,
                                "Ruta": os.path.join(directory, filename)
                            })
                    progress_bar.progress((i + 1) / len(files))
                
                if results:
                    st.session_state.df_suggestions = pd.DataFrame(results)
                else:
                    st.session_state.df_suggestions = None
                    st.info("No se encontraron archivos que necesiten renombrarse.")
            else:
                st.error("La ruta no existe.")

# Mostrar Editor de Datos
if st.session_state.df_suggestions is not None:
    st.write("### 📋 Editar Sugerencias")
    
    # El data_editor permite que el usuario interactúe con la tabla
    edited_df = st.data_editor(
        st.session_state.df_suggestions,
        column_config={
            "Aceptar": st.column_config.CheckboxColumn(help="Selecciona para renombrar"),
            "Nombre Actual": st.column_config.TextColumn(disabled=True),
            "Nombre Sugerido": st.column_config.TextColumn(width="large"),
            "Ruta": None # Ocultar ruta
        },
        disabled=["Nombre Actual"],
        hide_index=True,
        use_container_width=True,
        key="editor"
    )
    
    # Botón para ejecutar
    st.write("")
    if st.button("🚀 Aplicar Cambios Seleccionados", use_container_width=True):
        final_changes = edited_df[edited_df["Aceptar"] == True]
        
        if final_changes.empty:
            st.warning("No has seleccionado ningún archivo para renombrar.")
        else:
            success_count = 0
            for index, row in final_changes.iterrows():
                try:
                    old_path = row["Ruta"]
                    new_name = row["Nombre Sugerido"]
                    if not new_name.lower().endswith('.pdf'):
                        new_name += ".pdf"
                        
                    new_path = os.path.join(directory, new_name)
                    if os.path.exists(new_path):
                        base, ext = os.path.splitext(new_name)
                        idx = 1
                        while os.path.exists(os.path.join(directory, f"{base} ({idx}){ext}")):
                            idx += 1
                        new_path = os.path.join(directory, f"{base} ({idx}){ext}")
                    
                    os.rename(old_path, new_path)
                    success_count += 1
                except Exception as e:
                    st.error(f"Error con {row['Nombre Actual']}: {e}")
            
            st.success(f"✅ ¡Éxito! Se han renombrado {success_count} archivos.")
            st.session_state.df_suggestions = None

st.sidebar.markdown("""
### Manual de Usuario
1. **Analiza**: Escanea tu carpeta.
2. **Edita**: Haz doble clic en cualquier nombre sugerido para corregirlo.
3. **Selecciona**: Desmarca la casilla 'Aceptar' si no quieres renombrar ese archivo.
4. **Ejecuta**: Pulsa el botón rojo para aplicar los cambios físicos.
""")
