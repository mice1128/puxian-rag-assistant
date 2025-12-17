import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API 错误:', error)
    return Promise.reject(error)
  }
)

export default {
  // 对话
  chat(question) {
    return apiClient.post('/chat', { question })
  },
  
  // 获取统计
  getStats() {
    return apiClient.get('/stats')
  },
  
  // 知识库管理
  uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/knowledge/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  listFiles() {
    return apiClient.get('/knowledge/list')
  },
  
  deleteFile(filename) {
    return apiClient.delete(`/knowledge/delete/${filename}`)
  },
  
  rebuildVectorstore() {
    return apiClient.post('/knowledge/rebuild')
  }
}
