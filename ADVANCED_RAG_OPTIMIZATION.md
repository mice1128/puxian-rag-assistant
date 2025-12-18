# Advanced RAG 深度优化文档

## 📋 优化总览

### Phase 1: 基础增强（已完成 ✅）
- **混合检索**: Vector Search + BM25
- **RRF 融合**: Reciprocal Rank Fusion
- **智能重排序**: BGE Reranker

### Phase 2: 深度优化（已完成 ✅）
- **Query Rewrite**: 查询改写与扩展
- **Document Optimization**: 智能文档处理
- **Prompt Engineering**: Few-shot + Chain-of-Thought

---

## 🚀 Advanced RAG v2 核心功能

### 1. Query Rewrite（查询改写器）

#### 功能
使用 LLM 将用户查询改写为多个变体，从不同角度提升召回率。

#### 三种策略
```python
# 1. expand - 扩展查询（添加同义词）
原查询: "莆田话中'吃'怎么说？"
改写:
  - "莆田话或莆仙方言中表示'吃饭'、'食用'的词汇是什么？"
  - "在莆仙语中，'吃'字的发音和对应词汇"
  - "莆田话'吃东西'、'进食'怎么表达"

# 2. clarify - 澄清查询（消除歧义）
原查询: "走怎么说"
改写: "莆田话中'走路'、'行走'这个动作怎么说"

# 3. multi - 多角度（定义/用法/例句）
原查询: "食"
改写:
  - "莆田话'食'字的定义和含义"
  - "'食'在莆田话中的使用场景和用法"
  - "莆田话'食'字的例句和实际应用"
```

#### 优势
- **提升召回率**: 多个查询变体覆盖更多相关文档
- **消除歧义**: 将模糊查询澄清为精确表达
- **多角度检索**: 从定义、用法、例句等不同维度召回

---

### 2. Enhanced Prompt（增强提示词）

#### Few-shot Learning
提供真实的问答示例，让 LLM 学习回答模式：

```python
示例:
用户问: 莆田话中'走'怎么说？
参考资料: 莆仙话: 行, 国际音标: [kiã], 普通话: 走

回答: 在莆田话中，'走'说作'行'，发音为 [kiã]。

例如：
- 我要去行街（我要去逛街）
- 行去学堂（走去学校）

这个词保留了古汉语的用法，'行'在古代就有'走'的意思。
```

#### Chain-of-Thought（思维链）
引导 LLM 按步骤思考：

```
回答步骤:
1. 从参考资料中提取关键信息
2. 给出莆田话的说法和发音
3. 提供使用例句
4. 补充文化或语言学背景
```

#### 优势
- **结构化输出**: 答案更有条理
- **内容丰富**: 不仅给答案，还提供例句和背景
- **一致性好**: 所有回答遵循相同格式

---

### 3. 多查询混合检索

#### 工作流程
```
用户查询 → Query Rewrite (1→4 queries)
              ↓
    [查询1]  [查询2]  [查询3]  [查询4]
       ↓        ↓        ↓        ↓
  Vector+BM25 融合（每个查询独立检索）
              ↓
    RRF 融合所有结果
              ↓
       Reranker 重排序
              ↓
      Top-K 最相关文档
```

#### 代码示例
```python
rag = AdvancedRAGv2()

result = rag.generate(
    query="莆田话中'吃'怎么说？",
    use_query_rewrite=True,    # 启用查询改写
    retrieval_top_k=15,         # 混合检索召回 15 个
    final_top_k=3,              # Reranker 保留 3 个
    verbose=True
)

print(result['answer'])
```

---

## 📊 v1 vs v2 对比

| 维度 | v1 (基础版) | v2 (深度优化版) |
|------|------------|----------------|
| **查询处理** | 单查询 | 多查询变体（1→4） |
| **检索召回** | Vector + BM25 | 多查询 × (Vector + BM25) |
| **提示词** | 简单模板 | Few-shot + CoT |
| **答案质量** | 基础准确 | 详细 + 例句 + 背景 |
| **召回率** | 中 | 高（多角度） |
| **答案结构** | 简单 | 结构化 |
| **响应时间** | ~3s | ~5s（额外 2s 用于改写） |

---

## 🔧 使用指南

### 快速开始
```bash
# 1. 测试 v2
python test_v2_simple.py

# 2. 对比 v1 vs v2
python test_rag_v1_v2.py
```

### 集成到应用
```python
from advanced_rag_v2 import AdvancedRAGv2

# 初始化
rag = AdvancedRAGv2(
    collection_name="putian_dialect",
    embedding_model_path="/home/zl/LLM/bge-small-zh-v1.5",
    reranker_model_path="BAAI/bge-reranker-base",
    chroma_db_path="/home/zl/LLM/chroma_db_putian",
    vllm_api_url="http://127.0.0.1:8001/v1"
)

# 使用
result = rag.generate(
    query="你的问题",
    use_query_rewrite=True,  # 是否启用查询改写
    retrieval_top_k=15,       # 召回文档数
    final_top_k=3,            # 最终使用文档数
    verbose=True              # 是否打印详细日志
)

# 结果
print("答案:", result['answer'])
print("改写查询:", result['rewritten_queries'])
print("检索文档数:", result['num_docs'])
```

---

## 🎯 下一步优化方向

### Phase 3: 生产部署（可选）
1. **API 封装**: FastAPI 服务化
2. **缓存机制**: Redis 缓存热门查询
3. **性能优化**: 
   - 批量检索
   - 异步处理
   - GPU 优化
4. **监控日志**:
   - 查询日志
   - 性能指标
   - 错误追踪

### Phase 4: 高级功能（可选）
1. **多轮对话**: 上下文记忆
2. **个性化**: 用户偏好学习
3. **反馈循环**: 用户反馈优化
4. **多模态**: 支持音频输入/输出

---

## 📈 性能评估

### 预期提升（v2 相比 v1）
- **召回率**: +15-25%（多查询变体）
- **答案质量**: +30-40%（Few-shot + CoT）
- **用户满意度**: +20-30%（结构化输出）
- **响应时间**: +40%（~3s → ~5s）

### 测试建议
```python
# 准备测试集
test_queries = [
    "莆田话中'吃'怎么说？",
    "莆田话的'去'怎么发音",
    "莆仙方言'来'字的读音",
    # ... 更多测试查询
]

# 对比测试
for query in test_queries:
    v1_result = rag_v1.generate(query)
    v2_result = rag_v2.generate(query)
    
    # 人工评估
    # 1. 答案准确性
    # 2. 内容丰富度
    # 3. 格式规范性
```

---

## 🛠️ 故障排除

### 常见问题

#### 1. Query Rewrite 失败
**症状**: 返回空列表或格式错误
**解决**: 
```python
# 降低温度参数
self.llm_service.generate(
    prompt=prompt,
    temperature=0.1  # 降低随机性
)
```

#### 2. 响应时间过长
**症状**: 超过 10s
**解决**:
```python
# 减少查询变体数量
queries = queries[:2]  # 只用前2个

# 减少召回文档数
retrieval_top_k=10  # 从 15 降到 10
```

#### 3. 内存不足
**症状**: CUDA out of memory
**解决**:
```bash
# 使用更小的 Reranker
export RERANKER_MODEL="BAAI/bge-reranker-small"

# 或禁用 Reranker
reranker = None
```

---

## 📝 代码文件说明

```
puxian-rag-assistant/
├── advanced_rag.py              # v1: 基础版（Hybrid + Rerank）
├── advanced_rag_v2.py           # v2: 深度优化版（+Query Rewrite +Enhanced Prompt）
├── test_rag_v1_v2.py           # 对比测试脚本
├── test_v2_simple.py           # v2 简化测试
└── ADVANCED_RAG_OPTIMIZATION.md # 本文档
```

---

## ✅ 完成检查清单

- [x] Phase 1: Hybrid Search (Vector + BM25)
- [x] Phase 1: RRF Fusion
- [x] Phase 1: BGE Reranker
- [x] Phase 2: Query Rewrite（3种策略）
- [x] Phase 2: Enhanced Prompt（Few-shot + CoT）
- [x] Phase 2: 多查询混合检索
- [x] 创建对比测试脚本
- [x] 编写使用文档

**🎉 恭喜！Advanced RAG v2 深度优化完成！**
