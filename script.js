const chatContainer = document.getElementById('chat-container');
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// --- Variabel Global ---
// Use the same origin for backend when deployed to Vercel
const BACKEND_URL = window.location.origin;
let chatHistory = [];
let sessionId = null; // Akan diisi saat pesan pertama
let patientData = { name: 'unknown', age: 'unknown' }; // Menyimpan data pasien

// --- Event Listeners ---
sendButton.addEventListener('click', sendMessageFromInput); 
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessageFromInput();
});

// --- FUNGSI: Simpan chat secara otomatis ---
async function autoSaveChat() {
    if (chatHistory.length === 0 || !sessionId) {
        return;
    }
    
    // Kirim data pasien yang sudah diekstrak
    const dataToSave = {
        chatHistory: chatHistory,
        sessionId: sessionId,
        patientData: patientData // Sertakan data pasien
    };
    
    const SAVE_URL = `${BACKEND_URL}/save-chat`;

    try {
        const response = await fetch(SAVE_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dataToSave)
        });
        if (!response.ok) {
            console.error('Auto-save failed:', await response.json());
        }
    } catch (error) {
        console.error('Error auto-saving chat:', error);
    }
}


// =================================================================
// FUNGSI KONVERSI MARKDOWN (Menggunakan Marked.js & DOMPurify)
// =================================================================
marked.setOptions({
  breaks: false, 
  gfm: true      
});

function convertMarkdownToHTML(text) {
    let rawHtml = marked.parse(text);
    let safeHtml = DOMPurify.sanitize(rawHtml);
    return safeHtml;
}
// =================================================================

// Fungsi: Kirim pesan dari KOTAK INPUT
async function sendMessageFromInput() {
    const message = userInput.value.trim();
    if (message === '') return;
    
    // Buat sessionId pada pesan PERTAMA
    if (sessionId === null) {
        sessionId = Date.now().toString();
    }
    
    userInput.value = ''; // Kosongkan input SEKARANG
    await processUserMessage(message); 
}

// Fungsi: Prosesor pesan utama
async function processUserMessage(message) {
    displayMessage(message, 'user');
    chatHistory.push({
        timestamp: new Date().toISOString(),
        sender: 'User',
        message: message
    });
    await getBotResponse();
}

// Fungsi: Logika inti untuk mendapatkan respons bot
async function getBotResponse() {
    const botMessageElement = displayMessage('', 'bot');
    const botMessageObj = {
        timestamp: new Date().toISOString(),
        sender: 'Bot',
        message: ''
    };
    chatHistory.push(botMessageObj); 
    
    let rawBotText = ''; 

    try {
        const response = await fetch(`${BACKEND_URL}/chat`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ history: chatHistory })
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        // --- EKSTRAKSI DATA PASIEN DARI HEADER ---
        const patientHeader = response.headers.get('X-Patient-Data');
        if (patientHeader) {
            try {
                const parsedData = JSON.parse(patientHeader);
                // Perbarui data pasien jika tersedia
                if (parsedData.nama && parsedData.nama !== 'unknown') {
                    patientData.name = parsedData.nama;
                }
                if (parsedData.umur && parsedData.umur !== 'unknown') {
                    patientData.age = parsedData.umur;
                }
                console.log('Patient data updated:', patientData);
            } catch (e) {
                console.error('Failed to parse patient data from header:', e);
            }
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break; 
            
            const chunk = decoder.decode(value, { stream: true });
            rawBotText += chunk; 
            
            botMessageObj.message = rawBotText; 
            botMessageElement.innerHTML = convertMarkdownToHTML(rawBotText); 
            chatBox.scrollTop = chatBox.scrollHeight;
        }

    } catch (error) {
        console.error('Error:', error);
        const errorMsg = 'Maaf, terjadi kesalahan: ' + error.message;
        botMessageElement.innerHTML = errorMsg;
        botMessageElement.style.color = 'red';
        botMessageObj.message = errorMsg;
    }
    
    // Simpan chat dengan data pasien terbaru
    await autoSaveChat();
}

// Fungsi: Tampilkan Pesan di UI
function displayMessage(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${sender}-message`);

    if (sender === 'user') {
        messageElement.textContent = message;
    } else {
        messageElement.innerHTML = convertMarkdownToHTML(message);
    }
    
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    return messageElement;
}