# 📚 PDF Paper Renamer (Visual Engine)

**PDF Paper Renamer** es una herramienta profesional de terminal diseñada para automatizar la organización de bibliotecas científicas. A diferencia de los métodos tradicionales de extracción de texto, esta herramienta utiliza un **Motor Visual Pro** que analiza la jerarquía tipográfica de los documentos para identificar el título real basándose en el **tamaño de la fuente**.

## Características Principales
- **Análisis Tipográfico (Font-Size)**: Identifica el título detectando el texto con la fuente más grande de la portada, garantizando una precisión del 99%.
- **Filtros Inteligentes**: Ignora automáticamente metadatos de revistas (DOI, ISSN), correos electrónicos y encabezados de universidades.
- **Modo Simulación (`--test`)**: Permite previsualizar todos los cambios sugeridos antes de aplicarlos físicamente.
- **Gestión de Colisiones**: Detecta si ya existe un archivo con el mismo nombre y añade sufijos numerados automáticamente.
- **Sanitización Universal**: Genera nombres de archivos limpios y compatibles con Windows, macOS y Linux.

## 🚀 Instalación

1. Asegúrate de tener instalado **Python 3.x**.
2. Instala la dependencia necesaria (**PyMuPDF**):
   ```bash
   pip install pymupdf
   ```

## 🛠️ Uso

El script se ejecuta desde la terminal pasando la ruta de la carpeta donde se encuentran tus archivos PDF.

### 1. Modo Prueba (Recomendado)
Visualiza los nombres que el motor sugiere sin realizar cambios reales:
```bash
python3 rename_papers.py "/ruta/a/tus/pdfs" --test
```

### 2. Renombrado Real
Aplica los cambios definitivamente en tus archivos:
```bash
python3 rename_papers.py "/ruta/a/tus/pdfs"
```

