import streamlit as st
import plotly.express as px
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Aeroportos",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    if airport == "Todos":
        df_heatmap = pd.merge(df, codes, left_on='dest', right_on='iata')
        df_heatmap = df_heatmap["state"].value_counts()
        df_heatmap = df_heatmap.to_frame('count').reset_index()
    else:
        df_heatmap = pd.merge(df, codes, left_on='dest', right_on='iata')
        df_heatmap = df_heatmap[df_heatmap["origin"] == airport]["state"].value_counts()
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
    airports = df["origin"].unique()

    airport = st.sidebar.selectbox("Aeroporto", ["Todos"] + list(airports))
    if airport != "Todos":
        df_airport = df[df["origin"] == airport]
    else:
        df_airport = df

st.session_state["airport"] = airport

st.write("# Aeroporto: ", airport)

cols = st.columns((1.5, 4.5, 2), gap='medium')

with cols[0]:
    st.markdown("#### Número de voos por mês")

    df_flights = df_airport["month"].value_counts()
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

    df_flights = df_airport.groupby("month")["dep_delay"].mean()
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

    df_flights = df_airport.groupby("month")["arr_delay"].mean()
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

    choropleth = make_choropleth(df_airport)
    st.plotly_chart(choropleth, use_container_width=True)

    st.markdown("#### Horas em que mais saem voos")

    df_hours_flights = df_airport.groupby("hour")["id"].count()
    df_hours_flights = df_hours_flights.reset_index()
    df_hours_flights = df_hours_flights.rename(columns={"hour": "Hora", "id": "Quantidade de voos"})
    st.line_chart(df_hours_flights, x = 'Hora', y = 'Quantidade de voos')

    st.markdown("#### Top 10 maiores destinos")

    df_10_dest = df_airport.groupby("dest")["flight"].count().sort_values(ascending=False).head(10)
    df_10_dest = df_10_dest.reset_index()
    df_10_dest = df_10_dest.rename(columns={"dest": "Destino", "flight": "Quantidade de voos"})
    st.altair_chart(
        alt.Chart(df_10_dest).mark_bar().encode(x=alt.X('Destino', sort=None), y='Quantidade de voos'),
        use_container_width=True,
    )

    st.markdown("#### Top 10 maiores companias")

    df_10_airlines = df_airport.groupby("name")["flight"].count().sort_values(ascending=False).head(10)
    df_10_airlines = df_10_airlines.reset_index()
    df_10_airlines = df_10_airlines.rename(columns={"name": "Compania", "flight": "Quantidade de voos"})
    st.altair_chart(
        alt.Chart(df_10_airlines).mark_bar().encode(x=alt.X('Compania', sort=None), y='Quantidade de voos'),
        use_container_width=True,
    )

with cols[2]:
    st.markdown("#### Métricas")

    st.metric("Total de voos", df_airport.shape[0], f'{(df_airport.shape[0]/df.shape[0])*100:.2f}%')

    st.metric("Média de atraso na decolagem", f'{df_airport["dep_delay"].mean():.2f} minutos')

    st.metric("Média de atraso na chegada", f'{df_airport["arr_delay"].mean():.2f} minutos')

    st.metric("Distância percorrida", f'{format_number(df_airport["distance"].sum())} km')

    st.metric("Horas voando", f'{format_number_air(df_airport["air_time"].sum())} horas')

    st.metric("Companias voando", f'{df_airport["carrier"].unique().shape[0]} companias', f'{(df_airport["carrier"].unique().shape[0]/df["carrier"].unique().shape[0])*100:.2f}%')

    st.metric("Aviões distintos voando", f'{df_airport["tailnum"].unique().shape[0]} aviões', f'{(df_airport["tailnum"].unique().shape[0]/df["tailnum"].unique().shape[0])*100:.2f}%')

    st.metric("Destinos distintos", f'{df_airport["dest"].unique().shape[0]} destinos', f'{(df_airport["dest"].unique().shape[0]/df["dest"].unique().shape[0])*100:.2f}%')

    st.metric("Dia mais cheio", f'{df_airport["day"].value_counts(ascending=False).reset_index()["day"][0]}')

    st.metric("Mês mais cheio", f'{df_airport["month"].value_counts(ascending=False).reset_index()["month"][0]}')
    