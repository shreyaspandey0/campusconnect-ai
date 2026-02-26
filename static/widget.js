(function () {
    const API_URL = '/chat';
    const THEME_COLOR = '#004E9E';

    // --- Dependency Check ---
    // Ensure Font Awesome is loaded for icons
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
        document.head.appendChild(link);
    }

    // --- Styles ---
    const style = document.createElement('style');
    style.innerHTML = `
        #dgi-chat-widget-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
        }

        @keyframes fade-in {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Launcher Button */
        #dgi-chat-launcher {
            width: 60px;
            height: 60px;
            background-color: ${THEME_COLOR};
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.3s ease;
        }

        #dgi-chat-launcher:hover {
            transform: scale(1.1);
        }

        #dgi-chat-launcher i {
            color: white;
            font-size: 24px;
        }

        /* Chat Window */
        #dgi-chat-window {
            position: absolute;
            bottom: 80px;
            right: 0;
            width: 350px;
            height: 500px;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
            display: none;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid #e0e0e0;
        }

        #dgi-chat-header {
            background: linear-gradient(135deg, #004E9E, #003a75);
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 500;
        }

        #dgi-chat-header .close-btn {
            cursor: pointer;
            font-size: 18px;
        }

        /* Messages Area */
        #dgi-chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            background-color: #f9f9f9;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .message {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 10px;
            font-size: 14px;
            line-height: 1.6;
            overflow-wrap: anywhere;
            animation: fade-in 0.4s ease forwards;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        .message.user {
            align-self: flex-end;
            background-color: ${THEME_COLOR};
            color: white;
            border-bottom-right-radius: 2px;
        }

        .message.bot {
            align-self: flex-start;
            background-color: #e0e0e0;
            color: #333;
            border-bottom-left-radius: 2px;
        }
        
        .message.bot a {
            color: #004E9E;
            text-decoration: underline;
        }

        /* Input Area */
        #dgi-chat-input-area {
            padding: 15px;
            border-top: 1px solid #eee;
            background-color: white;
            display: flex;
            gap: 10px;
        }

        #dgi-chat-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
            font-family: inherit;
        }

        #dgi-chat-input:focus {
            border-color: ${THEME_COLOR};
        }

        #dgi-chat-send {
            background-color: ${THEME_COLOR};
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s;
        }

        #dgi-chat-send:hover {
            background-color: #003a75;
        }

        /* Typing Indicator */
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 5px 10px;
            background-color: #e0e0e0;
            border-radius: 10px;
            align-self: flex-start;
            width: fit-content;
        }
        
        .typing-dot {
            width: 6px;
            height: 6px;
            background-color: #666;
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out both;
        }
        
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
    `;
    document.head.appendChild(style);

    // --- DOM Elements ---
    const container = document.createElement('div');
    container.id = 'dgi-chat-widget-container';
    container.innerHTML = `
        <div id="dgi-chat-window">
            <div id="dgi-chat-header">
                <span>DGI Assistant</span>
                <span class="close-btn">&times;</span>
            </div>
            <div id="dgi-chat-messages">
                <div class="message bot">Hello! How can I help you with Dronacharya Group of Institutions today?</div>
            </div>
            <div id="dgi-chat-input-area">
                <input type="text" id="dgi-chat-input" placeholder="Type a message...">
                <button id="dgi-chat-send"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
        <div id="dgi-chat-launcher">
            <i class="fas fa-comment-dots"></i>
        </div>
    `;
    document.body.appendChild(container);

    const launcher = document.getElementById('dgi-chat-launcher');
    const window = document.getElementById('dgi-chat-window');
    const closeBtn = document.querySelector('#dgi-chat-header .close-btn');
    const input = document.getElementById('dgi-chat-input');
    const sendBtn = document.getElementById('dgi-chat-send');
    const messagesContainer = document.getElementById('dgi-chat-messages');

    // --- State ---
    let conversationHistory = [];

    // --- Functions ---

    function toggleChat() {
        if (window.style.display === 'none' || window.style.display === '') {
            window.style.display = 'flex';
            input.focus();
        } else {
            window.style.display = 'none';
        }
    }

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        // Add User Message
        addMessage(text, 'user');
        input.value = '';
        conversationHistory.push({ role: 'user', content: text });

        // Show Loading
        const loadingId = addLoading();

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    history: conversationHistory
                })
            });

            const data = await response.json();
            removeLoading(loadingId);

            // Add Bot Message
            addMessage(data.response, 'bot');
            conversationHistory.push({ role: 'model', content: data.response });

        } catch (error) {
            removeLoading(loadingId);
            addMessage("Sorry, I'm having trouble connecting to the server.", 'bot');
            console.error('Chat Error:', error);
        }
    }

    function formatMessage(text) {
        // Basic Markdown & Security Formatting
        let safeText = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        safeText = safeText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Bold
        safeText = safeText.replace(/(^|<br>)\* /g, '$1• '); // Bullets
        safeText = safeText.replace(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/g, '<a href="mailto:$1">$1</a>'); // Emails
        safeText = safeText.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>'); // Links
        safeText = safeText.replace(/(?<!href=")(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank">$1</a>'); // Auto-link URLs
        safeText = safeText.replace(/\n/g, '<br>'); // Newlines
        return safeText;
    }

    function typeWriter(element, html, speed = 2) {
        // Typewriter effect that respects HTML tags
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const nodes = Array.from(tempDiv.childNodes);
        element.innerHTML = '';

        let i = 0;
        function typeNode() {
            if (i >= nodes.length) return;

            const node = nodes[i];
            const clone = node.cloneNode(true);

            if (node.nodeType === Node.TEXT_NODE) {
                element.appendChild(clone);
                const text = clone.textContent;
                clone.textContent = '';
                let charIndex = 0;

                function typeChar() {
                    if (charIndex < text.length) {
                        clone.textContent += text.charAt(charIndex);
                        charIndex++;
                        setTimeout(typeChar, speed);
                    } else {
                        i++;
                        typeNode();
                    }
                }
                typeChar();
            } else {
                element.appendChild(clone);
                i++;
                setTimeout(typeNode, speed);
            }
        }
        typeNode();
    }

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        messagesContainer.appendChild(div);

        if (sender === 'bot') {
            const htmlContent = formatMessage(text);
            scrollToBottom();
            // Typewriter effect handles the text reveal
            typeWriter(div, htmlContent);
        } else {
            div.textContent = text;
            scrollToBottom();
        }
    }

    function addLoading() {
        const id = 'loading-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'typing-indicator';
        div.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        messagesContainer.appendChild(div);
        scrollToBottom();
        return id;
    }

    function removeLoading(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // --- Event Listeners ---
    launcher.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

})();
