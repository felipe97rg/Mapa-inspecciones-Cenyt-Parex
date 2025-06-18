import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image
import plotly.express as px
from streamlit_image_select import image_select
import base64

# Configurar la página
st.set_page_config(layout="wide", page_title="Dashboard Circuito 34.5 kV Cabrestero")

st.markdown("""
    <style>
        /* Fondo general con transparencia (95%) */
        .stApp {
            background-color: rgba(253, 246, 236, 0.95) !important;
        }

        /* Opcional: remover márgenes laterales */
        .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
""", unsafe_allow_html=True)



# =======================
# Fila 1: Título + KPIs
# =======================
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.image("IMAGENES/Logo PAREX - PNG.png", width=240)

with col2:
    st.markdown(
        """
        <div class='two alt-two'>
            <h1>Circuito 34.5 kV Cabrestero<span>Reporte de visualización</span></h1>
        </div>
        """,
        unsafe_allow_html=True
    )



with col3:
    st.image("IMAGENES/Cenyt_logo.png", width=240)

st.markdown("""
    <style>
        /* Contenedor de columna que contiene las imágenes */
        .element-container:has(img) {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            height: 100%;
        }

        /* Centrar también el texto verticalmente */
        .element-container:has(.two) {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            height: 100%;
        }

        /* Ajuste visual para imágenes */
        img {
            max-height: 120px;
            object-fit: contain;
        }

        /* === HEADING STYLE #2 === */
        .two h1 {
            position: relative;
            text-transform: capitalize;
            text-align: center;
            font-size: 2.2em;
            margin-bottom: 0.5em;
            color: #167658;
            font-family: 'Segoe UI', sans-serif;
        }

        .two h1:before {
            position: absolute;
            left: 50%;
            bottom: 0;
            width: 60px;
            height: 2px;
            content: "";
            background-color: #167658;
            transform: translateX(-50%);
        }

        .two h1 span {
            display: block;
            font-size: 13px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 4px;
            line-height: 2em;
            padding-top: 8px;
            color: rgba(0, 0, 0, 0.5);
        }
    </style>
""", unsafe_allow_html=True)


# =======================
# Cargar datos
# =======================
df = pd.read_csv('df_final2.csv', encoding='utf-8')
col_requeridas = ['LATITUD NUEVO', 'LONGITUD NUEVO', 'circuito', 'estructura']
if not all(col in df.columns for col in col_requeridas):
    st.error("Faltan columnas requeridas: " + ", ".join(col_requeridas))
    st.stop()

# KPIs principales
kpi1, kpi2 = st.columns(2)

with kpi1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{df['estructura'].dropna().shape[0]}</div>
            <div class="kpi-label">Cantidad de estructuras</div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{df['circuito'].dropna().nunique()}</div>
            <div class="kpi-label">Cantidad de circuitos</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
        .kpi-card {
            background-color: #f5f0dc;
            border: 1px solid #e0dccf;
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        }

        .kpi-value {
            font-size: 48px;
            font-weight: bold;
            color: #167658;
            margin-bottom: 0.2rem;
        }

        .kpi-label {
            font-size: 16px;
            color: #222;
        }
    </style>
""", unsafe_allow_html=True)


# =======================
# Filtro de circuitos
# =======================
circuitos_disponibles = df['circuito'].dropna().unique().tolist()
circuitos_disponibles.sort()
circuitos_seleccionados = st.multiselect(
    "Filtrar por uno o más circuitos:",
    options=circuitos_disponibles,
    default=circuitos_disponibles,
    help="Selecciona uno o más circuitos para filtrar los datos. Puedes seleccionar múltiples circuitos manteniendo presionada la tecla Ctrl (o Cmd en Mac).",
    key="circuito_filter",
    label_visibility="visible",
    placeholder="Selecciona circuitos (ej. Circuito 1, Circuito 2, ...)"
)
df_filtrado = df[df['circuito'].isin(circuitos_seleccionados)]

# =======================
# Fila 2: Gráfico + Mapa
# =======================
col_f2_1, col_f2_2 = st.columns([1, 2])



# Contenedor de la gráfica
with col_f2_1:
    with st.container():
        st.markdown("""
            <div style='
                background-color: #f5f0dc;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #e0dccf;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
                margin-bottom: 1rem;
            '>
                <h3 style='color:#167658; margin-top:0;'>Estructuras por Circuito</h3>
        """, unsafe_allow_html=True)

        conteo_circuitos = (
            df_filtrado.groupby('circuito')['estructura']
            .count()
            .reset_index()
            .rename(columns={'estructura': 'Cantidad de estructuras'})
            .sort_values('Cantidad de estructuras', ascending=True)
        )

        fig = px.bar(
            conteo_circuitos,
            x='Cantidad de estructuras',
            y='circuito',
            orientation='h',
            text='Cantidad de estructuras',
            color='Cantidad de estructuras',
            color_continuous_scale='greens'
        )

        fig.update_traces(
            textposition='outside',
            marker_line_color='#2e5e4e',
            marker_line_width=0.5
        )

        fig.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor='#f5f0dc',
            paper_bgcolor='#f5f0dc',
            font=dict(color='black', family="Segoe UI"),
            legend_font_color='black',
            xaxis=dict(color='black', tickfont=dict(color='black')),
            yaxis=dict(color='black', tickfont=dict(color='black')),
            margin=dict(t=20, r=20, b=20, l=20)
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


with col_f2_2:
    st.markdown("""
            <div style='
                background-color: #f5f0dc;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #e0dccf;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
                margin-bottom: 1rem;
            '>
                <h3 style='color:#167658; margin-top:0;'>Mapa de Estructuras</h3>
        """, unsafe_allow_html=True)
    centro = [df_filtrado["LATITUD NUEVO"].mean(), df_filtrado["LONGITUD NUEVO"].mean()]
    mapa = folium.Map(
        location=centro,
        zoom_start=13,
        tiles="http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google Satellite"
    )

    for _, row in df_filtrado.iterrows():
        lat, lon = row['LATITUD NUEVO'], row['LONGITUD NUEVO']
        if pd.notnull(lat) and pd.notnull(lon):
            popup_text = str(row['estructura'])
            tooltip_text = f"Circuito: {row['circuito']}"
            folium.Marker(
                location=[lat, lon],
                tooltip=tooltip_text,
                popup=folium.Popup(popup_text, max_width=250),
                icon=folium.Icon(icon='info-sign')
            ).add_to(mapa)

    map_data = st_folium(mapa , use_container_width=True, returned_objects=["last_object_clicked_popup"])

# =======================
# Fila 3: Tabla + Carrusel + Imagen
# =======================
col_f3_1, col_f3_2, col_f3_3 = st.columns([2, 1, 2])  # Puedes ajustar proporciones si deseas

# --------- PRIMERA COLUMNA: TABLA ----------
with col_f3_1:
    with st.container():
        st.markdown("""
            <div style='
                background-color: #f5f0dc;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #e0dccf;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
                margin-bottom: 1rem;
            '>
                <h3 style='color:#167658; text-align:center;'>Datos del Punto Seleccionado</h3>
        """, unsafe_allow_html=True)

        if map_data and map_data.get("last_object_clicked_popup"):
            estructura_val = map_data["last_object_clicked_popup"].strip()
            seleccion = df[df['estructura'].astype(str).str.strip() == estructura_val]

            if not seleccion.empty:
                st.dataframe(seleccion.transpose(), use_container_width=True, height=800)
            else:
                st.warning(f"No se encontró estructura: {estructura_val}")
        else:
            st.info("Haz clic en un marcador para ver detalles.")

        st.markdown("</div>", unsafe_allow_html=True)

# --------- SEGUNDA COLUMNA: CARRUSEL DE OPCIONES ----------
seleccionada = None
label_seleccionada = None

with col_f3_2:
    with st.container():
        st.markdown("""
            <div style='
                background-color: #f5f0dc;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #e0dccf;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
                margin-bottom: 1rem;
                text-align: center;
            '>
                <h3 style='color:#167658; margin-top:0;'>Imágenes</h3>
        """, unsafe_allow_html=True)

        if map_data and map_data.get("last_object_clicked_popup"):
            estructura_val = map_data["last_object_clicked_popup"].strip()
            seleccion = df[df['estructura'].astype(str).str.strip() == estructura_val]

            if not seleccion.empty:
                opciones = {
                    "Levantamiento": seleccion.iloc[0].get("fotoPath_limpio", None),
                    "Imagen termográfica": seleccion.iloc[0].get("Termografia", None),
                    "Imagen normal": seleccion.iloc[0].get("Imagen normal", None)
                }

                opciones_filtradas = {k: v for k, v in opciones.items() if pd.notnull(v) and v.strip() != ""}
                if opciones_filtradas:
                    image_paths = [f"IMAGENES/{ruta}" for ruta in opciones_filtradas.values()]
                    labels = list(opciones_filtradas.keys())

                    seleccionada = image_select(
                        label="Haz clic para ver una imagen:",
                        images=image_paths,
                        captions=labels,
                        use_container_width=True
                    )

                    if seleccionada:
                        index = image_paths.index(seleccionada)
                        label_seleccionada = labels[index]
                else:
                    st.info("📁 No hay imágenes disponibles.")
            else:
                st.warning(f"No se encontró estructura: {estructura_val}")
        else:
            st.info("Haz clic en un marcador para ver la imagen.")

        st.markdown("</div>", unsafe_allow_html=True)

# --------- TERCERA COLUMNA: VISUALIZACIÓN DE IMAGEN ----------
with col_f3_3:
    with st.container():
        st.markdown("""
            <div style='
                background-color: #f5f0dc;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #e0dccf;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
                margin-bottom: 1rem;
                text-align: center;
            '>
                <h3 style='color:#167658; margin-top:0;'>Vista seleccionada</h3>
        """, unsafe_allow_html=True)

        if seleccionada:
            try:
                img = Image.open(seleccionada)
                if label_seleccionada == "Levantamiento":
                    img = img.rotate(-90, expand=True)
                
                # Guardar imagen temporal con nombre estándar
                temp_path = "temp_image_display.png"
                img.save(temp_path)

                # Insertar con HTML
                st.markdown(f"""
                    <div style='display:flex; justify-content:center;'>
                        <img src="data:image/png;base64,{base64.b64encode(open(temp_path, 'rb').read()).decode()}"
                             style="max-width:100%; max-height:600px; border-radius:12px; border:2px solid #ccc;" 
                             alt="{label_seleccionada}">
                    </div>
                    <p style="text-align:center; color:#167658;"><strong>{label_seleccionada}</strong></p>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.warning("⚠️ No se pudo cargar o rotar la imagen.")
        else:
            st.info("Selecciona una imagen en la columna anterior.")

        st.markdown("</div>", unsafe_allow_html=True)

