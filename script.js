// --- Referensi Elemen ---
const chatContainer = document.getElementById('chat-container');
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// --- Variabel Global ---
const BACKEND_URL = 'http://localhost:5000';
let chatHistory = []; 
let sessionId = null; // Akan diisi saat pesan pertama

// --- Event Listeners ---
sendButton.addEventListener('click', sendMessageFromInput);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessageFromInput();
});
// Bot pasif, tidak ada 'DOMContentLoaded'

// --- FUNGSI: Simpan chat secara otomatis ---
async function autoSaveChat() {
    if (chatHistory.length === 0 || !sessionId) {
        return; // Jangan simpan jika tidak ada chat atau sesi
    }
    
    // Kirim data (HANYA riwayat dan ID sesi)
    const dataToSave = {
        chatHistory: chatHistory,
        sessionId: sessionId
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
// FUNGSI KONVERSI MARKDOWN (Menggunakan Marked.js & DOMPurify)
// Pastikan Anda sudah memuat library ini di index.html
// =================================================================
marked.setOptions({
  breaks: false, // Menggunakan paragraf standar (enter 2x)
  gfm: true      // Mengaktifkan GitHub Flavored Markdown (tabel, coretan, dll.)
});

function convertMarkdownToHTML(text) {
    // 1. Konversi Markdown ke HTML
    let rawHtml = marked.parse(text);
    // 2. Bersihkan HTML dari kode berbahaya (XSS)
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
    // 1. Tampilkan pesan user di UI
    displayMessage(message, 'user');
    // 2. Tambahkan pesan user ke riwayat
    chatHistory.push({
        timestamp: new Date().toISOString(),
        sender: 'User',
        message: message
    });
    // 3. Panggil bot untuk merespons
    await getBotResponse();
}

// Fungsi: Logika inti untuk mendapatkan respons bot
async function getBotResponse() {
    // 1. Tampilkan bubble bot kosong (placeholder)
    const botMessageElement = displayMessage('', 'bot');
    // 2. Tambahkan placeholder bot ke riwayat
    const botMessageObj = {
        timestamp: new Date().toISOString(),
        sender: 'Bot',
        message: '' // Awalnya kosong
    };
    chatHistory.push(botMessageObj); 
    
    let rawBotText = ''; // Untuk mengumpulkan stream

    try {
        // 3. Kirim SELURUH riwayat ke backend
        const response = await fetch(`${BACKEND_URL}/chat`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ history: chatHistory })
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        // 4. Baca stream respons
        while (true) {
            const { done, value } = await reader.read();
            if (done) break; // Stream selesai
            
            const chunk = decoder.decode(value, { stream: true });
            rawBotText += chunk; 
            
            // 5. Update object di riwayat DAN di UI
            botMessageObj.message = rawBotText; 
            botMessageElement.innerHTML = convertMarkdownToHTML(rawBotText); 
            
            // Auto-scroll
            chatBox.scrollTop = chatBox.scrollHeight;
        }

    } catch (error) {
        console.error('Error:', error);
        const errorMsg = 'Maaf, terjadi kesalahan: ' + error.message;
        botMessageElement.innerHTML = errorMsg;
        botMessageElement.style.color = 'red';
        botMessageObj.message = errorMsg; // Simpan error di riwayat
    }
    
    // 6. Simpan seluruh riwayat ke CSV (timpa file lama)
    await autoSaveChat();
}

// Fungsi: Tampilkan Pesan di UI
function displayMessage(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${sender}-message`);

    if (sender === 'user') {
        // Pesan user adalah teks biasa
        messageElement.textContent = message;
    } else {
        // Pesan bot dikonversi dari Markdown
        messageElement.innerHTML = convertMarkdownToHTML(message);
    }
    
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    return messageElement; // Kembalikan elemen untuk diisi oleh stream
}