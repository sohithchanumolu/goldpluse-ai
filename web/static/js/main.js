document.addEventListener('DOMContentLoaded', () => {
    // Mobile Navbar Toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            
            const spans = hamburger.querySelectorAll('span');
            if (navLinks.classList.contains('active')) {
                spans[0].style.transform = 'rotate(45deg) translate(5px, 6px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(5px, -6px)';
            } else {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });
    }

    // Add fade-in animation to main sections
    const fadeElements = document.querySelectorAll('.fade-wrapper');
    fadeElements.forEach(el => {
        el.classList.add('fade-in');
    });

    // Setup Chat Form
    const chatForm = document.getElementById('streamAskForm');
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
        
        // Stop Button listener
        document.getElementById('stopStreamBtn').addEventListener('click', () => {
            if (currentAbortController) {
                currentAbortController.abort();
            }
        });

        // Initialize marked with highlight.js
        if (typeof marked !== 'undefined' && typeof hljs !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                    return hljs.highlight(code, { language }).value;
                },
                langPrefix: 'hljs language-'
            });
        }
    }
});

// Helper for UI loading states
function showLoading(buttonId, loadingText = 'Loading...') {
    const btn = document.getElementById(buttonId);
    if (btn) {
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = `<span class="spinner"></span> ${loadingText}`;
        btn.disabled = true;
        btn.style.opacity = '0.8';
        btn.style.pointerEvents = 'none';
    }
}

function hideLoading(buttonId) {
    const btn = document.getElementById(buttonId);
    if (btn && btn.dataset.originalText) {
        btn.innerHTML = btn.dataset.originalText;
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.style.pointerEvents = 'auto';
    }
}

// --- Chat UI Variables ---
let currentAbortController = null;

function submitSuggested(text) {
    const input = document.getElementById('streamQuestionInput');
    if (input) {
        input.value = text;
        handleChatSubmit(new Event('submit'));
    }
}

async function handleChatSubmit(e) {
    e.preventDefault();
    
    const inputField = document.getElementById('streamQuestionInput');
    const question = inputField.value.trim();
    if (!question) return;
    
    inputField.value = '';
    
    const emptyState = document.getElementById('chatEmptyState');
    if (emptyState) emptyState.style.display = 'none';
    
    // Append User Message
    appendMessage(question, 'user-message');
    
    // Create AI Message Container with Typing Indicator
    const aiMessageContainer = createAiMessageContainer();
    const contentDiv = aiMessageContainer.querySelector('.message-content');
    
    // Update UI controls
    document.getElementById('sendBtn').classList.add('hidden');
    document.getElementById('stopStreamBtn').classList.remove('hidden');
    
    currentAbortController = new AbortController();
    
    try {
        const response = await fetch('/ask/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question }),
            signal: currentAbortController.signal
        });
        
        if (!response.ok) throw new Error('Network response was not ok');
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let done = false;
        let aiFullText = "";
        
        // Remove typing indicator on first chunk
        let firstChunk = true;
        
        while (!done) {
            const { value, done: readerDone } = await reader.read();
            done = readerDone;
            
            if (value) {
                if (firstChunk) {
                    contentDiv.innerHTML = '';
                    contentDiv.classList.add('markdown-body');
                    firstChunk = false;
                }
                
                const chunkText = decoder.decode(value, { stream: !done });
                aiFullText += chunkText;
                
                // Parse markdown and sanitize
                const parsedHtml = DOMPurify.sanitize(marked.parse(aiFullText));
                contentDiv.innerHTML = parsedHtml;
                
                scrollToBottom();
            }
        }
        
    } catch (err) {
        if (err.name === 'AbortError') {
            console.log('Stream stopped by user');
        } else {
            console.error('Streaming Error:', err);
            contentDiv.innerHTML = "<em>An error occurred while generating the response. Please try again.</em>";
        }
    } finally {
        currentAbortController = null;
        document.getElementById('sendBtn').classList.remove('hidden');
        document.getElementById('stopStreamBtn').classList.add('hidden');
        scrollToBottom();
    }
}

function appendMessage(text, typeClass) {
    const historyContainer = document.getElementById('chatHistory');
    
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${typeClass}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    msgDiv.appendChild(contentDiv);
    historyContainer.appendChild(msgDiv);
    
    scrollToBottom();
}

function createAiMessageContainer() {
    const historyContainer = document.getElementById('chatHistory');
    
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Typing indicator
    contentDiv.innerHTML = '<span class="typing-indicator">GoldPulse AI is analyzing market data... ●●○</span>';
    
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'message-actions';
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'action-btn copy-btn';
    copyBtn.title = 'Copy to clipboard';
    copyBtn.innerText = '📋';
    copyBtn.onclick = () => {
        navigator.clipboard.writeText(contentDiv.innerText);
        copyBtn.innerText = '✅';
        setTimeout(() => copyBtn.innerText = '📋', 2000);
    };
    
    actionsDiv.appendChild(copyBtn);
    msgDiv.appendChild(contentDiv);
    msgDiv.appendChild(actionsDiv);
    
    historyContainer.appendChild(msgDiv);
    scrollToBottom();
    
    return msgDiv;
}

function scrollToBottom() {
    const historyContainer = document.getElementById('chatHistory');
    if (historyContainer) {
        historyContainer.scrollTop = historyContainer.scrollHeight;
    }
}
