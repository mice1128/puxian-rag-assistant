<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <h1>🗣️ 莆仙话 RAG 助手</h1>
      </div>
      <div class="nav-links">
        <router-link to="/chat" class="nav-link">💬 智能对话</router-link>
        <router-link to="/knowledge" class="nav-link">📚 知识库</router-link>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavBar'
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
  font-weight: 500;
}

.nav-link:hover {
  background-color: rgba(255,255,255,0.1);
}

.nav-link.router-link-active {
  background-color: rgba(255,255,255,0.2);
}
</style>
