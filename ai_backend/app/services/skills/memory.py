from sqlalchemy.orm import Session
from app.models.sql_models import AccountMemory
from app.services.skill_manager import skill_registry, SkillContext

@skill_registry.register("account_memory_write", "Save info to long-term memory. Args: content, category")
def memory_write(content: str, category: str, context: SkillContext = None): # <--- 修改这里
    db: Session = context.db_session
    new_memory = AccountMemory(
        account_id=context.account_id,
        content=content,
        category=category
    )
    db.add(new_memory)
    db.commit()
    return "Success: Memory saved to MySQL."

@skill_registry.register("account_memory_read", "Read long-term memory. Args: query(optional), limit(int)")
def memory_read(query: str = "", limit: int = 5, context: SkillContext = None): # <--- 修改这里
    # 注意：context 虽然给了默认值 None 以通过语法检查，
    # 但实际运行中 SkillManager 会强制注入 context，所以不用担心它是 None
    
    db: Session = context.db_session
    
    # 简单实现：按时间倒序读取
    memories = db.query(AccountMemory)\
        .filter(AccountMemory.account_id == context.account_id)\
        .order_by(AccountMemory.created_at.desc())\
        .limit(limit)\
        .all()
    
    if not memories:
        return "No memory found."
    
    return "\n".join([f"[{m.created_at}] ({m.category}): {m.content}" for m in memories])