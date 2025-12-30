# app/services/skills/files.py
import os
from app.services.skill_manager import skill_registry, SkillContext
from app.core.config import settings
from app.core.file_parser import parse_file_content

@skill_registry.register(
    "read_full_document", 
    "Read the COMPLETE content of a file. Use ONLY when user asks for 'full content', 'whole file'. Args: filename"
)
def read_full_document(filename: str, context: SkillContext):
    # 1. 先找 Session 目录
    session_dir = os.path.join(settings.UPLOAD_DIR, context.account_id, "sessions", context.session_id)
    # 2. 再找 Global 目录
    global_dir = os.path.join(settings.UPLOAD_DIR, context.account_id, "global")
    
    target_path = None
    
    # 优先查找当前会话
    if context.session_id and os.path.exists(session_dir):
        if os.path.exists(os.path.join(session_dir, filename)):
            target_path = os.path.join(session_dir, filename)
    
    # 没找到，查全局
    if not target_path and os.path.exists(global_dir):
        if os.path.exists(os.path.join(global_dir, filename)):
            target_path = os.path.join(global_dir, filename)
            
    if not target_path:
        return f"Error: File '{filename}' not found in current session or global knowledge base."

    try:
        content = parse_file_content(target_path)
        # 截断防止超时
        if len(content) > 50000:
            return content[:50000] + "\n\n[System: File too large, truncated at 50k chars.]"
        return content
    except Exception as e:
        return f"Read Error: {e}"