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
let sessionId = ''; // --- Variabel untuk ID Sesi ---

// --- Event Listeners ---
sendButton.addEventListener('click', sendMessageFromInput);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessageFromInput();
});

// Event listener untuk tombol "Mulai Konsultasi"
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
    
    // Buat sessionId unik saat chat dimulai
    sessionId = Date.now().toString(); 
    
    patientModal.style.display = 'none';
    chatContainer.style.display = 'flex';
    await processUserMessage(complaint);
});


// =================================================================
// INI FUNGSI YANG HILANG/SALAH (PASTIKAN INI ADA)
// =================================================================
async function autoSaveChat() {
    // Cek jika ada data untuk disimpan
    if (chatHistory.length === 0 || !sessionId) {
        return; // Jangan lakukan apa-apa jika tidak ada data
    }

    // Siapkan data untuk dikirim (JSON)
    const dataToSave = {
        patientData: patientData,
        chatHistory: chatHistory,
        sessionId: sessionId // --- Kirim sessionId
    };
    
    const SAVE_URL = `${BACKEND_URL}/save-chat`; 

    try {
        // Kirim data ke backend menggunakan fetch
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


// Fungsi: Konversi Markdown ke HTML Aman
function convertMarkdownToHTML(text) {
    let safeText = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    let html = safeText.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/\n/g, '<br>');
    return html;
}

// Fungsi: Kirim pesan dari KOTAK INPUT
async function sendMessageFromInput() {
    const message = userInput.value.trim();
    if (message === '') return;

    userInput.value = ''; 
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
    // Tunggu bot merespons
    await getBotResponse(message);
}

// Fungsi: Logika inti untuk mendapatkan respons bot
async function getBotResponse(message) {
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
            body: JSON.stringify({ message: message })
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
        botMessageObj.message = errorMsg; 
    }
    
    // =================================================================
    // INI ADALAH BARIS 114 (ATAU SEKITARNYA) YANG MENYEBABKAN ERROR
    // INI MEMANGGIL FUNGSI DI ATAS
    // =================================================================
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