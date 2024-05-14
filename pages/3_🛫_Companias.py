import streamlit as st
import plotly.express as px
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Companias",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded"
)

if st.session_state.get("airport") != None and st.session_state.get("airport") != "Todos":
    airport = st.session_state.get("airport")
    df = st.session_state["data"]
    df = df[df["origin"] == st.session_state["airport"]]
else:
    airport = None
    df = st.session_state["data"]

def format_number(num):
    num = num/1.6
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

def format_number_air(num):
    num = num/60
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

def make_choropleth(df):
    codes = pd.read_csv("usa-airports.csv")
    codes = codes.drop(["name", "city", "country", "latitude", "longitude"], axis=1)

    if airline == "Todas":
        df_heatmap = pd.merge(df, codes, left_on='dest', right_on='iata')
        df_heatmap = df_heatmap["state"].value_counts()
        df_heatmap = df_heatmap.to_frame('count').reset_index()
    else:
        df_heatmap = pd.merge(df, codes, left_on='dest', right_on='iata')
        df_heatmap = df_heatmap[df_heatmap["name"] == airline]["state"].value_counts()
        df_heatmap = df_heatmap.to_frame('count').reset_index()

    choropleth = px.choropleth(df_heatmap, 
        locations='state', 
        color='count', 
        locationmode="USA-states",
        scope="usa",
        labels={'count':'Voos'}
    )

    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(255, 255, 255, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )

    return choropleth

with st.sidebar:
    st.selectbox("Aeroporto", [airport if airport != None else "Todos"], disabled=True)

    airlines = df["name"].unique()

    airline = st.sidebar.selectbox("Compania aérea", ["Todas"] + list(airlines))
    if airline != "Todas":
        df_airline = df[df["name"] == airline]
    else:
        df_airline = df

st.write("# Compania aérea: ", airline)

cols = st.columns((1.5, 4.5, 2), gap='medium')

with cols[0]:
    st.markdown("#### Número de voos por mês")

    df_flights = df_airline["month"].value_counts()
    df_flights = df_flights.sort_index()
    st.dataframe(
        df_flights,
        height=458,
        column_config={
            "month": "Mês",
            "count": "Voos"
        }    
    )

    st.markdown("#### Média de atraso na decolagem por mês")

    df_flights = df_airline.groupby("month")["dep_delay"].mean()
    df_flights = df_flights.sort_index()
    st.dataframe(
        df_flights,
        height=458,
        width=150,
        column_config={
            "month": "Mês",
            "dep_delay": "Atraso médio"
        }    
    )

    st.markdown("#### Média de atraso na chegada por mês")

    df_flights = df_airline.groupby("month")["arr_delay"].mean()
    df_flights = df_flights.sort_index()
    st.dataframe(
        df_flights,
        height=458,
        width=150,
        column_config={
            "month": "Mês",
            "arr_delay": "Atraso médio"
        }    
    )

with cols[1]:
    st.markdown("#### Heatmap de voos para cada estado")

    choropleth = make_choropleth(df_airline)
    st.plotly_chart(choropleth, use_container_width=True)

    st.markdown("#### Horas em que mais saem voos")

    df_hours_flights = df_airline.groupby("hour")["id"].count()
    df_hours_flights = df_hours_flights.reset_index()
    df_hours_flights = df_hours_flights.rename(columns={"hour": "Hora", "id": "Quantidade de voos"})
    st.line_chart(df_hours_flights, x = 'Hora', y = 'Quantidade de voos')

    st.markdown("#### Top 10 maiores destinos")

    df_10_dest = df_airline.groupby("dest")["flight"].count().sort_values(ascending=False).head(10)
    df_10_dest = df_10_dest.reset_index()
    df_10_dest = df_10_dest.rename(columns={"dest": "Destino", "flight": "Quantidade de voos"})
    st.altair_chart(
        alt.Chart(df_10_dest).mark_bar().encode(x=alt.X('Destino', sort=None), y='Quantidade de voos'),
        use_container_width=True,
    )

    st.markdown("#### Tempo de voo por mês")

    df_airtime = df_airline.groupby("month")["air_time"].sum()
    df_airtime = df_airtime.reset_index()
    df_airtime["air_time"] = df_airtime["air_time"] / 60
    df_airtime = df_airtime.rename(columns={"month": "Mês", "air_time": "Tempo de voo (horas)"})
    st.altair_chart(
        alt.Chart(df_airtime).mark_bar().encode(x=alt.X('Mês:N').scale(zero=False), y='Tempo de voo (horas):Q'),
        use_container_width=True,
    )

    st.markdown("#### Distância percorrida por mês")

    df_distance = df_airline.groupby("month")["distance"].sum()
    df_distance = df_distance.reset_index()
    df_distance["distance"] = df_distance["distance"] / 1.6
    df_distance = df_distance.rename(columns={"month": "Mês", "distance": "Distância (km)"})
    st.altair_chart(
        alt.Chart(df_distance).mark_bar().encode(x=alt.X('Mês:N').scale(zero=False), y='Distância (km):Q'),
        use_container_width=True,
    )

with cols[2]:
    st.markdown("#### Métricas")

    st.metric("Total de voos", df_airline.shape[0], f'{(df_airline.shape[0]/df.shape[0])*100:.2f}%')

    st.metric("Média de atraso na decolagem", f'{df_airline["dep_delay"].mean():.2f} minutos')

    st.metric("Média de atraso na chegada", f'{df_airline["arr_delay"].mean():.2f} minutos')

    st.metric("Distância percorrida", f'{format_number(df_airline["distance"].sum())} km')

    st.metric("Horas voando", f'{format_number_air(df_airline["air_time"].sum())} horas')

    st.metric("Aviões distintos voando", f'{df_airline["tailnum"].unique().shape[0]} aviões', f'{(df_airline["tailnum"].unique().shape[0]/df["tailnum"].unique().shape[0])*100:.2f}%')

    st.metric("Destinos distintos", f'{df_airline["dest"].unique().shape[0]} destinos', f'{(df_airline["dest"].unique().shape[0]/df["dest"].unique().shape[0])*100:.2f}%')

    st.metric("Dia mais cheio", f'{df_airline["day"].value_counts(ascending=False).reset_index()["day"][0]}')

    st.metric("Mês mais cheio", f'{df_airline["month"].value_counts(ascending=False).reset_index()["month"][0]}')