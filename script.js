// --- Referensi Elemen ---
const chatContainer = document.getElementById('chat-container');
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// --- Referensi Modal ---
const patientModal = document.getElementById('patient-modal');
const startChatButton = document.getElementById('start-chat-button');
const patientNameInput = document.getElementById('patient-name');
const patientAgeInput = document.getElementById('patient-age');
const patientGenderInput = document.getElementById('patient-gender');
const patientComplaintInput = document.getElementById('patient-complaint');

// --- Variabel Global ---
const BACKEND_URL = 'http://localhost:5000';
let patientData = {};
let chatHistory = [];
let sessionId = ''; 

// --- Event Listeners ---
sendButton.addEventListener('click', sendMessageFromInput);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessageFromInput();
});

startChatButton.addEventListener('click', async () => {
    const name = patientNameInput.value.trim();
    const age = patientAgeInput.value.trim();
    const gender = patientGenderInput.value;
    const complaint = patientComplaintInput.value.trim();

    if (!name || !age || !gender || !complaint) {
        alert('Harap isi semua data sebelum memulai.');
        return;
    }

    patientData = { name, age, gender, complaint };
    sessionId = Date.now().toString(); 
    
    patientModal.style.display = 'none';
    chatContainer.style.display = 'flex';
    
    await processUserMessage(complaint);
});


// --- FUNGSI: Simpan chat secara otomatis ---
async function autoSaveChat() {
    if (chatHistory.length === 0 || !sessionId) {
        return;
    }
    const dataToSave = {
        patientData: patientData,
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
// FUNGSI KONVERSI MARKDOWN YANG BARU (LEBIH BAIK)
// =================================================================

// Konfigurasi Marked.js agar:
// 1. Mengubah \n menjadi <br> (seperti fungsi lama Anda)
// 2. Menggunakan standar Markdown yang modern
marked.setOptions({
  breaks: false,
  gfm: true 
});

function convertMarkdownToHTML(text) {
    // 1. Ubah Markdown (termasuk *, **, \n) menjadi HTML
    // Gunakan opsi 'breaks: true' agar \n diubah jadi <br>
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
            
            // Gunakan fungsi konverter baru di setiap chunk
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
        // Pesan pengguna tidak perlu konversi, cukup teks
        messageElement.textContent = message;
    } else {
        // Pesan bot dikonversi menggunakan fungsi baru
        messageElement.innerHTML = convertMarkdownToHTML(message);
    }
    
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    return messageElement;
}