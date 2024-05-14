import streamlit as st
import pandas as pd
import webbrowser

st.set_page_config(
    page_title="NYC Flights 2013",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

df = pd.read_excel("dashboard.xlsx", "flights")

if "data" not in st.session_state:
    st.session_state["data"] = df

st.write("# NYC Flights 2013 ✈")

st.sidebar.write("Desenvolvido por: **Guilherme Lunetta**")

databutton = st.button("Acesse os dados no Kaggle")
if databutton:
    webbrowser.open_new_tab("https://www.kaggle.com/datasets/mahoora00135/flights")

st.markdown('''
O conjunto de dados **"nycflights13"** contém informações sobre os voos de um aeroporto. Esse conjunto de dados inclui informações como hora de partida e chegada, atrasos, companhia aérea, número do voo, origem e destino do voo, duração do voo, distância, hora e minuto do voo e data e hora exatas do voo.

Esses dados podem ser usados em análises e estratégias de gestão e fornecer informações úteis sobre o desempenho dos voos e o posicionamento das companhias aéreas. A análise dos dados deste conjunto de dados pode ser usada como base para as seguintes atividades:

* Análise de padrões e tendências de tempo: examinando a hora de partida e chegada da aeronave, mudanças e alterações de tempo, padrões e tendências no comportamento do voo podem ser identificados.

* Análise de empresas americanas: Ao visualizar informações sobre companhias aéreas, como número de voos, impacto e desempenho geral, você pode comparar e analisar o desempenho de cada empresa.

* Análise de atrasos e qualidade do serviço: Ao examinar atrasos e horários de chegada, posso coletar e analisar informações sobre a qualidade dos serviços prestados pelo aeroporto e companhias aéreas.

* Análise de rotas de voo: verificando a origem e o destino dos voos, distâncias e duração do voo, rotas populares e escolhas das pessoas podem ser identificadas e analisadas.

* Análise do desempenho do aeroporto: observando as características dos voos e o desempenho do aeroporto, é possível identificar e analisar os pontos fortes e fracos do aeroporto e sugerir melhorias.

Ele fornece várias ferramentas para análise e visualização de dados e pode ser usado como base para decisões gerenciais no setor da aviação.

''')

st.markdown('### Prévia dos dados')

st.dataframe(df.head(15))