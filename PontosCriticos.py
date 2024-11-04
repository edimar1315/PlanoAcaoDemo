import streamlit as st
import pandas as pd
from Config import connect_to_db

st.set_page_config(layout="wide")


def load_pontos_criticos():
    conn = connect_to_db()
    query = """
    SELECT pc.Id_ponto_critico, pc.Cliente, pc.Motivos, pc.Resolvido, pc.Atrasados, pc.Finalizado, pc.Agendamento_CX, pc.Departamento_solicitante
    FROM Pontos_Criticos pc
    """
    return pd.read_sql(query, conn)


def update_resolvido(ponto_critico_id, resolvido):
    conn = connect_to_db()
    query = f"UPDATE Pontos_Criticos SET Resolvido = '{resolvido}' WHERE Id_ponto_critico = {ponto_critico_id}"
    conn.execute(query)
    conn.commit()


def main():
    # Título da aplicação
    st.markdown("<h1 style='text-align: center'>Gerenciamento de Pontos Críticos</h1>", unsafe_allow_html=True)

    pontos_criticos = load_pontos_criticos()

    st.subheader("Atualizar Resolução de Ponto Crítico")
    ponto_critico_id = st.selectbox("Selecione o Ponto Crítico", pontos_criticos["Id_ponto_critico"])
    resolvido = st.selectbox("Resolvido", ["Sim", "Não"])

    if st.button("Atualizar"):
        update_resolvido(ponto_critico_id, resolvido)
        st.success("Status de resolução atualizado com sucesso!")
        st.experimental_rerun()

    st.dataframe(pontos_criticos, use_container_width=True)


if __name__ == "__main__":
    main()
