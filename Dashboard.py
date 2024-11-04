import streamlit as st
import pandas as pd
import plotly.express as px
from config import connect_to_db

st.set_page_config(layout="wide")


def dashboard_gerencial():
    conn = connect_to_db()
    query = "SELECT * FROM Plano_de_Acao"
    df = pd.read_sql(query, conn)

    # Filtro de cliente
    clientes = df['Cliente'].unique()
    cliente_selecionado = st.selectbox("Selecione um Cliente", ["Todos"] + list(clientes))

    if cliente_selecionado != "Todos":
        df = df[df['Cliente'] == cliente_selecionado]

    # Filtro de SLA
    df['SLA'] = pd.to_numeric(df['SLA'], errors='coerce')  # Converte para numérico, se necessário
    sla_min, sla_max = int(df['SLA'].min()), int(df['SLA'].max())

    # Garantir que o valor mínimo seja menor que o máximo
    if sla_min == sla_max:
        sla_max += 1  # Ajustar o máximo se mínimo e máximo forem iguais

    sla_min, sla_max = st.slider("Selecione o intervalo de SLA", sla_min, sla_max, (sla_min, sla_max))
    df_filtrado = df[(df['SLA'] >= sla_min) & (df['SLA'] <= sla_max)]

    # Exibir o intervalo de SLA selecionado
    st.write(f"Dados filtrados para SLA entre {sla_min} e {sla_max}")

    # Seleção de opções para os gráficos
    st.write("## Configurações do Dashboard")
    chart_type = st.selectbox("Escolha o tipo de gráfico",
                              ["Gráfico de Pizza", "Gráfico de Barras", "Gráfico Horizontal", "Box Plot", "Histograma",
                               "Gráfico de Dispersão"])

    # Exibindo gráfico baseado na seleção
    st.write("## Desempenho de Planos de Ação")

    if chart_type == "Gráfico de Pizza":
        fig = px.pie(df_filtrado, names='status', title="Distribuição por Status")
        st.plotly_chart(fig)

    elif chart_type == "Gráfico de Barras":
        fig_cliente = px.bar(df_filtrado.groupby('Cliente').count().reset_index(), x='Cliente', y='Id_plano_acao',
                             title="Distribuição por Clientes")
        st.plotly_chart(fig_cliente, use_container_width=True)

    elif chart_type == "Gráfico Horizontal":
        fig_bar_horizontal = px.bar(
            df_filtrado.groupby('Area_responsavel')['SLA'].sum().reset_index(),
            x='SLA', y='Area_responsavel',
            orientation='h', title="Progresso por Área Responsável"
        )
        st.plotly_chart(fig_bar_horizontal, use_container_width=True)

    elif chart_type == "Box Plot":
        fig_box = px.box(df_filtrado, x='Cliente', y='SLA', title="Box Plot de SLA por Cliente")
        st.plotly_chart(fig_box)

    elif chart_type == "Histograma":
        fig_hist = px.histogram(df_filtrado, x='SLA', title="Distribuição de SLA")
        st.plotly_chart(fig_hist)

    elif chart_type == "Gráfico de Dispersão":
        fig_scatter = px.scatter(df_filtrado, x='Data_inicio', y='SLA', color='Cliente',
                                 title="Progresso vs Data de Início")
        st.plotly_chart(fig_scatter)


def main():
    st.markdown("<h1 style='text-align: center'>Dashboards Interativos</h1>", unsafe_allow_html=True)
    dashboard_gerencial()


if __name__ == "__main__":
    main()