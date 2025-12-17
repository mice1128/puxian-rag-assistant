<template>
  <div class="chat-view">
    <div class="container">
      <div class="chat-container">
        <!-- 左侧信息面板 -->
        <aside class="info-panel">
          <div class="card">
            <h3>📊 系统信息</h3>
            <div class="stats" v-if="stats">
              <div class="stat-item">
                <span class="label">知识条目</span>
                <span class="value">{{ stats.total_documents }}</span>
              </div>
            </div>
          </div>
          
          <div class="card">
            <h3>💡 示例问题</h3>
            <div class="examples">
              <button 
                v-for="(example, idx) in examples" 
                :key="idx"
                @click="askExample(example)"
                class="example-btn"
              >
                {{ example }}
              </button>
            </div>
          </div>
        </aside>
        
        <!-- 右侧聊天区域 -->
        <main class="chat-area">
          <div class="card chat-card">
            <div class="messages" ref="messagesContainer">
              <div 
                v-for="(msg, idx) in messages" 
                :key="idx"
                :class="['message', msg.role]"
              >
                <div class="message-header">
                  <span class="role-tag">{{ msg.role === 'user' ? '👤 我' : '🤖 助手' }}</span>
                  <span class="time">{{ msg.time }}</span>
                </div>
                <div class="message-content" v-html="formatMessage(msg.content)"></div>
                
                <!-- 显示参考来源 -->
                <div v-if="msg.sources && msg.sources.length" class="sources">
                  <details>
                    <summary>📚 参考来源 ({{ msg.sources.length }})</summary>
                    <div class="source-item" v-for="(src, i) in msg.sources" :key="i">
                      {{ src.text.substring(0, 100) }}...
                    </div>
                  </details>
                </div>
              </div>
              
              <div v-if="loading" class="message assistant">
                <div class="message-header">
                  <span class="role-tag">🤖 助手</span>
                </div>
                <div class="message-content">
                  <div class="loading-dots">思考中<span>.</span><span>.</span><span>.</span></div>
                </div>
              </div>
            </div>
            
            <div class="input-area">
              <textarea 
                v-model="question"
                @keydown.enter.prevent="sendMessage"
                placeholder="请输入您的问题... (Shift+Enter 换行，Enter 发送)"
                rows="3"
              ></textarea>
              <button 
                @click="sendMessage"
                :disabled="loading || !question.trim()"
                class="btn btn-primary send-btn"
              >
                发送
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'
import { marked } from 'marked'

export default {
  name: 'ChatView',
  
  data() {
    return {
      question: '',
      messages: [],
      loading: false,
      stats: null,
      examples: [
        '"天"字莆仙话怎么说？',
        '请介绍一下莆仙语的声调系统',
        '莆仙话中"飯"字的读音是什么？'
      ]
    }
  },
  
  mounted() {
    this.loadStats()
  },
  
  methods: {
    async loadStats() {
      try {
        const res = await api.getStats()
        if (res.status === 'success') {
          this.stats = res.data
        }
      } catch (error) {
        console.error('加载统计失败:', error)
      }
    },
    
    async sendMessage() {
      if (!this.question.trim() || this.loading) return
      
      const userMessage = {
        role: 'user',
        content: this.question,
        time: new Date().toLocaleTimeString()
      }
      
      this.messages.push(userMessage)
      this.loading = true
      
      const currentQuestion = this.question
      this.question = ''
      
      try {
        const res = await api.chat(currentQuestion)
        
        if (res.status === 'success') {
          this.messages.push({
            role: 'assistant',
            content: res.data.answer,
            sources: res.data.sources,
            time: new Date().toLocaleTimeString()
          })
        } else {
          throw new Error(res.message)
        }
      } catch (error) {
        this.messages.push({
          role: 'assistant',
          content: '抱歉，处理您的问题时出现错误：' + error.message,
          time: new Date().toLocaleTimeString()
        })
      } finally {
        this.loading = false
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      }
    },
    
    askExample(example) {
      this.question = example
      this.sendMessage()
    },
    
    formatMessage(content) {
      return marked(content)
    },
    
    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    }
  }
}
</script>

<style scoped>
.chat-view {
  min-height: calc(100vh - 60px);
  padding: 20px 0;
}

.chat-container {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 左侧面板 */
.info-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-panel h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.stat-item .label {
  color: #666;
}

.stat-item .value {
  font-weight: 600;
  color: #1890ff;
}

.examples {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.example-btn {
  padding: 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s;
}

.example-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
  background: #e6f7ff;
}

/* 聊天区域 */
.chat-card {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  max-width: 80%;
  animation: fadeIn 0.3s;
}

.message.user {
  align-self: flex-end;
}

.message.assistant {
  align-self: flex-start;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.role-tag {
  font-weight: 600;
  font-size: 14px;
}

.time {
  font-size: 12px;
  color: #999;
}

.message-content {
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.6;
}

.user .message-content {
  background: #1890ff;
  color: white;
}

.assistant .message-content {
  background: #f5f5f5;
  color: #333;
}

.sources {
  margin-top: 10px;
  font-size: 13px;
}

.sources summary {
  cursor: pointer;
  color: #1890ff;
  margin-bottom: 8px;
}

.source-item {
  padding: 8px;
  background: #f9f9f9;
  border-left: 3px solid #1890ff;
  margin-bottom: 5px;
  font-size: 12px;
  color: #666;
}

.loading-dots {
  display: inline-block;
}

.loading-dots span {
  animation: blink 1.4s infinite;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

/* 输入区域 */
.input-area {
  border-top: 1px solid #e8e8e8;
  padding: 15px 20px;
  display: flex;
  gap: 10px;
}

.input-area textarea {
  flex: 1;
  padding: 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
}

.input-area textarea:focus {
  outline: none;
  border-color: #1890ff;
}

.send-btn {
  padding: 10px 30px;
  white-space: nowrap;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes blink {
  0%, 20% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}

@media (max-width: 768px) {
  .chat-container {
    grid-template-columns: 1fr;
  }
  
  .info-panel {
    order: 2;
  }
}
</style>
