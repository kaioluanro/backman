import streamlit as st
import backtest as bt
import pandas as pd

st.subheader("♟️Adicionar Items de Backtest")

gerenciar_lista = st.radio("Selecione o tipo de item para gerenciar:", ["Ativo", "Localização", "Estratégia", "Gatilhos"])
# Adicionar ou Remover Itens
item_input = st.text_input("Digite o item")

if gerenciar_lista == "Ativo":
    if st.button("Adicionar Ativo"):
        ativos_lista = bt.add_remove_item(bt.ativos_lista, "Adicionar", item_input)
        bt.salvar_lista_csv(ativos_lista, bt.ativo_csv_file)
        st.success(f"Ativo adicionado com sucesso! Atualização: {ativos_lista}")
    
    if st.button("Remover Ativo"):
        ativos_lista = bt.add_remove_item(bt.ativos_lista, "Remover", item_input)
        bt.salvar_lista_csv(bt.ativos_lista, bt.ativo_csv_file)
        st.success(f"Ativo removido com sucesso! Atualização: {ativos_lista}")
elif gerenciar_lista == "Localização":
    if st.button("Adicionar Localização"):
        localizacao_lista = bt.add_remove_item(bt.localizacao_lista, "Adicionar", item_input)
        bt.salvar_lista_csv(localizacao_lista, bt.localizacao_csv_file)
        st.success(f"Localização adicionada com sucesso! Atualização: {localizacao_lista}")
    
    if st.button("Remover Localização"):
        localizacao_lista = bt.add_remove_item(bt.localizacao_lista, "Remover", item_input)
        bt.salvar_lista_csv(bt.localizacao_lista, bt.localizacao_csv_file)
        st.success(f"Localização removida com sucesso! Atualização: {localizacao_lista}")
        
elif gerenciar_lista == "Estratégia":
    if st.button("Adicionar Estratégia"):
        estrategias_lista = bt.add_remove_item(bt.estrategias_lista, "Adicionar", item_input)
        bt.salvar_lista_csv(estrategias_lista, bt.estrategia_csv_file)
        st.success(f"Estrategia adicionada com sucesso! Atualização: {estrategias_lista}")
    
    if st.button("Remover Estratégia"):
        estrategias_lista = bt.add_remove_item(bt.estrategias_lista, "Remover", item_input)
        bt.salvar_lista_csv(estrategias_lista, bt.estrategia_csv_file)
        st.success(f"Estrategia removida com sucesso! Atualização: {estrategias_lista}")
elif gerenciar_lista == "Gatilhos":
    if st.button("Adicionar Gatilho"):
        gatilhos_lista = bt.add_remove_item(bt.gatilhos_lista, "Adicionar", item_input)
        bt.salvar_lista_csv(gatilhos_lista, bt.gatilho_csv_file)
        st.success(f"Gatilho adicionado com sucesso! Atualização: {gatilhos_lista}")
    
    if st.button("Remover Gatilho"):
        gatilhos_lista = bt.add_remove_item(bt.gatilhos_lista, "Remover", item_input)
        bt.salvar_lista_csv(gatilhos_lista, bt.gatilho_csv_file)
        st.success(f"Gatilho removido com sucesso! Atualização: {gatilhos_lista}")

st.subheader("Tabela Editação de itens")
col1, col2, col3, col4 = st.columns(4)

with col1:
    edited_df1 = st.data_editor(pd.read_csv(bt.ativo_csv_file), num_rows="dynamic")

with col2:
    edited_df2 = st.data_editor(pd.read_csv(bt.localizacao_csv_file), num_rows="dynamic")

with col3:    
    edited_df3 = st.data_editor(pd.read_csv(bt.estrategia_csv_file), num_rows="dynamic")
    
with col4:
    edited_df4 = st.data_editor(pd.read_csv(bt.gatilho_csv_file), num_rows="dynamic")

if st.button("Salvar alteração das Tabelas!"):
    edited_df1.to_csv(bt.ativo_csv_file, index=False)
    edited_df2.to_csv(bt.localizacao_csv_file, index=False)
    edited_df3.to_csv(bt.estrategia_csv_file, index=False)
    edited_df4.to_csv(bt.gatilho_csv_file, index=False)