from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from ..routes.auth import get_current_user_id
from ..db.mongo import get_db
from ..models import ChatRequest, ChatResponse
from ..rag import build_conversational_chain, get_vectorstore_for_user
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
import asyncio
from fastapi import Query

router = APIRouter()

user_histories = {}

def get_history(user_id: str, session_id: str):
    key = f"{user_id}:{session_id}"
    if key not in user_histories:
        user_histories[key] = ChatMessageHistory()
    return user_histories[key]

@router.post("/ask", response_model=ChatResponse)
async def ask(payload: ChatRequest, user_id: str = Depends(get_current_user_id)):
    if not payload.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if not payload.session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    history = get_history(user_id, payload.session_id)
    # Quick guard: if no vectors exist for this session, refuse to answer
    try:
        print(f"Chat: Attempting to access vectorstore for user {user_id}, session '{payload.session_id}'")
        vs = get_vectorstore_for_user(user_id, payload.session_id)
        # Check if collection has any documents
        collection = vs._collection
        count = collection.count()
        print(f"Chat: Vectorstore collection has {count} documents")
        if count == 0:
            print(f"Chat: No documents found in vectorstore for session '{payload.session_id}'")
            # Check if this might be a renamed session - try to find documents in the original session
            if not payload.session_id.startswith("Session "):
                print(f"Chat: Attempting to find original session for renamed session '{payload.session_id}'...")
                try:
                    import re
                    
                    # Query MongoDB to find which original session this renamed session came from
                    db = await get_db()
                    
                    # Look for documents in this renamed session to find the original session_id
                    docs = []
                    original_session_id = None
                    async for doc in db.documents.find({"owner_id": user_id, "session_id": payload.session_id}):
                        docs.append(doc)
                        # Get the original_session_id from the first document
                        if original_session_id is None and "original_session_id" in doc:
                            original_session_id = doc["original_session_id"]
                    
                    if docs and original_session_id:
                        print(f"Chat: Found {len(docs)} documents in MongoDB for session '{payload.session_id}' with original session '{original_session_id}'")
                        
                        # Try to use the original session's vectorstore
                        try:
                            vs_fallback = get_vectorstore_for_user(user_id, original_session_id)
                            fallback_count = vs_fallback._collection.count()
                            print(f"Chat: Original session '{original_session_id}' has {fallback_count} documents")
                            if fallback_count > 0:
                                print(f"Chat: Using fallback vectorstore from original session '{original_session_id}' for renamed session '{payload.session_id}'")
                                chain = build_conversational_chain(user_id, history, session_id=original_session_id)
                                result = chain.invoke({"input": payload.message, "chat_history": history.messages})
                                answer = result.get("answer")
                                sources = []
                                for d in (result.get("context", []) or []):
                                    meta = d.metadata or {}
                                    sources.append({
                                        "filename": meta.get("source") or meta.get("filename") or "",
                                        "page": meta.get("page", meta.get("page_number")),
                                        "score": meta.get("rrf_score") or meta.get("similarity") or None,
                                        "snippet": (d.page_content or "")[:300]
                                    })
                                history.add_user_message(payload.message)
                                history.add_ai_message(answer)
                                await db.messages.insert_many([
                                    {"owner_id": user_id, "session_id": payload.session_id, "role": "user", "content": payload.message, "ts": __import__('datetime').datetime.utcnow()},
                                    {"owner_id": user_id, "session_id": payload.session_id, "role": "assistant", "content": answer, "ts": __import__('datetime').datetime.utcnow()},
                                ])
                                return ChatResponse(answer=answer, sources=sources)
                        except Exception as session_error:
                            print(f"Chat: Error accessing original session '{original_session_id}': {session_error}")
                    else:
                        print(f"Chat: No documents found in MongoDB for session '{payload.session_id}' or no original_session_id tracked")
                    
                    print(f"Chat: No suitable fallback session found for '{payload.session_id}'")
                except Exception as fallback_error:
                    print(f"Chat: Fallback attempt failed: {fallback_error}")
            return ChatResponse(answer="I don't know based on the uploaded documents. Please upload a PDF document first.")
    except Exception as e:
        print(f"Chat: Vectorstore access error for user {user_id}, session '{payload.session_id}': {e}")
        import traceback
        traceback.print_exc()
        return ChatResponse(answer="I don't know based on the uploaded documents. Please upload a PDF document first.")
    chain = build_conversational_chain(user_id, history, session_id=payload.session_id)
    result = chain.invoke({"input": payload.message, "chat_history": history.messages})
    answer = result.get("answer")
    # Extract citations from the retrieved context if available
    sources = []
    for d in (result.get("context", []) or []):
        meta = d.metadata or {}
        sources.append({
            "filename": meta.get("source") or meta.get("filename") or "",
            "page": meta.get("page", meta.get("page_number")),
            "score": meta.get("rrf_score") or meta.get("similarity") or None,
            "snippet": (d.page_content or "")[:300]
        })
    # ChatMessageHistory updates are handled by RunnableWithMessageHistory in Streamlit; here we emulate persistence in memory
    history.add_user_message(payload.message)
    history.add_ai_message(answer)
    # Persist message to Mongo for this session
    db = await get_db()
    await db.messages.insert_many([
        {"owner_id": user_id, "session_id": payload.session_id, "role": "user", "content": payload.message, "ts": __import__('datetime').datetime.utcnow()},
        {"owner_id": user_id, "session_id": payload.session_id, "role": "assistant", "content": answer, "ts": __import__('datetime').datetime.utcnow()},
    ])
    return ChatResponse(answer=answer, sources=sources) 

# Experimental: Server-sent events stream for typing animation
@router.post("/ask_stream")
async def ask_stream(payload: ChatRequest, user_id: str = Depends(get_current_user_id)):
    if not payload.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    history = get_history(user_id, payload.session_id)
    chain = build_conversational_chain(user_id, history, session_id=payload.session_id)

    async def event_generator():
        # Use the underlying LLM stream if supported through LangChain
        # Fallback: chunk the final answer to simulate streaming
        result = chain.invoke({"input": payload.message, "chat_history": history.messages})
        text = result["answer"]
        chunk_size = 20
        for i in range(0, len(text), chunk_size):
            yield text[i:i+chunk_size]
            await asyncio.sleep(0.03)
        history.add_user_message(payload.message)
        history.add_ai_message(text)

    return StreamingResponse(event_generator(), media_type="text/plain")

@router.get("/history")
async def get_history_messages(session_id: str = Query(...), user_id: str = Depends(get_current_user_id)):
    db = await get_db()
    out = []
    async for m in db.messages.find({"owner_id": user_id, "session_id": session_id}).sort("ts", 1):
        out.append({"role": m.get("role"), "content": m.get("content")})
    return out


