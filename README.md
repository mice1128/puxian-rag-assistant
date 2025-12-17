# 莆仙话 RAG 助手

基于 Qwen2.5-7B-GPTQ-Int4 和 BGE-small-zh-v1.5 的莆仙话（莆仙语）知识问答系统。

## ✨ 特性

- 🤖 **本地大模型**：使用 Qwen2.5-7B-GPTQ-Int4（4.5GB VRAM）
- 🔍 **语义检索**：BGE-small-zh-v1.5 嵌入模型 + ChromaDB 向量库
- 📚 **多格式支持**：CSV, PDF, TXT, DOCX, MD
- 💬 **智能对话**：基于 RAG 的问答系统
- 🎨 **现代界面**：Vue 3 + Vite 前端
- 🚀 **轻量级**：无登录系统，仅 2 个核心页面

## 🏗️ 架构

```
后端：Flask + Qwen2.5 + BGE + ChromaDB
前端：Vue 3 + Vite + Axios
```

## 📋 系统要求

- Python 3.10+
- Node.js 18+
- CUDA GPU（推荐，至少 4.5GB VRAM）
- Conda 环境管理器
- nvm（Node 版本管理器）

## 🚀 快速开始

### 1. 初始化项目

```bash
cd /home/zl/LLM/puxian-rag-assistant
./scripts/init.sh
```

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# 模型路径（修改为你的实际路径）
QWEN_MODEL_PATH=/home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4
EMBEDDING_MODEL_PATH=/home/zl/LLM/bge-small-zh-v1.5

# 知识库路径
KNOWLEDGE_DIR=./data/knowledge
VECTORSTORE_DIR=./data/vectorstore/chroma_db
```

### 3. 启动服务

**启动后端**（新终端）：
```bash
./scripts/start_backend.sh
# 访问: http://127.0.0.1:5000
```

**启动前端**（新终端）：
```bash
./scripts/start_frontend.sh
# 访问: http://localhost:5173
```

## 📁 项目结构

```
puxian-rag-assistant/
├── backend/                 # Flask 后端
│   ├── app/
│   │   ├── __init__.py     # 应用工厂
│   │   ├── config.py       # 配置管理
│   │   ├── routes/         # 路由（chat, knowledge, health）
│   │   ├── services/       # 服务层（qwen, embedding, rag, knowledge）
│   │   └── utils/          # 工具（file_parser）
│   ├── run.py              # 启动脚本
│   └── requirements.txt    # Python 依赖
│
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── views/          # ChatView, KnowledgeView
│   │   ├── components/     # NavBar
│   │   ├── router/         # 路由配置
│   │   └── api/            # API 客户端
│   ├── package.json
│   └── vite.config.js
│
├── data/                   # 数据目录
│   ├── knowledge/          # 知识库文件
│   └── vectorstore/        # ChromaDB 向量库
│
├── scripts/                # 启动脚本
│   ├── init.sh             # 初始化
│   ├── start_backend.sh    # 后端启动
│   └── start_frontend.sh   # 前端启动
│
├── docs/                   # 文档
└── .env                    # 环境变量
```

## 🔧 功能说明

### 智能对话（Chat）

- 支持 RAG 问答
- 显示参考来源
- 示例问题引导
- Markdown 格式化

### 知识库管理（Knowledge）

- 文件上传（CSV, PDF, TXT, DOCX, MD）
- 文件列表查看
- 文件删除
- 向量库重建

## 🌐 API 接口

### 健康检查
```
GET /health
```

### 对话
```
POST /api/chat
Body: { "question": "你的问题" }
```

### 知识库管理
```
POST   /api/knowledge/upload      # 上传文件
GET    /api/knowledge/list        # 列出文件
DELETE /api/knowledge/delete/:id  # 删除文件
POST   /api/knowledge/rebuild     # 重建向量库
```

### 统计信息
```
GET /api/stats
```

## 🛠️ 开发

### 后端开发

```bash
cd backend
conda activate qwen_rag
python run.py
```

### 前端开发

```bash
cd frontend
nvm use 18
npm run dev
```

## 📦 依赖

### Python（后端）
- flask==3.1.2
- transformers==4.37.0
- sentence-transformers
- chromadb==0.4.22
- auto-gptq
- pdfminer.six
- python-docx

### Node.js（前端）
- vue@^3.4.0
- vue-router@^4.2.0
- axios@^1.6.0
- marked@^11.0.0
- vite@^5.0.0

## 🔍 使用示例

1. **上传知识库**
   - 进入"知识库"页面
   - 点击"选择文件"
   - 选择 CSV/PDF/TXT 文件
   - 点击"上传"

2. **智能对话**
   - 进入"智能对话"页面
   - 输入问题
   - 查看回答和参考来源

## 🐛 故障排除

### 后端无法启动
- 检查 conda 环境：`conda activate qwen_rag`
- 检查依赖：`pip install -r requirements.txt`
- 检查 .env 文件中的模型路径

### 前端无法启动
- 检查 Node 版本：`nvm use 18`
- 安装依赖：`npm install`
- 检查后端是否运行（前端需要代理到后端）

### 模型加载失败
- 确认模型路径正确（绝对路径）
- 检查 CUDA 是否可用
- 检查显存是否足够（至少 4.5GB）

## 📝 许可

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系

如有问题，请提交 Issue。
