# DocFusion Architecture Overview

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      PRODUCTION (Render)                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────┐       ┌──────────────────────┐     │
│  │  Frontend Service   │       │   Backend Service    │     │
│  │  (Static Site)      │       │   (Web Service)      │     │
│  │                     │       │                      │     │
│  │  • React + Vite     │ HTTPS │  • FastAPI           │     │
│  │  • Tailwind CSS     ├──────>│  • Python 3.11       │     │
│  │  • React Router     │       │  • Uvicorn           │     │
│  │                     │       │                      │     │
│  │  URL: /             │       │  URL: /api/*         │     │
│  └─────────────────────┘       └──────────┬───────────┘     │
│                                            │                 │
│                                            │                 │
│                                            ▼                 │
│                                 ┌────────────────────┐       │
│                                 │  MongoDB Atlas     │       │
│                                 │  (Database)        │       │
│                                 │                    │       │
│                                 │  • Users           │       │
│                                 │  • Documents       │       │
│                                 │  • Sessions        │       │
│                                 │  • Chat History    │       │
│                                 └────────────────────┘       │
│                                                               │
└──────────────────────────────────────────────────────────────┘

     External Services:
     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
     │ Cloudinary   │  │  Groq AI     │  │  OpenAI      │
     │ (File Store) │  │  (LLM)       │  │  (LLM)       │
     └──────────────┘  └──────────────┘  └──────────────┘
           │                  │                  │
           └──────────────────┴──────────────────┘
                              ▲
                              │
                         Backend calls
```

---

## Technology Stack

### Frontend
- **Framework**: React 19.1
- **Build Tool**: Vite 7.1
- **Styling**: Tailwind CSS 4.1
- **Routing**: React Router DOM 6.28
- **HTTP Client**: Axios
- **Markdown**: React Markdown with rehype-sanitize
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: MongoDB (Motor - async driver)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Passlib with bcrypt
- **File Storage**: Cloudinary
- **RAG System**: LangChain
- **Vector Store**: ChromaDB
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **LLM**: Groq / OpenAI

---

## Directory Structure

```
DocFusion/
├── backend/
│   ├── api/
│   │   ├── core/
│   │   │   ├── config.py          # Configuration management
│   │   │   └── security.py        # JWT & password utilities
│   │   ├── db/
│   │   │   └── mongo.py           # MongoDB connection
│   │   ├── routes/
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── chat.py            # Chat/RAG endpoints
│   │   │   ├── documents.py       # Document management
│   │   │   └── sessions.py        # Session management
│   │   ├── models.py              # Pydantic models
│   │   ├── rag.py                 # RAG logic
│   │   ├── server.py              # FastAPI app setup
│   │   └── email_service.py       # Email functionality
│   ├── requirements.txt           # Python dependencies
│   └── env.example                # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js          # Axios configuration
│   │   ├── auth/
│   │   │   └── AuthProvider.jsx   # Authentication context
│   │   ├── components/
│   │   │   ├── ChatBubble.jsx     # Chat message UI
│   │   │   ├── ProgressBar.jsx    # Upload progress
│   │   │   ├── Spinner.jsx        # Loading indicator
│   │   │   └── TypingDots.jsx     # Typing animation
│   │   ├── pages/
│   │   │   ├── Chat.jsx           # Chat interface
│   │   │   ├── Dashboard.jsx      # Main dashboard
│   │   │   ├── Login.jsx          # Login page
│   │   │   └── Register.jsx       # Registration page
│   │   ├── App.jsx                # Main app component
│   │   └── main.jsx               # Entry point
│   ├── package.json               # Node dependencies
│   ├── vite.config.js             # Vite configuration
│   └── env.example                # Environment template
│
├── render.yaml                    # Render Blueprint
├── DEPLOYMENT_GUIDE.md            # Detailed deployment guide
├── RENDER_QUICK_START.md          # Quick deployment steps
└── ARCHITECTURE.md                # This file
```

---

## Data Flow

### 1. User Authentication Flow
```
User → Frontend (Login) → Backend (/api/auth/login)
                             ↓
                        Verify credentials
                             ↓
                        Generate JWT token
                             ↓
                        Return token
                             ↓
Frontend stores token → Includes in Authorization header
```

### 2. Document Upload Flow
```
User selects PDF → Frontend → Backend (/api/documents/upload)
                                  ↓
                          Upload to Cloudinary
                                  ↓
                          Process with LangChain
                                  ↓
                          Create embeddings
                                  ↓
                          Store in ChromaDB
                                  ↓
                          Save metadata in MongoDB
                                  ↓
                          Return document info
```

### 3. Chat/RAG Flow
```
User asks question → Frontend → Backend (/api/chat/query)
                                    ↓
                            Retrieve user's session
                                    ↓
                            Get relevant docs from ChromaDB
                                    ↓
                            Build context with chat history
                                    ↓
                            Send to LLM (Groq/OpenAI)
                                    ↓
                            Store Q&A in MongoDB
                                    ↓
                            Return answer
                                    ↓
Frontend displays answer with markdown formatting
```

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Login and get JWT
- `GET /api/auth/me` - Get current user info

### Documents
- `POST /api/documents/upload` - Upload PDF
- `GET /api/documents` - List user's documents
- `DELETE /api/documents/{id}` - Delete document

### Chat
- `POST /api/chat/query` - Ask question
- `GET /api/chat/history/{session_id}` - Get chat history

### Sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions` - List user's sessions
- `GET /api/sessions/{id}` - Get session details
- `DELETE /api/sessions/{id}` - Delete session

### Health
- `GET /api/health` - Check service status

---

## Environment Configuration

### Backend Environment Variables
```env
# Database
MONGODB_URL=mongodb+srv://...

# Security
JWT_SECRET_KEY=random-secure-string

# AI Services
GROQ_API_KEY=...
OPENAI_API_KEY=...
HUGGINGFACE_TOKEN=...

# File Storage
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

### Frontend Environment Variables
```env
# Development
VITE_API_URL=http://localhost:8000

# Production
VITE_API_URL=https://your-backend.onrender.com
```

---

## Security Features

1. **Authentication**: JWT-based authentication
2. **Password Security**: Bcrypt hashing
3. **CORS**: Configured for specific origins
4. **Input Validation**: Pydantic models
5. **Markdown Sanitization**: Rehype-sanitize on frontend
6. **Environment Variables**: Secrets not in code

---

## Deployment Models

### Model 1: Separate Services (Current Implementation)
**Pros:**
- Independent scaling
- Clear separation of concerns
- Faster rebuilds
- Better for CDN integration

**Cons:**
- More services to manage
- CORS configuration needed

### Model 2: Monolithic (Single Service)
**Pros:**
- Simpler deployment
- Single URL
- No CORS issues

**Cons:**
- Couples frontend and backend
- Slower rebuilds
- Less flexible scaling

---

## Performance Considerations

### Backend
- **Async/Await**: All database operations are async
- **Connection Pooling**: MongoDB Motor uses connection pooling
- **Caching**: Embeddings model cached with `@st.cache_resource`

### Frontend
- **Code Splitting**: Vite automatically splits code
- **Lazy Loading**: Route-based code splitting possible
- **Asset Optimization**: Vite optimizes assets during build

### Database
- **Indexes**: MongoDB indexes on frequently queried fields
- **Vector Search**: ChromaDB for efficient similarity search

---

## Monitoring & Debugging

### Logs to Check
1. **Render Backend Logs**: API errors, database connections
2. **Render Frontend Logs**: Build errors
3. **Browser Console**: Client-side errors, API responses
4. **MongoDB Logs**: Query performance, connection issues

### Common Issues
1. **CORS Errors**: Check `allow_origins` in backend
2. **Environment Variables**: Verify all are set in Render
3. **Database Connection**: Check MONGODB_URL format
4. **API Timeout**: Backend may be spinning up (free tier)

---

## Future Enhancements

### Potential Improvements
- [ ] WebSocket for real-time chat
- [ ] Redis for session caching
- [ ] PostgreSQL for metadata (faster queries)
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline
- [ ] Automated testing
- [ ] Rate limiting
- [ ] API versioning
- [ ] Monitoring dashboard

---

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Vite Docs](https://vite.dev/)
- [Render Docs](https://render.com/docs)
- [LangChain Docs](https://python.langchain.com/)
- [MongoDB Atlas](https://www.mongodb.com/atlas)

