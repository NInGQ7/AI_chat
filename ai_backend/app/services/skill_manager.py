import inspect
import json
from typing import Callable, Dict, Any
from app.models.schemas import SkillContext

class SkillRegistry:
    def __init__(self):
        self._skills: Dict[str, Callable] = {}
        self._descriptions: Dict[str, str] = {}

    def register(self, name: str, description: str):
        """装饰器：注册技能"""
        def decorator(func):
            self._skills[name] = func
            self._descriptions[name] = description
            return func
        return decorator

    def get_descriptions_prompt(self) -> str:
        """生成 Prompt 用的工具描述"""
        return "\n".join([f"- {name}: {desc}" for name, desc in self._descriptions.items()])

    async def execute(self, skill_name: str, args: dict, context: SkillContext) -> str:
        """路由并执行"""
        if skill_name not in self._skills:
            return f"Error: Skill '{skill_name}' not found."
        
        func = self._skills[skill_name]
        
        # 统一权限预检查
        if not self._check_permission(skill_name, context):
            return f"Error: Permission denied for skill '{skill_name}'."

        try:
            # 自动注入 context (如果函数需要)
            sig = inspect.signature(func)
            if 'context' in sig.parameters:
                # 某些技能是同步的(如DB操作)，某些是异步的
                if inspect.iscoroutinefunction(func):
                    return await func(**args, context=context)
                else:
                    return func(**args, context=context)
            else:
                if inspect.iscoroutinefunction(func):
                    return await func(**args)
                else:
                    return func(**args)
        except Exception as e:
            return f"Error executing {skill_name}: {str(e)}"

    def _check_permission(self, skill_name: str, context: SkillContext) -> bool:
        perms = context.permissions
        if skill_name == "tavily_search" and not perms.get("webSearchEnabled"):
            return False
        if skill_name in ["knowledge_base_upload", "knowledge_base_delete"] and not perms.get("knowledgeBaseWriteEnabled"):
            return False
        if skill_name == "knowledge_base_query" and not perms.get("knowledgeBaseEnabled"):
            return False
        if "account_memory" in skill_name and not perms.get("memoryEnabled"):
            return False
        return True

# 全局单例
skill_registry = SkillRegistry()