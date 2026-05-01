# 📚 PDF Paper Renamer (Interactive Pro)

**PDF Paper Renamer** es una solución profesional para la organización de bibliotecas académicas. Utiliza un **Motor Visual Pro** basado en jerarquía tipográfica para identificar títulos reales por su tamaño de fuente, ofreciendo ahora una interfaz interactiva completa para un control total del usuario.

## Características Principales

- **Análisis Visual 4.2**: Identifica títulos detectando el texto con la fuente más grande de la portada.
- **Interfaz Interactiva**: Dashboard moderno para gestionar el proceso de renombrado de forma visual.
- **Edición en Tiempo Real**: Permite corregir o modificar manualmente los nombres sugeridos antes de aplicarlos.
- **Selección Granular**: Casillas de verificación para elegir exactamente qué archivos renombrar.
- **Filtros Anti-Ruido**: Ignora automáticamente encabezados universitarios, preprints y metadatos técnicos.
- **Gestión de Colisiones**: Manejo automático de nombres duplicados mediante sufijos numerados.

## 🚀 Instalación

1. Asegúrate de tener instalado **Python 3.x**.
2. Instala las dependencias necesarias:
   ```bash
   pip install streamlit pymupdf pandas
   ```

## 🛠️ Modos de Uso

### 1. Dashboard Interactivo (Recomendado)
Para una experiencia de gestión profesional con edición y selección:
```bash
streamlit run app.py
```

### 2. Terminal (CLI)
Para procesos rápidos y directos desde la línea de comandos:
```bash
python rename_papers.py "/ruta/a/tus/papers"
```

## 📖 Guía del Dashboard
1. **Analiza**: Pega la ruta de tu carpeta y pulsa el botón de lupa.
2. **Revisa**: Observa la tabla de sugerencias generada.
3. **Edita**: Haz doble clic en cualquier celda de "Nombre Sugerido" para realizar correcciones manuales.
4. **Selecciona**: Desmarca los archivos que no desees modificar.
5. **Ejecuta**: Pulsa el botón "Aplicar Cambios" para realizar el renombrado físico en el disco.
