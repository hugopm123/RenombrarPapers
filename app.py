import streamlit as st
import os
import re
import fitz  # PyMuPDF
from pathlib import Path

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="PDF Paper Renamer - Visual Engine",
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
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #262730;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DEL MOTOR VISUAL (4.2) ---

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
            "journal", "review article", "original article"
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
            return full_title if len(full_title.split()) >= 3 else None
    except:
        pass
    return None

# --- INTERFAZ STREAMLIT ---

st.title("📚 PDF Paper Renamer Pro")

with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        directory = st.text_input("Ruta de la carpeta:", placeholder="/Volumes/SSD/Maestria/Papers usados")
    with col2:
        st.write("") # Espaciador
        st.write("") 
        scan_btn = st.button("🔍 Analizar Carpeta")

if directory:
    if not os.path.exists(directory):
        st.error("❌ La ruta especificada no existe.")
    else:
        path = Path(directory)
        files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf') and not f.startswith('._')]
        
        if scan_btn:
            st.session_state.suggestions = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, filename in enumerate(files):
                status_text.text(f"Analizando: {filename}")
                title = extract_title_visual(os.path.join(directory, filename))
                if title:
                    new_name = sanitize_filename(title) + ".pdf"
                    if filename != new_name:
                        st.session_state.suggestions.append({
                            "Original": filename,
                            "Sugerido": new_name,
                            "Completo": os.path.join(directory, filename)
                        })
                progress_bar.progress((i + 1) / len(files))
            
            status_text.text(f"Análisis completado. {len(st.session_state.suggestions)} cambios sugeridos.")

        if "suggestions" in st.session_state and st.session_state.suggestions:
            st.write("### 📋 Sugerencias de Renombrado")
            
            # Mostrar tabla de cambios
            st.table(st.session_state.suggestions)
            
            st.warning("⚠️ Esta acción renombrará los archivos físicamente en tu disco.")
            
            if st.button("🚀 Aplicar Cambios Ahora"):
                success_count = 0
                for item in st.session_state.suggestions:
                    try:
                        old_path = item["Completo"]
                        new_path = os.path.join(directory, item["Sugerido"])
                        
                        # Manejo de colisiones
                        if os.path.exists(new_path):
                            base, ext = os.path.splitext(item["Sugerido"])
                            idx = 1
                            while os.path.exists(os.path.join(directory, f"{base} ({idx}){ext}")):
                                idx += 1
                            new_path = os.path.join(directory, f"{base} ({idx}){ext}")
                        
                        os.rename(old_path, new_path)
                        success_count += 1
                    except Exception as e:
                        st.error(f"Error con {item['Original']}: {e}")
                
                st.success(f"✅ ¡Éxito! Se han renombrado {success_count} archivos.")
                st.session_state.suggestions = [] # Limpiar después de procesar
        elif scan_btn:
            st.info("Todos los archivos ya tienen nombres correctos según el motor visual.")

st.sidebar.markdown("""
### Instrucciones
1. Pega la ruta de tu carpeta.
2. Haz clic en **Analizar**.
3. Revisa la tabla previa de sugerencias.
4. Haz clic en **Aplicar Cambios**.
""")
