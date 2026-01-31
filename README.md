# 📚 Kindle Analytics & Manager

**Kindle Analytics** es una herramienta interactiva construida con Python y Streamlit que transforma tu archivo caótico de `My Clippings.txt` en un **Dashboard de Lectura** visual y organizado.

Permite visualizar tu consistencia de lectura con un calendario estilo GitHub, obtener estadísticas detalladas y exportar tus subrayados limpios y ordenados por libro.

*(¡Recuerda subir una captura de pantalla de tu app y reemplazar este link!)*

## ✨ Características

* **📊 Dashboard Visual:** KPIs de libros leídos, notas totales y rachas de lectura.
* **🟩 Calendario de Actividad (Heatmap):** Visualiza tus días de lectura con un gráfico de calor idéntico al de las contribuciones de GitHub. Soporta vista anual e histórica completa.
* **📂 Exportación Limpia:** Convierte el archivo crudo del Kindle en:
* **Archivos .txt individuales** por libro (organizados en ZIP).
* **Un solo archivo maestro** formateado con cabeceras legibles.


* **🧠 Lógica Inteligente de Fechas:** Detecta cuándo empezaste y terminaste un libro usando etiquetas personalizadas, ignorando relecturas posteriores para no alterar tu historial.
* **🛠️ Corrección de Errores:** Limpia automáticamente títulos duplicados y caracteres invisibles que suele generar el Kindle.

---

## 🚀 Instalación y Ejecución

Sigue estos pasos para correr la aplicación en tu computadora local.

### Prerrequisitos

* Python 3.8 o superior.

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/kindle-analytics.git
cd kindle-analytics

```

### 2. Crear un entorno virtual (Opcional pero recomendado)

**Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate

```

**Mac/Linux:**

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

Automáticamente se abrirá una pestaña en tu navegador (usualmente en `http://localhost:8501`).

---

## 📖 Guía de Uso en Kindle (Etiquetas Mágicas)

Para que el sistema detecte con precisión cuándo terminaste un libro, puedes usar un sistema de **Etiquetas (Tags)** escribiendo una nota directamente en tu Kindle.

### ¿Cómo hacerlo?

1. En tu Kindle, ve a la última página del libro o selecciona una frase final.
2. Toca "Nota" y escribe una de las siguientes etiquetas.
3. Guarda la nota.

### Las Etiquetas Disponibles

#### 1. `#end` (Finalización Estándar)

Úsalo para organizar tu biblioteca retroactivamente o normalmente.

* **Comportamiento:**
* Si creas esta nota **menos de 30 días** después de tu último subrayado, el sistema usará la fecha de la nota como "Fecha de Fin".
* Si estás organizando libros viejos y creas esta nota **meses después** de haber leído el libro, el sistema inteligente **ignorará la fecha de hoy** y usará la fecha de tu último subrayado real para respetar la historia.



#### 2. `#endtoday` (Finalización Forzada)

Úsalo cuando termines un libro **HOY**, sin importar si lo empezaste hace años o si no subrayaste nada en meses.

* **Comportamiento:** Fuerza al sistema a marcar el libro como terminado en la fecha exacta de esta nota. Ignora cualquier cálculo de inactividad.

### Ejemplo de flujo de trabajo

* **Termino un libro hoy:** Hago una nota que diga `#endtoday`.
* **Organizo un libro que leí en 2022:** Abro el libro y hago una nota que diga `#end`. El sistema detectará que es viejo y pondrá la fecha de fin en 2022, no hoy.

---

## ⚙️ Estructura del Proyecto

```text
kindle-analytics/
├── app.py              # Código principal de la aplicación (Frontend + Backend)
├── requirements.txt    # Lista de librerías necesarias
├── README.md           # Este archivo
└── .gitignore          # Archivos ignorados por git

```

## 🛠️ Tecnologías Usadas

* [Streamlit](https://streamlit.io/) - Para la interfaz web.
* [Pandas](https://pandas.pydata.org/) - Para el procesamiento de datos.
* [Plotly](https://plotly.com/) - Para los gráficos interactivos y el Heatmap.

## 📄 Licencia

Este proyecto es de uso libre. ¡Siéntete libre de modificarlo para adaptarlo a tus necesidades de lectura!