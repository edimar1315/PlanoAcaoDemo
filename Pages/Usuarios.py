import streamlit as st
from config import connect_to_db, connection_string
import pandas as pd
import pyodbc

st.set_page_config(layout="wide")


def validar_campos(nome_usuario, email, senha_hash):
    if not nome_usuario or not email or not senha_hash:
        st.error("Todos os campos são obrigatórios")
        return False
    return True


def executar_query(query, params=()):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
    except pyodbc.Error as e:
        st.error(f"Erro ao executar a query: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def adicionar_usuario():
    st.header("Adicionar Novo Usuário")
    nome_usuario = st.text_input("Nome")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    papel = st.selectbox("Papel", ["Admin", "Usuario"])
    if st.button("Salvar"):
        if validar_campos(nome_usuario, email, senha):
            query = "INSERT INTO Usuarios (Nome_usuario, Email, Senha_hash, Papel) VALUES (?, ?, HASHBYTES('SHA2_256', ?), ?)"
            executar_query(query, (nome_usuario, email, senha, papel))
            st.success("Usuário adicionado com sucesso")


def fetch_user_list():
    conn = connect_to_db()
    try:
        df_users = pd.read_sql("SELECT Nome_usuario FROM Usuarios", conn)
        return df_users["Nome_usuario"].tolist()
    except pyodbc.Error as e:
        st.error(f"Erro ao obter lista de usuários: {str(e)}")
        return []
    finally:
        conn.close()


def fetch_user_info(usuario_selecionado):
    conn = connect_to_db()
    try:
        query = "SELECT Email, Papel FROM Usuarios WHERE Nome_usuario = ?"
        usuario_info = pd.read_sql(query, conn, params=[usuario_selecionado])
        return usuario_info
    except pyodbc.Error as e:
        st.error(f"Erro ao obter informações do usuário: {str(e)}")
        return None
    finally:
        conn.close()


def editar_usuario():
    st.header("Editar Usuário")
    # Listar usuários existentes
    user_list = fetch_user_list()
    if user_list:
        usuario_selecionado = st.selectbox("Selecione um Usuário", user_list)

        if usuario_selecionado:
            usuario_info = fetch_user_info(usuario_selecionado)
            if usuario_info is not None:
                email_atual = usuario_info.at[0, "Email"]
                papel_atual = usuario_info.at[0, "Papel"]

                # Formulário para editar usuário
                email = st.text_input("E-mail", value=email_atual)
                senha = st.text_input("Senha", type="password")
                papel = st.selectbox("Papel", ["Admin", "Usuario"], index=["Admin", "Usuario"].index(papel_atual))

                if st.button("Salvar"):
                    if validar_campos(usuario_selecionado, email, senha):
                        query = "UPDATE Usuarios SET Email = ?, Senha_hash = HASHBYTES('SHA2_256', ?), Papel = ? WHERE Nome_usuario = ?"
                        executar_query(query, (email, senha, papel, usuario_selecionado))
                        st.success("Usuário atualizado com sucesso")


def listar_usuarios():
    conn = connect_to_db()
    query = "SELECT Nome_usuario, Email, Papel FROM Usuarios"
    try:
        df = pd.read_sql(query, conn)
        st.dataframe(df, use_container_width=True)
    except pyodbc.Error as e:
        st.error(f"Erro ao listar usuários: {str(e)}")
    finally:
        conn.close()


def connect_to_db():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        return None


def main():
    # Título da aplicação
    st.markdown("<h1 style='text-align: center'>Relação de Usuários</h1>", unsafe_allow_html=True)

    opcao = st.sidebar.radio("Gerenciamento de Usuários", ["Listar Usuários", "Adicionar Usuário", "Editar Usuário"])

    if opcao == "Listar Usuários":
        listar_usuarios()
    elif opcao == "Adicionar Usuário":
        adicionar_usuario()
    elif opcao == "Editar Usuário":
        editar_usuario()


if __name__ == "__main__":
    main()
