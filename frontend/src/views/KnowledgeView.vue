<template>
  <div class="knowledge-view">
    <div class="container">
      <div class="card">
        <h2>📚 知识库管理</h2>
        
        <!-- 上传区域 -->
        <div class="upload-section">
          <div class="upload-info">
            <p>支持的文件格式：CSV, PDF, TXT, DOCX, MD</p>
            <p class="hint">上传文件后将自动添加到向量库</p>
          </div>
          
          <div class="upload-area">
            <input 
              type="file" 
              ref="fileInput"
              @change="handleFileSelect"
              accept=".csv,.pdf,.txt,.docx,.md"
              style="display: none"
            />
            <button @click="$refs.fileInput.click()" class="btn btn-primary">
              📁 选择文件
            </button>
            <button 
              v-if="selectedFile"
              @click="uploadFile"
              :disabled="uploading"
              class="btn btn-primary"
            >
              {{ uploading ? '上传中...' : '✅ 上传' }}
            </button>
            <span v-if="selectedFile" class="file-name">{{ selectedFile.name }}</span>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="actions">
          <button @click="loadFiles" class="btn btn-primary">
            🔄 刷新列表
          </button>
          <button @click="rebuildVectorstore" class="btn btn-primary">
            🔨 重建向量库
          </button>
        </div>
        
        <!-- 文件列表 -->
        <div class="file-list">
          <h3>已上传文件 ({{ files.length }})</h3>
          
          <div v-if="loading" class="loading">加载中...</div>
          
          <table v-else-if="files.length" class="files-table">
            <thead>
              <tr>
                <th>文件名</th>
                <th>格式</th>
                <th>大小</th>
                <th>修改时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="file in files" :key="file.name">
                <td>{{ file.name }}</td>
                <td>
                  <span class="file-type">{{ file.extension }}</span>
                </td>
                <td>{{ formatFileSize(file.size) }}</td>
                <td>{{ formatDate(file.modified) }}</td>
                <td>
                  <button 
                    @click="deleteFile(file.name)"
                    class="btn btn-danger btn-sm"
                  >
                    🗑️ 删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-else class="empty-state">
            <p>暂无文件，请上传知识库文件</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'KnowledgeView',
  
  data() {
    return {
      files: [],
      selectedFile: null,
      loading: false,
      uploading: false
    }
  },
  
  mounted() {
    this.loadFiles()
  },
  
  methods: {
    async loadFiles() {
      this.loading = true
      try {
        const res = await api.listFiles()
        if (res.status === 'success') {
          this.files = res.data
        }
      } catch (error) {
        alert('加载文件列表失败：' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    handleFileSelect(event) {
      this.selectedFile = event.target.files[0]
    },
    
    async uploadFile() {
      if (!this.selectedFile) return
      
      this.uploading = true
      try {
        const res = await api.uploadFile(this.selectedFile)
        
        if (res.status === 'success') {
          alert(res.message)
          this.selectedFile = null
          this.$refs.fileInput.value = ''
          await this.loadFiles()
        } else {
          throw new Error(res.message)
        }
      } catch (error) {
        alert('上传失败：' + error.message)
      } finally {
        this.uploading = false
      }
    },
    
    async deleteFile(filename) {
      if (!confirm(`确定要删除文件 "${filename}" 吗？`)) return
      
      try {
        const res = await api.deleteFile(filename)
        
        if (res.status === 'success') {
          alert(res.message)
          await this.loadFiles()
        } else {
          throw new Error(res.message)
        }
      } catch (error) {
        alert('删除失败：' + error.message)
      }
    },
    
    async rebuildVectorstore() {
      if (!confirm('确定要重建向量库吗？这将重新处理所有文件。')) return
      
      this.loading = true
      try {
        const res = await api.rebuildVectorstore()
        
        if (res.status === 'success') {
          alert(res.message)
        } else {
          throw new Error(res.message)
        }
      } catch (error) {
        alert('重建失败：' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
    },
    
    formatDate(dateStr) {
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.knowledge-view {
  padding: 20px 0;
  min-height: calc(100vh - 60px);
}

.card h2 {
  margin: 0 0 20px 0;
  color: #333;
}

.upload-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.upload-info {
  margin-bottom: 15px;
}

.upload-info p {
  margin: 5px 0;
  color: #666;
}

.upload-info .hint {
  font-size: 14px;
  color: #999;
}

.upload-area {
  display: flex;
  gap: 10px;
  align-items: center;
}

.file-name {
  color: #1890ff;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.file-list h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.files-table {
  width: 100%;
  border-collapse: collapse;
}

.files-table th,
.files-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

.files-table th {
  background: #fafafa;
  font-weight: 600;
  color: #333;
}

.files-table tbody tr:hover {
  background: #f9f9f9;
}

.file-type {
  display: inline-block;
  padding: 2px 8px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 13px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>
