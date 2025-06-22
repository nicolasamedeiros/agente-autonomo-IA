import pandas as pd
import numpy as np
from datetime import datetime
import json

class AgenteAnaliseDesmatamento:
    def __init__(self, df):
        self.df = df
        self.nome = "Amazon Agent"
        self.descricao = (
            "O Amazon Agent é um especialista autônomo em análise de dados de desmatamento da Amazônia. "
            "Ele utiliza dados históricos e estatísticas para identificar tendências, "
            "detectar anomalias, gerar alertas sobre áreas críticas e "
            "fornecer insights e recomendações para mitigar o desmatamento. "
            "Seu objetivo é auxiliar na compreensão do fenômeno do desmatamento e "
            "apoiar a tomada de decisões estratégicas para a preservação da Amazônia Legal."
        )
        self.contexto = self._gerar_contexto()
        self.ultima_analise = None
        self.historico_analises = []
    
    def _gerar_contexto(self):
        """Gera um contexto baseado nos dados atuais"""
        return {
            'estados': list(self.df.columns[1:-1]),
            'periodo': f"{self.df['Ano/Estados'].min()} - {self.df['Ano/Estados'].max()}",
            'ultima_atualizacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'estatisticas_gerais': self._calcular_estatisticas_gerais()
        }
    
    def _calcular_estatisticas_gerais(self):
        """Calcula estatísticas gerais dos dados"""
        return {
            'total_amazonia': self.df['AMZ LEGAL'].sum(),
            'media_amazonia': self.df['AMZ LEGAL'].mean(),
            'max_amazonia': self.df['AMZ LEGAL'].max(),
            'min_amazonia': self.df['AMZ LEGAL'].min(),
            'estados_mais_afetados': self._identificar_estados_mais_afetados(),
            'tendencia_recente': self._calcular_tendencia_recente()
        }
    
    def _identificar_estados_mais_afetados(self):
        """Identifica os estados mais afetados pelo desmatamento"""
        estados = self.df.columns[1:-1]
        medias = self.df[estados].mean()
        return medias.sort_values(ascending=False).head(3).to_dict()
    
    def _calcular_tendencia_recente(self):
        """Calcula a tendência de desmatamento nos últimos 5 anos"""
        ultimos_5_anos = self.df.tail(5)
        variacao = ((ultimos_5_anos['AMZ LEGAL'].iloc[-1] - ultimos_5_anos['AMZ LEGAL'].iloc[0]) / 
                    ultimos_5_anos['AMZ LEGAL'].iloc[0]) * 100
        return {
            'variacao_percentual': variacao,
            'tendencia': 'aumento' if variacao > 0 else 'reducao'
        }
    
    def analisar_dados(self):
        """Realiza uma análise autônoma dos dados"""
        analise = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'alertas': self._gerar_alertas(),
            'insights': self._gerar_insights(),
            'recomendacoes': self._gerar_recomendacoes()
        }
        
        self.ultima_analise = analise
        self.historico_analises.append(analise)
        return analise
    
    def _gerar_alertas(self):
        """Gera alertas baseados em anomalias nos dados"""
        alertas = []
        
        # Alerta para aumento significativo
        ultimos_2_anos = self.df.tail(2)
        variacao_recente = ((ultimos_2_anos['AMZ LEGAL'].iloc[-1] - ultimos_2_anos['AMZ LEGAL'].iloc[0]) / 
                           ultimos_2_anos['AMZ LEGAL'].iloc[0]) * 100
        
        if variacao_recente > 20:
            alertas.append({
                'tipo': 'aumento_significativo',
                'descricao': f'Aumento de {variacao_recente:.1f}% no desmatamento nos últimos 2 anos',
                'severidade': 'alta'
            })
        
        # Alerta para estados críticos
        for estado in self.df.columns[1:-1]:
            ultimo_ano = self.df[estado].iloc[-1]
            media_estado = self.df[estado].mean()
            if ultimo_ano > media_estado * 1.5:
                alertas.append({
                    'tipo': 'estado_critico',
                    'descricao': f'{estado} apresentou desmatamento {((ultimo_ano/media_estado)-1)*100:.1f}% acima da média',
                    'severidade': 'media'
                })
        
        return alertas
    
    def _gerar_insights(self):
        """Gera insights baseados na análise dos dados"""
        insights = []
        
        # Insight sobre tendência geral
        tendencia = self._calcular_tendencia_recente()
        insights.append({
            'tipo': 'tendencia_geral',
            'descricao': f'Tendência de {tendencia["tendencia"]} no desmatamento nos últimos 5 anos',
            'detalhes': f'Variação de {tendencia["variacao_percentual"]:.1f}%'
        })
        
        # Insight sobre estados mais afetados
        estados_criticos = self._identificar_estados_mais_afetados()
        insights.append({
            'tipo': 'estados_criticos',
            'descricao': 'Estados com maior média de desmatamento',
            'detalhes': estados_criticos
        })
        
        return insights
    
    def _gerar_recomendacoes(self):
        """Gera recomendações baseadas na análise"""
        recomendacoes = []
        
        # Recomendação baseada na tendência
        tendencia = self._calcular_tendencia_recente()
        if tendencia['tendencia'] == 'aumento':
            recomendacoes.append({
                'tipo': 'acao_imediata',
                'descricao': 'Implementar medidas urgentes de controle do desmatamento',
                'prioridade': 'alta'
            })
        
        # Recomendação para estados críticos
        estados_criticos = self._identificar_estados_mais_afetados()
        for estado in estados_criticos:
            recomendacoes.append({
                'tipo': 'foco_estado',
                'descricao': f'Intensificar fiscalização em {estado}',
                'prioridade': 'media'
            })
        
        return recomendacoes
    
    def exportar_analise(self, formato='json'):
        """Exporta a última análise no formato especificado"""
        if not self.ultima_analise:
            return None
            
        if formato == 'json':
            return json.dumps(self.ultima_analise, indent=2, ensure_ascii=False)
        elif formato == 'dict':
            return self.ultima_analise
        else:
            raise ValueError("Formato não suportado")
    
    def monitorar_mudancas(self):
        """Monitora mudanças nos dados e gera alertas"""
        # Implementar lógica de monitoramento contínuo
        pass 