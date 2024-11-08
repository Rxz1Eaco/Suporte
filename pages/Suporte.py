import pandas as pd 
import streamlit as st 
import plotly.express as px
import matplotlib.pyplot as plt 
import seaborn as sns

st.title("Suporte 👨🏾‍💻 - São Luís Mottu")
st.info("Destina para analisar o cenário entre o dia 01/10 - 31/10")
st.sidebar.write("Desenvolvido por [Éaco Rocha](https://github.com/Rxz1Eaco)")

with st.expander('Data'):
    df = pd.read_excel("dadossuporte.xlsx")
    df = df.drop([494, 495]) # REMOVENDO LINHAS EM BRANCO
    Linhas , Colunas = df.shape
    st.write(f"A base de dados tem um Total de {Linhas} Linhas e um Total de {Colunas} Colunas ")
    st.write(df)


with st.expander('Data Analysis'):
    st.markdown("### Quantidade de Serviços por Motorista")
    df_motoristas = df.groupby('Motorista').size().reset_index(name='Total de Serviços')
    df['Data'] = pd.to_datetime(df['Data'])
    df['data_fechamento'] = pd.to_datetime(df['data_fechamento'])
    df['duração_minutos'] = (df['data_fechamento'] - df['Data']).dt.total_seconds() / 60
    df_abaixo_120 = df[df['duração_minutos'] < 120]
    df_motoristas_abaixo_120 = df_abaixo_120.groupby('Motorista').size().reset_index(name='Total Serviços < 120 minutos')
    df_combined = pd.merge(df_motoristas, df_motoristas_abaixo_120, on='Motorista', how='left')
    df_combined['Total Serviços < 120 minutos'] = df_combined['Total Serviços < 120 minutos'].fillna(0).astype(int)
    df_combined['Diferença'] = df_combined['Total de Serviços'] - df_combined['Total Serviços < 120 minutos']
    df_combined['% Serviços < 120 Minutos'] = (df_combined['Total Serviços < 120 minutos'] / df_combined['Total de Serviços']) * 100
    st.write(df_combined)
    st.markdown("### Motoristas % de Serviços < 120 Minutos < 90%")
    df_filtered = df_combined[df_combined['% Serviços < 120 Minutos'] < 90]
    st.write(df_filtered)

    df['Turno'] = df['Data'].apply(lambda x: 'Manhã' if 6 <= x.hour < 12 else ('Tarde' if 12 <= x.hour < 18 else 'Noite'))
    turno_tempo_medio = df.groupby('Turno')['Tempo total (min)'].mean().reset_index()
    st.write("### Tempo Médio de Serviço por Turno")
    st.write(turno_tempo_medio)

    corr = df[['Tempo total (min)', 'dias_entre_manut_e_servico_rua']].corr().iloc[0,1]
    st.write(f"Correlação entre o Tempo Total de Serviço e os Dias entre Manutenção e Serviço: {corr:.2f}")

    tempo_ideal = 90  # Exemplo de tempo ideal em minutos
    df['Acima do Tempo Ideal'] = df['Tempo total (min)'] > tempo_ideal
    servicos_acima_ideal = df['Acima do Tempo Ideal'].sum()
    total_servicos = df.shape[0]
    perc_acima_ideal = (servicos_acima_ideal / total_servicos) * 100
    st.write(f"Percentual de Serviços Acima do Tempo Ideal ({tempo_ideal} minutos): {perc_acima_ideal:.2f}%")


with st.expander('Data Visualization'):
    fig = px.bar(
    df_combined,
    x='Motorista',
    y=['Total de Serviços', 'Total Serviços < 120 minutos'],
    title="Quantidade de Serviços por Motorista",
    labels={'value': 'Quantidade de Serviços', 'Motorista': 'Motorista'},
    barmode='group'
)
    fig = px.bar(
        df_combined,
        x='Motorista',
        y=['Total de Serviços', 'Total Serviços < 120 minutos'],
        title="Quantidade de Serviços por Motorista",
        labels={'value': 'Quantidade de Serviços', 'Motorista': 'Motorista'},
        barmode='group'
    )

    # Adicionar uma linha para a porcentagem de serviços abaixo de 120 minutos
    fig.add_scatter(
        x=df_combined['Motorista'],
        y=df_combined['% Serviços < 120 Minutos'],
        mode='lines+markers',
        name='% Serviços < 120 Minutos',
        yaxis="y2"
    )

    # Configurar o layout para o eixo secundário e limitar o eixo y principal a 100
    fig.update_layout(
        yaxis=dict(
            title="Quantidade de Serviços",
            range=[0, 200],  # Limite máximo do eixo y principal para 100
            title_standoff=0  # Move o rótulo do eixo principal para cima
        ),
        yaxis2=dict(
            title="Serviços < 120 Minutos",
            overlaying="y",
            side="right",
            range=[0, 100],
            title_standoff=20  # Move o rótulo do eixo secundário para cima
        ),
        legend=dict(title="Legenda")
    )

    # Exibir gráfico no Streamlit
    st.plotly_chart(fig)
    
    def definir_cor(row):
        #Distância , 5 e 10
        if row['distancia'] < 10:
            if row['Tempo total (min)'] < 90:
                return 'Verde Médio'  
            elif 90 <= row['Tempo total (min)'] < 120:
                return 'Amarelo Vivo'  
            else:
                return 'Vermelho Claro'  
        elif 10 < row['distancia'] < 20:
            if row['Tempo total (min)'] < 90:
                return 'Amarelo Vivo'  
            elif 90 <= row['Tempo total (min)'] < 120:
                return 'Amarelo Vivo'  # LARANJA
            else:
                return 'Vermelho Claro'  #ROXO
        else:
            if row['Tempo total (min)'] < 90:
                return 'Vermelho Claro'  # Alterado para Rosa Claro
            elif 90 <= row['Tempo total (min)'] < 120:
                return 'Vermelho Claro'  #PRETO
            else:
                return 'Vermelho Claro' #MARROM

    df['Cor'] = df.apply(definir_cor, axis=1)
    fig = px.scatter(df, x='distancia', y='Tempo total (min)',  
                    color='Cor',  # Coluna que define a cor 
                    hover_name='Motorista',
                    color_discrete_map={
                        'Verde Médio': '#32CD32',          # Verde Médio
                        'Amarelo Vivo': '#FFD700',         # Amarelo Vivo
                        'Vermelho Claro': '#FF7F7F',       # Vermelho Claro
                    },  # Mapeamento de cores 
                    title='Correlação entre Distância e Tempo de Serviço')
    st.write("Verificar se a distância entre o cliente e a oficina afeta o tempo do serviço.")
    st.plotly_chart(fig)
    info_cores = """
        ### Cores e suas Condições:

        *Verde Médio*
        - *Significado*: Indica um bom desempenho, onde a proximidade do cliente à oficina e o tempo de serviço são ambos favoráveis.".

        *Amarelo Vivo*
        - *Significado*: Sugere uma situação de atenção. O tempo de serviço está começando a se prolongar, embora a distância ainda seja curta.

        *Vermelho Claro*
        - *Significado*: Representa um alerta. A proximidade à oficina não está compensando o tempo excessivo de serviço, indicando possíveis problemas de eficiência.

        """
    st.write(info_cores)
    # Convertendo a coluna 'Data' para datetime
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

    # Verificando e ajustando os nomes das colunas
    df.rename(columns=lambda x: x.strip(), inplace=True)  # Remove espaços em branco
    if 'MotivoAbertura' not in df.columns or 'filial' not in df.columns:
            st.error("As colunas 'MotivoAbertura' ou 'filial' não foram encontradas. Verifique o arquivo.")
    else:
            # Contando os problemas por filial e motivo de abertura
            filial_problema = df.groupby(['MotivoAbertura', 'filial']).size().reset_index(name='count')

            # Contando o total de problemas por motivo de abertura (independente da filial)
            problemas_por_motivo = filial_problema.groupby('MotivoAbertura')['count'].sum().reset_index()

            # Ordenando os motivos de abertura pela quantidade de problemas
            problemas_por_motivo = problemas_por_motivo.sort_values(by='count', ascending=False)

            # Calculando a porcentagem acumulada
            problemas_por_motivo['acumulado'] = problemas_por_motivo['count'].cumsum() / problemas_por_motivo['count'].sum() * 100

            # Exibindo o gráfico de Pareto
            st.write("### Gráfico de Pareto - Distribuição de Problemas por Motivo de Abertura")

            fig, ax1 = plt.subplots(figsize=(12, 8))

            # Gráfico de barras para os problemas
            ax1.bar(problemas_por_motivo['MotivoAbertura'], problemas_por_motivo['count'], color='skyblue')
            ax1.set_xlabel("Motivo da Abertura")
            ax1.set_ylabel("Número de Problemas", color='skyblue')
            ax1.tick_params(axis='y', labelcolor='skyblue')
            ax1.set_xticklabels(problemas_por_motivo['MotivoAbertura'], rotation=45, ha="right")

            # Adicionando a linha de porcentagem acumulada
            ax2 = ax1.twinx()
            ax2.plot(problemas_por_motivo['MotivoAbertura'], problemas_por_motivo['acumulado'], color='red', marker='o', linestyle='-', linewidth=2)
            ax2.set_ylabel("Porcentagem Acumulada (%)", color='red')
            ax2.tick_params(axis='y', labelcolor='red')

            st.pyplot(fig)





    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

        # Verificando e ajustando os nomes das colunas
    df.rename(columns=lambda x: x.strip(), inplace=True)  # Remove espaços em branco
    if 'MotivoAbertura' not in df.columns or 'filial' not in df.columns or 'Motorista' not in df.columns:
            st.error("As colunas 'MotivoAbertura', 'filial' ou 'Motorista' não foram encontradas. Verifique o arquivo.")
    else:
            # Contando os problemas por filial, motivo de abertura e motorista
            filial_motorista_problema = df.groupby(['MotivoAbertura', 'filial', 'Motorista']).size().unstack(level='Motorista', fill_value=0)

            # Ordenando os motivos de abertura pela soma total de problemas em ordem decrescente
            filial_motorista_problema = filial_motorista_problema.loc[filial_motorista_problema.sum(axis=1).sort_values(ascending=False).index]

            # Exibindo o gráfico no Streamlit
            st.write("### Distribuição de Problemas por Filial, Motivo da Abertura e Motorista (Ordenado do Maior para o Menor)")

            fig, ax = plt.subplots(figsize=(14, 10))
            sns.heatmap(filial_motorista_problema, cmap="YlGnBu", annot=True, fmt="d", ax=ax)
            ax.set_xlabel("Motorista")
            ax.set_ylabel("Motivo da Abertura e Filial")

            st.pyplot(fig)
