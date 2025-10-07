import os
from typing import Optional
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from typing import List, Tuple
from .core import config


def get_embeddings():
    if config.HUGGINGFACE_TOKEN:
        os.environ["HUGGINGFACE_TOKEN"] = config.HUGGINGFACE_TOKEN
    # Use a stronger embedding model and normalize for cosine distance
    # "sentence-transformers/all-mpnet-base-v2" offers higher quality than MiniLM for RAG
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        encode_kwargs={"normalize_embeddings": True},
    )


def get_user_chroma_dir(user_id: str, session_id: str | None = None) -> str:
    base = config.CHROMA_PERSIST_DIR
    if session_id:
        return os.path.join(base, f"user_{user_id}", f"session_{session_id}")
    return os.path.join(base, f"user_{user_id}")


def get_vectorstore_for_user(user_id: str, session_id: str | None = None) -> Chroma:
    if not session_id:
        # Enforce per-session isolation; caller must provide session_id
        raise ValueError("session_id is required for vectorstore access")
    persist_dir = get_user_chroma_dir(user_id, session_id)
    os.makedirs(persist_dir, exist_ok=True)
    embeddings = get_embeddings()
    return Chroma(persist_directory=persist_dir, embedding_function=embeddings)


def index_pdf_for_user(user_id: str, temp_pdf_path: str, session_id: str | None = None):
    if not session_id:
        raise ValueError("session_id is required for indexing")
    loader = PyPDFLoader(temp_pdf_path)
    docs = loader.load()
    # Filter out empty pages (e.g., scanned PDFs without OCR)
    docs = [d for d in docs if (d.page_content or "").strip()]
    if not docs:
        raise ValueError("No extractable text found in the PDF. Try another file or OCR.")
    # Slightly smaller chunks generally improve recall; keep modest overlap for continuity
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    splits = splitter.split_documents(docs)
    if not splits:
        raise ValueError("No text chunks generated from the PDF.")
    vs = get_vectorstore_for_user(user_id, session_id)
    vs.add_documents(splits)


def get_llm() -> ChatOpenAI:
    # Deterministic answers; we rely on retrieved context only
    return ChatOpenAI(api_key=config.OPENAI_API_KEY, model="gpt-4o-mini", temperature=0)


def build_conversational_chain(user_id: str, history: Optional[BaseChatMessageHistory], session_id: str | None = None):
    if not session_id:
        raise ValueError("session_id is required for chat")
    vs = get_vectorstore_for_user(user_id, session_id)
    # Embedding retriever (primary). Avoid score_threshold here due to Chroma compatibility.
    embedding_retriever = vs.as_retriever(search_kwargs={"k": 8})

    # Build a lightweight BM25 retriever over all docs in the session for hybrid search
    bm25 = None
    try:
        # Try to get all documents from the collection
        collection = vs._collection
        all_data = collection.get(include=["documents", "metadatas"])
        texts = all_data.get("documents", []) or []
        metas = all_data.get("metadatas", []) or []
        
        print(f"Chroma collection has {len(texts)} documents")
        
        if texts and len(texts) > 0:
            bm25_docs: List[Document] = [Document(page_content=t, metadata=m or {}) for t, m in zip(texts, metas)]
            bm25 = BM25Retriever.from_documents(bm25_docs)
            bm25.k = 8
            print(f"BM25 initialized with {len(bm25_docs)} documents")
        else:
            print("WARNING: No documents found in Chroma collection - did you upload a PDF?")
    except Exception as e:
        print(f"BM25 initialization failed: {e}")
        import traceback
        traceback.print_exc()
        bm25 = None
    llm = get_llm()

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question"
        " which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(llm, embedding_retriever, contextualize_q_prompt)

    system_prompt = (
        "You are a grounded RAG assistant.\n"
        "Use ONLY the information in the retrieved context to answer.\n"
        "Do NOT use prior knowledge or invent facts.\n\n"
        "When answering from context, be clear and structured (headings, bullet points, numbered lists as needed).\n\n"
        "Retrieved context follows.\n{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Compose a custom retrieval function that performs multi-query expansion and RRF fusion
    def retrieve(query: str, chat_history) -> List[Document]:
        # Multi-query expansion: generate several paraphrases of the user query
        # Simplified to avoid breaking on subsequent queries
        queries = [query]
        try:
            mq_prompt = ChatPromptTemplate.from_messages([
                ("system", "Generate 2 alternative search queries to find relevant information. Return as a JSON array of strings. Keep queries concise and relevant."),
                ("human", "{q}")
            ])
            mq = llm.invoke(mq_prompt.format_messages(q=query)).content
            import json
            parsed = json.loads(mq)
            if isinstance(parsed, list):
                for alt in parsed:
                    if isinstance(alt, str) and alt.strip() and alt not in queries:
                        queries.append(alt.strip())
        except Exception as e:
            # Log for debugging but don't fail
            print(f"Multi-query expansion failed: {e}")
            pass

        def dedup_by_text(docs: List[Document]) -> List[Document]:
            seen = set()
            unique = []
            for d in docs:
                key = (d.page_content.strip(), str(d.metadata))
                if key in seen:
                    continue
                seen.add(key)
                unique.append(d)
            return unique

        # Collect candidates per retriever
        candidates: List[Tuple[Document, int]] = []  # (doc, rank)
        print(f"Retrieve: Processing {len(queries)} queries: {[q[:50] for q in queries]}")
        for i, q in enumerate(queries):
            # Embedding hits - always retrieve, don't filter by threshold at this stage
            try:
                docs = embedding_retriever.invoke(q)
                print(f"  Query {i+1}: Embedding retriever returned {len(docs)} docs for: '{q[:50]}...'")
            except Exception as e:
                print(f"  Query {i+1}: Embedding invoke failed: {e}, trying get_relevant_documents")
                try:
                    docs = embedding_retriever.get_relevant_documents(q)
                    print(f"  Query {i+1}: get_relevant_documents returned {len(docs)} docs")
                except Exception as e2:
                    print(f"  Query {i+1}: get_relevant_documents also failed: {e2}")
                    docs = []
            for rank, d in enumerate(docs):
                candidates.append((d, rank))
            # BM25 hits
            if bm25 is not None:
                try:
                    bm25_docs = bm25.get_relevant_documents(q)
                    print(f"  BM25 returned {len(bm25_docs)} docs for query: {q[:50]}")
                    for rank, d in enumerate(bm25_docs):
                        candidates.append((d, rank))
                except Exception as e:
                    print(f"  BM25 retrieval failed: {e}")
                    pass

        # Reciprocal Rank Fusion
        scores = {}
        for d, r in candidates:
            key = (d.page_content, tuple(sorted(d.metadata.items()))) if isinstance(d.metadata, dict) else (d.page_content, str(d.metadata))
            scores[key] = scores.get(key, 0) + 1.0 / (60 + r)  # 60 for stability

        # Rebuild documents with aggregated scores
        scored_docs = []
        for d, r in candidates:
            key = (d.page_content, tuple(sorted(d.metadata.items()))) if isinstance(d.metadata, dict) else (d.page_content, str(d.metadata))
            if key in scores:
                d.metadata = dict(d.metadata or {})
                d.metadata["rrf_score"] = scores[key]
                scored_docs.append(d)
        # Sort by fused score desc, then truncate
        scored_docs.sort(key=lambda x: x.metadata.get("rrf_score", 0), reverse=True)
        out = dedup_by_text(scored_docs)[:6]
        print(f"Retrieve: Final result: {len(out)} documents after deduplication and ranking")
        
        return out

    # Return a simple invokable object that mirrors the output shape of create_retrieval_chain
    class SimpleRAG:
        def invoke(self, inputs):
            q = inputs.get("input", "")
            chat_history = inputs.get("chat_history", [])
            print(f"SimpleRAG: Processing query: '{q[:100]}...'")
            docs = retrieve(q, chat_history)
            print(f"SimpleRAG: Retrieved {len(docs)} documents")
            if not docs:
                print("SimpleRAG: No documents retrieved, returning 'I don't know' response")
                return {"answer": "I don't know based on the uploaded documents. Please make sure you have uploaded PDF documents to this session.", "context": []}
            answer = question_answer_chain.invoke({
                "input": q,
                "chat_history": chat_history,
                "context": docs,
            })
            print(f"SimpleRAG: Generated answer: '{answer[:100]}...'")
            # create_stuff_documents_chain returns a string by default
            return {"answer": answer, "context": docs}

    return SimpleRAG()


