import streamlit as st
import pandas as pd
from Config import connect_to_db
import datetime
from sqlalchemy import text

st.set_page_config(layout="wide")


# Função para carregar os planos de ação do banco de dados
def load_planos_por_cliente():
    conn = connect_to_db()
    query = """
    SELECT pa.Id_plano_acao, pa.Cliente, pa.Progresso, pa.Atribuido_a, pa.Data_inicio, pa.Data_fim, pa.status
    FROM Plano_de_Acao pa
    """
    df = pd.read_sql(query, conn)
    return df


# Função para atualizar o status de um plano de ação
def atualizar_status_plano(id_plano, novo_status):
    conn = connect_to_db()

    # Progresso ajustado de acordo com o novo status
    progresso = 50 if novo_status == "aberto" else 100

    query = text("""
    UPDATE Plano_de_Acao
    SET Status = :novo_status, Progresso = :progresso, 
        Data_fim = CASE WHEN :novo_status = 'fechado' THEN GETDATE() ELSE NULL END
    WHERE Id_plano_acao = :id_plano
    """)

    conn.execute(query, {"novo_status": novo_status, "progresso": progresso, "id_plano": id_plano})
    conn.commit()


# Função para criar cartões de plano de ação
def criar_cartao(plano, col):
    # Converter Data de Início e Data de Fim para o formato pt-BR
    data_inicio = plano['Data_inicio'].strftime('%d/%m/%Y %H:%M:%S') if pd.notnull(plano['Data_inicio']) else '---'
    data_fim = plano['Data_fim'].strftime('%d/%m/%Y %H:%M:%S') if pd.notnull(plano['Data_fim']) and plano[
        'status'] == 'fechado' else '---'

    with col:
        st.markdown(f"""
            **Cliente**: {plano['Cliente']}  
            **Atribuído a**: {plano['Atribuido_a']}  
            **Data de Início**: {data_inicio}  
            **Data de Fim**: {data_fim}  
            **Status**: {plano['status']}  
            **Progresso**: {plano['Progresso']}%  
        """)
        novo_status = st.selectbox(
            f"Atualizar status do plano {plano['Id_plano_acao']}",
            ["aberto", "fechado"],
            index=["aberto", "fechado"].index(plano['status'].lower())
        )
        if st.button(f"Mover Plano {plano['Id_plano_acao']}"):
            atualizar_status_plano(plano['Id_plano_acao'], novo_status)
            st.rerun()


def main():
    st.markdown("<center><h1>Kanban de Planos de Ação por Status</h1></center>", unsafe_allow_html=True)

    # Carregar os planos de ação
    planos = load_planos_por_cliente()

    # Filtro opcional por status
    status = st.selectbox("Filtrar por Status", ["Todos", "aberto", "fechado"])

    if status != "Todos":
        planos = planos[planos["status"] == status]

    # Dividir a tela em três colunas para o Kanban
    col1, col2, col3 = st.columns(3)

    # Agrupar os planos de ação por status, usando o status real do banco de dados
    abertos = planos[planos["status"] == "aberto"]
    fechados = planos[planos["status"] == "fechado"]

    # Exibir os planos em suas respectivas colunas
    with col1:
        st.header("Abertos")
        for idx, plano in abertos.iterrows():
            criar_cartao(plano, col1)

    with col3:
        st.header("Fechados")
        for idx, plano in fechados.iterrows():
            criar_cartao(plano, col3)


if __name__ == "__main__":
    main()
