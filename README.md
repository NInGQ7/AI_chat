
# 🤖 Enterprise AI Knowledge Agent (企业级 AI 全能助手)

这是一个基于 **FastAPI + Vue3** 的全栈 AI 智能助手系统。

它摒弃了传统的 LangChain 强封装模式，采用**自研 ReAct Agent 协议**，实现了对 **DeepSeek-R1/V3** 等国产推理模型的完美适配。系统核心特色在于**混合检索增强生成 (Hybrid RAG)** 架构，既支持从海量知识库中精准检索，也能对 Excel/PDF 等复杂文档进行**全量深度分析**，并具备严格的多租户数据隔离机制。


---

## ✨ 核心特性 (Key Features)

### 🧠 深度适配推理模型 (DeepSeek R1 Ready)
*   **模型无关性 (Model Agnostic)**：底层基于 OpenAI SDK 封装，但针对 **DeepSeek-V3** (日常对话) 和 **DeepSeek-R1** (深度推理) 进行了专门优化。
*   **自定义 Agent 协议**：放弃不稳定的 Function Call，采用 `<SKILL_CALL>` XML 协议，大幅提升推理模型调用工具的准确率。
*   **思维链清洗**：后端自动过滤 R1 模型的 `<think>` 标签，确保前端输出简洁明了。

### 📚 混合检索 RAG (Hybrid Retrieval Strategy)
*   **三级阅读策略**：
    1.  **Preview (预览)**：上传即生成高信噪比预览（如 Excel 表头+前20行），注入短期记忆，解决“盲猜”问题。
    2.  **Vector Search (检索)**：基于 ChromaDB 的向量检索，回答细节问题（低 Token 消耗，速度快）。
    3.  **Full Context (全量)**：支持按需读取硬盘原文件（如“读取整个文件”），自动注入对话历史，实现上帝视角总结。
*   **深度文件解析**：集成 `Pandas` + `Tabulate`，将 Excel 清洗转换为 **Markdown 表格**，让 LLM 能精准理解行、列关系。支持 PDF (pdfplumber)、Word、Txt。

### 🛡️ 企业级数据安全
*   **多租户隔离**：基于 `account_id` 的物理/逻辑双重隔离。
*   **会话级隔离**：聊天框上传的文件仅在当前会话有效，删除会话即销毁。
*   **级联删除 (Cascade Delete)**：删除会话时，自动事务性清理 **MySQL 记录 + Chroma 向量索引 + 本地物理文件**，确保数据零残留。

### 💻 现代化前端交互
*   **ChatGPT 风格 UI**：Vue 3 + Tailwind CSS，极简白/灰风格，像素级对齐。
*   **流式打字机**：优化的打字机特效（防抖动），支持 Markdown 表格、代码块实时渲染。
*   **完整会话管理**：支持侧边栏历史记录、重命名、新建、删除。

---

## 🛠️ 技术栈 (Tech Stack)

### Backend (后端)
*   **Framework**: FastAPI (Asynchronous)
*   **Database**: MySQL (Metadata), ChromaDB (Vector Store)
*   **ORM**: SQLAlchemy
*   **LLM Client**: AsyncOpenAI (with Timeout & Retry logic)
*   **Data ETL**: Pandas, OpenPyXL, Tabulate, PDFPlumber
*   **Auth**: Python-JOSE (JWT), Passlib (Bcrypt)

### Frontend (前端)
*   **Core**: Vue 3 (Composition API, Setup Sugar)
*   **Build Tool**: Vite
*   **Styling**: Tailwind CSS
*   **Routing**: Vue Router 4
*   **HTTP**: Axios (Interceptors for Auth)
*   **Markdown**: Marked + DOMPurify

---

## 📂 项目结构 (Project Structure)

```text
ai_project/
├── ai_backend/                 # 后端工程
│   ├── app/
│   │   ├── api/                # API 路由 (Auth, Chat, Sessions)
│   │   ├── core/               # 核心引擎 (Agent Loop, LLM Client, DB Config)
│   │   ├── models/             # SQL & Pydantic 模型
│   │   ├── services/           # 业务逻辑 (Skills: KB, File, Search)
│   │   │   ├── skills/         # 具体工具实现 (kb.py, files.py)
│   │   │   └── skill_manager.py # 工具注册与路由分发
│   │   └── main.py             # 入口文件
│   ├── data/                   # 持久化数据 (向量库/文件存储 - 自动生成)
│   └── requirements.txt
├── ai_frontend/                # 前端工程
│   ├── src/
│   │   ├── api/                # Axios 接口封装
│   │   ├── components/         # Login 组件
│   │   ├── views/              # 页面 (ChatBoard, KnowledgeBase)
│   │   ├── composables/        # Hooks (useTypewriter)
│   │   └── router/             # 路由配置
│   └── package.json
└── README.md
🚀 快速开始 (Getting Started)
前置要求

Python 3.10+

Node.js 16+

MySQL 8.0+ (必须支持 utf8mb4)

1. 后端部署
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
# 新建 .env 文件并填入以下内容
touch .env

.env 配置参考：

code
Ini
download
content_copy
expand_less
# 数据库连接 (注意 charset=utf8mb4 是必须的)
DATABASE_URL=mysql+pymysql://root:你的密码@localhost:3306/ai_agent_db?charset=utf8mb4

# 模型配置 (DeepSeek 示例)
OPENAI_API_KEY=sk-your-deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat

# 可选配置
TAVILY_API_KEY=tvly-your-key
SECRET_KEY=your-secret-key-for-jwt

初始化数据库：
请在 MySQL 客户端中执行：

CREATE DATABASE ai_agent_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

启动服务：

python -m app.main

后端将在 http://localhost:8000 启动，Swagger 文档位于 /docs。

2. 前端部署

cd ai_frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev

前端将在 http://localhost:3000 启动。

📖 使用指南 (Usage)

注册与登录：首次访问会自动跳转登录页，点击“注册”创建账号。

单次文件分析 (Session RAG)：

在聊天框左下角点击 附件图标 上传文件（支持 Excel/PDF/Word）。

智能预览：上传后，AI 会自动读取 Excel 表头或文档摘要。

日常问答：直接提问（如“分析数据趋势”），AI 会调用向量检索，省钱且快。

全量读取：发送指令“读取整个文件”或“输出完整内容”，AI 会读取硬盘原文件并注入对话。

全局知识库 (Global RAG)：

点击左侧边栏底部的 “知识库管理”。

在此处上传的文件属于全局文件，该账号下的所有会话均可检索到，适合存储公司规章、常用文档。

会话管理：

点击左上角 “新建对话” 开启新话题。

点击会话标题右侧的 “铅笔” 重命名，“垃圾桶” 删除会话。

🧩 核心逻辑解析 (Q&A)
Q1: 为什么不用 LangChain/LangGraph？

A: 为了获得对 Prompt 和 Execution Loop 的完全控制权。
LangChain 封装过重，在调试 DeepSeek R1 这种推理模型时，标准框架的 Function Call 往往不稳定。我们采用 FastAPI + 自研 ReAct 循环，配合正则解析 XML，实现了最高的稳定性和调试透明度，同时性能更好。

Q2: Excel 是如何被 AI 读懂的？

A: LLM 无法直接阅读二进制 .xlsx。我们在 file_parser.py 中引入了 Pandas + Tabulate，将 Excel 数据清洗后转换为 Markdown 表格 字符串。这使得 AI 能够清晰地识别行、列和表头关系，从而进行复杂的数据分析。

Q3: 什么是“混合检索 (Hybrid RAG)”？

A: 我们的系统不单纯依赖向量检索（容易漏掉上下文），也不单纯依赖全文读取（Token 爆炸）。
系统默认使用向量检索（查细节），但当用户意图涉及“全文总结”时，动态切换为读取原文件。同时，上传时的“智能预览”机制解决了冷启动问题。
