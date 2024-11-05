import streamlit as st
import pandas as pd
from config import connect_to_db
from sqlalchemy import text

st.set_page_config(layout="wide")


def load_atas():
    conn = connect_to_db()
    query = """
    SELECT ar.Id_ata, ar.Nome_cliente, ar.Gerente_de_contas, ar.Data_de_recebimento, ar.Nota, 
           ar.status, pa.O_que_acao
    FROM Atas_Recebidas ar
    LEFT JOIN Plano_de_Acao pa ON ar.Id_plano_acao = pa.Id_plano_acao
    """
    df = pd.read_sql(query, conn, )
    conn.close()
    return df


from sqlalchemy import text


def update_status(ata_id, status):
    conn = connect_to_db()
    try:
        # Usando parâmetros nomeados para evitar erros
        query = text("UPDATE Atas_Recebidas SET status = :status WHERE Id_ata = :ata_id")
        st.write(f"Query: {query}")  # Debug: mostrar a query
        st.write(f"Parameters: status: {status}, Id_ata: {ata_id}")  # Debug: mostrar os parâmetros

        # Executando a query com parâmetros nomeados
        conn.execute(query, {"status": status, "ata_id": ata_id})
        conn.commit()
        st.write(f"Atualização bem-sucedida para Id_ata: {ata_id}")

    except Exception as e:
        st.error(f"Erro ao atualizar o status: {e}")
        st.write(f"Erro: {e}")  # Adicionando mais detalhes do erro no log
    finally:
        conn.close()


def main():
    # Título da aplicação
    st.markdown("<h1 style='text-align: center'>Gerenciamento de Atas Recebidas</h1>", unsafe_allow_html=True)

    atas = load_atas()

    st.subheader("Atualizar Status de Ata")
    ata_id = st.selectbox("Selecione a Ata", atas["Id_ata"])
    status = st.selectbox("Selecione o Status", ["Atrasado", "Em andamento", "Resolvido", "Sem ATA"])

    if st.button("Atualizar"):
        update_status(ata_id, status)
        st.success("Status atualizado com sucesso!")
        st.rerun()

    st.dataframe(atas, use_container_width=True)


if __name__ == "__main__":
    main()


