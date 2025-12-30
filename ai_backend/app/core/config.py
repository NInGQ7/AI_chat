import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "AI All-in-One Backend"
    # MySQL 配置: mysql+pymysql://user:password@host:port/db_name
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:1234@localhost:3306/ai_agent_db")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-ai/DeepSeek-R1")
    
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    VECTOR_DB_PATH = "./data/chroma_db"
    UPLOAD_DIR = "./data/temp_files"

settings = Settings()