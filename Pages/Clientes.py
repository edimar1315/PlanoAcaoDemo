import streamlit as st
import pandas as pd
from config import connect_to_db
from sqlalchemy import text

from Pages.Gerenciamento import index

st.set_page_config(layout="wide")


def load_clientes():
    conn = connect_to_db()
    query = "SELECT * FROM Clientes"
    return pd.read_sql(query, conn, index_col="Id_cliente", )


def add_cliente(nome, filial, endereco, status):
    conn = connect_to_db()

    def create_insert_query():
        return text("""
        INSERT INTO Clientes (Nome_do_cliente, Filial, Endereco, Status)
        VALUES (:nome, :filial, :endereco, :status)
        """)

    INSERT_QUERY = create_insert_query()
    conn.execute(INSERT_QUERY, {
        "nome": nome,
        "filial": filial,
        "endereco": endereco,
        "status": status
    })
    conn.commit()
    # limpar campos após insert
    st.empty()
    st.write("")
    conn.close()


def main():
    st.markdown("<h1 style='text-align: center'>Cadastrar Novo Cliente</h1>", unsafe_allow_html=True)
    nome = st.text_input("Nome do Cliente")
    filial = st.text_input("Filial")
    endereco = st.text_input("Endereço")
    status = st.selectbox("Status", ["Ativo", "Inativo"])

    if st.button("Cadastrar"):
        add_cliente(nome, filial, endereco, status)
        st.success("Cliente cadastrado com sucesso!")
        st.rerun()

        st.title("Gerenciamento de Clientes")

    clientes = load_clientes()

    st.dataframe(clientes, use_container_width=True)


if __name__ == "__main__":
    main()
