const chatContainer = document.getElementById('chat-container');
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// --- Variabel Global ---
const BACKEND_URL = 'https://bills-ordinance-stream-pcs.trycloudflare.com';
let chatHistory = []; 
let sessionId = null; // Akan diisi saat pesan pertama
let patientData = { name: 'unknown', age: 'unknown', gender: 'unknown' }; // Default
let isLoading = false; // Track loading state

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


// --- Fungsi untuk mengekstrak data dari teks user (IMPROVED) ---
function extractInitialDataFromMessage(message) {
    const lowerMessage = message.toLowerCase();
    
    // 1. Daftar kata sapaan yang akan diabaikan
    const greetings = [
        'halo', 'hai', 'hi', 'selamat', 'pagi', 
        'siang', 'sore', 'malam', 'permisi', 'dok', 'dokter',
        'assalamualaikum', 'wr', 'wb'
    ];
    
    // 2. Ekstraksi Nama - Improved logic
    // Cari pola: "nama saya [nama]" atau "saya [nama]" atau kata pertama jika bukan sapaan
    const namePatterns = [
        /nama\s+(?:saya|aku|saya)\s+([a-z]+(?:\s+[a-z]+)?)/i,
        /saya\s+([a-z]+(?:\s+[a-z]+)?)/i,
        /perkenalkan\s+(?:nama\s+)?saya\s+([a-z]+(?:\s+[a-z]+)?)/i
    ];
    
    let nameFound = false;
    for (const pattern of namePatterns) {
        const match = message.match(pattern);
        if (match && match[1]) {
            const extractedName = match[1].trim();
            // Capitalize first letter of each word
            patientData.name = extractedName.split(' ').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
            ).join(' ');
            nameFound = true;
            break;
        }
    }
    
    // Fallback: ambil kata pertama jika bukan sapaan
    if (!nameFound) {
        const firstWord = message.split(/\s+/)[0].replace(/[,\.!?]/g, '').toLowerCase();
        if (firstWord && !greetings.includes(firstWord) && firstWord.length > 1) {
            patientData.name = firstWord.charAt(0).toUpperCase() + firstWord.slice(1).toLowerCase();
        }
    }
    
    // 3. Ekstraksi Umur - Improved patterns
    const agePatterns = [
        /(\d+)\s*(?:tahun|thn|years?|yo)/i,
        /umur\s+(?:saya\s+)?(?:adalah\s+)?(\d+)/i,
        /berusia\s+(\d+)/i,
        /usia\s+(?:saya\s+)?(?:adalah\s+)?(\d+)/i,
        /(\d+)\s*(?:th|tahun)/i
    ];
    
    for (const pattern of agePatterns) {
        const match = message.match(pattern);
        if (match && match[1]) {
            const age = parseInt(match[1], 10);
            if (age > 0 && age < 150) { // Validasi umur masuk akal
                patientData.age = age.toString();
                break;
            }
        }
    }
    
    // 4. Ekstraksi Gender - New feature
    const genderPatterns = {
        'male': [/laki-laki|laki|l|pria|cowok|male|man/i],
        'female': [/perempuan|wanita|cewek|cewe|p|female|woman/i]
    };
    
    for (const [gender, patterns] of Object.entries(genderPatterns)) {
        for (const pattern of patterns) {
            if (pattern.test(message)) {
                patientData.gender = gender === 'male' ? 'Laki-laki' : 'Perempuan';
                break;
            }
        }
        if (patientData.gender !== 'unknown') break;
    }
    
    console.log('Data Pasien yang diekstrak:', patientData);
}


// Fungsi: Generate UUID untuk session ID
function generateSessionId() {
    // Use crypto.randomUUID() if available (modern browsers)
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID();
    }
    // Fallback for older browsers
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Fungsi: Kirim pesan dari KOTAK INPUT
async function sendMessageFromInput() {
    const message = userInput.value.trim();
    if (message === '' || isLoading) return; // Prevent sending while loading
    
    // Buat sessionId pada pesan PERTAMA menggunakan UUID
    if (sessionId === null) {
        sessionId = generateSessionId();
        
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

// Fungsi: Tampilkan loading indicator
function showLoadingIndicator() {
    const loadingElement = document.createElement('div');
    loadingElement.id = 'typing-indicator';
    loadingElement.classList.add('message', 'bot-message', 'typing-indicator');
    loadingElement.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    chatBox.appendChild(loadingElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    return loadingElement;
}

// Fungsi: Hapus loading indicator
function removeLoadingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Fungsi: Logika inti untuk mendapatkan respons bot
async function getBotResponse() {
    isLoading = true;
    sendButton.disabled = true; // Disable send button while loading
    
    // Show loading indicator
    const loadingIndicator = showLoadingIndicator();
    
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

        // Remove loading indicator once we start receiving data
        removeLoadingIndicator();

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
        removeLoadingIndicator(); // Remove loading indicator on error
        const errorMsg = 'Maaf, terjadi kesalahan: ' + error.message;
        botMessageElement.innerHTML = errorMsg;
        botMessageElement.style.color = 'red';
        botMessageObj.message = errorMsg;
    } finally {
        isLoading = false;
        sendButton.disabled = false; // Re-enable send button
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