# 本地测试脚本

本目录包含命令行测试脚本，无需启动前后端即可测试所有功能。

## 📋 脚本列表

### 1. test_qwen.py - Qwen 模型对话测试

直接与 Qwen 模型对话，不使用 RAG。

**使用方法：**
```bash
cd /home/zl/LLM/puxian-rag-assistant
conda activate qwen_rag
python tests/test_qwen.py
```

**功能：**
- 加载 Qwen2.5-7B-GPTQ-Int4 模型
- 命令行交互式对话
- 显示 GPU 信息和 Token 使用量

---

### 2. test_knowledge.py - 知识库管理工具

导入、查看、搜索、清空知识库。

**使用方法：**

**导入文件到知识库：**
```bash
python tests/test_knowledge.py import --file data/knowledge/putian_dialect.csv
```

支持格式：CSV, PDF, TXT, DOCX, MD

**查看知识库统计：**
```bash
python tests/test_knowledge.py list
```

**搜索知识库：**
```bash
python tests/test_knowledge.py search --query "天字怎么说"
```

**清空知识库：**
```bash
python tests/test_knowledge.py clear
```

---

### 3. test_rag.py - RAG 问答测试

完整的 RAG 问答流程：检索 + 生成。

**使用方法：**
```bash
cd /home/zl/LLM/puxian-rag-assistant
conda activate qwen_rag
python tests/test_rag.py
```

**前提条件：**
必须先导入知识库（使用 test_knowledge.py）

**功能：**
- 基于知识库的智能问答
- 显示参考来源
- 显示相似度和元数据

---

## 🚀 快速开始

### 1. 激活环境
```bash
conda activate qwen_rag
cd /home/zl/LLM/puxian-rag-assistant
```

### 2. 导入知识库
```bash
python tests/test_knowledge.py import --file data/knowledge/putian_dialect.csv
```

### 3. 测试 RAG 问答
```bash
python tests/test_rag.py
```

---

## 💡 使用场景

### 场景 1：测试模型是否正常
```bash
python tests/test_qwen.py
# 输入: 你好
# 检查是否能正常回答
```

### 场景 2：批量导入知识库
```bash
# 导入 CSV
python tests/test_knowledge.py import --file data/knowledge/putian_dialect.csv

# 导入 PDF
python tests/test_knowledge.py import --file docs/某文档.pdf

# 导入 Markdown
python tests/test_knowledge.py import --file docs/README.md
```

### 场景 3：调试 RAG 效果
```bash
# 先搜索看检索是否准确
python tests/test_knowledge.py search --query "天字" --top-k 5

# 再测试 RAG 完整流程
python tests/test_rag.py
```

### 场景 4：重建知识库
```bash
# 清空
python tests/test_knowledge.py clear

# 重新导入
python tests/test_knowledge.py import --file data/knowledge/putian_dialect.csv

# 验证
python tests/test_knowledge.py list
```

---

## 🔧 参数说明

### test_knowledge.py

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| action | - | 操作类型 | import, list, search, clear |
| --file | -f | 文件路径 | data/knowledge/file.csv |
| --query | -q | 搜索查询 | "天字怎么说" |
| --top-k | -k | 返回数量 | 5 |

---

## 📝 注意事项

1. **首次运行较慢**：首次加载模型需要 10-20 秒
2. **显存要求**：Qwen2.5-7B-GPTQ-Int4 需要约 4.5GB VRAM
3. **知识库持久化**：导入的数据保存在 `data/vectorstore/chroma_db`
4. **环境隔离**：所有脚本使用 `qwen_rag` conda 环境

---

## 🐛 故障排除

### 问题 1：ModuleNotFoundError
```bash
# 确保在项目根目录运行
cd /home/zl/LLM/puxian-rag-assistant
python tests/test_rag.py
```

### 问题 2：CUDA out of memory
```bash
# 减少 max_new_tokens
# 编辑 .env 文件：MAX_TOKENS=256
```

### 问题 3：知识库为空
```bash
# 先导入知识库
python tests/test_knowledge.py import --file data/knowledge/putian_dialect.csv
```

---

## 📊 示例输出

### test_qwen.py 输出示例
```
============================================================
🤖 Qwen 模型对话测试
============================================================

设备信息:
  CUDA 可用: True
  GPU 数量: 2
  当前 GPU: 0
  GPU 名称: Quadro RTX 5000

初始化 Qwen 服务...
  模型路径: /home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4
  设备: cuda

加载模型（首次较慢，请稍候）...
✅ 模型加载完成！

============================================================
开始对话（输入 'exit' 或 'quit' 退出）
============================================================

你: 你好

助手: 你好！有什么我可以帮助你的吗？

[Token 数: 15]
```

### test_rag.py 输出示例
```
问题: 天字莆仙话怎么说？

正在思考...

回答:
------------------------------------------------------------
根据参考资料，"天"字在莆仙话中读作 "tieng"。
------------------------------------------------------------

📚 参考来源 (3 条):

  [1] 汉字: 天 | 莆仙话拼音: tieng | 释义: 天空
      元数据: {'source': 'putian_dialect.csv', 'row': 1}

💡 使用 Token: 128
```
