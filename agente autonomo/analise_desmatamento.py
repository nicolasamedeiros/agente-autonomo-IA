import pandas as pd
import matplotlib
matplotlib.use('Agg') # Usar backend Agg para evitar problemas com threads de GUI
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np

# Configuração do estilo dos gráficos
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def carregar_dados():
    """Carrega e prepara os dados do arquivo CSV."""
    df = pd.read_csv('prodes_desmatamento.csv', sep=';')
    df.columns = df.columns.str.strip()
    return df

def analise_detalhada(df):
    """Realiza uma análise detalhada dos dados."""
    analise = []
    
    # Análise geral da Amazônia Legal
    total_amazonia = df['AMZ LEGAL'].sum()
    media_amazonia = df['AMZ LEGAL'].mean()
    max_amazonia = df['AMZ LEGAL'].max()
    min_amazonia = df['AMZ LEGAL'].min()
    ano_max = df.loc[df['AMZ LEGAL'] == max_amazonia, 'Ano/Estados'].iloc[0]
    ano_min = df.loc[df['AMZ LEGAL'] == min_amazonia, 'Ano/Estados'].iloc[0]
    
    analise.append(f"Análise da Amazônia Legal:")
    analise.append(f"- Total desmatado no período: {total_amazonia:,.2f} km²")
    analise.append(f"- Média anual de desmatamento: {media_amazonia:,.2f} km²")
    analise.append(f"- Maior índice de desmatamento: {max_amazonia:,.2f} km² (ano {ano_max})")
    analise.append(f"- Menor índice de desmatamento: {min_amazonia:,.2f} km² (ano {ano_min})")
    
    # Análise por estado
    estados = df.columns[1:-1]  # Exclui 'Ano/Estados' e 'AMZ LEGAL'
    analise.append("\nAnálise por Estado:")
    
    for estado in estados:
        total_estado = df[estado].sum()
        media_estado = df[estado].mean()
        max_estado = df[estado].max()
        min_estado = df[estado].min()
        ano_max_estado = df.loc[df[estado] == max_estado, 'Ano/Estados'].iloc[0]
        ano_min_estado = df.loc[df[estado] == min_estado, 'Ano/Estados'].iloc[0]
        
        analise.append(f"\n{estado}:")
        analise.append(f"- Total desmatado: {total_estado:,.2f} km²")
        analise.append(f"- Média anual: {media_estado:,.2f} km²")
        analise.append(f"- Maior índice: {max_estado:,.2f} km² (ano {ano_max_estado})")
        analise.append(f"- Menor índice: {min_estado:,.2f} km² (ano {ano_min_estado})")
    
    # Análise de tendência
    analise.append("\nAnálise de Tendência:")
    # Calcula a variação percentual entre o primeiro e último ano
    primeiro_ano = df['AMZ LEGAL'].iloc[0]
    ultimo_ano = df['AMZ LEGAL'].iloc[-1]
    variacao = ((ultimo_ano - primeiro_ano) / primeiro_ano) * 100
    
    analise.append(f"- Variação total no período: {variacao:,.2f}%")
    
    # Análise da última década
    ultima_decada = df.tail(10)
    media_decada = ultima_decada['AMZ LEGAL'].mean()
    variacao_decada = ((ultima_decada['AMZ LEGAL'].iloc[-1] - ultima_decada['AMZ LEGAL'].iloc[0]) / 
                       ultima_decada['AMZ LEGAL'].iloc[0]) * 100
    
    analise.append(f"- Média da última década: {media_decada:,.2f} km²")
    analise.append(f"- Variação na última década: {variacao_decada:,.2f}%")
    
    return "\n".join(analise)

def analise_geral(df):
    """Realiza uma análise geral dos dados."""
    print("\nEstatísticas Descritivas:")
    print(df.describe())
    
    print("\nInformações do Dataset:")
    print(df.info())

def plotar_evolucao_amazonia_legal(df):
    """Plota a evolução do desmatamento na Amazônia Legal."""
    plt.figure(figsize=(12, 6))
    plt.plot(df['Ano/Estados'], df['AMZ LEGAL'], marker='o')
    plt.title('Evolução do Desmatamento na Amazônia Legal (1988-2024)')
    plt.xlabel('Ano')
    plt.ylabel('Área Desmatada (km²)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('evolucao_amazonia_legal.png')
    plt.close()

def plotar_estados_mais_afetados(df):
    """Plota os estados mais afetados pelo desmatamento."""
    # Calcula a média de desmatamento por estado
    estados = df.columns[1:-1]  # Exclui 'Ano/Estados' e 'AMZ LEGAL'
    medias = df[estados].mean()
    
    plt.figure(figsize=(12, 6))
    medias.sort_values(ascending=False).plot(kind='bar')
    plt.title('Média de Desmatamento por Estado (1988-2024)')
    plt.xlabel('Estado')
    plt.ylabel('Área Média Desmatada (km²)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('estados_mais_afetados.png')
    plt.close()

def analise_correlacao(df):
    """Analisa a correlação entre os estados."""
    estados = df.columns[1:-1]
    correlacao = df[estados].corr()
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlacao, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlação entre Estados')
    plt.tight_layout()
    plt.savefig('correlacao_estados.png')
    plt.close()

def previsao_futura(df):
    """Realiza uma previsão simples para os próximos anos."""
    X = np.array(range(len(df))).reshape(-1, 1)
    y = df['AMZ LEGAL'].values
    
    modelo = LinearRegression()
    modelo.fit(X, y)
    
    # Previsão para os próximos 5 anos
    anos_futuros = np.array(range(len(df), len(df) + 5)).reshape(-1, 1)
    previsao = modelo.predict(anos_futuros)
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['Ano/Estados'], df['AMZ LEGAL'], marker='o', label='Dados Históricos')
    anos_futuros_labels = [str(int(df['Ano/Estados'].iloc[-1]) + i + 1) for i in range(5)]
    plt.plot(anos_futuros_labels, previsao, marker='o', linestyle='--', label='Previsão')
    plt.title('Previsão de Desmatamento na Amazônia Legal')
    plt.xlabel('Ano')
    plt.ylabel('Área Desmatada (km²)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('previsao_futura.png')
    plt.close()

def main():
    """Função principal que executa todas as análises."""
    print("Iniciando análise do desmatamento na Amazônia...")
    
    # Carrega os dados
    df = carregar_dados()
    
    # Realiza as análises
    analise_geral(df)
    plotar_evolucao_amazonia_legal(df)
    plotar_estados_mais_afetados(df)
    analise_correlacao(df)
    previsao_futura(df)
    
    print("\nAnálise concluída! Os gráficos foram salvos no diretório atual.")

if __name__ == "__main__":
    main() 