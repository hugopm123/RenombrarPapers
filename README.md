# 📚 PDF Paper Renamer (Online & Visual)

**PDF Paper Renamer** es una solución profesional para la organización de bibliotecas académicas. Utiliza un **Motor Visual Pro** basado en jerarquía tipográfica para identificar títulos reales por su tamaño de fuente.

## 🚀 Cómo usar

### 1. Versión Web (Online)
La forma más fácil de usarlo. No requiere instalación local.
1. Entra a la URL de tu aplicación en **Streamlit Cloud**.
2. Arrastra tus archivos PDF.
3. Edita los nombres si es necesario y descarga el resultado en un archivo **ZIP**.

### 2. Instalación Local
Si prefieres correrlo en tu computadora:
```bash
pip install streamlit pymupdf pandas
streamlit run app.py
```

## ✨ Características
- **Análisis Visual**: Detecta títulos buscando el texto más prominente de la portada.
- **Edición en Vivo**: Corrige cualquier sugerencia directamente en la tabla antes de descargar.
- **Filtros Anti-Ruido**: Ignora metadatos, universidades y preprints.
- **Privacidad**: Los archivos se procesan en memoria y no se almacenan en el servidor.

---
*Optimiza tu gestión bibliográfica con inteligencia visual.*
