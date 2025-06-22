from flask import Flask, render_template, request, send_file, jsonify, session, redirect, url_for
import os
from analise_desmatamento import (
    carregar_dados,
    analise_geral,
    plotar_evolucao_amazonia_legal,
    plotar_estados_mais_afetados,
    analise_correlacao,
    previsao_futura,
    analise_detalhada
)
from agente_analise import AgenteAnaliseDesmatamento
import json
import time
import threading
import queue
import openai
import logging
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuração da API OpenAI
openai.api_key = "sk-XXXXXXXXXXXXXXXXXXXXXXXX"

# Configuração do Flask
app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'chave_secreta_do_app'

# Cria pasta de uploads se não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Cria pasta de gráficos se não existir
if not os.path.exists('static/graficos'):
    os.makedirs('static/graficos')

# Variáveis globais
agente = None
perguntas_queue = queue.Queue()
respostas_completas = {}

def limpar_sessao():
    """Limpa a sessão atual"""
    session.clear()
    # Limpa também as respostas completas em memória
    respostas_completas.clear()
    print("\n🔄 Histórico de perguntas e respostas em memória limpo!\n")

def gerar_imagem(prompt):
    """Gera uma imagem usando a API DALL-E"""
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        return response['data'][0]['url']
    except Exception as e:
        print(f"Erro ao gerar imagem: {str(e)}")
        return None

def gerar_grafico(df, tipo_grafico):
    """Gera um gráfico baseado no tipo solicitado"""
    try:
        plt.figure(figsize=(10, 6))
        
        if tipo_grafico == "evolucao":
            sns.lineplot(data=df, x='ano', y='desmatamento_km2')
            plt.title('Evolução do Desmatamento na Amazônia Legal')
            plt.xlabel('Ano')
            plt.ylabel('Desmatamento (km²)')
        elif tipo_grafico == "estados":
            df_estados = df.groupby('estado')['desmatamento_km2'].sum().sort_values(ascending=False)
            sns.barplot(x=df_estados.index, y=df_estados.values)
            plt.title('Desmatamento por Estado')
            plt.xticks(rotation=45)
            plt.xlabel('Estado')
            plt.ylabel('Desmatamento Total (km²)')
        
        # Cria o diretório static/graficos se não existir
        if not os.path.exists('static/graficos'):
            os.makedirs('static/graficos')
        
        # Gera um nome único para o arquivo
        timestamp = int(time.time())
        filename = f'grafico_{tipo_grafico}_{timestamp}.png'
        filepath = os.path.join('static/graficos', filename)
        
        # Salva o gráfico
        plt.savefig(filepath, format='png', bbox_inches='tight', dpi=300)
        plt.close()
        
        # Retorna o caminho relativo para a imagem
        return f'/static/graficos/{filename}'
    except Exception as e:
        print(f"Erro ao gerar gráfico: {str(e)}")
        return None

def processar_perguntas():
    """Processa perguntas pendentes na fila"""
    while True:
        try:
            if not perguntas_queue.empty():
                pergunta_id, pergunta = perguntas_queue.get()
                print(f"\n📝 Nova pergunta recebida: {pergunta}\n")
                
                try:
                    # Obtém dados e análises
                    df = agente.df
                    analise_texto = analise_detalhada(df)
                    analise_agente = agente.analisar_dados()
                    
                    # Verifica se a pergunta pede por uma imagem ou gráfico
                    imagem_url = None
                    if "gráfico" in pergunta.lower() or "grafico" in pergunta.lower():
                        if "evolução" in pergunta.lower() or "evolucao" in pergunta.lower():
                            imagem_url = gerar_grafico(df, "evolucao")
                        elif "estados" in pergunta.lower():
                            imagem_url = gerar_grafico(df, "estados")
                        else:
                            imagem_url = gerar_imagem(f"Gráfico mostrando {pergunta}")
                    elif "imagem" in pergunta.lower() or "foto" in pergunta.lower():
                        imagem_url = gerar_imagem(pergunta)
                    
                    # Prepara contexto para o ChatGPT
                    contexto = f"""
                    Você é o {agente.nome}, um especialista autônomo em análise de dados de desmatamento da Amazônia. {agente.descricao} Suas respostas devem ser baseadas nas análises fornecidas e devem ser claras e objetivas.
                    
                    Análise detalhada dos dados:
                    {analise_texto}
                    
                    Análise do agente:
                    {analise_agente}
                    
                    Pergunta: {pergunta}
                    
                    Por favor, responda de forma clara e objetiva, utilizando as análises fornecidas.
                    """
                    
                    print("🤖 Enviando pergunta para o ChatGPT...")
                    
                    try:
                        # Consulta o ChatGPT
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {
                                    "role": "system",
                                    "content": f"Você é o {agente.nome}, um especialista autônomo em análise de dados de desmatamento da Amazônia. {agente.descricao} Suas respostas devem ser baseadas nas análises fornecidas e devem ser claras e objetivas."
                                },
                                {
                                    "role": "user",
                                    "content": contexto
                                }
                            ],
                            temperature=0.7,
                            max_tokens=1000
                        )
                        
                        resposta = response.choices[0].message.content
                        print(f"\n💬 Resposta do ChatGPT:\n{resposta}\n")
                        
                        # Se houver uma imagem, adiciona à resposta
                        if imagem_url:
                            if imagem_url.startswith('/static/'):
                                # É um gráfico local
                                resposta = f"{resposta}\n\n<img src='{imagem_url}' alt='Gráfico gerado' style='max-width: 100%; height: auto;'>"
                            else:
                                # É uma imagem do DALL-E
                                resposta = f"{resposta}\n\n<img src='{imagem_url}' alt='Imagem gerada' style='max-width: 100%; height: auto;'>"
                        
                        # Armazena a resposta no dicionário global
                        respostas_completas[pergunta_id] = resposta
                        print("✅ Resposta armazenada em memória!")
                            
                    except Exception as e:
                        erro_msg = f"Erro ao consultar ChatGPT: {str(e)}"
                        print(f"\n❌ {erro_msg}\n")
                        respostas_completas[pergunta_id] = erro_msg
                        print("❌ Erro de consulta registrado em memória!")
                            
                except Exception as e:
                    erro_msg = f"Erro ao processar pergunta: {str(e)}"
                    print(f"\n❌ {erro_msg}\n")
                    respostas_completas[pergunta_id] = erro_msg
                    print("❌ Erro de processamento registrado em memória!")
                            
            time.sleep(0.5)
        except Exception as e:
            print(f"\n❌ Erro na thread de processamento: {str(e)}\n")
            time.sleep(0.5)

# Inicia a thread de processamento
thread_perguntas = threading.Thread(target=processar_perguntas, daemon=True)
thread_perguntas.start()

@app.route('/')
def index():
    """Rota principal"""
    limpar_sessao()
    return render_template('index.html')

@app.route('/perguntas')
def perguntas():
    """Rota para exibir e atualizar perguntas"""
    try:
        print(f"\n🔍 Requisição para /perguntas. X-Requested-With: {request.headers.get('X-Requested-With')}\n")
        respostas_sessao = session.get('respostas', [])
        
        # Itera sobre as perguntas na sessão e verifica se já temos a resposta completa
        respostas_para_enviar = []
        atualizou_sessao = False
        # Precisamos de uma cópia para iterar, pois podemos modificar respostas_sessao
        copia_respostas_sessao = list(respostas_sessao)
        
        # Mantemos a ordem original (mais antiga no topo, mais recente no final)
        for p_id, pergunta, resposta_placeholder in copia_respostas_sessao:
            # Corrige a verificação para usar pergunta_id
            if p_id in respostas_completas:
                resposta_real = respostas_completas.pop(p_id) # Usa p_id como chave
                respostas_para_enviar.append({'pergunta': pergunta, 'resposta': resposta_real})
                # Atualiza a sessão para refletir a resposta real
                for i, (current_p_id, current_p, current_r) in enumerate(respostas_sessao):
                    if current_p_id == p_id:
                        respostas_sessao[i] = (current_p_id, current_p, resposta_real)
                        atualizou_sessao = True
                        break
            else:
                respostas_para_enviar.append({'pergunta': pergunta, 'resposta': resposta_placeholder})
        
        if atualizou_sessao:
            session['respostas'] = respostas_sessao
            session.modified = True
            print("✅ Sessão atualizada com respostas completas!")

        # Nao inverte mais aqui, pois o frontend vai adicionar no final e rolar para baixo
        # respostas_para_enviar.reverse() 
        
        # Verifica se a requisição é uma chamada AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            print("✅ Backend detectou AJAX. Enviando JSON...")
            response = jsonify(respostas_para_enviar)
            response.headers['Content-Type'] = 'application/json'
            return response
        
        # Se não for AJAX, renderiza o template completo
        print("🌐 Backend não detectou AJAX. Renderizando HTML...")
        return render_template('perguntas.html', respostas=respostas_para_enviar) # Passa o novo formato
    except Exception as e:
        print(f"\n❌ Erro na rota /perguntas: {str(e)}\n")
        # Em caso de erro em requisição AJAX, retorna JSON de erro
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            print("❌ Erro na rota /perguntas (AJAX). Enviando JSON de erro...")
            return jsonify({'error': str(e)}), 500
        # Em caso de erro em requisição normal, renderiza o template com erro
        print("❌ Erro na rota /perguntas (HTML). Renderizando HTML de erro...")
        return render_template('perguntas.html', error=str(e))

@app.route('/perguntar', methods=['POST'])
def perguntar():
    """Rota para receber novas perguntas"""
    try:
        global agente
        
        if agente is None:
            print("\n❌ Erro: Agente não inicializado\n")
            return jsonify({'error': 'Agente não inicializado'}), 400
            
        pergunta = request.form.get('pergunta')
        if not pergunta:
            print("\n❌ Erro: Pergunta vazia\n")
            return jsonify({'error': 'Pergunta não fornecida'}), 400
            
        # Gera ID único e armazena pergunta
        pergunta_id = str(int(time.time())) # ID único para a pergunta
        respostas = session.get('respostas', [])
        respostas.append((pergunta_id, pergunta, "Aguarde, sua pergunta está sendo analisada...")) # Armazena ID, pergunta e placeholder
        session['respostas'] = respostas
        session.modified = True
        
        # Adiciona à fila
        perguntas_queue.put((pergunta_id, pergunta))
        print(f"\n📨 Pergunta adicionada à fila: {pergunta}\n")
        
        return jsonify({'status': 'success', 'message': 'Pergunta recebida com sucesso'})
    except Exception as e:
        print(f"\n❌ Erro na rota /perguntar: {str(e)}\n")
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Rota para upload de arquivo CSV"""
    global agente
    print("Iniciando upload de arquivo...")
    
    if 'file' not in request.files:
        print("Nenhum arquivo encontrado na requisição")
        return 'Nenhum arquivo selecionado', 400
        
    file = request.files['file']
    if file.filename == '':
        print("Nome do arquivo vazio")
        return 'Nenhum arquivo selecionado', 400
        
    if file and file.filename.endswith('.csv'):
        print(f"Processando arquivo: {file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'prodes_desmatamento.csv')
        file.save(filepath)
        print(f"Arquivo salvo em: {filepath}")
        
        try:
            print("Carregando dados...")
            df = carregar_dados()
            print("Dados carregados com sucesso")
            
            print("Gerando análises...")
            analise_geral(df)
            plotar_evolucao_amazonia_legal(df)
            plotar_estados_mais_afetados(df)
            analise_correlacao(df)
            previsao_futura(df)
            
            print("Inicializando agente...")
            agente = AgenteAnaliseDesmatamento(df)
            analise_agente = agente.analisar_dados()
            print("Análise do agente concluída")
            
            print("Gerando análise detalhada...")
            analise_texto = analise_detalhada(df)
            
            print("Renderizando template...")
            return render_template('resultado.html', 
                                 analise=analise_texto,
                                 analise_agente=analise_agente)
        except Exception as e:
            print(f"Erro durante o processamento: {str(e)}")
            return f'Erro ao processar o arquivo: {str(e)}', 500
            
    print("Arquivo inválido")
    return 'Arquivo inválido. Por favor, envie um arquivo CSV.', 400

@app.route('/imagem/<nome_arquivo>')
def mostrar_imagem(nome_arquivo):
    """Rota para exibir imagens"""
    return send_file(nome_arquivo)

if __name__ == '__main__':
    print("\nSistema de perguntas e respostas iniciado!")
    print("Aguardando perguntas...\n")
    app.run(debug=True) 