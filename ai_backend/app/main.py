# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
import os

# 1. 导入数据模型 (确保建表成功)
import app.models.sql_models 

# ---------------------------------------------------------
# 2. 【关键修复】导入所有技能模块，触发注册机制
# ---------------------------------------------------------
import app.services.skills.search   # 注册联网搜索
import app.services.skills.kb       # 注册知识库
import app.services.skills.memory   # 注册记忆
import app.services.skills.files    # 注册文件处理
# ---------------------------------------------------------

from app.api.endpoints import router

# 初始化数据库表
Base.metadata.create_all(bind=engine)

# 确保目录存在
os.makedirs("./data/chroma_db", exist_ok=True)
os.makedirs("./data/temp_files", exist_ok=True)

app = FastAPI(title="AI Agent Backend")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)