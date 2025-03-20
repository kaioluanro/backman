import streamlit as st
import pandas as pd

st.subheader("🖋️Editar o banco de Dados")

edited_df = st.data_editor(pd.read_csv('dados_formulario.csv'), num_rows="dynamic")

if st.button("Salvar"):
    edited_df.to_csv('dados_formulario.csv', index=False)
    st.success("Dados salvos com sucesso!")