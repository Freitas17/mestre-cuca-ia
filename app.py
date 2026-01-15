import os
# Adicione 'render_template' na importação
from flask import Flask, request, jsonify, render_template 
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
chave_api = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=chave_api)
# Use o modelo que funcionou no seu teste (gemini-pro ou gemini-1.5-flash)
model = genai.GenerativeModel('gemini-1.5-flash') 

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# --- NOVO: Rota para servir o Site ---
@app.route('/')
def home():
    return render_template('index.html')

# --- NOVO: Rota para servir arquivos do PWA (manifest, sw.js) ---
# O navegador espera que esses arquivos estejam na raiz, mas movemos para static.
# Essa "gambiarra técnica" resolve isso:
from flask import send_from_directory

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

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