import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { Configuration, OpenAIApi } from 'openai';
import { Request, Response } from 'express';

dotenv.config();

const app = express();
const port = process.env.PORT || 5000;

// Configuração do OpenAI
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

// Middleware
app.use(cors());
app.use(express.json());

// Armazenamento em memória para as perguntas e respostas
interface ChatMessage {
  id: string;
  pergunta: string;
  resposta: string;
  timestamp: number;
}

const chatHistory: ChatMessage[] = [];

// Rota para obter o histórico de chat
app.get('/api/chat', (req: Request, res: Response) => {
  res.json(chatHistory.sort((a, b) => b.timestamp - a.timestamp));
});

// Rota para enviar uma nova pergunta
app.post('/api/chat', async (req: Request, res: Response) => {
  try {
    const { pergunta } = req.body;
    
    if (!pergunta) {
      return res.status(400).json({ error: 'Pergunta não fornecida' });
    }

    // Adiciona a pergunta ao histórico com resposta pendente
    const messageId = Date.now().toString();
    const newMessage: ChatMessage = {
      id: messageId,
      pergunta,
      resposta: 'Aguarde, sua pergunta está sendo analisada...',
      timestamp: Date.now()
    };
    
    chatHistory.push(newMessage);
    
    // Responde imediatamente com o ID da mensagem
    res.json({ id: messageId });

    try {
      // Faz a chamada para a API do ChatGPT
      const completion = await openai.createChatCompletion({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "system",
            content: "Você é um especialista em análise de desmatamento da Amazônia. Suas respostas devem ser claras e objetivas."
          },
          {
            role: "user",
            content: pergunta
          }
        ],
        temperature: 0.7,
        max_tokens: 1000
      });

      const resposta = completion.data.choices[0]?.message?.content || 'Desculpe, não foi possível obter uma resposta.';

      // Atualiza a resposta no histórico
      const messageIndex = chatHistory.findIndex(msg => msg.id === messageId);
      if (messageIndex !== -1) {
        chatHistory[messageIndex].resposta = resposta;
      }
    } catch (error) {
      console.error('Erro ao consultar ChatGPT:', error);
      // Atualiza a mensagem com o erro
      const messageIndex = chatHistory.findIndex(msg => msg.id === messageId);
      if (messageIndex !== -1) {
        chatHistory[messageIndex].resposta = 'Desculpe, ocorreu um erro ao processar sua pergunta.';
      }
    }
  } catch (error) {
    console.error('Erro ao processar requisição:', error);
    res.status(500).json({ error: 'Erro interno do servidor' });
  }
});

app.listen(port, () => {
  console.log(`Servidor rodando na porta ${port}`);
}); 