# app/services/skills/kb.py
import chromadb
import uuid
from app.services.skill_manager import skill_registry, SkillContext
from app.core.config import settings

chroma_client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)

def get_collection(account_id: str):
    return chroma_client.get_or_create_collection(name=f"kb_{account_id}")

def store_file_to_vector_db(account_id: str, text: str, metadata: dict):
    collection = get_collection(account_id)
    doc_id = str(uuid.uuid4())
    
    # 确保 metadata 健壮性
    meta = {
        "title": metadata.get("title", "unknown"),
        "scope": metadata.get("scope", "global"),
        "session_id": metadata.get("session_id", "none"),
        "account_id": account_id
    }
    
    # 文本切片 (1000字符一片)
    chunk_size = 1000
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    # 如果文件是空的或解析失败
    if not chunks: return None

    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = [meta for _ in range(len(chunks))]
    
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)
    return doc_id

@skill_registry.register("knowledge_base_query", "Search in uploaded files or knowledge base. Args: query")
def kb_query(query: str, context: SkillContext = None):
    print(f">>> KB Query: {query}")
    collection = get_collection(context.account_id)
    
    # 构造混合查询过滤器
    # 逻辑: scope='global' OR session_id='current_session'
    where_filter = {"scope": "global"}
    
    if context.session_id:
        where_filter = {
            "$or": [
                {"scope": "global"},
                {"session_id": context.session_id}
            ]
        }

    try:
        results = collection.query(
            query_texts=[query],
            n_results=10, # 增大搜索范围，提高召回率
            where=where_filter
        )
    except Exception as e:
        return f"DB Error: {str(e)}"
    
    if not results['documents'] or not results['documents'][0]: 
        return "System Notification: No relevant info found in Knowledge Base."
    
    output = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        src_title = meta.get('title', 'Unknown')
        src_scope = meta.get('scope', 'Global')
        output.append(f"[Source: {src_title} ({src_scope})]\n{doc}")
        
    return "\n---\n".join(output)

# 仅用于删除全局知识库文件（会话文件随会话删除）
@skill_registry.register("knowledge_base_delete", "Delete global doc. Args: title")
def kb_delete(title: str, context: SkillContext = None):
    collection = get_collection(context.account_id)
    collection.delete(where={"$and": [{"title": title}, {"scope": "global"}]})
    return f"Deleted global document '{title}'."