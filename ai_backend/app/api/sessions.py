from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import uuid
import os
import shutil

# 引入项目组件
from app.core.database import get_db
from app.models.sql_models import ChatSession, ChatMessage, User, SessionFile
from app.core.security import get_current_user
from app.core.file_parser import parse_file_content
from app.services.skills.kb import store_file_to_vector_db, get_collection
from app.core.config import settings

# ---------------------------------------------------------
# 1. 必须最先定义 router 对象
# ---------------------------------------------------------
router = APIRouter()

# ---------------------------------------------------------
# 2. 定义 Pydantic 模型
# ---------------------------------------------------------
class SessionBase(BaseModel):
    id: str
    title: str
    created_at: str

class SessionUpdate(BaseModel):
    title: str

# ---------------------------------------------------------
# 3. 路由接口实现
# ---------------------------------------------------------

# 新建会话
@router.post("/", response_model=SessionBase)
def create_session(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    # 默认标题
    new_session = ChatSession(id=session_id, user_id=user.id, title="新会话")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"id": new_session.id, "title": new_session.title, "created_at": str(new_session.created_at)}

# 获取会话列表
@router.get("/", response_model=List[SessionBase])
def get_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user.id).order_by(ChatSession.updated_at.desc()).all()
    return [{"id": s.id, "title": s.title, "created_at": str(s.created_at)} for s in sessions]

# 重命名会话
@router.patch("/{session_id}")
def update_session(session_id: str, payload: SessionUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.title = payload.title
    db.commit()
    return {"msg": "Title updated"}

# [新增] 上传会话级文件
@router.post("/{session_id}/upload")
def upload_session_file(
    session_id: str, 
    file: UploadFile = File(...), 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # 1. 验证
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
    if not session: raise HTTPException(status_code=404, detail="Session not found")

    # 2. 保存
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(user.id), "sessions", session_id)
    os.makedirs(user_upload_dir, exist_ok=True)
    file_path = os.path.join(user_upload_dir, file.filename)
    with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)

    # 3. 解析
    try:
        full_text = parse_file_content(file_path)
    except:
        full_text = "Error parsing file."

    # 4. 存向量 (RAG)
    store_file_to_vector_db(
        account_id=str(user.id),
        text=full_text, 
        metadata={"title": file.filename, "scope": "session", "session_id": session_id}
    )

    # 5. 存 SQL
    db_file = SessionFile(session_id=session_id, file_path=file_path, original_name=file.filename)
    db.add(db_file)

    # 6. 生成智能预览 (省 Token)
    preview = ""
    lines = full_text.split('\n')
    # 取前 20 行非空内容 (Excel表头通常在这里)
    valid_lines = [line for line in lines if line.strip()][:20]
    preview = "\n".join(valid_lines)

    chat_content = (
        f"System Notification: User uploaded '{file.filename}'. Content indexed.\n"
        f"**File Preview (First 20 lines)**:\n```\n{preview}\n```\n"
        f"INSTRUCTIONS: Use `knowledge_base_query` to search details. Use `read_full_document` ONLY if user asks for full content."
    )

    # 7. 写入历史
    system_msg = ChatMessage(session_id=session_id, role="system", content=chat_content)
    db.add(system_msg)
    session.updated_at = system_msg.created_at
    db.commit()

    return {"msg": "Uploaded", "filename": file.filename}

# 删除会话 (级联删除文件)
@router.delete("/{session_id}")
def delete_session(session_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # 1. 删除 Chroma 向量
        kb_coll = get_collection(str(user.id))
        # 注意: Chroma 的 delete 需要传入 filter
        kb_coll.delete(where={"session_id": session_id})

        # 2. 删除物理文件
        session_files = db.query(SessionFile).filter(SessionFile.session_id == session_id).all()
        for f in session_files:
            if os.path.exists(f.file_path):
                try:
                    os.remove(f.file_path)
                except OSError:
                    pass # 忽略文件不存在等错误
        
        # 3. 删除数据库记录
        # SessionFile 和 ChatMessage 表建议在 SQL 模型里设置 cascade="all, delete"
        # 这里为了保险手动删一下 SessionFile
        db.query(SessionFile).filter(SessionFile.session_id == session_id).delete()
        
        # ChatMessage 通常有关联级联，可以直接删 Session
        # 但为防万一：
        db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
        
        db.delete(session)
        db.commit()
        return {"msg": "Session deleted"}
        
    except Exception as e:
        db.rollback()
        print(f"Delete Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

# 获取消息历史
@router.get("/{session_id}/messages")
def get_messages(session_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return [{"role": m.role, "content": m.content} for m in messages]