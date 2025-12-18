# 推理引擎模块

独立的模型推理引擎，支持多种推理后端，无需依赖完整的后端/前端架构。

## 🎯 功能特性

### 支持的推理引擎
1. **Transformers 原生** - Hugging Face 原生推理
   - 简单易用，兼容性好
   - 适合开发和调试
   - 单请求推理

2. **vLLM 优化** - 高性能推理引擎
   - PagedAttention 内存优化
   - Continuous Batching 动态批处理
   - 优化的 CUDA kernels
   - 高吞吐量，低延迟

### 核心优势
- ✅ 独立运行，不依赖后端
- ✅ 统一接口，易于切换
- ✅ 性能基准测试
- ✅ 批处理支持
- ✅ GPU 灵活配置

## 📦 安装依赖

### Transformers 引擎
```bash
# 已在 backend/requirements.txt 中
pip install torch==2.1.2 transformers==4.37.0
```

### vLLM 引擎（新增）
```bash
# 安装 vLLM
pip install vllm

# 注意：vLLM 要求
# - CUDA >= 11.8
# - Python >= 3.8
# - 足够的 GPU 显存
```

## 🚀 快速开始

### 1. 基础使用

```python
from inference_engine import TransformersEngine, VLLMEngine
from inference_engine.config import InferenceConfig

# 创建配置
config = InferenceConfig(
    model_path="/home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4",
    gpu_id=1,
    max_tokens=512,
    temperature=0.7
)

# 使用 Transformers 引擎
tf_engine = TransformersEngine(config)
tf_engine.load_model()
result = tf_engine.generate("莆仙话中祭祀怎么说？")
print(result['text'])

# 使用 vLLM 引擎
vllm_engine = VLLMEngine(config)
vllm_engine.load_model()
result = vllm_engine.generate("莆仙话中祭祀怎么说？")
print(result['text'])
```

### 2. 批量推理

```python
# vLLM 批处理（高效）
prompts = [
    "莆仙话中祭祀怎么说？",
    "莆仙话的"厝"是什么意思？",
    "如何用莆仙话说"吃饭"？"
]

results = vllm_engine.batch_generate(prompts)
for r in results:
    print(f"输出: {r['text']}")
    print(f"吞吐: {r['throughput']} tokens/s")
```

### 3. 性能对比测试

```bash
# 基础对比测试
cd /home/zl/LLM/puxian-rag-assistant
conda run -n qwen_rag python inference_engine/benchmark.py

# 指定参数
python inference_engine/benchmark.py \
    --model-path /home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4 \
    --gpu-id 1 \
    --num-runs 5 \
    --batch-test \
    --output results/inference_benchmark.json
```

## 📊 性能指标

### 预期性能提升（vLLM vs Transformers）

| 指标 | Transformers | vLLM | 提升 |
|------|--------------|------|------|
| 延迟 | ~2.5s | ~0.8s | **3x** |
| 吞吐量 | ~50 tokens/s | ~150 tokens/s | **3x** |
| 批处理 | 串行 | 并行优化 | **5-10x** |
| 显存利用 | ~5GB | ~6GB | 略高 |

*实际性能取决于硬件和模型*

## 🔧 配置说明

### InferenceConfig 参数

```python
@dataclass
class InferenceConfig:
    # 模型路径
    model_path: str = "/home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4"
    
    # GPU 配置
    gpu_id: int = 1  # 使用 GPU 1
    tensor_parallel_size: int = 1  # 张量并行（多GPU）
    
    # 生成参数
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    
    # vLLM 特定
    quantization: str = "gptq"  # GPTQ 量化
    gpu_memory_utilization: float = 0.9  # GPU 显存利用率
```

## 🏗️ 架构设计

```
inference_engine/
├── __init__.py              # 模块入口
├── config.py                # 配置管理
├── base_engine.py           # 抽象基类
├── transformers_engine.py   # Transformers 实现
├── vllm_engine.py          # vLLM 实现
└── benchmark.py            # 性能测试
```

### 类层次

```
BaseInferenceEngine (抽象基类)
├── load_model()        # 加载模型
├── generate()          # 单个生成
├── batch_generate()    # 批量生成
├── warmup()            # 预热
└── benchmark()         # 性能测试

TransformersEngine      # Transformers 实现
VLLMEngine             # vLLM 实现
```

## 🎯 使用场景

### 场景 1: 开发调试
- 使用 **TransformersEngine**
- 简单直接，容易调试
- 适合快速验证逻辑

### 场景 2: 生产部署
- 使用 **VLLMEngine**
- 高性能，低延迟
- 支持高并发

### 场景 3: 批量处理
- 使用 **VLLMEngine.batch_generate()**
- 自动优化批处理
- 吞吐量提升 5-10x

## 🔗 集成到现有项目

### 集成到 RAG 服务

```python
# backend/app/services/rag_service.py
from inference_engine import VLLMEngine
from inference_engine.config import InferenceConfig

class RAGService:
    def __init__(self):
        # 使用 vLLM 替代原生 Transformers
        config = InferenceConfig(gpu_id=1)
        self.llm = VLLMEngine(config)
        self.llm.load_model()
    
    def ask(self, question):
        # 构建提示词
        prompt = f"问题：{question}\n答案："
        
        # 使用 vLLM 生成
        result = self.llm.generate(prompt)
        return result['text']
```

## 📈 性能优化建议

### vLLM 配置优化

1. **显存利用率**
   ```python
   config.gpu_memory_utilization = 0.95  # 提高到 95%
   ```

2. **张量并行**（多 GPU）
   ```python
   config.tensor_parallel_size = 2  # 使用 2 个 GPU
   ```

3. **最大序列长度**
   ```python
   config.max_model_len = 4096  # 限制最大长度节省显存
   ```

### 批处理最佳实践

```python
# 动态批处理（vLLM 自动优化）
prompts = collect_prompts()  # 收集多个请求
results = vllm_engine.batch_generate(prompts)
```

## 🐛 故障排查

### vLLM 安装问题
```bash
# CUDA 不兼容
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu118

# 显存不足
# 降低 gpu_memory_utilization 或使用更小的模型
```

### 性能不如预期
- 检查 GPU 利用率: `nvidia-smi`
- 确保使用批处理
- 调整 `max_model_len` 和 `gpu_memory_utilization`

## 📝 开发计划

- [ ] 支持流式输出
- [ ] 实现 API 服务器模式
- [ ] 添加更多推理后端（TensorRT-LLM）
- [ ] 实现自动混合精度
- [ ] 添加性能监控 dashboard

## 📚 参考资料

- [vLLM 官方文档](https://docs.vllm.ai/)
- [Transformers 文档](https://huggingface.co/docs/transformers)
- [PagedAttention 论文](https://arxiv.org/abs/2309.06180)
