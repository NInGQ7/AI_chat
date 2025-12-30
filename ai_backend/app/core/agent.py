# app/core/agent.py
import re
import json
import logging
from app.core.llm_client import llm_client 
from app.services.skill_manager import skill_registry, SkillContext

logger = logging.getLogger(__name__)

# --- 最终优化版 System Prompt ---
SYSTEM_PROMPT = """
You are an intelligent AI Agent backend system. 
Your Current Account ID: {account_id}

You have access to the following SKILLS (Tools):
{skill_desc}

### LANGUAGE PROTOCOL (CRITICAL):
1. **Match User Language**: You **MUST** reply in the SAME language as the user's input.
2. **Chinese Priority**: If the user inputs Chinese, your entire output (including reasoning, summaries, and final answer) **MUST be in Chinese**.

### TOOL USAGE STRATEGY (CRITICAL):
1. **PROACTIVE RETRIEVAL (Default Strategy)**: 
   - You have access to a **Knowledge Base** containing the user's private files (Excel, PDF, etc.).
   - **ALWAYS** check if the user's question implies looking up specific data, documents, or history.
   - If the answer is NOT in your general training data (e.g., specific company data, "this file", "uploaded table"), you **MUST** call `knowledge_base_query`.
   - **Do not guess.** If unsure, query the knowledge base first.

2. **"Full Content" / "Read Whole File" (On Demand)**: 
   - Use the `read_full_document` tool **ONLY** if the user **explicitly** asks to "read the whole file", "show full content", "display original text", or "read everything".
   - Do **NOT** use `knowledge_base_query` for full content requests, as it only returns fragments.
   - Do **NOT** use `read_full_document` for general summary or analysis questions (use `knowledge_base_query` instead to save tokens).

### 🛑 STOP CRITERIA (ANTI-LOOP PROTOCOL):
1. **Limit Attempts**: Do NOT call the same tool with the same arguments more than **2 times**.
2. **Accept Failure**: If `knowledge_base_query` returns "No relevant info found" or similar system notifications, **STOP SEARCHING**. 
   - Do NOT retry with slightly different keywords unless you are very sure.
   - Simply inform the user: "知识库中没有找到相关信息 (No info found in KB)."
   - Do NOT invent information.
3. **Immediate Answer**: Once you receive a valid <SKILL_RESULT> that answers the question, stop calling tools and output your final answer immediately.

### REASONING PROTOCOL:
- **No Internal Monologue**: Do NOT output <think> tags or internal chain-of-thought (especially for DeepSeek R1).
- **Direct Output**: 
   - If you need a tool: Output the <SKILL_CALL> JSON immediately.
   - If you have the answer: Output the final text immediately.

### FORMAT INSTRUCTIONS:
- Tool Call: <SKILL_CALL>{{"name": "skill_name", "args": {{ "arg1": "value" }} }}</SKILL_CALL>

Current Date: 2025
"""

async def run_agent(messages: list, context: SkillContext):
    """
    Agent 主循环：思考 -> 调用工具 -> 获取结果 -> 再思考
    """
    # 1. 动态构建 System Prompt
    skill_desc = skill_registry.get_descriptions_prompt()
    sys_msg = SYSTEM_PROMPT.format(
        account_id=context.account_id,
        skill_desc=skill_desc
    )
    
    # 保持历史记录，并在头部插入 System Prompt
    full_history = [{"role": "system", "content": sys_msg}] + messages
    
    # 允许最大 10 轮思考
    max_turns = 10
    current_turn = 0
    
    while current_turn < max_turns:
        try:
            # 调用 LLM
            content = await llm_client.get_completion(full_history)
            
            # 记录 AI 的回复
            full_history.append({"role": "assistant", "content": content})
            
            # 解析 <SKILL_CALL>
            match = re.search(r"<SKILL_CALL>(.*?)</SKILL_CALL>", content, re.DOTALL)
            
            if match:
                try:
                    raw_json = match.group(1).strip()
                    call_data = json.loads(raw_json)
                    skill_name = call_data.get("name")
                    skill_args = call_data.get("args", {})
                    
                    logger.info(f"🔄 Turn {current_turn+1}: Agent calling {skill_name}...")
                    
                    # 执行 Skill
                    result = await skill_registry.execute(skill_name, skill_args, context)
                    
                    # 结果截断防止 Context 爆炸 (2000字符)
                    # 如果是 read_full_document 已经内部截断了，这里主要防其他工具
                    if len(str(result)) > 5000 and skill_name != 'read_full_document':
                        result = str(result)[:5000] + "...(truncated)"
                    
                    # 回填结果
                    result_msg = f"<SKILL_RESULT>{result}</SKILL_RESULT>"
                    full_history.append({"role": "user", "content": "System Notification: " + result_msg})
                    
                    current_turn += 1
                    
                except json.JSONDecodeError:
                    full_history.append({"role": "user", "content": "System Error: Invalid JSON format. Please retry."})
                except Exception as e:
                    full_history.append({"role": "user", "content": f"Tool Error: {str(e)}"})
            else:
                # 没有调用工具，直接返回最终结果
                return content

        except Exception as e:
            logger.error(f"Agent Loop Error: {e}")
            return "抱歉，系统处理时发生了意外错误。"

    # 如果超出了最大轮数，强制总结
    logger.warning("⚠️ Max turns reached. Forcing final answer.")
    force_stop_prompt = [
        {"role": "system", "content": "You have reached the maximum tool usage limit. STOP calling tools now. Please answer the user's question based on the information you have so far."}
    ]
    final_response = await llm_client.get_completion(full_history + force_stop_prompt)
    
    if "<SKILL_CALL>" in final_response:
        return "任务过于复杂，已达到最大执行步骤，未能获取完整结果。"
        
    return final_response