import streamlit as st
from config import connect_to_db
import pandas as pd
import pyodbc
import hashlib
from datetime import datetime

# Configurações de layout
st.set_page_config(layout="wide")


# Função para hashear a senha com sal
def hash_senha(senha, salt="sEcUrE"):
    return hashlib.sha256((senha + salt).encode()).hexdigest()


# Política de senha: checar força da senha
def validar_forca_senha(senha):
    if len(senha) < 8:
        return "A senha deve ter pelo menos 8 caracteres."
    if not any(char.isdigit() for char in senha):
        return "A senha deve conter pelo menos um número."
    if not any(char.isupper() for char in senha):
        return "A senha deve conter pelo menos uma letra maiúscula."
    if not any(char.islower() for char in senha):
        return "A senha deve conter pelo menos uma letra minúscula."
    if not any(char in '!@#$%^&*()_+=' for char in senha):
        return "A senha deve conter pelo menos um símbolo especial (!@#$%^&*()_+=)."
    return None


# Função para validar credenciais de login
def validar_login(email, senha):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT Senha_hash FROM Usuarios WHERE Email = ? AND Senha_hash = ?"
    cursor.execute(query, (email, senha))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if usuario:
        senha_hash_armazenada = usuario[0]
        if senha_hash_armazenada == hash_senha(senha):
            # Atualiza o último login
            conn = connect_to_db()
            cursor = conn.cursor()
            update_query = "UPDATE Usuarios SET Data_ultimo_login = ? WHERE Email = ?"
            cursor.execute(update_query, (datetime.now(), email))
            conn.commit()
            cursor.close()
            conn.close()
            return True
    return False


# Função para iniciar sessão do usuário
def iniciar_sessao(email, ):
    st.session_state['usuario'] = email


# Função para verificar se o usuário está logado
def verificar_sessao():
    return 'usuario' in st.session_state


# Função para encerrar a sessão do usuário
def encerrar_sessao():
    if 'usuario' in st.session_state:
        del st.session_state['usuario']


# Função de login
def login():
    st.header("Login")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if validar_login(email, senha):
            st.success("Login realizado com sucesso!")
            iniciar_sessao(email)
            st.experimental_rerun()  # Recarrega a página após o login
        else:
            st.error("Credenciais inválidas. Tente novamente.")


# Função para adicionar usuário com política de senha
def adicionar_usuario():
    st.header("Adicionar Novo Usuário")
    nome_usuario = st.text_input("Nome")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    confirm_senha = st.text_input("Confirme a senha", type="password")
    papel = st.selectbox("Papel", ["Admin", "Usuario"])

    if st.button("Salvar"):
        # Validação de senha
        erro_senha = validar_forca_senha(senha)
        if erro_senha:
            st.error(erro_senha)
            return

        if senha != confirm_senha:
            st.error("As senhas não coincidem!")
            return

        conn = connect_to_db()
        cursor = conn.cursor()
        senha_hash = hash_senha(senha)
        query = "INSERT INTO Usuarios (Nome_usuario, Email, Senha_hash, Papel, Data_criacao) VALUES (?, ?, ?, ?, ?)"
        try:
            cursor.execute(query, (nome_usuario, email, senha_hash, papel, datetime.now()))
            conn.commit()
            st.success("Usuário adicionado com sucesso!")
        except pyodbc.Error as e:
            st.error(f"Erro ao adicionar usuário: {str(e)}")
        finally:
            cursor.close()
            conn.close()


# Função para editar um usuário existente
def editar_usuario():
    st.header("Editar Usuário")

    # Listar usuários existentes
    conn = connect_to_db()
    try:
        df_usuarios = pd.read_sql("SELECT Nome_usuario FROM Usuarios", conn)
        usuarios = df_usuarios["Nome_usuario"].tolist()
    except pyodbc.Error as e:
        st.error(f"Erro ao obter lista de usuários: {str(e)}")
    finally:
        conn.close()

    usuario_selecionado = st.selectbox("Selecione um usuário para editar", usuarios)

    if usuario_selecionado:
        conn = connect_to_db()
        try:
            query = "SELECT Email, Papel FROM Usuarios WHERE Nome_usuario = ?"
            usuario_info = pd.read_sql(query, conn, params=[usuario_selecionado])
            email_atual = usuario_info.at[0, "Email"]
            papel_atual = usuario_info.at[0, "Papel"]
        except pyodbc.Error as e:
            st.error(f"Erro ao obter informações do usuário: {str(e)}")
        finally:
            conn.close()

        # Formulário para editar usuário
        email = st.text_input("E-mail", value=email_atual)
        senha = st.text_input("Senha", type="password")
        papel = st.selectbox("Papel", ["Admin", "Usuario"], index=["Admin", "Usuario"].index(papel_atual))

        if st.button("Salvar"):
            conn = connect_to_db()
            cursor = conn.cursor()
            senha_hash = hash_senha(senha)
            query = "UPDATE Usuarios SET Email = ?, Senha_hash = ?, Papel = ? WHERE Nome_usuario = ?"
            try:
                cursor.execute(query, (email, senha_hash, papel, usuario_selecionado))
                conn.commit()
                st.success("Usuário atualizado com sucesso")
            except pyodbc.Error as e:
                st.error(f"Erro ao atualizar usuário: {str(e)}")
            finally:
                cursor.close()
                conn.close()


# Função para listar usuários
def listar_usuarios():
    conn = connect_to_db()
    query = "SELECT Nome_usuario, Email, Papel, Data_criacao, Data_ultimo_login FROM Usuarios"
    try:
        df = pd.read_sql(query, conn)
        st.dataframe(df)
    except pyodbc.Error as e:
        st.error(f"Erro ao listar usuários: {str(e)}")
    finally:
        conn.close()


# Função para renderizar o conteúdo conforme a navegação do usuário
def render_conteudo(opcao):
    if opcao == "Atas":
        st.title("Atas")
        st.write("Conteúdo da tela Atas.")
    elif opcao == "clientes":
        st.title("Clientes")
        st.write("Conteúdo da tela Clientes.")
    elif opcao == "gerenciamento":
        st.title("Gerenciamento de Planos de Ação")
        st.write("Conteúdo da tela Gerenciamento.")
    elif opcao == "Kanban Cliente":
        st.title("Kanban Cliente")
        st.write("Conteúdo da tela Kanban Cliente.")
    elif opcao == "Kanban Status":
        st.title("Kanban Status")
        st.write("Conteúdo da tela Kanban Status.")
    elif opcao == "Planos de Ação":
        st.title("Cadastro de Planos de Ação")
        st.write("Conteúdo da tela Planos de Ação.")
    elif opcao == "Pontos Críticos":
        st.title("Pontos Críticos")
        st.write("Conteúdo da tela Pontos Críticos.")
    elif opcao == "Usuários":
        st.title("Usuários")
        listar_usuarios()
    elif opcao == "Home":
        st.title("Home")


# Função principal
def main():
    if not verificar_sessao():
        # Redireciona para a página de login se não estiver logado
        login()
    else:
        st.sidebar.success(f"Bem-vindo, {st.session_state['usuario']}")
        if st.sidebar.button("Sair"):
            encerrar_sessao()
            st.sidebar.info("Sessão encerrada.")
            st.experimental_rerun()

        opcao = st.sidebar.radio("Escolha uma tela",
                                 ["Atas", "Clientes", "Gerenciamento", "Kanban Cliente", "Kanban Status",
                                  "Planos de Ação", "Pontos Críticos", "Usuários"])
        render_conteudo(opcao)


if __name__ == "__main__":
    main()

