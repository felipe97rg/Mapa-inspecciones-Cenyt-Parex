import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image
import plotly.express as px

# Configurar la página
st.set_page_config(layout="wide", page_title="Dashboard Circuito 34.5 kV Cabrestero")

# Título principal
st.markdown(
    "<h1 style='text-align: center; color: red;'>📍 Dashboard Circuito 34.5 kV Cabrestero</h1>",
    unsafe_allow_html=True
)

# Cargar archivo
df = pd.read_csv('df_final.csv', encoding='utf-8')

# Validar columnas requeridas
col_requeridas = ['LATITUD NUEVO', 'LONGITUD NUEVO', 'circuito', 'estructura']
if not all(col in df.columns for col in col_requeridas):
    st.error("Faltan columnas requeridas: " + ", ".join(col_requeridas))
    st.stop()

# KPIs principales
kpi1, kpi2 = st.columns(2)
kpi1.metric("📌 Total Estructuras", df['estructura'].dropna().shape[0])
kpi2.metric("🔌 Cantidad de Circuitos", df['circuito'].dropna().nunique())

# Crear columnas principales del dashboard
col_izq, col_der = st.columns([1.2, 1.8])

# Columna derecha: filtro múltiple + mapa
with col_der:
    st.subheader("🗺️ Mapa de Estructuras")

    with st.container():
        # Filtro múltiple por circuito
        circuitos_disponibles = df['circuito'].dropna().unique().tolist()
        circuitos_disponibles.sort()
        circuitos_seleccionados = st.multiselect(
            "🔍 Filtra por uno o más circuitos:",
            options=circuitos_disponibles,
            default=circuitos_disponibles
        )

        # Filtrar el dataframe según selección
        df_filtrado = df[df['circuito'].isin(circuitos_seleccionados)]

        # Crear mapa base centrado en los datos filtrados
        centro = [df_filtrado["LATITUD NUEVO"].mean(), df_filtrado["LONGITUD NUEVO"].mean()]
        mapa = folium.Map(
            location=centro,
            zoom_start=13,
            tiles="http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            attr="Google Satellite"
        )

        # Agregar marcadores
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

        # Mostrar el mapa interactivo
        map_data = st_folium(mapa, height=600, width=900, returned_objects=["last_object_clicked_popup"])

# Columna izquierda: información del punto seleccionado
with col_izq:
    
    st.subheader("📊 Estructuras por Circuito")

    # Contar estructuras por circuito en el dataframe filtrado
    conteo_circuitos = (
        df[df['circuito'].isin(circuitos_seleccionados)]
        .groupby('circuito')['estructura']
        .count()
        .reset_index()
        .rename(columns={'estructura': 'Cantidad de estructuras'})
        .sort_values('Cantidad de estructuras', ascending=True)
    )

    # Gráfico con degradado morado según cantidad
    fig = px.bar(
        conteo_circuitos,
        x='Cantidad de estructuras',
        y='circuito',
        orientation='h',
        title="Cantidad de estructuras por circuito",
        text='Cantidad de estructuras',
        color='Cantidad de estructuras',
        color_continuous_scale='purples'  # escala de morado claro a oscuro
    )
    # Ajustar estilo de etiquetas
    fig.update_traces(textposition='outside')
    fig.update_layout(coloraxis_showscale=False)  # oculta la barra de escala si no la quieres visible
    st.plotly_chart(fig, use_container_width=True)

    # Tabla con Información del punto seleccionado
    st.subheader("📋 Datos del Punto Seleccionado")

    if map_data and map_data.get("last_object_clicked_popup"):
        estructura_val = map_data["last_object_clicked_popup"].strip()
        seleccion = df[df['estructura'].astype(str).str.strip() == estructura_val]

        if not seleccion.empty:
            st.dataframe(seleccion.transpose(), use_container_width=True)

            # Mostrar imagen rotada si está disponible
            ruta_img = seleccion.iloc[0].get("fotoPath_limpio", None)
            if pd.notnull(ruta_img) and ruta_img.strip() != "":
                st.subheader("🖼️ Imagen asociada")
                try:
                    img = Image.open(f"IMAGENES/{ruta_img}")
                    img_rotated = img.rotate(-90, expand=True)
                    st.image(img_rotated, use_container_width=True, caption=f"Estructura: {estructura_val}")
                except Exception as e:
                    st.warning(f"No se pudo cargar la imagen: {ruta_img}")
            else:
                st.info("📁 No hay imagen disponible para esta estructura.")
        else:
            st.warning(f"No se encontró estructura: {estructura_val}")
    else:
        st.info("Haz clic en un marcador para ver detalles.")
