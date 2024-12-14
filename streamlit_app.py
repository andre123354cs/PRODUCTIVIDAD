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
    <h1 style='text-align: center; color: #ff6347; font-size: 40px;'>Aumenta tu productividad optimizando el recaudo. ¡Alcanza tus metas y maximiza tu eficiencia! 📈</h1>
    """, unsafe_allow_html=True)

# Diccionario de pagos cruzados
Pagos_Cruzados = {
        "Comfama": r"https://drive.usercontent.google.com/u/0/uc?id=1u5LH75bdQ5AhJAi67uFfA40EtpANPFNs&export=download",
        "Azzorti": r"https://drive.usercontent.google.com/u/0/uc?id=1R1f6PWmaag4Gm9TGjM_z-EuSz2OEIpQV&export=download",
        "Cueros": r"https://drive.usercontent.google.com/u/0/uc?id=1aBkcFKmqPbJVTZvoUuQGymsUuYWHtyQQ&export=download",
        "keypagos" : r"https://drive.usercontent.google.com/u/0/uc?id=17CSMaLPPY1pOa7_ZykXzvQfhRbPNbGHh&export=download",
        "Linea_Directa": r"https://drive.usercontent.google.com/u/0/uc?id=1ityd0ukmDHOvbZfExIldjucF56L-oJS5&export=download",
        "Nova_Mexico": r"https://drive.usercontent.google.com/u/0/uc?id=17Mv66TRBPDOHqAAh170PjlRenJaDASd6&export=download",
        "Nova Colombia": r"https://drive.usercontent.google.com/u/0/uc?id=1sSZN5nMI7XTULgiiHFffpr72xMmS712A&export=download",
}

# Diccionario de metas
Metas = {
    "Comfama": 100000000,
    "Azzorti": 100000000,
    "Cueros": 40000000,
    "keypagos": 100000000,
    "Linea_Directa": 15000000,
    "Nova_Mexico": 1000000,
    "Nova Colombia": 100000000,
}

# Diccionario de nombres de meses en español
meses_espanol = {
    1.0: "Enero",
    2.0: "Febrero",
    3.0: "Marzo",
    4.0: "Abril",
    5.0: "Mayo",
    6.0: "Junio",
    7.0: "Julio",
    8.0: "Agosto",
    9.0: "Septiembre",
    10.0: "Octubre",
    11.0: "Noviembre",
    12.0: "Diciembre"
}

# Función para formatear los valores del recaudo
def formatear_valor(valor):
    if valor >= 1e9:
        return f"{valor / 1e9:.2f} mil millones"
    elif valor >= 1e6:
        return f"{valor / 1e6:.2f} millones"
    elif valor >= 1e3:
        return f"{valor / 1e3:.2f} mil"
    else:
        return str(valor)

# Filtro para seleccionar la cartera
cartera_seleccionada = st.selectbox('Selecciona la cartera', list(Pagos_Cruzados.keys()))

@st.cache_data
def cargar_datos(url):
    return pd.read_parquet(url)

if cartera_seleccionada:
    url = Pagos_Cruzados[cartera_seleccionada]
    try:
        df = cargar_datos(url)

        # Filtrar los datos por Cartera_x
        df_filtrado = df[df['Cartera_Pagos'] == cartera_seleccionada]
        
        # Crear columna acumulada de pagos por día en cada mes
        df_filtrado['Acumulado_Pagos'] = df_filtrado.groupby(['Mes_Creacion'])['Pagos'].cumsum()

        # Filtro para seleccionar los meses a comparar
        meses = df_filtrado['Mes_Creacion'].unique()
        meses_nombres = [meses_espanol[mes] for mes in meses]
        
        seleccion_meses = []
        cols = st.columns(6)
        for i, mes in enumerate(meses_nombres):
            if cols[i % 6].button(mes):
                if mes in seleccion_meses:
                    seleccion_meses.remove(mes)
                else:
                    seleccion_meses.append(mes)
        
        meses_seleccionados_num = [key for key, value in meses_espanol.items() if value in seleccion_meses]

        if len(meses_seleccionados_num) > 0:
            # Crear la gráfica de comparación de acumulado de pagos
            fig = go.Figure()
            
            # Agregar líneas para los meses seleccionados
            for mes in meses_seleccionados_num:
                df_mes = df_filtrado[df_filtrado['Mes_Creacion'] == mes]
                fig.add_trace(go.Scatter(x=df_mes['Dia'], y=df_mes['Acumulado_Pagos'], mode='lines+markers', name=f'Acumulado {meses_espanol[mes]}'))
                # Mostrar la última etiqueta de cada línea
                fig.add_annotation(x=df_mes['Dia'].iloc[-1], y=df_mes['Acumulado_Pagos'].iloc[-1],
                                text=formatear_valor(df_mes['Acumulado_Pagos'].iloc[-1]), showarrow=True, arrowhead=2)
            
            # Añadir línea discontinua para la meta acumulada diaria hasta 30 días
            meta = Metas[cartera_seleccionada]
            dias = np.arange(1, 31)
            meta_diaria = meta / 30  # Meta diaria
            meta_acumulada = np.cumsum([meta_diaria] * 30)  # Acumulado de meta diaria
            
            fig.add_trace(go.Scatter(x=dias, y=meta_acumulada, mode='lines', name='Meta', line=dict(dash='dash', color='red')))
            
            # Añadir título y etiquetas
            fig.update_layout(
                title=f'Comparación de Acumulado de Pagos para los Meses Seleccionados',
                xaxis_title='Día',
                yaxis_title='Acumulado de Pagos',
                hovermode='x unified'
            )
            
            # Mostrar la gráfica en Streamlit
            st.plotly_chart(fig)
        
        # Crear la segunda gráfica con el valor máximo del acumulado por mes
        df_max_acumulado = df_filtrado.groupby('Mes_Creacion')['Acumulado_Pagos'].max().reset_index()
        df_max_acumulado['Mes'] = df_max_acumulado['Mes_Creacion'].map(meses_espanol)
        
        colores = df_max_acumulado['Acumulado_Pagos'].apply(lambda x: 'red' if x == df_max_acumulado['Acumulado_Pagos'].min() else ('green' if x == df_max_acumulado['Acumulado_Pagos'].max() else 'yellow'))
        
        fig2 = go.Figure(data=[go.Bar(
            x=df_max_acumulado['Mes'], 
            y=df_max_acumulado['Acumulado_Pagos'],
            text=[formatear_valor(val) for val in df_max_acumulado['Acumulado_Pagos']],
            marker_color=colores,
            textposition='outside'
        )])
        
        fig2.update_layout(
            title='Valor Máximo del Acumulado de Pagos por Mes',
            xaxis_title='Mes',
            yaxis_title='Acumulado de Pagos'
        )
        
        # Mostrar la segunda gráfica en Streamlit
        st.plotly_chart(fig2)

    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
