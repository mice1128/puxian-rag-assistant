# API 文档

## 基础信息

- **Base URL**: `http://127.0.0.1:5000`
- **API Prefix**: `/api`
- **Content-Type**: `application/json`

## 接口列表

### 1. 健康检查

检查服务状态。

**请求**
```
GET /health
```

**响应**
```json
{
  "status": "healthy",
  "service": "Puxian RAG Assistant",
  "version": "1.0.0"
}
```

---

### 2. 获取统计信息

获取系统统计信息。

**请求**
```
GET /api/stats
```

**响应**
```json
{
  "status": "success",
  "data": {
    "total_documents": 1234,
    "vectorstore_path": "/path/to/chroma_db"
  }
}
```

---

### 3. 智能对话

基于 RAG 的问答接口。

**请求**
```
POST /api/chat
Content-Type: application/json

{
  "question": "你的问题"
}
```

**响应**
```json
{
  "status": "success",
  "data": {
    "answer": "这是回答内容...",
    "sources": [
      {
        "text": "参考资料1",
        "metadata": {
          "source": "file.csv",
          "row": 1
        }
      }
    ],
    "tokens_used": 256
  }
}
```

**错误响应**
```json
{
  "status": "error",
  "message": "错误信息"
}
```

---

### 4. 上传知识库文件

上传文件到知识库。

**请求**
```
POST /api/knowledge/upload
Content-Type: multipart/form-data

file: <文件>
```

**支持格式**: CSV, PDF, TXT, DOCX, MD

**响应**
```json
{
  "status": "success",
  "message": "文件上传成功，已添加 100 条知识",
  "data": {
    "filename": "knowledge.csv",
    "added_count": 100,
    "total_documents": 1234
  }
}
```

---

### 5. 列出知识库文件

获取所有已上传的文件。

**请求**
```
GET /api/knowledge/list
```

**响应**
```json
{
  "status": "success",
  "data": [
    {
      "name": "knowledge.csv",
      "size": 12345,
      "modified": "2024-01-01T12:00:00",
      "extension": ".csv"
    }
  ]
}
```

---

### 6. 删除知识库文件

删除指定文件。

**请求**
```
DELETE /api/knowledge/delete/<filename>
```

**响应**
```json
{
  "status": "success",
  "message": "文件 knowledge.csv 已删除"
}
```

---

### 7. 重建向量库

重新处理所有知识库文件，重建向量库。

**请求**
```
POST /api/knowledge/rebuild
```

**响应**
```json
{
  "status": "success",
  "message": "向量库重建成功，共 1234 条知识",
  "data": {
    "total_count": 1234,
    "files_processed": ["file1.csv", "file2.pdf"]
  }
}
```

---

## 状态码

- `200`: 成功
- `400`: 请求错误（参数不正确）
- `404`: 资源不存在
- `500`: 服务器错误
- `501`: 功能未实现

## 错误处理

所有错误响应格式：

```json
{
  "status": "error",
  "message": "具体错误信息"
}
```

## 使用示例

### cURL

**对话接口**
```bash
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "莆仙话中天字怎么说？"}'
```

**上传文件**
```bash
curl -X POST http://127.0.0.1:5000/api/knowledge/upload \
  -F "file=@knowledge.csv"
```

### Python

```python
import requests

# 对话
response = requests.post(
    'http://127.0.0.1:5000/api/chat',
    json={'question': '你的问题'}
)
data = response.json()
print(data['data']['answer'])

# 上传文件
with open('knowledge.csv', 'rb') as f:
    response = requests.post(
        'http://127.0.0.1:5000/api/knowledge/upload',
        files={'file': f}
    )
print(response.json())
```

### JavaScript (Axios)

```javascript
import axios from 'axios'

// 对话
const chatResponse = await axios.post('/api/chat', {
  question: '你的问题'
})
console.log(chatResponse.data.data.answer)

// 上传文件
const formData = new FormData()
formData.append('file', file)

const uploadResponse = await axios.post('/api/knowledge/upload', formData)
console.log(uploadResponse.data.message)
```

## 限制

- 单次请求超时：60 秒
- 文件上传大小限制：根据 Flask 配置（建议不超过 100MB）
- 并发请求：建议不超过 10 个

## 注意事项

1. 所有路径使用绝对路径
2. 模型加载需要时间，首次请求可能较慢
3. 向量库重建是耗时操作，谨慎使用
4. 文件上传会自动更新向量库
