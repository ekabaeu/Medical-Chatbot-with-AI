const chatContainer = document.getElementById('chat-container');
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// --- Variabel Global ---
const BACKEND_URL = 'http://localhost:5000';
let chatHistory = []; 
let sessionId = null; // Akan diisi saat pesan pertama
let patientData = { name: 'unknown', age: 'unknown' }; // Default

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
        patientData: patientData 
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


// --- Fungsi untuk mengekstrak data dari teks user (LOGIKA ANDA) ---
function extractInitialDataFromMessage(message) {
    // 1. Ambil kata pertama dan bersihkan (hapus koma, dll)
    const firstWord = message.split(' ')[0].replace(/,/g, '').toLowerCase();
    
    // 2. Buat daftar kata sapaan yang akan diabaikan
    const greetings = [
        'halo', 'hai', 'hi', 'selamat', 'pagi', 
        'siang', 'sore', 'malam', 'permisi', 'dok'
    ];
    
    // 3. Logika Asumsi Nama
    // Jika kata pertama BUKAN sapaan, asumsikan itu adalah nama
    if (!greetings.includes(firstWord)) {
        // Ambil kata pertama, bersihkan, dan kapitalisasi
        let assumedName = message.split(' ')[0].replace(/,/g, '');
        patientData.name = assumedName.charAt(0).toUpperCase() + assumedName.slice(1).toLowerCase();
    }
    
    // 4. Logika Ekstraksi Umur
    const ageMatch = message.match(/(\d+)\s*(?:tahun|thn)/i);
    if (ageMatch && ageMatch[1]) {
        patientData.age = ageMatch[1];
    } else {
         const ageMatch2 = message.match(/umur\s+(\d+)/i);
         if (ageMatch2 && ageMatch2[1]) {
             patientData.age = ageMatch2[1];
         }
    }
    
    console.log('Data Pasien yang diekstrak:', patientData);
}


// Fungsi: Kirim pesan dari KOTAK INPUT
async function sendMessageFromInput() {
    const message = userInput.value.trim();
    if (message === '') return;
    
    // Buat sessionId pada pesan PERTAMA
    if (sessionId === null) {
        sessionId = Date.now().toString();
        
        // Panggil fungsi ekstraksi HANYA PADA PESAN PERTAMA
        extractInitialDataFromMessage(message);
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
        botMessageElement.message = errorMsg;
    }
    
    // Simpan ke CSV (dengan data pasien terbaru)
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