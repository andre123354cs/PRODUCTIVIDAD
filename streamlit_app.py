import streamlit as st
import pandas as pd
import locale
import pyarrow.parquet as pq
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pyrebase

st.set_page_config(
    page_title="MetaData",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Función para limpiar el caché
def clear_cache():
    st.cache_data.clear()

# Botón para ejecutar la limpieza del caché
if st.button('Actualizar'):
    clear_cache()
    st.toast(f"✅ ¡Actualización en curso! 🎉")

st.markdown("""
    <h1 style='text-align: center; color: #005780; font-size: 15px;'>Nuestro desarrollo de software está transformando la forma en que trabajamos. Al automatizar tareas repetitivas, liberamos tiempo y recursos para que puedas concentrarte en lo que realmente importa.🖥</h1>
    """, unsafe_allow_html=True)

# Diccionario de pagos cruzados
Pagos_Cruzados = {
    "Comfama": r"https://drive.usercontent.google.com/u/0/uc?id=1u5LH75bdQ5AhJAi67uFfA40EtpANPFNs&export=download",
    "Azzorti": r"https://drive.usercontent.google.com/u/0/uc?id=1R1f6PWmaag4Gm9TGjM_z-EuSz2OEIpQV&export=download",
    "Cueros": r"https://drive.usercontent.google.com/u/0/uc?id=1aBkcFKmqPbJVTZvoUuQGymsUuYWHtyQQ&export=download",
    "Keypago": r"https://drive.usercontent.google.com/u/0/uc?id=17CSMaLPPY1pOa7_ZykXzvQfhRbPNbGHh&export=download",
    "Linea Directa": r"https://drive.usercontent.google.com/u/0/uc?id=1ityd0ukmDHOvbZfExIldjucF56L-oJS5&export=download",
    "Nova Mexico": r"https://drive.usercontent.google.com/u/0/uc?id=17Mv66TRBPDOHqAAh170PjlRenJaDASd6&export=download",
    "Nova Colombia": r"https://drive.usercontent.google.com/u/0/uc?id=1sSZN5nMI7XTULgiiHFffpr72xMmS712A&export=download",
}

# Diccionario de metas
Metas = {
    "Comfama": 100000000,
    "Azzorti": 100000000,
    "Cueros": 100000000,
    "Keypago": 100000000,
    "Linea Directa": 100000000,
    "Nova Mexico": 100000000,
    "Nova Colombia": 100000000,
}

# Filtro para seleccionar la cartera
cartera_seleccionada = st.selectbox('Selecciona la cartera', list(Pagos_Cruzados.keys()))

# Mostrar la tabla correspondiente a la cartera seleccionada y crear acumulado de pagos
if cartera_seleccionada:
    url = Pagos_Cruzados[cartera_seleccionada]
    try:
        df = pd.read_parquet(url)
        
        # Filtrar los datos por Cartera_x
        df_filtrado = df[df['Cartera_x'] == cartera_seleccionada]
        
        # Ordenar los datos por Mes_Creacion y Dia
        df_filtrado = df_filtrado.sort_values(by=['Mes_Creacion', 'Dia'])
        
        # Crear columna acumulada de pagos por día en cada mes
        df_filtrado['Acumulado_Pagos'] = df_filtrado.groupby(['Mes_Creacion'])['Pagos'].cumsum()
        
        # Filtro para seleccionar uno o más meses
        meses = df_filtrado['Mes_Creacion'].unique()
        meses_seleccionados = st.multiselect('Selecciona los meses', meses, default=meses[:2])
        
        # Filtrar los datos según los meses seleccionados
        df_meses = df_filtrado[df_filtrado['Mes_Creacion'].isin(meses_seleccionados)]
        
        # Crear la gráfica
        fig = go.Figure()
        
        for mes in meses_seleccionados:
            df_mes = df_meses[df_meses['Mes_Creacion'] == mes]
            fig.add_trace(go.Scatter(x=df_mes['Dia'], y=df_mes['Acumulado_Pagos'], mode='lines+markers', name=f'Acumulado {mes}'))
        
            # Mostrar la última etiqueta de cada línea
            fig.add_annotation(x=df_mes['Dia'].iloc[-1], y=df_mes['Acumulado_Pagos'].iloc[-1],
                               text=f"{df_mes['Acumulado_Pagos'].iloc[-1]:,.2f}", showarrow=True, arrowhead=2)
        
        # Añadir línea discontinua para la meta acumulada diaria
        dias = np.arange(1, 31)
        meta_acumulada_diaria = (Metas[cartera_seleccionada] / 30) * dias
        fig.add_trace(go.Scatter(x=dias, y=meta_acumulada_diaria, mode='lines', name='Meta Acumulada Diaria', line=dict(dash='dash', color='red')))
        
        # Mostrar la última etiqueta de la línea de meta
        fig.add_annotation
