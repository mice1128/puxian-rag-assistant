# 评估实验说明

## 目录结构

```
evaluation/
├── README.md                   # 本文件
├── data/                       # 测试数据集
│   ├── test_questions.json     # 测试问题集
│   └── ground_truth.json       # 标准答案（可选）
├── results/                    # 评估结果
│   ├── rag_eval_*.json         # RAG 效果评估结果
│   ├── performance_*.json      # 性能测试结果
│   └── reports/                # 评估报告
├── eval_rag_quality.py         # RAG 质量评估
├── eval_performance.py         # 性能评估（速度、显存）
├── eval_retrieval.py           # 检索效果评估
├── batch_test.py               # 批量测试
└── analyze_results.py          # 结果分析与可视化
```

## 评估维度

### 1. RAG 质量评估 (eval_rag_quality.py)
- **准确性**: 答案是否正确回答问题
- **相关性**: 检索文档与问题的相关度
- **完整性**: 答案是否包含必要信息
- **幻觉检测**: 是否生成知识库外的内容

### 2. 检索效果评估 (eval_retrieval.py)
- **召回率@K**: 前K个结果中相关文档占比
- **精确率@K**: 前K个结果中的准确率
- **MRR**: 平均倒数排名
- **NDCG**: 归一化折损累积增益

### 3. 性能评估 (eval_performance.py)
- **推理速度**: Tokens/秒
- **显存占用**: VRAM 使用情况
- **端到端延迟**: 从问题到答案的时间
- **吞吐量**: QPS (Queries Per Second)

### 4. 批量测试 (batch_test.py)
- 自动运行测试集
- 支持多参数组合实验
- 生成详细日志

## 使用方法

### 1. 准备测试数据
```bash
# 创建测试问题集
python -c "
import json
questions = [
    {'id': 1, 'question': '莆仙话中祭祀怎么说？', 'category': '词汇'},
    {'id': 2, 'question': '莆仙话的声调有几个？', 'category': '语音'}
]
with open('evaluation/data/test_questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
"
```

### 2. 运行评估
```bash
# RAG 质量评估
conda run -n qwen_rag python evaluation/eval_rag_quality.py

# 检索效果评估
conda run -n qwen_rag python evaluation/eval_retrieval.py

# 性能评估
conda run -n qwen_rag python evaluation/eval_performance.py

# 批量测试
conda run -n qwen_rag python evaluation/batch_test.py --test-file data/test_questions.json
```

### 3. 分析结果
```bash
# 生成评估报告
conda run -n qwen_rag python evaluation/analyze_results.py --result-dir results/
```

## 实验配置

可以测试不同的参数组合：
- `TOP_K`: 1, 3, 5, 10
- `TEMPERATURE`: 0.1, 0.5, 0.7, 1.0
- `MAX_TOKENS`: 256, 512, 1024
- 嵌入模型: BGE-small, BGE-base, m3e-base

## 评估指标说明

### RAG 质量指标
- **答案准确性**: 1-5 分，人工评分或自动评估
- **检索相关性**: 检索文档与问题的余弦相似度
- **答案流畅度**: 语言通顺程度
- **幻觉率**: 答案中非知识库内容的比例

### 检索指标
- **Recall@K**: 前K个结果包含正确文档的比例
- **Precision@K**: 前K个结果中相关文档的比例
- **F1@K**: Precision 和 Recall 的调和平均
- **MRR**: Mean Reciprocal Rank

### 性能指标
- **Token 生成速度**: tokens/s
- **首Token延迟**: TTFT (Time To First Token)
- **显存峰值**: Peak VRAM usage
- **平均延迟**: 平均响应时间

## 注意事项

1. 评估前确保知识库已导入（5817条词汇）
2. 性能测试时关闭其他GPU任务
3. 批量测试建议在GPU 1上运行（避免影响GPU 0）
4. 结果自动保存在 `results/` 目录
