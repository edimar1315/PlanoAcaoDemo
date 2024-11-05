import streamlit as st

st.set_page_config(layout="wide")


#st.image("image\logo.png")



def main():
    st.title("Sistema de Criação e Gerenciamento de Planos de Ação Empresarial")

    st.write("""
        Bem-vindo ao sistema de gestão de planos de ação empresarial.
        Utilize o menu lateral para navegar pelas funcionalidades disponíveis.
    """)

if __name__ == "__main__":
    main()
