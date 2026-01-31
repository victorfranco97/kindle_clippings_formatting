import streamlit as st
import pandas as pd
import re
from datetime import datetime
from unidecode import unidecode
import io
import zipfile
import plotly.graph_objects as go
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Kindle Analytics", page_icon="📊", layout="wide")

# --- FUNCIONES DE BACKEND ---

def parse_date(date_str):
    """Convierte fecha de Kindle a datetime."""
    if not date_str: return None
    date_str = unidecode(date_str.lower().strip())
    
    month_map = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12',
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }

    # Regex flexible para capturar fechas con o sin hora
    # Busca: DiaSemana(opcional) + Dia + "de"(opcional) + Mes + "de"(opcional) + Año
    match = re.search(r'(?:\w+,?\s+)?(\d{1,2})\s+(?:de\s+)?(\w+)\s+(?:de\s+)?(\d{4})', date_str)
    
    if match:
        day, month, year = match.groups()
        month_num = month_map.get(month, '01')
        try:
            return datetime.strptime(f"{year}-{month_num}-{day.zfill(2)}", "%Y-%m-%d")
        except ValueError:
            return None
    return None

def clean_filename_str(text):
    """Limpia strings para que sean nombres de archivo válidos y sin guiones bajos al inicio."""
    # Reemplazar caracteres inválidos por guion bajo
    clean = re.sub(r'[^\w\- \.]', '_', text)
    # Colapsar múltiples guiones bajos en uno solo
    clean = re.sub(r'_{2,}', '_', clean)
    # Eliminar guiones bajos o espacios al inicio y final
    clean = clean.strip('_').strip()
    return clean

def process_file(uploaded_file):
    """Procesa el archivo My Clippings.txt."""
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    raw_text = stringio.read()
    clippings = raw_text.split('==========')
    
    data = []
    
    for clip in clippings:
        lines = clip.strip().split('\n')
        if len(lines) < 4:
            continue
            
        # 1. Título y Autor
        title_author = lines[0].rsplit('(', 1)
        
        # LIMPIEZA CRÍTICA DE TÍTULO: Elimina BOM (\ufeff) y espacios invisibles
        title = title_author[0].replace('\ufeff', '').strip()
        
        author = title_author[1].strip().rstrip(')').strip() if len(title_author) > 1 else "Desconocido"
        
        # 2. Fecha y Locación
        meta_line = lines[1]
        date_match = re.search(r'A\u00f1adido el (.+)$|Added on (.+)$', meta_line)
        raw_date = date_match.group(1) or date_match.group(2) if date_match else ""
        parsed_date = parse_date(raw_date)
        
        loc_match = re.search(r'(Loc\.|page|página|location)\s(\d+)', meta_line, re.IGNORECASE)
        location = int(loc_match.group(2)) if loc_match else 0
        
        # 3. Contenido
        content = "\n".join(lines[3:]).strip()
        
        if content:
            data.append({
                'Autor': author,
                'Título': title,
                'Fecha': parsed_date,
                'Locación': location,
                'Texto': content
            })
            
    return pd.DataFrame(data)

def generate_summary(df, inactivity_days=30):
    """Genera estadísticas con lógica de Tags y Anti-Relectura."""
    summary_data = []
    today = datetime.now()
    
    grouped = df.groupby(['Autor', 'Título'])
    
    for (author, title), group in grouped:
        valid_dates = group['Fecha'].dropna()
        start_date = valid_dates.min() if not valid_dates.empty else None
        
        # Buscar etiquetas
        finish_row = group[group['Texto'].str.contains(r'#(endtoday|fin|end)\b', case=False, regex=True)]
        
        max_loc = group['Locación'].max()
        completion_date = None
        status = ""
        final_date_display = "N/A"
        reading_days = 0
        
        if not finish_row.empty:
            status = "✅ Completado"
            tag_date = finish_row.iloc[0]['Fecha']
            tag_text = finish_row.iloc[0]['Texto'].lower()
            is_force_today = '#endtoday' in tag_text
            
            other_notes = group.drop(finish_row.index)
            
            if not other_notes.empty and tag_date:
                past_notes = other_notes[other_notes['Fecha'] <= tag_date]
                last_historic_highlight = past_notes['Fecha'].max() if not past_notes.empty else tag_date
            else:
                last_historic_highlight = tag_date

            # LÓGICA DE PRIORIDAD DE FECHAS
            if is_force_today:
                # Si es endtoday, USAMOS LA FECHA DEL TAG, sin importar nada más.
                completion_date = tag_date
            elif tag_date and last_historic_highlight:
                difference = (tag_date - last_historic_highlight).days
                if difference > 30:
                    completion_date = last_historic_highlight
                else:
                    completion_date = tag_date
            else:
                completion_date = tag_date
                
            final_date_display = completion_date.strftime('%Y-%m-%d') if completion_date else "S/F"
            
            if start_date and completion_date:
                reading_days = (completion_date - start_date).days
                if reading_days < 0: reading_days = 0
            
        else:
            last_activity = valid_dates.max() if not valid_dates.empty else None
            days_inactive = (today - last_activity).days if last_activity else 0
            
            if days_inactive < inactivity_days:
                status = "📖 Leyendo actualmente"
            else:
                status = "💤 Inactivo"
                
            final_date_display = last_activity.strftime('%Y-%m-%d') if last_activity else "N/A"
            
            if start_date:
                reading_days = (today - start_date).days

        summary_data.append({
            'Autor': author,
            'Título': title,
            'Estado': status,
            'Días leyendo': reading_days,
            'Fecha Inicio': start_date.strftime('%Y-%m-%d') if start_date else "N/A",
            'Fecha Fin / Última': final_date_display,
            'Max Locación': max_loc,
            'Total Notas': len(group)
        })
        
    status_order = {"📖": 0, "💤": 1, "✅": 2}
    df_result = pd.DataFrame(summary_data)
    
    if not df_result.empty:
        df_result['sort_key'] = df_result['Estado'].str[0].map(status_order).fillna(3)
        df_result = df_result.sort_values(by=['sort_key', 'Fecha Fin / Última'], ascending=[True, False])
        df_result = df_result.drop(columns=['sort_key'])
        
    return df_result

def plot_github_heatmap(df, year):
    """Crea un gráfico de calor estilo GitHub."""
    df_year = df[df['Fecha'].dt.year == year].copy()
    
    daily_counts = pd.DataFrame(columns=['Fecha', 'Count'])
    if not df_year.empty:
        daily_counts = df_year['Fecha'].value_counts().reset_index()
        daily_counts.columns = ['Fecha', 'Count']
        daily_counts = daily_counts.sort_values('Fecha')
    
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date)
    
    full_df = pd.DataFrame({'Fecha': date_range})
    full_df = full_df.merge(daily_counts, on='Fecha', how='left').fillna(0)
    
    full_df['Week'] = full_df['Fecha'].dt.isocalendar().week
    full_df['Weekday_Name'] = full_df['Fecha'].dt.day_name()
    
    full_df.loc[(full_df['Fecha'].dt.month == 1) & (full_df['Week'] > 50), 'Week'] = 1
    full_df.loc[(full_df['Fecha'].dt.month == 12) & (full_df['Week'] == 1), 'Week'] = 53

    hover_text = [
        f"<b>{d.strftime('%d %b %Y')}</b><br>Notas: {int(c)}" 
        for d, c in zip(full_df['Fecha'], full_df['Count'])
    ]

    days_order = ['Sunday', 'Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday']
    
    month_ticks = []
    month_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    for i in range(1, 13):
        first_day_month = datetime(year, i, 1)
        week_num = first_day_month.isocalendar().week
        if i == 1 and week_num > 50: week_num = 1
        month_ticks.append(week_num)

    fig = go.Figure(data=go.Heatmap(
        z=full_df['Count'],
        x=full_df['Week'],
        y=full_df['Weekday_Name'],
        text=hover_text,
        hoverinfo='text',
        colorscale=[[0, "#ebedf0"], [0.01, "#9be9a8"], [0.5, "#30a14e"], [1, "#216e39"]],
        showscale=False,
        xgap=2,
        ygap=2
    ))

    fig.update_layout(
        title=dict(text=f"<b>{year}</b>", x=0, font=dict(size=20, color="#333")),
        height=180,
        yaxis=dict(
            categoryorder='array', categoryarray=days_order, tickmode='array',
            tickvals=['Monday', 'Wednesday', 'Friday'], ticktext=['Lun', 'Mié', 'Vie'],
            showgrid=False, zeroline=False, tickfont=dict(size=10)
        ),
        xaxis=dict(
            title="", showgrid=False, zeroline=False, tickmode='array',
            tickvals=month_ticks, ticktext=month_labels, tickfont=dict(size=10)
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=10)
    )
    
    return fig

# --- FRONTEND ---

st.title("📚 Kindle Analytics & Manager")
st.markdown("Sube tu archivo `My Clippings.txt` para obtener reportes detallados y gráficos de tu lectura.")

uploaded_file = st.file_uploader("Arrastra tu archivo aquí", type=['txt'])

if uploaded_file is not None:
    df = process_file(uploaded_file)
    
    if df.empty:
        st.error("No se encontraron datos.")
    else:
        global_max_date = df['Fecha'].max()
        file_date_str = global_max_date.strftime('%Y-%m-%d') if global_max_date else datetime.now().strftime('%Y-%m-%d')
        base_filename = f"{file_date_str}_Kindle"
        
        available_years = sorted(df['Fecha'].dropna().dt.year.unique(), reverse=True)

        # --- SIDEBAR: CONFIGURACIÓN Y DESCARGAS ---
        with st.sidebar:
            st.header("⚙️ Configuración")
            inactivity_days = st.number_input("Días para Inactivo", 1, 365, 30, help="Días sin subrayar para considerar el libro abandonado.")
            
            summary_df = generate_summary(df, inactivity_days)
            
            st.divider()
            
            st.header("📥 Zona de Descargas")
            
            # 1. BOTÓN REPORTE CSV
            st.markdown("**1. Reporte de Progreso**")
            csv = summary_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Descargar Tabla (.csv)",
                data=csv,
                file_name=f"{base_filename}_Reporte.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.markdown("---")
            
            # 2. BOTÓN NOTAS (TXT/ZIP)
            st.markdown("**2. Mis Notas y Citas**")
            output_mode = st.radio("Formato:", ["Archivo Único (.txt)", "Separado por Autor (.zip)"])
            add_timestamp = st.checkbox("Incluir encabezado de fecha", value=True)
            
            timestamp_str = f"Export generado el: {datetime.now().strftime('%d/%m/%Y')}\n" + "="*50 + "\n\n" if add_timestamp else ""
            
            if output_mode == "Archivo Único (.txt)":
                full_text = timestamp_str
                df_sorted = df.sort_values(by=['Autor', 'Título', 'Fecha'])
                
                for (author, title), book_group in df_sorted.groupby(['Autor', 'Título']):
                    dates = book_group['Fecha'].dropna()
                    if not dates.empty:
                        start_str = dates.min().strftime('%d/%m/%Y')
                        end_str = dates.max().strftime('%d/%m/%Y')
                        date_range = f"{start_str} - {end_str}"
                    else:
                        date_range = "Fechas desconocidas"
                    
                    full_text += f"Título del libro: {title}\n"
                    full_text += f"Autor: {author}\n"
                    full_text += f"Estimado de fechas de lectura: {date_range}\n\n"
                    
                    for _, row in book_group.iterrows():
                        full_text += f"\"{row['Texto']}\"\n\n"
                    
                    full_text += "="*50 + "\n\n"
                
                st.download_button(
                    label="📝 Descargar Notas (.txt)", 
                    data=full_text, 
                    file_name=f"{base_filename}_Notas.txt", 
                    mime="text/plain", 
                    use_container_width=True
                )
            
            else: 
                # Modo ZIP
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for author, author_group in df.groupby('Autor'):
                        for title, book_group in author_group.groupby('Título'):
                            book_content = timestamp_str
                            book_content += f"Título del libro: {title}\nAutor: {author}\n\n"
                            
                            for _, row in book_group.iterrows():
                                d_str = row['Fecha'].strftime('%d/%m/%Y') if row['Fecha'] else "S/F"
                                book_content += f"\"{row['Texto']}\"\n(Fecha: {d_str})\n\n"
                            
                            # USAMOS LA NUEVA FUNCIÓN DE LIMPIEZA
                            clean_filename = clean_filename_str(title)
                            filename = f"{clean_filename}.txt"
                            
                            # Limpieza también para la carpeta del autor
                            clean_author = clean_filename_str(author)
                            
                            zf.writestr(f"{clean_author}/{filename}", book_content)
                
                st.download_button(
                    label="🗂️ Descargar Notas (.zip)", 
                    data=zip_buffer.getvalue(), 
                    file_name=f"{base_filename}_Notas.zip", 
                    mime="application/zip", 
                    use_container_width=True
                )
                
            st.info(f"📅 Última actividad detectada: {file_date_str}")

        # --- ÁREA PRINCIPAL (TABS) ---
        tab1, tab2 = st.tabs(["📋 Tabla de Datos", "📈 Estadísticas Gráficas"])

        with tab1:
            st.subheader("Progreso de Lectura")
            st.dataframe(summary_df, use_container_width=True, height=600)

        with tab2:
            st.subheader("📊 Dashboard de Lectura")
            
            st.markdown("### 🟩 Calendario de Actividad")
            
            if available_years:
                view_mode = st.radio("Modo de visualización:", ["Año Individual", "Histórico Completo (Vertical)"], horizontal=True)
                
                if view_mode == "Año Individual":
                    selected_year = st.selectbox("Seleccionar Año:", available_years)
                    fig_heatmap = plot_github_heatmap(df, selected_year)
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                else:
                    st.markdown("---")
                    for year in available_years:
                        fig_heatmap = plot_github_heatmap(df, year)
                        st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.warning("No hay fechas válidas.")
            
            st.divider()

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Total Libros", len(summary_df))
            kpi2.metric("Completados", len(summary_df[summary_df['Estado'] == "✅ Completado"]))
            kpi3.metric("Total Notas", len(df))
            kpi4.metric("Leyendo Ahora", len(summary_df[summary_df['Estado'] == "📖 Leyendo actualmente"]))
            
            st.divider()
            
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.write("**Estado de tu Biblioteca**")
                fig_donut = px.pie(summary_df, names='Estado', hole=0.5, color='Estado',
                                   color_discrete_map={"✅ Completado": "#2ecc71", "📖 Leyendo actualmente": "#3498db", "💤 Inactivo": "#95a5a6"})
                st.plotly_chart(fig_donut, use_container_width=True)
                
            with col_g2:
                st.write("**Top 10 Autores**")
                top_authors = df['Autor'].value_counts().head(10).reset_index()
                top_authors.columns = ['Autor', 'Notas']
                fig_bar = px.bar(top_authors, x='Notas', y='Autor', orientation='h', text='Notas')
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_bar, use_container_width=True)