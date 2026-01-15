import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
chave_api = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=chave_api)
# Use o modelo que funcionou no seu teste (gemini-pro ou gemini-1.5-flash)
model = genai.GenerativeModel('gemini-1.5-flash') 

app = Flask(__name__)
CORS(app)

# --- Configuração do Chat ---
# Iniciamos o chat com a personalidade definida
chat_session = model.start_chat(history=[
    {
        "role": "user",
        "parts": ["Você é o 'Mestre Cuca IA', um chef divertido e experiente. Ajudar com receitas e dúvidas culinárias. Seja breve e use emojis."]
    },
    {
        "role": "model",
        "parts": ["Entendido! Sou o Mestre Cuca IA. 👨‍🍳 O que vamos cozinhar hoje?"]
    }
])

@app.route('/chat', methods=['POST'])
def conversar():
    dados = request.json
    mensagem_usuario = dados.get('mensagem', '')

    if not mensagem_usuario:
        return jsonify({"erro": "Fale algo!"}), 400

    try:
        # Envia a mensagem para o chat (ele lembra do histórico automaticamente)
        response = chat_session.send_message(mensagem_usuario)
        return jsonify({"resposta": response.text})

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"resposta": "Opa, queimei a panela! Tente de novo."}), 500

@app.route('/limpar', methods=['POST'])
def limpar_chat():
    # Rota opcional para reiniciar a memória do chef
    global chat_session
    chat_session = model.start_chat(history=[])
    return jsonify({"status": "Memória limpa!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)  