# app/api/endpoints.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import shutil
import os

# 核心组件
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.agent import run_agent
from app.core.llm_client import llm_client
from app.core.config import settings

# 新增引用：用于解析和存入向量库
from app.core.file_parser import parse_file_content
from app.services.skills.kb import store_file_to_vector_db

# 数据模型
from app.models.sql_models import User, ChatSession, ChatMessage
from app.models.schemas import SkillContext

# 引入子路由
from app.api import auth, sessions

router = APIRouter()

# 1. 注册子路由
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])

# 2. Schema 定义
class ChatRequest(BaseModel):
    session_id: str
    message: str
    knowledgeBaseEnabled: bool = True
    knowledgeBaseWriteEnabled: bool = False
    webSearchEnabled: bool = False
    memoryEnabled: bool = True

class ChatResponse(BaseModel):
    response: str
    new_title: Optional[str] = None

# 3. 辅助功能
async def generate_title(session_id: str, first_user_msg: str, db: Session):
    try:
        prompt = [{"role": "system", "content": "Summarize user input to a title (max 10 chars)."}, {"role": "user", "content": first_user_msg}]
        title = await llm_client.get_completion(prompt)
        clean_title = title.strip().replace('"', '')[:15]
        session_record = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session_record:
            session_record.title = clean_title
            db.commit()
    except Exception: pass

# 4. 核心聊天接口
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    session_record = db.query(ChatSession).filter(ChatSession.id == req.session_id, ChatSession.user_id == user.id).first()
    if not session_record:
        raise HTTPException(status_code=404, detail="Session not found")

    user_message_db = ChatMessage(session_id=req.session_id, role="user", content=req.message)
    db.add(user_message_db)
    db.commit()

    history_records = db.query(ChatMessage).filter(ChatMessage.session_id == req.session_id).order_by(ChatMessage.created_at.asc()).limit(20).all()
    history_context = [{"role": m.role, "content": m.content} for m in history_records]

    # 注入 Session ID
    skill_ctx = SkillContext(
        account_id=str(user.id),
        session_id=req.session_id,
        db_session=db,
        permissions={
            "knowledgeBaseEnabled": req.knowledgeBaseEnabled,
            "knowledgeBaseWriteEnabled": req.knowledgeBaseWriteEnabled,
            "webSearchEnabled": req.webSearchEnabled,
            "memoryEnabled": req.memoryEnabled
        }
    )

    ai_response_text = await run_agent(history_context, skill_ctx)

    ai_message_db = ChatMessage(session_id=req.session_id, role="assistant", content=ai_response_text)
    db.add(ai_message_db)
    session_record.updated_at = ai_message_db.created_at
    
    if len(history_records) <= 2: 
        background_tasks.add_task(generate_title, req.session_id, req.message, db)
        new_title = "Generating..." 
    else:
        new_title = None

    db.commit()
    return ChatResponse(response=ai_response_text, new_title=new_title)

# -----------------------------------------------------------------------------
# 5. 【关键修复】全局知识库上传接口
# -----------------------------------------------------------------------------
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    # 1. 保存
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(user.id), "global")
    os.makedirs(user_upload_dir, exist_ok=True)
    file_path = os.path.join(user_upload_dir, file.filename)
    with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    
    # 2. 解析
    try:
        content = parse_file_content(file_path)
    except Exception as e:
        return {"status": "error", "detail": str(e)}

    # 3. 存入向量库 (Scope=global)
    store_file_to_vector_db(
        account_id=str(user.id),
        text=content,
        metadata={"title": file.filename, "scope": "global", "session_id": "none"}
    )
            
    return {"filename": file.filename, "status": "success", "info": "Indexed globally"}

# [新增] 获取全局知识库列表接口 (可选，方便你刷新列表)
@router.get("/knowledge/files")
def get_knowledge_files(user: User = Depends(get_current_user)):
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(user.id), "global")
    if not os.path.exists(user_upload_dir):
        return []
    
    files = []
    for f in os.listdir(user_upload_dir):
        file_path = os.path.join(user_upload_dir, f)
        if os.path.isfile(file_path):
            # 获取文件时间
            timestamp = os.path.getmtime(file_path)
            from datetime import datetime
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
            files.append({"name": f, "date": date_str})
    
    # 按时间倒序
    files.sort(key=lambda x: x['date'], reverse=True)
    return files

# [新增] 删除全局知识库文件接口
@router.delete("/knowledge/file")
def delete_knowledge_file(
    filename: str, 
    user: User = Depends(get_current_user)
):
    try:
        error_msg = []
        
        # 1. 删除向量数据库数据 (优先执行，确保逻辑上不可见)
        try:
            collection = get_collection(str(user.id))
            # 尝试删除
            collection.delete(where={
                "$and": [
                    {"title": filename},
                    {"scope": "global"}
                ]
            })
        except Exception as db_e:
            print(f"Vector DB delete error: {db_e}")
            error_msg.append(f"DB Error: {str(db_e)}")

        # 2. 删除磁盘文件 (放到后面，并增加异常捕获)
        user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(user.id), "global")
        file_path = os.path.join(user_upload_dir, filename)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                # 如果是 Windows 文件占用错误 (WinError 32)
                print(f"Disk delete error: {e}")
                error_msg.append("File is currently in use and cannot be deleted from disk, but it has been removed from Knowledge Base.")
        
        if error_msg:
            # 如果有错误但不影响逻辑删除，返回 200 但带上警告
            return {"msg": "Partial success", "details": error_msg}
            
        return {"msg": f"File '{filename}' deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")