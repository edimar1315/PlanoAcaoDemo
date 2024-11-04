import streamlit as st
import pandas as pd
from Config import connect_to_db
from sqlalchemy import text

st.set_page_config(layout="wide")


# Conexão com o banco de dados
@st.cache_data(show_spinner=True)
def load_planos_acao():
    try:
        conn = connect_to_db()
        query = "SELECT * FROM Plano_de_Acao"
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None
    finally:
        conn.close()


# Função para formatar as datas e lidar com valores nulos
def formatar_data(data):
    if pd.isnull(data):  # Verifica se o valor é nulo
        return None
    try:
        return pd.to_datetime(data, errors='coerce')  # Tenta converter a data
    except Exception as e:
        st.error(f"Erro ao converter data: {data}. {e}")
        return None


# Função para formatar a data em pt-BR
def formatar_data_pt_br(data):
    if pd.isnull(data):
        return '---'
    return data.strftime('%d/%m/%Y %H:%M:%S')


# Título da aplicação
st.markdown("<center><h1>Gerenciamento de Planos de Ação</h1></center>", unsafe_allow_html=True)

# Carregando os dados com barra de progresso
with st.spinner('Carregando dados...'):
    df = load_planos_acao()

# Verificar se os dados foram carregados corretamente
if df is None:
    st.error("Erro ao carregar dados. Verifique se a conexão com o banco está funcionando.")
else:
    # Formatar as datas para exibição
    df['Data_inicio'] = df['Data_inicio'].apply(formatar_data)
    df['Data_fim'] = df['Data_fim'].apply(formatar_data)

    # Seleção de clientes
    clientes = df["Cliente"].unique()
    clientes_selecionados = st.multiselect("Selecione os Clientes", clientes)

    # Filtrar os planos
    df_filtrado = df[df["Cliente"].isin(clientes_selecionados)] if clientes_selecionados else df

    # Tabela editável
    df_editavel = st.data_editor(df_filtrado.copy().head(1000), use_container_width=True)

    # Atualizar os dados na tabela
    if df_editavel is not None and not df_editavel.empty:
        try:
            conn = connect_to_db()
            for index, row in df_editavel.iterrows():
                # Formatar as datas para envio ao banco de dados
                data_inicio = formatar_data(row['Data_inicio'])  # Formatando data de início
                data_fim = formatar_data(row['Data_fim'])  # Formatando data de fim

                # Verifica se as datas formatadas são válidas
                if data_inicio is None or (data_fim is None and row['Progresso'] == 'fechado'):
                    st.error("As datas de início e fim não podem estar vazias.")
                    continue

                # Garantir que os parâmetros sejam uma tupla
                params = {
                    'Cliente': str(row['Cliente']),
                    'O_que_acao': str(row['O_que_acao']),
                    'Area_responsavel': str(row['Area_responsavel']),
                    'Atribuido_a': str(row['Atribuido_a']),
                    'Filial': str(row['Filial']),
                    'Palavra_chave': str(row['Palavra_chave']),
                    'Progresso': str(row['Progresso']),
                    'Data_inicio': data_inicio,
                    'Data_fim': data_fim,
                    'SLA': row['SLA'],
                    'Departamento_solicitante': str(row['Departamento_solicitante']),
                    'Id_plano_acao': row['Id_plano_acao']
                }

                # Executa a atualização usando o método execute diretamente na conexão
            query = text(
                "UPDATE Plano_de_Acao SET Cliente = :Cliente, O_que_acao = :O_que_acao, Area_responsavel = :Area_responsavel, Atribuido_a = :Atribuido_a, Filial = :Filial, Palavra_chave = :Palavra_chave, Progresso = :Progresso, Data_inicio = :Data_inicio, Data_fim = :Data_fim, SLA = :SLA, Departamento_solicitante = :Departamento_solicitante WHERE Id_plano_acao = :Id_plano_acao")
            conn.execute(query, params)
            conn.commit()
            # st.success("Dados atualizados com sucesso!")
            st.empty()
            st.write("")


        except Exception as e:
            st.error(f"Erro ao atualizar dados: {e}")  # Mensagem de erro ao atualizar
            print(f"Erro detalhado: {e}")  # Log detalhado para depuração
        finally:
            if conn:
                conn.close()

    # Estilização
    st.markdown("""
        <style>
            .stApp { font-family: 'sans-serif'; }
            .stButton { background-color: #4CAF50; color: white; padding: 15px 32px; font-size: 16px; }
            .stdataframe { font-family: 'sans-serif'; }
        </style>
    """, unsafe_allow_html=True)