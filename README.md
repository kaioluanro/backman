# install

- faz o git clone do projeto
- roda pip install -r requirements.txt
- ao finalizar de install todas as dependencias, roda o comando "streamlit run main.py"


# Documentação Estatistica

## Frequencia

Numero de vezes que o trade apareceu em relaçao a todos os trades feitos.

## Frequencia(%)

Mesmo que frenquencia, porem representado em porcentagem.

## Média de Acertos(%)

Porcentagem de trades acertados, ou taxa de acertos.

## Drawdown (%)

Porcentagem da perda maxima.

## EV ( Em dolar ) (Valor experado)

resultado médio esperado do valor($) pela estatistica. Quando maior o EV melhor e positivo melhor

## Score

Pontuaçao para uma estratagia/setup

## Variação Media (%)

Porcentagem media da variaçao do preço do takeprofit

## Razão Recompensa/Risco

A Razão Risk/Reward (Risco/Retorno) é uma métrica essencial em trading que compara o potencial ganho de uma operação (reward) com o potencial perda (risk). Ela ajuda a avaliar se uma estratégia vale a pena, considerando o equilíbrio entre lucros e riscos.
    
    Estratégias com Razão > 1 são desejáveis, pois compensam as perdas com menos acertos.

    Exemplo: Com razão 3:1, você só precisa acertar 25% das operações para ser lucrativo.

    Estratégias com Razão < 1 exigem uma alta taxa de acertos (win rate) para serem viáveis.


## Horário

Ranqueia os três horarios com mais trade positivos.

## Dia

Ranqueia os três dias da semana com mais trade positivos.