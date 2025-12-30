from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
class ChatRequest(BaseModel):
    account_id: str
    message: str
    history: List[Dict[str, str]] = [] # [{"role": "user", "content": "..."}]
    
    # 权限开关
    knowledgeBaseEnabled: bool = True
    knowledgeBaseWriteEnabled: bool = False
    webSearchEnabled: bool = True
    memoryEnabled: bool = True

class ChatResponse(BaseModel):
    response: str
    used_skills: List[str] = []

class SkillContext(BaseModel):
    account_id: str
    session_id: Optional[str] = None  # <--- 新增这一行
    db_session: Any = None 
    permissions: Dict[str, bool]