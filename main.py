import streamlit as st

# CSS para ajustar a largura do container principal
st.markdown(
    """
    <style>
    .stMainBlockContainer {
        max-width: 180vw; /* Ajuste a largura aqui */
        max-height: 400px;
        margin: 0 auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


pages = {
    "🛍️Recursos": [
        st.Page("backtest.py", title="🕹️Backtest Manual"),
    ],
    "🛠️Configuração": [
        st.Page("editData.py", title="🖋️Editar o banco de Dados"),
        st.Page("genreItems.py", title="♟️Adicionar Items de Backtest"),
    ],
}

pg = st.navigation(pages)
pg.run()