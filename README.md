# 🚀 DocMind AI — Intelligent Document Chatbot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge\&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=for-the-badge\&logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge\&logo=react)
![Vite](https://img.shields.io/badge/Vite-Build_Tool-646CFF?style=for-the-badge\&logo=vite)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge\&logo=docker)
![LangChain](https://img.shields.io/badge/LangChain-RAG-success?style=for-the-badge)
![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-orange?style=for-the-badge)
![Gemini AI](https://img.shields.io/badge/Gemini-AI-purple?style=for-the-badge\&logo=google)
![OCR](https://img.shields.io/badge/OCR-Tesseract-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=24&pause=1000&color=00C2FF&center=true&vCenter=true&width=700&lines=AI-Powered+Document+Chatbot;Chat+with+PDFs+DOCX+PPTX+and+Images;FastAPI+%2B+React+%2B+Docker+%2B+RAG;Built+with+LangChain+and+Gemini+AI" />

### 📄 Chat with PDFs, DOCX, PPTX, Excel & Images using AI

</div>

---

# ✨ Features

✅ Upload multiple document formats
✅ AI-powered semantic search (RAG)
✅ Chat with your files in real-time
✅ OCR support for scanned images & PDFs
✅ FastAPI backend + React frontend
✅ FAISS vector database integration
✅ Gemini AI integration
✅ Modern responsive UI
✅ Dockerized full-stack deployment

---

# 🧠 Supported File Types

* PDF
* DOCX
* PPTX
* XLSX / CSV
* TXT
* Markdown
* HTML
* Images (OCR supported)

---

# 🛠️ Tech Stack

## 🔹 Backend

* FastAPI
* LangChain
* FAISS
* Sentence Transformers
* Google Gemini API
* PyMuPDF
* Tesseract OCR

## 🔹 Frontend

* React
* Vite
* Axios
* Tailwind CSS

## 🔹 Deployment

* Docker
* Docker Compose
* Supervisor

---

# 📂 Project Structure

```bash
ai-doc-chatbot/
│
├── backend/
│   ├── app/
│   ├── storage/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── docker-compose.yml
├── supervisord.conf
└── README.md
```

---

# ⚡ Installation (Local Setup)

## 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/ai-doc-chatbot.git
cd ai-doc-chatbot
```

---

## 2️⃣ Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

---

## 3️⃣ Add Environment Variables

Create `.env` inside backend folder:

```env
GOOGLE_API_KEY=your_api_key_here
```

---

# 🐳 Docker Deployment

## Build & Run

```bash
docker compose up --build
```

---

## Run in Background

```bash
docker compose up -d
```

---

# 📡 API Endpoints

## Upload File

```http
POST /upload-file
```

## Ask Question

```http
POST /ask
```

---

# 🧠 How RAG Works

1. Documents are uploaded
2. Text is extracted
3. Content is chunked
4. Embeddings are generated
5. FAISS stores vectors
6. User asks questions
7. Relevant chunks are retrieved
8. Gemini AI generates final response

---

# 🔒 Environment Variables

| Variable       | Description    |
| -------------- | -------------- |
| GOOGLE_API_KEY | Gemini API key |

---

# 🚧 Future Improvements

* Multi-user authentication
* Chat history
* Cloud storage support
* Streaming AI responses
* Voice interaction
* Dark mode enhancements
* Deployment on AWS/Vercel

---

# 🤝 Contributing

Pull requests are welcome.

For major changes, please open an issue first to discuss what you would like to change.

---

# ⭐ Support

If you like this project:

⭐ Star the repository
🍴 Fork the project
🛠️ Contribute improvements

---

# 👨‍💻 Author

Developed with ❤️ by **Meeran Pathan**

---

# 📜 License

This project is licensed under the MIT License.

---

# 🏷️ Tags

```txt
AI
Artificial Intelligence
RAG
LangChain
FastAPI
React
Vite
Docker
Gemini AI
Machine Learning
Document Chatbot
PDF Chatbot
OCR
FAISS
Vector Database
Semantic Search
Python
Full Stack AI
LLM
Generative AI
Tesseract OCR
Open Source
```
