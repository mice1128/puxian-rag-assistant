# 莆仙话 RAG 助手 - 技术栈

## 🎯 核心架构
- **模式**: RAG (Retrieval-Augmented Generation)
- **部署**: 单机本地部署，GPU 加速
- **架构**: 前后端分离

---

## 🤖 AI 模型层

### 大语言模型 (LLM)
- **模型**: Qwen2.5-7B-Instruct-GPTQ-Int4
- **量化**: 4-bit GPTQ (显存优化)
- **显存占用**: ~4.5GB
- **推理框架**: transformers 4.37.0 + auto-gptq 0.7.1

### 向量嵌入模型
- **模型**: BAAI/bge-small-zh-v1.5
- **维度**: 512维中文语义向量
- **框架**: sentence-transformers 2.5.0

### 模型加载策略
- **懒加载**: 首次调用时加载，减少启动时间
- **单例模式**: 全局共享模型实例
- **GPU 绑定**: 强制使用 GPU 1 (cuda:1)

---

## 🗄️ 数据层

### 向量数据库
- **数据库**: ChromaDB 0.4.22
- **存储**: 持久化本地文件系统
- **数据规模**: 5817 条莆仙话词汇
- **批处理**: 500条/批（规避API限制）

### 知识库数据
- **格式**: CSV (9列结构化数据)
- **字段**: 莆仙话、拼音、国际音标、释义、例句、文化注释等
- **来源**: hinghwa-RAG Markdown 转换

---

## ⚙️ 后端技术栈

### Web 框架
- **框架**: Flask 3.1.2
- **CORS**: flask-cors 6.0.2
- **API**: RESTful JSON API

### 深度学习框架
- **PyTorch**: 2.1.2 (兼容 CUDA 12.1)
- **torchvision**: 0.16.2
- **accelerate**: 0.26.1 (模型加载加速)
- **peft**: 0.7.1 (参数高效微调支持)

### 数据处理
- **numpy**: 1.26.4 (必须 1.x，2.x 不兼容)
- **pandas**: 2.2.0
- **文件解析**: pdfminer.six, python-docx, openpyxl

### 工具库
- **环境变量**: python-dotenv 1.0.0
- **配置**: pyyaml 6.0.1
- **进度条**: tqdm 4.66.1

---

## 🎨 前端技术栈

### 核心框架
- **框架**: Vue 3.4
- **路由**: Vue Router 4.2
- **构建工具**: Vite 5.0

### UI/交互
- **HTTP 客户端**: Axios 1.6
- **Markdown 渲染**: marked 11.0
- **样式**: 原生 CSS

### 页面结构
- **对话页**: 实时 RAG 问答
- **知识库管理**: 文件上传、查看、删除

---

## 🖥️ 硬件环境

### GPU 配置
- **显卡**: 2 × NVIDIA Quadro RTX 5000 (16GB × 2)
- **CUDA**: 12.9 (Driver 575.57.08)
- **使用策略**: GPU 1 专用于 RAG 推理

### 系统环境
- **OS**: Linux
- **Python**: 3.10 (conda 环境: qwen_rag)
- **Node.js**: 18.20.8 (通过 nvm 管理)

---

## 📊 RAG 流程配置

### 检索参数
- **TOP_K**: 3 (默认检索 3 条最相关文档)
- **相似度**: 余弦距离

### 生成参数
- **max_tokens**: 512
- **temperature**: 0.7
- **top_p**: 0.9
- **do_sample**: True

---

## 🔧 开发工具

### 测试工具
- **CLI 测试**: test_qwen.py, test_knowledge.py, test_rag.py
- **评估框架**: evaluation/ (质量、检索、性能、批量测试)

### 脚本工具
- **环境初始化**: scripts/init.sh
- **启动脚本**: scripts/start_backend.sh, start_frontend.sh
- **数据转换**: scripts/convert_markdown_to_csv.py

---

## 📦 项目结构
```
puxian-rag-assistant/
├── backend/              # Flask 后端
│   ├── app/
│   │   ├── services/     # RAG/Qwen/Embedding 服务
│   │   ├── routes/       # API 路由
│   │   └── utils/        # 文件解析工具
│   └── requirements.txt
├── frontend/             # Vue 3 前端
│   ├── src/
│   │   ├── views/        # ChatView + KnowledgeView
│   │   └── components/   # NavBar 等组件
│   └── package.json
├── data/
│   ├── knowledge/        # CSV 知识库文件
│   └── vectorstore/      # ChromaDB 持久化存储
├── evaluation/           # 评估实验框架
├── tests/                # CLI 测试脚本
└── scripts/              # 启动/转换脚本
```

---

## ⚠️ 已知约束

### 版本兼容性
- **torch 2.1.2**: 不能升级到 2.9+ (有兼容性问题)
- **numpy 1.26.4**: 必须 1.x，2.x 会导致崩溃
- **transformers 4.37.0**: 不能升级到 4.5x+ (peft 依赖冲突)

### 性能限制
- **ChromaDB 批处理**: 单次最多 ~5461 条记录
- **模型加载**: 首次加载需 10-20 秒
- **显存峰值**: 约 5GB (模型 + 推理)

---

## 🎯 优化方向建议

### 1. 模型层
- [ ] 尝试更大模型 (Qwen2.5-14B) 提升准确性
- [ ] 测试其他嵌入模型 (bge-base-zh, m3e-base)
- [ ] 实现流式输出 (Server-Sent Events)

### 2. RAG 策略
- [ ] 引入 Reranker 二次排序
- [ ] 实现混合检索 (向量 + BM25)
- [ ] 动态 TOP_K (根据置信度调整)

### 3. 性能优化
- [ ] vLLM 部署加速推理
- [ ] 模型量化进一步压缩 (AWQ)
- [ ] 实现批处理推理

### 4. 功能扩展
- [ ] 对话历史记忆 (多轮对话)
- [ ] 用户反馈机制 (收集标注数据)
- [ ] 知识库自动更新

### 5. 工程化
- [ ] Docker 容器化部署
- [ ] API 接口文档 (Swagger/OpenAPI)
- [ ] 监控和日志系统 (Prometheus + Grafana)

---

**生成时间**: 2025-12-16  
**版本**: v1.0  
**联系**: 用于技术讨论和优化方案制定
