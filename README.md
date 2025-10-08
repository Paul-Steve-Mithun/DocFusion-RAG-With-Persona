# 🤖 Persona RAG - Intelligent Document Chat System

<div align="center">

![DocFusion Logo](Persona%20Rag/frontend/src/assets/DocFusion.png)

**A powerful Retrieval-Augmented Generation (RAG) chatbot with multi-session support and intelligent document querying**

[![React](https://img.shields.io/badge/React-19.1.1-61DAFB?logo=react&logoColor=white)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Latest-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![LangChain](https://img.shields.io/badge/🦜_LangChain-Latest-blue)](https://www.langchain.com/)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Persona RAG** is an advanced document-based conversational AI system that allows users to upload PDF documents and interact with them through natural language queries. Built with cutting-edge RAG (Retrieval-Augmented Generation) technology, it combines semantic search with large language models to provide accurate, context-aware responses.

### 🎪 Key Highlights

- **Multi-Session Management**: Create and manage multiple chat sessions with different document contexts
- **Hybrid Retrieval**: Combines vector similarity search (ChromaDB) with BM25 keyword matching for optimal results
- **User Authentication**: Secure JWT-based authentication with MongoDB user management
- **Modern UI**: Beautiful, responsive React interface with Tailwind CSS
- **Real-time Chat**: Engaging chat experience with typing indicators and markdown support
- **Document History**: Track all uploaded documents per session with timestamps

---

## ✨ Features

### 🔐 **Authentication & User Management**
- User registration and login with secure password hashing (bcrypt)
- JWT token-based authentication
- Session-based user isolation for data privacy

### 📄 **Document Management**
- Upload and index PDF documents per session
- Automatic text extraction and chunking
- Document history tracking with metadata
- Multi-document support within sessions

### 🧠 **Advanced RAG Pipeline**
- **Hybrid Retrieval**: Combines vector embeddings (sentence-transformers/all-mpnet-base-v2) with BM25
- **Multi-Query Expansion**: Automatically generates related queries for comprehensive retrieval
- **Reranking**: Smart deduplication and relevance scoring
- **Contextual Chat History**: Maintains conversation context for coherent multi-turn dialogues

### 💬 **Chat Interface**
- Real-time conversational AI responses
- Markdown rendering with code syntax highlighting
- Chat history persistence
- Typing indicators and loading states
- Mobile-responsive design

### 🎨 **Modern UI/UX**
- Clean, intuitive dashboard
- Session management interface
- Document upload with progress tracking
- Responsive design for all screen sizes
- Dark-themed professional interface

---

## 🛠 Tech Stack

### **Backend**
| Technology | Purpose |
|------------|---------|
| ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) | REST API framework |
| ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) | Core backend language |
| ![LangChain](https://img.shields.io/badge/LangChain-blue?style=flat) | RAG orchestration framework |
| ![ChromaDB](https://img.shields.io/badge/ChromaDB-orange?style=flat) | Vector database for embeddings |
| ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb&logoColor=white) | User & document metadata storage |
| ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white) | LLM for response generation |
| ![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=flat&logo=huggingface&logoColor=black) | Embedding models |

**Key Libraries:**
- `langchain` - RAG pipeline orchestration
- `sentence-transformers` - Text embeddings
- `pypdf` - PDF parsing
- `motor` - Async MongoDB driver
- `python-jose` - JWT tokens
- `passlib` - Password hashing

### **Frontend**
| Technology | Purpose |
|------------|---------|
| ![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black) | UI framework |
| ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white) | Build tool & dev server |
| ![TailwindCSS](https://img.shields.io/badge/Tailwind-38B2AC?style=flat&logo=tailwind-css&logoColor=white) | Styling framework |
| ![Axios](https://img.shields.io/badge/Axios-5A29E4?style=flat&logo=axios&logoColor=white) | HTTP client |
| ![React Router](https://img.shields.io/badge/React_Router-CA4245?style=flat&logo=react-router&logoColor=white) | Routing |

**Key Libraries:**
- `react-markdown` - Markdown rendering in chat
- `lucide-react` - Modern icon library
- `remark-gfm` - GitHub Flavored Markdown support
- `rehype-sanitize` - XSS protection

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Login/     │  │  Dashboard   │  │  Chat Page   │          │
│  │   Register   │  │  (Sessions)  │  │  (Q&A)       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ REST API (Axios)
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    Auth      │  │  Documents   │  │     Chat     │          │
│  │   Routes     │  │   Routes     │  │   Routes     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                  │                  │
│         │                  │                  │                  │
│  ┌──────▼──────────────────▼──────────────────▼──────┐          │
│  │              RAG Engine (LangChain)                │          │
│  │  • Multi-Query Expansion                           │          │
│  │  • Hybrid Retrieval (Vector + BM25)                │          │
│  │  • Reranking & Deduplication                       │          │
│  │  • History-Aware Retrieval                         │          │
│  └────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
         │                  │                         │
         │                  │                         │
    ┌────▼──────┐  ┌────────▼────────┐   ┌───────────▼──────────┐
    │  MongoDB  │  │   ChromaDB      │   │   Cloudinary         │
    │  • Users  │  │   • Embeddings  │   │   • PDF Storage      │
    │  • Sess.  │  │   • Vectors     │   │   • CDN Delivery     │
    │  • Docs   │  │   • BM25 Index  │   │   (25GB Free Tier)   │
    │  • Chat   │  │   (per user/    │   └──────────────────────┘
    └───────────┘  │    session)     │
                   └─────────────────┘
```

### **Data Flow**

1. **Authentication**: User registers/logs in → JWT token issued
2. **Session Creation**: User creates a session → stored in MongoDB
3. **Document Upload**: PDF uploaded → stored in Cloudinary → extracted, chunked, embedded → vectors stored in ChromaDB + metadata in MongoDB
4. **Query Processing**:
   - User sends question
   - Multi-query expansion generates related queries
   - Hybrid retrieval: Vector search + BM25 keyword matching
   - Retrieved documents reranked
   - LLM generates answer with context
   - Response streamed to frontend
5. **Document Viewing**: User clicks document → redirected to Cloudinary CDN URL → PDF opens in browser

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **MongoDB** ([Download](https://www.mongodb.com/try/download/community))
- **OpenAI API Key** ([Get one](https://platform.openai.com/api-keys))
- **Cloudinary Account** ([Sign up free](https://cloudinary.com)) - Required for PDF storage
- **Git** ([Download](https://git-scm.com/))

---

## 🚀 Installation

### **1. Clone the Repository**

```bash
git clone https://github.com/YOUR_USERNAME/persona-rag.git
cd persona-rag
```

### **2. Backend Setup**

```bash
# Navigate to backend directory
cd "Persona Rag/backend"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see Environment Variables section)
# Then run the server
python main.py
```

The backend will start on `http://localhost:8000`

### **3. Frontend Setup**

```bash
# Open a new terminal and navigate to frontend directory
cd "Persona Rag/frontend"

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on `http://localhost:5173`

---

## 🔧 Environment Variables

### **Backend (.env file in `Persona Rag/backend/`)**

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# HuggingFace (optional, for embedding models)
HUGGINGFACE_TOKEN=hf_your-token-here

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/persona_rag

# JWT Authentication
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256

# ChromaDB Storage
CHROMA_PERSIST_DIR=./chroma_db

# Cloudinary Configuration (REQUIRED for PDF storage)
# Sign up at https://cloudinary.com to get these credentials
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### **Environment Variable Details**

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key for GPT models |
| `HUGGINGFACE_TOKEN` | ⚠️ Optional | Token for downloading HuggingFace models |
| `MONGODB_URI` | ✅ Yes | MongoDB connection string |
| `JWT_SECRET` | ✅ Yes | Secret key for JWT token signing (change in production!) |
| `JWT_ALGORITHM` | ⚠️ Optional | JWT algorithm (default: HS256) |
| `CHROMA_PERSIST_DIR` | ⚠️ Optional | Directory for ChromaDB storage (default: ./chroma_db) |
| `CLOUDINARY_CLOUD_NAME` | ✅ Yes | Your Cloudinary cloud name for PDF storage |
| `CLOUDINARY_API_KEY` | ✅ Yes | Your Cloudinary API key |
| `CLOUDINARY_API_SECRET` | ✅ Yes | Your Cloudinary API secret |

> **📝 Note:** Cloudinary is used for persistent PDF storage. This is essential for deployment on platforms like Render where local storage is ephemeral. See [CLOUDINARY_SETUP.md](CLOUDINARY_SETUP.md) for detailed setup instructions.

---

## 🎮 Usage

### **Step 1: Start the Application**

1. Start MongoDB (if not running as a service)
2. Start the backend server: `python main.py` (from backend directory)
3. Start the frontend: `npm run dev` (from frontend directory)
4. Open browser: `http://localhost:5173`

### **Step 2: Register & Login**

1. Click "Sign Up" and create an account
2. Login with your credentials

### **Step 3: Create a Session**

1. On the Dashboard, create a new session (e.g., "South of France Travel")
2. Click on the session to enter the chat interface

### **Step 4: Upload Documents**

1. Click the "Upload Document" button
2. Select one or more PDF files
3. Wait for the documents to be processed and indexed

### **Step 5: Start Chatting**

1. Ask questions about your uploaded documents
2. The AI will retrieve relevant context and provide accurate answers
3. Continue the conversation - the system maintains chat history

### **Example Queries**

For travel documents:
- "What are the best restaurants to try in Marseille?"
- "Tell me about the history of Nice"
- "What activities would you recommend in Cannes?"

---

## 📁 Project Structure

```
RAG/
├── Persona Rag/
│   ├── backend/
│   │   ├── api/
│   │   │   ├── core/
│   │   │   │   ├── config.py          # Configuration management
│   │   │   │   └── security.py        # JWT & password utilities
│   │   │   ├── db/
│   │   │   │   └── mongo.py           # MongoDB connection
│   │   │   ├── routes/
│   │   │   │   ├── auth.py            # Authentication endpoints
│   │   │   │   ├── chat.py            # Chat endpoints
│   │   │   │   ├── documents.py       # Document upload/management
│   │   │   │   └── sessions.py        # Session management
│   │   │   ├── models.py              # Pydantic data models
│   │   │   ├── rag.py                 # RAG pipeline implementation
│   │   │   └── server.py              # FastAPI app setup
│   │   ├── main.py                    # Application entry point
│   │   └── requirements.txt           # Python dependencies
│   │
│   └── frontend/
│       ├── src/
│       │   ├── api/
│       │   │   └── client.js          # API client with Axios
│       │   ├── auth/
│       │   │   └── AuthProvider.jsx   # Auth context provider
│       │   ├── components/
│       │   │   ├── ChatBubble.jsx     # Chat message component
│       │   │   ├── ProgressBar.jsx    # Upload progress
│       │   │   ├── Spinner.jsx        # Loading spinner
│       │   │   └── TypingDots.jsx     # Typing indicator
│       │   ├── pages/
│       │   │   ├── Login.jsx          # Login page
│       │   │   ├── Register.jsx       # Registration page
│       │   │   ├── Dashboard.jsx      # Session management
│       │   │   └── Chat.jsx           # Chat interface
│       │   ├── App.jsx                # Main app component
│       │   └── main.jsx               # React entry point
│       ├── package.json               # Node dependencies
│       └── vite.config.js             # Vite configuration
│
├── .gitignore                         # Git ignore rules
└── README.md                          # This file
```

---

## 🔌 API Endpoints

### **Authentication**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/auth/register` | Register new user | ❌ |
| `POST` | `/api/auth/login` | Login user | ❌ |
| `GET` | `/api/auth/me` | Get current user | ✅ |

### **Sessions**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/sessions` | List user sessions | ✅ |
| `POST` | `/api/sessions` | Create new session | ✅ |
| `DELETE` | `/api/sessions/{session_id}` | Delete session | ✅ |

### **Documents**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/documents/upload` | Upload & index PDF | ✅ |
| `GET` | `/api/documents` | List documents | ✅ |

### **Chat**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/chat/ask` | Ask question | ✅ |
| `GET` | `/api/chat/history` | Get chat history | ✅ |

---

## 📸 Screenshots

<!-- Add your screenshots here -->

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)
*Session management interface*

### Chat Interface
![Chat](docs/screenshots/chat.png)
*Conversational AI with document context*

### Document Upload
![Upload](docs/screenshots/upload.png)
*PDF document upload and processing*

> **Note**: Add screenshots to `docs/screenshots/` directory

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### **Development Guidelines**

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangChain](https://www.langchain.com/) - RAG framework
- [OpenAI](https://openai.com/) - GPT models
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [HuggingFace](https://huggingface.co/) - Embedding models
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python API framework
- [React](https://reactjs.org/) - UI library

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

<div align="center">

**Made with ❤️ by [Your Name]**

⭐ Star this repo if you find it helpful!

</div>

