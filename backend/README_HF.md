---
title: DocFusion RAG Backend
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# DocFusion - RAG Backend API

This is the backend API for DocFusion, a Retrieval-Augmented Generation (RAG) chatbot that allows users to upload PDF documents and interact with them using natural language queries.

## Features

- 🔐 JWT-based authentication
- 📄 PDF document upload and processing
- 🤖 AI-powered chat with RAG
- 💾 MongoDB integration
- 🔍 Vector similarity search with ChromaDB
- 📊 Session management

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/documents/upload` - Upload PDF documents
- `POST /api/chat/ask` - Ask questions about documents
- `GET /api/sessions` - List chat sessions

## Tech Stack

- **Framework**: FastAPI
- **Vector DB**: ChromaDB
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **LLM**: OpenAI GPT-4
- **Database**: MongoDB
- **Storage**: Cloudinary

## Environment Variables Required

Set these in the Hugging Face Space settings:

```
MONGODB_URL=your_mongodb_connection_string
JWT_SECRET_KEY=your_jwt_secret
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key (optional)
HUGGINGFACE_TOKEN=your_hf_token
CLOUDINARY_CLOUD_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
```

## Frontend

The frontend is a separate React application that connects to this API.

For the complete project, visit: [GitHub Repository]

## License

MIT License
