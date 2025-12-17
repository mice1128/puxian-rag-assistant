# 快速开始

## 5 分钟上手指南

### 前置条件

确保已安装：
- ✅ Conda（Python 环境管理）
- ✅ nvm（Node.js 版本管理）
- ✅ CUDA GPU（可选，推荐）

### 步骤 1：初始化项目

```bash
cd /home/zl/LLM/puxian-rag-assistant
./scripts/init.sh
```

这会：
- 创建 `.env` 配置文件
- 创建数据目录
- 安装后端依赖（Python）
- 安装前端依赖（Node.js）

### 步骤 2：配置模型路径

编辑 `.env` 文件：

```bash
vim .env  # 或使用你喜欢的编辑器
```

修改模型路径：
```
QWEN_MODEL_PATH=/home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4
EMBEDDING_MODEL_PATH=/home/zl/LLM/bge-small-zh-v1.5
```

### 步骤 3：启动后端

新开一个终端：
```bash
cd /home/zl/LLM/puxian-rag-assistant
./scripts/start_backend.sh
```

等待模型加载（首次较慢），看到：
```
✅ 莆仙话 RAG 助手启动成功
🚀 启动 Flask 开发服务器...
```

### 步骤 4：启动前端

再新开一个终端：
```bash
cd /home/zl/LLM/puxian-rag-assistant
./scripts/start_frontend.sh
```

看到：
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### 步骤 5：访问应用

打开浏览器访问：
```
http://localhost:5173
```

## 第一次使用

### 1. 上传知识库

1. 点击顶部导航栏的 **📚 知识库**
2. 点击 **📁 选择文件**
3. 选择你的知识库文件（CSV/PDF/TXT/DOCX/MD）
4. 点击 **✅ 上传**

### 2. 开始对话

1. 点击顶部导航栏的 **💬 智能对话**
2. 在输入框输入问题
3. 按 Enter 发送
4. 查看回答和参考来源

## 示例数据

### CSV 格式（推荐）

创建 `putian_dialect.csv`：

```csv
汉字,莆仙话拼音,释义
天,tieng,天空
地,dei,大地
人,ning,人类
```

### TXT 格式

创建 `knowledge.txt`：

```
莆仙话简介

莆仙话，又称莆仙语，是闽语的一个分支。

主要分布在福建省莆田市和仙游县。
```

## 常见问题

### Q: 后端启动失败？

**检查 Conda 环境**
```bash
conda activate qwen_rag
conda list | grep flask
```

**重新安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

### Q: 前端无法连接后端？

**确认后端正在运行**
```bash
curl http://127.0.0.1:5000/health
```

应该返回：
```json
{"status": "healthy", ...}
```

### Q: 模型加载失败？

**检查模型路径**
```bash
ls -la /home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4
ls -la /home/zl/LLM/bge-small-zh-v1.5
```

确保路径存在且包含模型文件。

### Q: 显存不足？

Qwen2.5-7B-GPTQ-Int4 需要约 4.5GB VRAM。

**检查显存使用**
```bash
nvidia-smi
```

**降低并发或使用 CPU**（较慢）

## 下一步

- 📖 阅读 [README.md](../README.md) 了解架构
- 🔌 查看 [API.md](./API.md) 学习 API 使用
- 🛠️ 自定义配置文件 `.env`
- 📚 准备更多知识库文件

## 获取帮助

遇到问题？
1. 查看终端日志
2. 检查 `logs/app.log`
3. 提交 GitHub Issue
