import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
chave_api = os.getenv("GEMINI_API_KEY")

# Configura IA
genai.configure(api_key=chave_api)
# Use o modelo que funcionou no seu teste local
model = genai.GenerativeModel('gemini-2.5-flash') 

# Configura o Flask com as pastas corretas
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# --- INÍCIO DO CHAT (Lógica da IA) ---
chat_session = model.start_chat(history=[
    {
        "role": "user",
        "parts": ["Você é o 'Mestre Cuca IA', um chef divertido. Ajude com receitas. Seja breve."]
    },
    {
        "role": "model",
        "parts": ["Entendido! Sou o Mestre Cuca IA. 👨‍🍳 O que vamos cozinhar hoje?"]
    }
])

# -------------------------------------------------------------------------
# ⚠️ ATENÇÃO: AS ROTAS DEVEM FICAR AQUI, SEM RECUO (INDENTAÇÃO)
# -------------------------------------------------------------------------

# 1. Rota da Página Inicial (Obrigatória para o erro 404 sumir)
@app.route('/')
def home():
    return render_template('index.html')

# 2. Rotas para o PWA funcionar (Manifest e Service Worker)
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

# 3. Rota do Chat (Backend)
@app.route('/chat', methods=['POST'])
def conversar():
    dados = request.json
    mensagem_usuario = dados.get('mensagem', '')
    if not mensagem_usuario:
        return jsonify({"erro": "Fale algo!"}), 400
    try:
        response = chat_session.send_message(mensagem_usuario)
        return jsonify({"resposta": response.text})
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"resposta": "Erro na cozinha!"}), 500

@app.route('/limpar', methods=['POST'])
def limpar_chat():
    global chat_session
    chat_session = model.start_chat(history=[])
    return jsonify({"status": "Memória limpa!"})


# --- ROTA ESPIÃ (Para descobrir o nome do modelo) ---
@app.route('/modelos', methods=['GET'])
def listar_modelos():
    try:
        lista_modelos = []
        for m in genai.list_models():
            # Filtra apenas modelos que geram texto
            if 'generateContent' in m.supported_generation_methods:
                lista_modelos.append(m.name)
        return jsonify({"modelos_disponiveis": lista_modelos})
    except Exception as e:
        return jsonify({"erro": str(e)})
# -------------------------------------------------------------------------

# O bloco abaixo só roda no seu PC local. O Render ignora isso.
if __name__ == '__main__':
    app.run(debug=True, port=5000)