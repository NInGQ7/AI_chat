# app/core/llm_client.py
import logging
import re
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError
from app.core.config import settings
import httpx # 显式引入 httpx 以配置超时
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        # 【核心修复】配置更长的超时时间 (例如 120秒)
        timeout = httpx.Timeout(120.0, connect=60.0)
        
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=timeout # 注入超时设置
        )
        self.model = settings.OPENAI_MODEL

    async def get_completion(self, messages: list, temperature: float = 0.5) -> str:
        """
        纯文本对话接口
        """
        try:
            # 针对 DeepSeek R1 的优化
            if "reasoner" in self.model or "R1" in self.model:
                temperature = 0.6

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages, # 直接发送文本消息列表，不需要处理图片
                temperature=temperature,
                stream=False
            )
            
            content = response.choices[0].message.content
            if not content:
                return ""
            
            # 过滤 DeepSeek R1 的思考过程标签，只保留结果
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
            
            return content

        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return f"System Error: {str(e)}"

llm_client = LLMClient()