🤖 Enterprise AI Knowledge Agent (AI 全能助手)
这是一个基于 FastAPI + Vue3 的全栈 AI 智能助手系统。它摒弃了传统的 LangChain 强封装模式，采用自研 Agent 协议，实现了对 DeepSeek-R1/V3 等推理模型的完美适配。
系统核心特色在于混合检索增强生成 (Hybrid RAG) 架构，支持从海量知识库中精准检索，同时也支持对 Excel/PDF 等复杂文档的全量深度分析，并具备严格的多租户数据隔离机制。
✨ 核心特性 (Key Features)
🧠 智能体架构 (Agentic Architecture)
模型无关性 (Model Agnostic)：底层支持 OpenAI 格式接口，完美适配 DeepSeek-V3 (日常对话) 和 DeepSeek-R1 (深度推理)。
自定义协议：放弃 Function Call，采用 <SKILL_CALL> XML 协议，大幅提升推理模型调用工具的稳定性。
思维链过滤：后端自动清洗 R1 模型的 <think> 标签，确保前端输出简洁。
📚 混合检索 RAG (Hybrid Retrieval)
三级阅读策略：
Preview：上传即生成高信噪比预览（如 Excel 表头），注入短期记忆。
Vector Search：基于 ChromaDB 的向量检索，回答细节问题（低 Token 消耗）。
Full Context：支持按需读取几十万字的原文件（如“总结全文”），自动注入对话历史。
深度文件解析：集成 Pandas + Tabulate，将 Excel 转换为 Markdown 表格，让 AI 能精准分析数据。支持 PDF (pdfplumber)、Word、Txt。
🛡️ 企业级数据管理
多租户隔离：基于 account_id 的物理/逻辑双重隔离。
会话级隔离：单次上传的文件仅在当前会话有效，互不干扰。
级联删除：删除会话时，自动清理 MySQL 记录 + Chroma 向量索引 + 本地物理文件，确保无数据残留。
💻 现代化前端交互
ChatGPT 风格 UI：Vue 3 + Tailwind CSS，极简白/灰风格。
流式打字机：优化的打字机特效，支持 Markdown 实时渲染。
多会话管理：侧边栏历史记录，支持重命名、新建、删除。
🛠️ 技术栈 (Tech Stack)
Backend (后端)
Framework: FastAPI (Asynchronous)
Database: MySQL (Metadata), ChromaDB (Vector Store)
ORM: SQLAlchemy
LLM Client: AsyncOpenAI (Compatible with DeepSeek)
Data Processing: Pandas, OpenPyXL, Tabulate, PDFPlumber
Auth: Python-JOSE (JWT), Passlib (Bcrypt)
Frontend (前端)
Core: Vue 3 (Composition API)
Build Tool: Vite
Styling: Tailwind CSS
Routing: Vue Router 4
HTTP: Axios
Markdown: Marked + DOMPurify
📂 项目结构 (Project Structure)
code
Text
ai_project/
├── ai_backend/                 # 后端工程
│   ├── app/
│   │   ├── api/                # API 路由 (Auth, Chat, Sessions)
│   │   ├── core/               # 核心引擎 (Agent Loop, LLM Client, DB)
│   │   ├── models/             # SQL & Pydantic 模型
│   │   ├── services/           # 业务逻辑 (Skills: KB, File, Search)
│   │   │   ├── skills/         # 具体工具实现
│   │   │   └── skill_manager.py # 工具注册与路由
│   │   └── main.py             # 入口文件
│   ├── data/                   # 持久化数据 (向量库/文件存储)
│   └── requirements.txt
├── ai_frontend/                # 前端工程
│   ├── src/
│   │   ├── api/                # Axios 封装
│   │   ├── components/         # Login 组件
│   │   ├── views/              # 页面 (ChatBoard, KnowledgeBase)
│   │   ├── composables/        # Hooks (Typewriter)
│   │   └── router/             # 路由配置
│   └── package.json
└── README.md
🚀 快速开始 (Getting Started)
前置要求
Python 3.10+
Node.js 16+
MySQL 8.0+
1. 后端部署
code
Bash
cd ai_backend

# 1. 创建虚拟环境
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
# 复制 .env.example 为 .env 并填入 Key
touch .env
.env 配置示例：
code
Ini
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ai_agent_db?charset=utf8mb4
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
TAVILY_API_KEY=tvly-your-key (可选)
SECRET_KEY=your-secret-key
初始化数据库：
请在 MySQL 中执行：
code
SQL
CREATE DATABASE ai_agent_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
启动服务：
code
Bash
python -m app.main
后端将在 http://localhost:8000 启动。
2. 前端部署
code
Bash
cd ai_frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
前端将在 http://localhost:3000 启动。
📖 使用指南 (Usage)
注册与登录：首次使用需在登录页点击“注册”，创建账号。
单次文件分析 (Session RAG)：
在聊天框左下角点击 附件图标 上传文件（支持 Excel/PDF）。
上传后，AI 会自动读取预览。
可以直接提问细节（走向量检索）。
如果需要全文总结，请明确指令：“读取整个文件并总结”。
全局知识库 (Global RAG)：
点击左侧边栏底部的 “知识库管理”。
在此处上传的文件属于全局文件，该账号下的所有会话均可检索到。
会话管理：
点击左上角 “新建对话” 开启新话题。
点击会话标题右侧的 “铅笔” 重命名，“垃圾桶” 删除会话（注意：相关文件也会被物理删除）。
🧩 核心逻辑解析
1. 为什么不用 LangChain？
为了获得对 Prompt 和 Execution Loop 的完全控制权。特别是在处理 DeepSeek R1 这种推理模型时，标准框架的 Function Call 往往不稳定。我们采用 ReAct 思想手写了 Agent 循环，配合正则解析 XML，实现了最高的稳定性和调试透明度。
2. Excel 是如何被 AI 读懂的？
LLM 无法直接阅读二进制 .xlsx。我们在 file_parser.py 中引入了 Pandas，将 Excel 数据清洗后转换为 Markdown 表格 字符串。这使得 AI 能够清晰地识别行、列和表头关系，从而进行复杂的数据分析。
3. 数据如何隔离？
向量库：每个用户拥有独立的 Collection (kb_{user_id})。
检索时：单次文件打标 scope='session'，全局文件打标 scope='global'。
查询时：构造 Filter where={"$or": [{"scope": "global"}, {"session_id": current_id}]}。
