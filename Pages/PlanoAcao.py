import streamlit as st
import pandas as pd
from Config import connect_to_db
from datetime import datetime
from sqlalchemy import text

st.set_page_config(layout="wide")

@st.cache_data
def add_plano_acao(cliente, acao, area, responsavel, filial, palavras, data_inicio, data_de_previsao_de_fechamento, sla, Departamento_solicitante):
    conn = connect_to_db()

    print("Conexão com o banco de dados estabelecida")

    # Verificando se as datas estão vazias
    if data_inicio is None:
        st.error("A data de início não pode estar vazia.")
        return

    # Convertendo as datas para o formato adequado para SQL Server
    try:
        data_inicio = data_inicio.strftime('%Y-%m-%d %H:%M:%S')  # Formato: YYYY-MM-DD HH:MM:SS
        data_de_previsao_de_fechamento = data_de_previsao_de_fechamento.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        st.error(f"Erro ao converter as datas: {e}")
        return

    query = text("""
        INSERT INTO Plano_de_Acao (
            Cliente, O_que_acao, Area_responsavel, Atribuido_a, Filial, Palavra_chave, 
            Progresso, Data_inicio, Data_de_Previsao_de_Fechamento, SLA, Departamento_solicitante, Status
        )
        VALUES (
            :cliente, :acao, :area, :responsavel, :filial, :palavras, 
            50, :data_inicio, :data_de_previsao_de_fechamento, :sla, :Departamento_solicitante, 'Aberto'
        )
    """)

    print("Query gerada:", query)

    try:
        conn.execute(query, {
            "cliente": cliente,
            "acao": acao,
            "area": area,
            "responsavel": responsavel,
            "filial": filial,
            "palavras": palavras,
            "data_inicio": data_inicio,
            "data_de_previsao_de_fechamento": data_de_previsao_de_fechamento,
            "sla": sla,
            "Departamento_solicitante": Departamento_solicitante
        })
        print("Query executada")
        conn.commit()
        print("Commit executado")
        st.success("Plano de ação cadastrado com sucesso!")

        # limpar os campos
        st.empty()
        st.write("")

        # Limpar os campos de entrada e atualizar a página
        st.rerun()

    except Exception as e:
        st.error(f"Erro ao cadastrar plano de ação: {e}")

def main():
    st.markdown("<h1 style='text-align: center'>Cadastro de Plano de Ação</h1>", unsafe_allow_html=True)

    cliente = st.text_input("Cliente")  # campo cliente, obter da tabela clientes
    acao = st.text_input("O que / Ação")
    area = st.text_input("Área Responsável")
    responsavel = st.text_input("Atribuído a")
    filial = st.text_input("Filial")
    palavras = st.text_input("Palavras-chave")

    # Recebendo as datas do usuário
    data_inicio = st.date_input("Data de Início")
    data_de_previsao_de_fechamento = st.date_input("Data de Previsão de Fechamento")

    # Verificar se as datas estão preenchidas
    if data_inicio:
        data_inicio = datetime.combine(data_inicio, datetime.min.time())

    sla = st.number_input("SLA (dias)", min_value=1)
    Departamento_solicitante = st.text_input("Departamento Solicitante")

    if st.button("Cadastrar Plano"):
        add_plano_acao(cliente, acao, area, responsavel, filial, palavras, data_inicio, data_de_previsao_de_fechamento, sla, Departamento_solicitante)

if __name__ == "__main__":
    main()
