
# 📚 Kindle Analytics & Manager

**Kindle Analytics** es una herramienta interactiva construida con Python y Streamlit que transforma tu archivo caótico de `My Clippings.txt` en un **Dashboard de Lectura** visual, organizado y lleno de estadísticas.

Esta aplicación te permite visualizar tu consistencia de lectura con un calendario estilo GitHub, obtener métricas detalladas y exportar tus subrayados en formatos limpios y legibles, eliminando el ruido del formato original de Amazon.

![Kindle Analytics Screenshot](https://via.placeholder.com/1000x500?text=Sube+una+captura+de+pantalla+aqui)
*(Reemplaza este link con una captura real de tu dashboard)*

## ✨ Características Principales

* **📊 Dashboard Visual:** KPIs de libros leídos, notas totales y estado de tu biblioteca.
* **🟩 Calendario de Actividad (Heatmap):** Visualiza tus hábitos de lectura con un gráfico de calor idéntico al de las contribuciones de GitHub. Soporta vista anual e histórica completa (vertical).
* **📂 Exportación Limpia:** Convierte el archivo crudo del Kindle en:
    * **Archivos .txt individuales** por libro (organizados en ZIP).
    * **Un solo archivo maestro** con cabeceras legibles y ordenado por autor.
* **🧠 Lógica Inteligente de Fechas:** Detecta cuándo empezaste y terminaste un libro usando etiquetas personalizadas, ignorando relecturas posteriores para no alterar tu historial.
* **🛠️ Corrección de Errores:** Limpia automáticamente títulos duplicados, caracteres invisibles y errores de formato comunes del Kindle.

---

## ✨ Transformación: Antes y Después

El script toma el formato repetitivo del Kindle y lo convierte en un resumen elegante.

**🔴 Antes (Archivo Crudo `My Clippings.txt`):**
```text
De la brevedad de la vida (Séneca)
- La nota en la página 13 | posición 185 | Añadido el martes, 28 de febrero de 2025 02:53:35

No tenemos escaso tiempo, sino que perdemos mucho.
==========
De la brevedad de la vida (Séneca)
- La nota en la página 14 | posición 190 | Añadido el martes, 28 de febrero de 2025 03:10:00

Todo lo teméis como mortales, todo lo queréis como inmortales.
==========

```

**🟢 Después (Formato Limpio de Kindle Analytics):**

```text
Título del libro: De la brevedad de la vida
Autor: Séneca
Estimado de fechas de lectura: 28/02/2025 - 28/02/2025

"No tenemos escaso tiempo, sino que perdemos mucho."

"Todo lo teméis como mortales, todo lo queréis como inmortales."

```

---

## 📂 ¿Dónde encuentro el archivo `My Clippings.txt`?

Este archivo se genera automáticamente en tu Kindle cada vez que subrayas algo. Para obtenerlo:

1. **Conecta tu Kindle** a tu computadora (PC o Mac) usando el cable USB.
2. Abre el **Explorador de Archivos** (Windows) o **Finder** (Mac).
3. Verás aparecer una unidad externa llamada **Kindle**.
4. Entra en la carpeta **`documents`**.
5. Busca el archivo llamado **`My Clippings.txt`** (o *Mis recortes.txt*).
6. Cópialo a tu computadora para subirlo a la aplicación.

---

## 🚀 Instalación y Ejecución

Sigue estos pasos para correr la aplicación en tu computadora local.

### Prerrequisitos

* Python 3.8 o superior instalado.

### 1. Clonar el repositorio

```bash
git clone https://github.com/victorfranco97/kindle_clippings_formatting
cd kindle-analytics

```

### 2. Crear un entorno virtual (Recomendado)

Para mantener las librerías aisladas:

**En Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate

```

**En Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate

```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt

```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py

```

Automáticamente se abrirá una pestaña en tu navegador (usualmente en `http://localhost:8501`) donde podrás arrastrar tu archivo.

---

## 📖 Guía de Uso en Kindle (Etiquetas Mágicas)

Kindle no guarda explícitamente la "Fecha de finalización" de un libro. Para solucionar esto y tener estadísticas precisas, este sistema usa **Etiquetas (Tags)** que puedes escribir como notas directamente en tu Kindle.

### ¿Cómo hacerlo?

1. En tu Kindle, selecciona una palabra en la última página (o donde termines).
2. Toca "Nota" y escribe una de las etiquetas de abajo.
3. Guarda la nota.

### Las Etiquetas Disponibles

#### 1. `#end` (Finalización Inteligente/Retroactiva)

Úsalo para organizar tu biblioteca vieja o tu lectura normal.

* **Comportamiento:**
* Si creas esta nota **menos de 30 días** después de tu último subrayado, el sistema usa la fecha de la nota como fecha de fin.
* **Modo Organización:** Si abres un libro que leíste hace 2 años y agregas `#end` hoy para organizarlo, el sistema detectará la gran diferencia de tiempo e **ignorará la fecha de hoy**, usando la fecha de tu último subrayado real de hace 2 años. ¡Tu historial se mantiene intacto!



#### 2. `#endtoday` (Finalización Forzada)

Úsalo cuando termines un libro **HOY**, sin importar las circunstancias.

* **Comportamiento:** Fuerza al sistema a marcar el libro como terminado en la fecha exacta de esta nota. Es útil si leíste un libro durante meses sin subrayar nada y quieres certificar que lo terminaste hoy.

---

## ⚙️ Estructura del Proyecto

```text
kindle-analytics/
├── app.py              # Código principal (Frontend + Backend)
├── requirements.txt    # Dependencias (streamlit, pandas, plotly, unidecode)
├── README.md           # Documentación
└── .gitignore          # Archivos ignorados por git

```

## 🛠️ Tecnologías Usadas

* **[Streamlit](https://streamlit.io/):** Para la interfaz web interactiva.
* **[Pandas](https://pandas.pydata.org/):** Para el procesamiento y limpieza de datos.
* **[Plotly](https://plotly.com/):** Para los gráficos interactivos y el Heatmap.

## 📄 Licencia

Este proyecto es de código abierto. Siéntete libre de usarlo, modificarlo y compartirlo.

```

```