# **Quick-Deploy Flask \+ JS menggunakan Cloudflare Quick Tunnels**

Panduan ini menunjukkan cara menjalankan demo aplikasi full-stack (Flask backend \+ JS/HTML frontend) secara publik menggunakan Cloudflare Quick Tunnels (.trycloudflare.com).

Ini adalah cara cepat untuk melakukan tes, tetapi **bukan** untuk hosting permanen.

🚨 **PERINGATAN PENTING:**

* Ini hanya untuk **tes dan demo**.  
* URL .trycloudflare.com yang Anda dapatkan bersifat **SEMENTARA**.  
* Jika Anda menutup terminal atau me-restart server, URL akan **mati** dan Anda akan mendapatkan URL **baru** saat menjalankannya lagi.  
* Anda harus menjalankan **4 terminal** secara bersamaan agar ini berfungsi.

## **Prasyarat**

* **cloudflared:** Pastikan cloudflared sudah terinstal di sistem Anda.  
* **Python 3:** Dibutuhkan untuk menjalankan server Flask dan server file sederhana.  
* **Folder Proyek:**  
  * /folder-backend/ (berisi app.py)  
  * /folder-frontend/ (berisi index.html, script.js, style.css)

## **Langkah-langkah (Membutuhkan 4 Terminal)**

### **1\. Backend: Jalankan Server Flask (Terminal 1\)**

Pastikan backend Flask Anda menggunakan **CORS** agar frontend dapat mengaksesnya. Jika belum, instal flask-cors.

pip install Flask flask-cors

Buat file app.py Anda seperti ini:

\# Di dalam: /folder-backend/app.py

from flask import Flask, jsonify  
from flask\_cors import CORS \# 1\. Impor CORS

app \= Flask(\_\_name\_\_)  
CORS(app) \# 2\. Tambahkan ini untuk mengizinkan SEMUA origin

@app.route('/api/generate') \# Ganti dengan rute Anda  
def get\_data():  
    \# ...logika Anda memanggil Ollama...  
    return jsonify({"message": "Respons dari backend"})

if \_\_name\_\_ \== '\_\_main\_\_':  
    app.run(port=5000) \# 3\. Jalankan di port 5000

**Jalankan server Flask:**

\# Buka Terminal 1  
cd /path/ke/folder-backend  
python app.py

### **2\. Backend: Jalankan Tunnel (Terminal 2\)**

Ini akan membuat URL publik untuk backend Flask Anda.

\# Buka Terminal 2  
cloudflared tunnel \--url localhost:5000

Terminal akan menampilkan URL. **Salin URL ini**.

\+-----------------------------------------------------------+  
|  Your quick Tunnel is following this URL:                 |  
|  \[https://backend-url-anda.trycloudflare.com\](https://backend-url-anda.trycloudflare.com)               |  
\+-----------------------------------------------------------+

### **3\. Frontend: Edit Kode & Jalankan Server (Terminal 3\)**

**Bagian A: Edit script.js**

Tempelkan URL backend dari Langkah 2 ke file JavaScript frontend Anda.

// Di dalam: /folder-frontend/script.js

const BACKEND\_URL \= '\[https://backend-url-anda.trycloudflare.com\](https://backend-url-anda.trycloudflare.com)';

// ... sisa kode fetch Anda ...  
// contoh: fetch(BACKEND\_URL \+ '/api/generate')

**Bagian B: Sajikan (Serve) Frontend**

Kita perlu menyajikan file HTML/JS Anda dari port lokal (misal: 8000).

\# Buka Terminal 3  
\# Pindah ke folder frontend Anda  
cd /path/ke/folder-frontend

\# Sajikan file di port 8000  
python \-m http.server 8000

### **4\. Frontend: Jalankan Tunnel (Terminal 4\)**

Ini akan membuat URL publik untuk frontend Anda.

\# Buka Terminal 4  
cloudflared tunnel \--url localhost:8000

Terminal akan menampilkan URL frontend publik Anda.

\+-----------------------------------------------------------+  
|  Your quick Tunnel is following this URL:                 |  
|  \[https://frontend-url-anda.trycloudflare.com\](https://frontend-url-anda.trycloudflare.com)              |  
\+-----------------------------------------------------------+

## **Selesai\!**

Buka **URL Frontend** (https://frontend-url-anda.trycloudflare.com dari Langkah 4\) di browser Anda.

Aplikasi Anda sekarang berjalan. Frontend tersebut akan memanggil **URL Backend** (https://backend-url-anda.trycloudflare.com dari Langkah 2\) untuk mengambil data. Biarkan ke-4 terminal tetap terbuka.