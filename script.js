document.addEventListener('DOMContentLoaded', () => {
    // 1. Seleção dos Elementos do DOM
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const btnEnviar = document.getElementById('btn-enviar');
    const btnLimpar = document.querySelector('.btn-reset');

    // 2. Configuração dos Event Listeners (Ações)
    
    // Enviar com tecla ENTER
    if (userInput) {
        userInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') enviarMensagem();
        });
    }

    // Enviar com clique no botão
    if (btnEnviar) {
        btnEnviar.addEventListener('click', enviarMensagem);
    }

    // Botão de Limpar/Reiniciar
    if (btnLimpar) {
        btnLimpar.addEventListener('click', limparChat);
    }

    // 3. Funções da Lógica

    async function enviarMensagem() {
        const texto = userInput.value;
        if (!texto) return;

        // Adiciona mensagem do usuário na tela
        addBubble(texto, 'user');
        userInput.value = ''; // Limpa input
        userInput.focus(); // Devolve o foco para digitar mais

        // Mostra indicador de "Digitando..."
        const loadingId = addLoading();

        try {
            // Chama o Backend Python
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensagem: texto })
            });
            const data = await response.json();

            // Remove loading e mostra resposta
            removeLoading(loadingId);
            
            // Formata a resposta (quebra linhas e negrito básico)
            let respostaFormatada = data.resposta
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Negrito do Markdown
                .replace(/\n/g, '<br>'); // Quebra de linha

            addBubble(respostaFormatada, 'bot');

        } catch (error) {
            console.error(error);
            removeLoading(loadingId);
            addBubble("Tive um problema na cozinha (Erro de conexão). O servidor está rodando?", 'bot');
        }
    }

    function addBubble(html, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        
        const bubble = document.createElement('div');
        bubble.classList.add('bubble');
        bubble.innerHTML = html;
        
        msgDiv.appendChild(bubble);
        chatWindow.appendChild(msgDiv);
        
        // Rola para baixo suavemente
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function addLoading() {
        const id = 'loading-' + Date.now();
        const html = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', 'bot');
        msgDiv.id = id;
        msgDiv.innerHTML = `<div class="bubble">${html}</div>`;
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return id;
    }

    function removeLoading(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    async function limparChat() {
        // Limpa visualmente
        chatWindow.innerHTML = ''; 
        
        try {
            // Avisa o backend para esquecer o histórico
            await fetch('http://127.0.0.1:5000/limpar', { method: 'POST' });
            
            // Mensagem de boas-vindas novamente
            addBubble("Memória limpa! O que vamos cozinhar agora? 👨‍🍳", 'bot');
        } catch (error) {
            console.error("Erro ao limpar chat:", error);
        }
    }
});