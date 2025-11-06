// --- Referensi Elemen ---
const chatContainer = document.getElementById('chat-container');
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// --- Variabel Global ---
const BACKEND_URL = 'http://localhost:5000';
let chatHistory = []; 

// --- Event Listeners ---
sendButton.addEventListener('click', sendMessageFromInput);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessageFromInput();
});


// --- FUNGSI: Simpan chat secara otomatis (DIRINGKAS) ---
async function autoSaveChat() {
    if (chatHistory.length === 0) {
        return; 
    }
    
    // Kita hanya mengirim riwayat chat mentah
    const dataToSave = {
        chatHistory: chatHistory
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
        } else {
            console.log('Chat auto-saved successfully.');
        }
    } catch (error) {
        console.error('Error auto-saving chat:', error);
    }
}


// =================================================================
// FUNGSI KONVERSI MARKDOWN (MODIFIKASI: Sembunyikan JSON)
// =================================================================
marked.setOptions({
  breaks: false, // Menggunakan paragraf standar
  gfm: true 
});

function convertMarkdownToHTML(text) {
    let cleanText = text;

    // --- BARU: Cari dan HAPUS baris JSON dari TAMPILAN ---
    // Ini mencari baris yang dimulai dengan '{"PATIENT_DATA":'
    // dan menghapusnya dari teks sebelum di-render.
    const jsonBlockRegex = /^{\"PATIENT_DATA\":(.*?)}\n?/m;
    
    // Ganti blok JSON dengan string kosong
    cleanText = text.replace(jsonBlockRegex, '');

    // 1. Ubah sisa Markdown menjadi HTML
    let rawHtml = marked.parse(cleanText);
    
    // 2. Bersihkan HTML dari kode berbahaya (XSS)
    let safeHtml = DOMPurify.sanitize(rawHtml);
    
    return safeHtml;
}
// =================================================================


// Fungsi: Kirim pesan dari KOTAK INPUT
async function sendMessageFromInput() {
    const message = userInput.value.trim();
    if (message === '') return;
    
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
            body: JSON.stringify({ history: chatHistory }) // Hanya kirim riwayat
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break; 
            
            const chunk = decoder.decode(value, { stream: true });
            rawBotText += chunk; 
            
            // Simpan teks mentah (DENGAN JSON) ke riwayat
            botMessageObj.message = rawBotText; 
            
            // Tampilkan teks yang sudah dibersihkan (TANPA JSON)
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
    
    await autoSaveChat();
}

// Fungsi: Tampilkan Pesan di UI
function displayMessage(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${sender}-message`);

    if (sender === 'user') {
        messageElement.textContent = message;
    } else {
        // Terapkan fungsi konversi di sini (penting untuk placeholder)
        messageElement.innerHTML = convertMarkdownToHTML(message);
    }
    
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    return messageElement;
}