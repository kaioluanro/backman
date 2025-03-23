import streamlit as st
import pandas as pd
import os
import time
import statistics
from collections import defaultdict
# ============



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

# Caminho do arquivo CSV para os dados do formulário
dados_csv_file = 'dados_formulario.csv'

# Caminhos dos arquivos CSV para os itens individuais
ativo_csv_file = 'ativos.csv'
localizacao_csv_file = 'localizacao.csv'
estrategia_csv_file = 'estrategia.csv'
gatilho_csv_file = 'gatilho.csv'

# Dicionário para armazenar os dados
dados = {
    "Ativo": [],
    "Timeframe": [],
    "Contexto": [],
    "Horário":[],
    "Dia da Semana":[],
    "Localização": [],
    "Estratégia": [],
    "Gatilhos": [],
    "Alvos": [],
    "Variar": [],
    "Stop": []
}

# Listas de opções
timeframes_lista = ["2m", "5m", "15m", "1h", "4h", "D", "S"]
alvos_lista = ["0.5", "0.61", "1", "1.414", "1.61", "2", "MAIS", "1b", "2c", "3c"]
horarios_lista = [f"{hora:02d}:{minuto:02d}" for hora in range(24) for minuto in (0, 30)]
dias_da_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

# Função para carregar os dados dos arquivos CSV individuais
def carregar_dados_csv():
    ativos_lista = carregar_lista_csv(ativo_csv_file)
    localizacao_lista = carregar_lista_csv(localizacao_csv_file)
    estrategias_lista = carregar_lista_csv(estrategia_csv_file)
    gatilhos_lista = carregar_lista_csv(gatilho_csv_file)
    return ativos_lista, localizacao_lista, estrategias_lista, gatilhos_lista

# Função para carregar uma lista de um CSV
def carregar_lista_csv(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        df = pd.read_csv(caminho_arquivo)
        return df.iloc[:, 0].dropna().tolist()  # Considerando que cada item esteja em uma coluna
    else:
        return []

def calcular_estatisticas_acerto(df, grouped=['Timeframe','Localização', 'Estratégia', 'Gatilho']):
    # Agrupar por Ativo, Estratégia, Localização e Gatilho
    ativos = df['Ativo'].unique()
    
    # Calculo de Estaticas
    estatisticas = {}
    saldoPorGatilho = {}
    for ativo in ativos:
        
        #Projeçao no Chat
               
        sub_df = df[df['Ativo'] == ativo].groupby(grouped)
        stop_count = 0
        saldo_inicial = 100
        saldo_acumulado = saldo_inicial

        for (timeframe, localizacao, estrategia, gatilho), group in sub_df:
            
            acertos = {}
            total_linhas = len(group)
            for alvo in alvos_lista:
                acertos[alvo] = group[alvo].mean() * 100  # Porcentagem de acerto por alvo
            
            numStops=0
            mediaVariarStop=[]
            for s in group['Variar']:
                if s<0:
                    numStops+=1
                mediaVariarStop.append(s)

            
            # Calcular média de acerto e frequência
            media_acertos = sum(acertos.values()) / len(acertos)
            #Frequncia da operaçao
            frequencia = total_linhas
            #Porcentagem da frequencia no Total de trades
            porcenFreq = (len(group[df['Ativo'] == ativo][df['Timeframe']== timeframe]['Variar'])/len(df[df['Ativo'] == ativo][df['Timeframe'] == timeframe]))*100

            #Calcular Horario e Dia mais lucrativos
            frequencia_dias = group[group['Variar'] > 0]['Dia da Semana'].value_counts()
            frequencia_horarios = group[group['Variar'] > 0]['Horário'].value_counts()

            # Selecionar os 3 mais frequentes
            top_3_dias = frequencia_dias.nlargest(3)
            top_3_horarios = frequencia_horarios.nlargest(3)
            
            # Calcular saldo acumulado simulado para o grupo
            variacoes = group[df['Ativo'] == ativo][df['Timeframe']== timeframe][group['Gatilho']==gatilho]['Variar']
            saldo_acumulado = 100 #saldo Inicial com $100
            saldo_acumulado_neg = 0
            saldo_acumulado_pos = 0
            saldo_lista = []
            for var in variacoes:
                entrada= saldo_acumulado*(20/100) #entrada
                saldo_acumulado += ((var * 10)/entrada) # saldo_acumulado + ((variaçao% * alavacangem)/entrada)
                saldo_lista.append(saldo_acumulado)

                if var < 0:
                    saldo_acumulado_neg += saldo_acumulado
                else:
                    saldo_acumulado_pos += saldo_acumulado
            
            retorno_total = (saldo_acumulado - saldo_inicial) / saldo_inicial
            
            # Calcular drawdown
            if saldo_lista:
                saldo_series = pd.Series(saldo_lista)
                maximo_acumulado = saldo_series.cummax()
                drawdown = ((saldo_series - maximo_acumulado) / maximo_acumulado * 100).min()
            else:
                drawdown = 0
            
            
            # Win Rate e Razão Risco/Retorno
            trades_positivos = variacoes[variacoes > 0]
            trades_negativos = variacoes[variacoes < 0]
            win_rate = (len(trades_positivos) / len(variacoes)) * 100 if len(variacoes) > 0 else 0
            avg_win = trades_positivos.mean() if len(trades_positivos) > 0 else 0 #Nao esta no front
            avg_loss = abs(trades_negativos.mean()) if len(trades_negativos) > 0 else 0 #Nao esta no front
            razao_risk_reward = avg_win / avg_loss if avg_loss != 0 else float('inf')
            
            # Calcular EV (valor esperado)
            ev = ((trades_positivos.mean()*10)*saldo_acumulado_pos)+(((trades_negativos.mean()*10)*saldo_acumulado_neg))
            
            
            # Profit Factor (Lucro Total / Prejuízo Total)
            lucro_total = trades_positivos.sum()
            prejuizo_total = abs(trades_negativos.sum())
            profit_factor = lucro_total / prejuizo_total if prejuizo_total != 0 else float('inf')
                        
            # --- Cálculo do Score ---
            score = (
                (porcenFreq * 0.03 )+
                (retorno_total * 0.025) +
                (win_rate * 0.035) +
                (profit_factor * 0.025) +
                (ev * 0.04) -
                (abs(drawdown) * 0.015) -
                (avg_loss * 0.02)# Penaliza perdas acima de um limite
                ##(razao_risk_reward * 0.12)
            )

            # Adicionar ao dicionário com índice combinado
            estatisticas[(ativo, timeframe, localizacao, estrategia, gatilho)] = {
                'Projecao': pd.DataFrame(list(saldo_lista), columns=['PnL']),
                'Frequência': frequencia,
                'Frequência(%)': porcenFreq,
                'Horário':top_3_horarios,
                'Dia': top_3_dias,
                'Média de Acertos(%)': win_rate,
                'Drawdown (%)': drawdown,
                'Variação Media (%)': statistics.mean(group['Variar']),
                'Razão Recompensa/Risco': razao_risk_reward,
                'EV': ev,
                'Score': score,
                'Alvos':pd.DataFrame(list(acertos.items()), columns=["Alvo", "Porcentagem de Acerto"]).set_index("Alvo").transpose()
            }

    
    
    return ativos,estatisticas,df[df['Ativo'] == ativo]
    
# Função para adicionar ou remover itens
def add_remove_item(lista, action, item):
    if len(lista) > 0:
        if action == "Adicionar" and item not in lista:
            lista.append(item)
        elif action == "Remover" and item in lista:
            lista.remove(item)
        return lista
    else:
        if action == "Adicionar" and item not in lista:
            lista.append("-")
            lista.append(item)
        elif action == "Remover" and item in lista:
            lista.remove(item)
        return lista

# Carregar as listas ao iniciar
ativos_lista, localizacao_lista, estrategias_lista, gatilhos_lista = carregar_dados_csv()

# Título do formulário
st.title("🕹️Backtest Manual")

# Função para carregar as listas a partir dos CSVs
def carregar_dados_csv():
    ativos_lista = carregar_lista_csv(ativo_csv_file)
    localizacao_lista = carregar_lista_csv(localizacao_csv_file)
    estrategias_lista = carregar_lista_csv(estrategia_csv_file)
    gatilhos_lista = carregar_lista_csv(gatilho_csv_file)
    return ativos_lista, localizacao_lista, estrategias_lista, gatilhos_lista

# Função para carregar lista de um CSV
def carregar_lista_csv(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        df = pd.read_csv(caminho_arquivo)
        return df.iloc[:, 0].dropna().tolist()  # Carrega a primeira coluna
    else:
        return []

# Função para salvar os dados no CSV dos dados do formulário
def salvar_dados_formulario(ativos_lista, localizacao_lista, estrategias_lista, gatilhos_lista, variar, alvos_lista, stop, dados):
    # Igualar o tamanho das listas
    ativos_lista, localizacao_lista, estrategias_lista, gatilhos_lista = equalizar_listas(
        ativos_lista, localizacao_lista, estrategias_lista, gatilhos_lista)

    if stop:
        variar = -float(variar)
        
    # Criar o DataFrame para os dados do formulário
    df = pd.DataFrame({
        'Ativo': ativos_lista,
        'Timeframe': dados["Timeframe"],
        'Horário': dados["Horário"],
        'Dia da Semana': dados["Dia da Semana"],
        'Contexto': dados["Contexto"],
        'Localização': localizacao_lista,
        'Estratégia': estrategias_lista,
        'Gatilho': gatilhos_lista,
        "Variar": variar
    })
    
    # Adicionar as colunas de alvos
    for alvo in alvos_lista:
        df[alvo] = [True if alvo in alvos else False for alvos in dados["Alvos"]]
    
    df['Stop'] = stop

    # Adicionar o novo registro ao arquivo CSV
    if os.path.exists(dados_csv_file):
        df.to_csv(dados_csv_file, mode='a', header=False, index=False)
    else:
        df.to_csv(dados_csv_file, mode='w', header=True, index=False)

# Função para preencher listas para garantir que tenham o mesmo tamanho
def equalizar_listas(*listas):
    ##max_len = max(len(lista) for lista in listas if isinstance(lista, list))
    listas_equalizadas = []
    for lista in listas:
        #lista.append(None)  # Preenche com None ou valor padrão
        listas_equalizadas.append(lista)
    return listas_equalizadas

# Função para salvar os itens no CSV de Ativo, Localização, Estratégia, Gatilho
def salvar_lista_csv(lista, caminho_arquivo):
    df = pd.DataFrame(lista, columns=[os.path.basename(caminho_arquivo).replace('.csv', '')])
    df.to_csv(caminho_arquivo, index=False)

# Popup para Gerenciar Itens
with st.expander("Gerenciar Itens", expanded=False):
    pass
# Formulário de entrada para dados principais
st.subheader("Preencha os dados do Formulário")

# Dividindo os campos em colunas
col1, col2, col3 = st.columns(3)
col21, col22 = st.columns(2)

# Campos principais organizados em três colunas
with col1:
    ativo_s = st.selectbox("Ativo", ativos_lista)
    localizacao_s = st.selectbox("Localização", localizacao_lista)
    variacao_s = st.text_input("Variação %")

with col2:
    estrategia_s = st.selectbox("Estratégia", estrategias_lista)
    gatilho_s = st.selectbox("Gatilhos", gatilhos_lista)
    horario_s = st.selectbox("Horário", horarios_lista)

with col3:
    contexto_s = st.text_area("Contexto", height=120)
    dia_semana_s = st.selectbox("Dia da Semana", dias_da_semana)

# Timeframes e Alvos em uma quarta coluna
with col21:
    st.subheader("Timeframes")
    timeframe_selecionados_s = []
    timeframe_cols = st.columns(len(timeframes_lista))  # Dividir timeframes em colunas
    for idx, tf in enumerate(timeframes_lista):
        if timeframe_cols[idx].checkbox(tf, key=f"timeframe_{tf}"):
            timeframe_selecionados_s.append(tf)
    st.subheader("Alvos")
    alvos_selecionados_s = []
    alvos_cols = st.columns(len(alvos_lista))  # Dividir alvos em colunas
    for idx, alvo in enumerate(alvos_lista):
        if alvos_cols[idx].checkbox(alvo, key=f"alvo_{alvo}"):
            alvos_selecionados_s.append(alvo)
    stop_s = st.checkbox("Stop")


# Botão para salvar
if st.button("Salvar"):
    # Adicionando os dados ao DataFrame
    dados["Ativo"].append(ativo_s)
    dados["Timeframe"].append(", ".join(timeframe_selecionados_s))  # Concatenar timeframes como string
    dados["Contexto"].append(contexto_s)
    dados["Localização"].append(localizacao_s)
    dados["Estratégia"].append(estrategia_s)
    dados["Gatilhos"].append(gatilho_s)
    dados["Variar"].append(variacao_s)
    dados["Alvos"].append(alvos_selecionados_s)  # Lista de alvos
    dados["Stop"].append(stop_s)  # Lista de alvos
    dados["Horário"].append(horario_s)
    dados["Dia da Semana"].append(dia_semana_s)
    
    # Criando ou atualizando o DataFrame
    if variacao_s != '':
        salvar_dados_formulario(ativo_s, localizacao_s, estrategia_s, gatilho_s,variacao_s, alvos_lista, stop_s, dados)
        st.success("Dados salvos com sucesso!")
    else:
        st.error("⛔ Campo Variação esta vazio! ")
        msg= st.toast('Campo Variação esta vazio', icon='⛔')
        time.sleep(3)
        msg.toast('Por Favor adicione a porcentagem de variação...')
        time.sleep(3)
        msg.toast('Tente novamente!')
        
# verificar se o arquivo existe
if os.path.isfile(dados_csv_file):
    # Carregar os dados do CSV
    df2 = pd.read_csv(dados_csv_file)

    # Calcular as estatísticas de acerto
    ativos,estatisticas,total_trades_ativo = calcular_estatisticas_acerto(df2)
    #print(ativos)
    
    # Exibir as estatísticas no Streamlit
    st.subheader("Estatísticas de Acerto por Ativo e Combinção de Estratégia, Localização e Gatilho")
    
    #Abas
    tab1, tab2 = st.tabs(["Ativos", "Localizaçao"])
    with tab1:
        
        # Chamada ao Janela do Filtro
        sortedList = ['Frequência(%)','Média de Acertos(%)', 'Drawdown (%)', 'Variação Media (%)', 'Razão Recompensa/Risco', 'EV', 'Score']
        sortedList_s=''
        
        st.subheader("Filtros", divider="red")
        col_flt_ativo, col_flt_tmFrame, col_flt_sorted,_,_,_ = st.columns(6)
        with col_flt_ativo:
            ativosList_s = st.selectbox("Ativo", ativos)
        with col_flt_tmFrame:
            timerFrameList_s = st.selectbox("Timer Frame", timeframes_lista)
        with col_flt_sorted:
            sortedList_s = st.selectbox("Ordem da Lista", sortedList)
        st.divider()
        # Iteração no dicionário 'estatisticas'
        for ativo in ativos:
            

            if sortedList_s == '':
                x = sorted(estatisticas.items(), key=lambda x: float(x[1]["EV"]), reverse=True)
            else:
                x = sorted(estatisticas.items(), key=lambda x: float(x[1][sortedList_s]), reverse=True)
                
            #st.html(f"<h3>{ativo}</h3>")
            for chave, valores in x:
                #print(list(chave)) # Console 
                ativo_,timeframe, localizacao, estrategia, gatilho = chave
                
                if (ativosList_s == ativo_) and (ativo_==ativo) and (timeframe==timerFrameList_s):
                    with st.expander(f"{ativo_} - {timeframe} - {localizacao} - {estrategia} - {gatilho}", expanded=False):
                        # Informação da Estatisca
                        
                        col31, col32, col33 = st.columns(3) # Colunas de Metricas
                        for metrica, valor in valores.items():
                            if type(valor) is pd.DataFrame:
                                #Chart PnL
                                if valor.columns[0] == 'PnL':
                                    st.write(f"**Projeção PnL:** ") 
                                    st.area_chart(valor, color=["#5BD96C"])
                            if type(valor) is not pd.DataFrame:
                                    #Metricas
                                    if (metrica == 'Frequência'):
                                        with col31:
                                            st.metric(metrica,f"{valor}/{len(total_trades_ativo[df2['Timeframe']==timerFrameList_s])}")
                                    elif (metrica == 'Frequência(%)') or (metrica == 'Variação Media (%)') or (metrica == 'Razão Recompensa/Risco'):
                                        with col33:
                                            st.metric(metrica,f"{valor:.2f}")
                                    elif (metrica == 'Horário') or (metrica == 'Dia'):
                                        with col31:
                                            st.write(f"**{metrica}:** ") 
                                            st.write(valor)

                                    if (metrica == 'Média de Acertos(%)') or (metrica == 'Drawdown (%)') or (metrica == 'EV') or (metrica == 'Score'):
                                        with col32:
                                            st.metric(metrica,f"{valor:.2f}")
                            if type(valor) is pd.DataFrame:
                                #Alvos estatisticas
                                if valor.columns[0] != 'PnL':
                                    st.write(f"**{metrica} Estatistica:** ") 
                                    st.write(valor)
    with tab2:
            st.subheader("Filtros", divider="red")
            col_flt_ativo, col_flt_tmFrame, col_flt_sorted,_,_,_ = st.columns(6)
            with col_flt_ativo:
                ativosList_s = st.selectbox("Ativo.", ativos)
            with col_flt_tmFrame:
                timerFrameList_s = st.selectbox("Timer Frame.", timeframes_lista)
            st.divider()
            
            lastLocalizacao = []
            listaLocalizacao = {}
            for chave, valores in x:
                #print(list(chave)) # Console 
                _,_, localizacao, _, _ = chave
                if localizacao not in lastLocalizacao:
                                                
                    lastLocalizacao.append(localizacao)
            
            
            # Iteração no dicionário 'estatisticas'
            for ativo in ativos:
                
                for chave, valores in x:
                    
                    ativo_,timeframe, localizacao, estrategia, gatilho = chave
                    if (ativo_==ativosList_s) and (ativo_==ativo) and (timeframe==timerFrameList_s):
                        
                        # Inicializar métricas com valores padrão
                        Frequencia = 0
                        Frequência_p = 0
                        VariaçãoMedia = 0
                        RecompensaRisco = 0
                        MédiaAcertos = 0
                        Drawdown = 0
                        EV = 0
                        Score = 0

                        # Processar as métricas disponíveis
                        for metrica, valor in valores.items():
                            if metrica == 'Total Trade':
                                totalTrade = valor
                            elif metrica == 'Frequência':
                                Frequencia = valor
                            elif metrica == 'Frequência(%)':
                                Frequência_p = valor
                            elif metrica == 'Variação Media (%)':
                                VariaçãoMedia = valor
                            elif metrica == 'Razão Recompensa/Risco':
                                RecompensaRisco = valor
                            elif metrica == 'Média de Acertos(%)':
                                MédiaAcertos = valor
                            elif metrica == 'Drawdown (%)':
                                Drawdown = valor
                            elif metrica == 'EV':
                                EV = valor
                            elif metrica == 'Score':
                                Score = valor

                        # Se a localização ainda não foi registrada, cria a entrada no dicionário
                        if localizacao not in listaLocalizacao:
                            listaLocalizacao[localizacao] = {
                                'ativo':ativo,
                                'local': localizacao,
                                'Total Trade': total_trades_ativo,
                                'Frequência': Frequencia,
                                'Frequência(%)': Frequência_p,
                                'Variação Media (%)': VariaçãoMedia,
                                'Razão Recompensa/Risco': RecompensaRisco,
                                'Média de Acertos(%)': MédiaAcertos,
                                'Drawdown (%)': Drawdown,
                                'EV': EV,
                                'Score': Score
                            }
                        else:
                            # Somar os valores existentes com os novos valores
                            listaLocalizacao[localizacao]['Frequência'] += Frequencia
                            listaLocalizacao[localizacao]['Frequência(%)'] += Frequência_p
                            listaLocalizacao[localizacao]['Variação Media (%)'] += VariaçãoMedia
                            listaLocalizacao[localizacao]['Razão Recompensa/Risco'] += RecompensaRisco
                            listaLocalizacao[localizacao]['Média de Acertos(%)'] += MédiaAcertos
                            listaLocalizacao[localizacao]['Drawdown (%)'] += Drawdown
                            listaLocalizacao[localizacao]['EV'] += EV
                            listaLocalizacao[localizacao]['Score'] += Score
                            
            try:
                for l in lastLocalizacao:
                    with st.container(border=True):
                        st.markdown(f"#### **{listaLocalizacao[l]['ativo']}-{l} - {timerFrameList_s}**")
                        col_freq, col_freq_q, col_var, col_raz, col_media, col_draw, col_EV, col_Score = st.columns(8)
                        
                        for m, v in listaLocalizacao[l].items():
                            if m == 'Frequência':
                                with col_freq:
                                    st.metric(m,f"{v}/{len(total_trades_ativo[df2['Timeframe']==timerFrameList_s])}")
                            elif m == 'Frequência(%)':
                                with col_freq_q:
                                    st.metric(m,f"{v:.2f}")
                            elif m == 'Variação Media (%)':
                                with col_var:
                                    st.metric(m,f"{v:.2f}")
                            elif m == 'Razão Recompensa/Risco':
                                with col_raz:
                                    st.metric(m,f"{v:.2f}")
                            elif m == 'Média de Acertos(%)':
                                with col_media:
                                    st.metric(m,f"{v:.2f}")
                            elif m == 'Drawdown (%)':
                                with col_draw:
                                    st.metric(m,f"{v:.2f}")
                            elif m == 'EV':
                                with col_EV:
                                    st.metric(m,f"{v:.2f}")
                            elif m == 'Score':
                                with col_Score:
                                    st.metric(m,f"{v:.2f}")
            except:
                st.warning('Nada para esse filtro.')        
                                
                    
else:
    st.subheader("Não base de Dados! Adicione dados!")
    
