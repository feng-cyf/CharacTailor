<template>
  <div class="game-container">
    <div class="game-header">
      <h1>游戏功能</h1>
      <p>选择游戏和角色开始对战</p>
    </div>
    
    <div class="game-content-split">
      <!-- 五子棋界面 -->
      <div class="game-panel gomoku-panel">
        <div class="panel-header">
          <div class="game-icon-large">🪁</div>
          <h2>五子棋</h2>
        </div>
        <p class="game-description">五子连珠，谁与争锋</p>
        
        <div class="persona-section">
          <h3>选择对战角色</h3>
          <div class="persona-loading" v-if="isLoadingPersonas">
            <div class="loading-spinner"></div>
            <p>加载角色中...</p>
          </div>
          <div class="persona-list" v-else>
            <div 
              v-for="persona in personas" 
              :key="persona.persona_id"
              class="persona-item"
              :class="{ active: selectedGomokuPersona?.persona_id === persona.persona_id }"
              @click="selectedGomokuPersona = persona"
            >
              <div class="persona-avatar">{{ getPersonaAvatar(persona.persona_name) }}</div>
              <div class="persona-info">
                <h4>{{ persona.persona_name }}</h4>
                <span class="persona-model" :class="persona.is_cloud_model ? 'cloud' : 'local'">
                  {{ persona.is_cloud_model ? '云端模型' : '本地模型' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <button 
          class="start-game-btn"
          @click="startGomokuGame"
          :disabled="!selectedGomokuPersona"
        >
          🎮 开始五子棋 🎮
        </button>
      </div>
      
      <!-- 剧情体验界面 -->
      <div class="game-panel scene-panel">
        <div class="panel-header fade-in-down">
          <div class="game-icon-large animated-icon float">🎭</div>
          <h2>剧情体验</h2>
        </div>
        <p class="game-description fade-in-up">互动式剧情探索</p>
        
        <div class="scene-description improved">
          <div class="feature-list">
            <div class="feature-item fade-in-up delay-100">
              <span class="feature-icon float">✨</span>
              <span class="feature-text">多样化场景选择</span>
            </div>
            <div class="feature-item fade-in-up delay-200">
              <span class="feature-icon float">💬</span>
              <span class="feature-text">沉浸式对话体验</span>
            </div>
            <div class="feature-item fade-in-up delay-300">
              <span class="feature-icon float">🎨</span>
              <span class="feature-text">精美场景画面</span>
            </div>
          </div>
          <div class="scene-preview fade-in-up delay-300">
            <div class="preview-indicator">
              <span class="dot pulse"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>
        
        <button 
          class="start-game-btn scene-btn zoom-in delay-400"
          @click="startSceneGame"
        >
          🎬 开始剧情体验 🎬
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTokenStore } from '../utils/tokenStore'
import { getUserPersonas } from '../utils/api'

export default {
  name: 'Game',
  setup() {
    const router = useRouter()
    const tokenStore = useTokenStore()
    
    const personas = ref([])
    const selectedGomokuPersona = ref(null) // 五子棋角色选择
    const isLoadingPersonas = ref(false)
    
    // 获取用户角色列表
    const fetchUserPersonas = async () => {
      try {
        isLoadingPersonas.value = true
        const userInfo = tokenStore.getUserInfo()
        const userId = userInfo?.user_id || 'default_user'
        const response = await getUserPersonas(userId)
        
        if (response && response.code === 200 && response.data) {
          personas.value = Array.isArray(response.data) ? response.data : []
          // 自动选择第一个角色作为默认值
          if (personas.value.length > 0 && !selectedGomokuPersona.value) {
            selectedGomokuPersona.value = personas.value[0]
          }
        }
      } catch (error) {
        console.error('获取角色列表失败:', error)
      } finally {
        isLoadingPersonas.value = false
      }
    }
    
    // 获取角色头像（使用角色名首字母）
    const getPersonaAvatar = (name) => {
      return name ? name.charAt(0).toUpperCase() : '?'
    }
    
    // 开始五子棋游戏
    const startGomokuGame = () => {
      if (!selectedGomokuPersona.value) {
        return
      }
      
      // 跳转到五子棋游戏页面
      router.push({
        path: '/game/gomoku',
        query: {
          persona_id: selectedGomokuPersona.value.persona_id,
          persona_name: selectedGomokuPersona.value.persona_name
        }
      })
    }
    
    // 开始剧情体验游戏
    const startSceneGame = () => {
      // 跳转到剧情对话页面，不再传递角色参数
      router.push({
        path: '/scene/dialog'
      })
    }
    
    onMounted(() => {
      fetchUserPersonas()
    })
    
    return {
      personas,
      selectedGomokuPersona,
      isLoadingPersonas,
      startGomokuGame,
      startSceneGame,
      getPersonaAvatar
    }
  }
}
</script>

<style scoped>
.game-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.game-header {
  text-align: center;
  color: white;
  margin-bottom: 40px;
}

.game-header h1 {
  margin: 0 0 10px 0;
  font-size: 36px;
}

.game-header p {
  margin: 0;
  font-size: 18px;
  opacity: 0.9;
}

.game-content-split {
  flex: 1;
  display: flex;
  gap: 30px;
  padding: 20px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.game-panel {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.gomoku-panel {
  border: 3px solid transparent;
  background-clip: padding-box;
  position: relative;
}

.gomoku-panel::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: -1;
  margin: -3px;
  border-radius: 16px;
  background: linear-gradient(45deg, #ff6b6b, #ff8e53);
  opacity: 0.8;
}

.scene-panel {
  border: 3px solid transparent;
  background-clip: padding-box;
  position: relative;
}

.scene-panel::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: -1;
  margin: -3px;
  border-radius: 16px;
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  opacity: 0.8;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.game-icon-large {
  font-size: 64px;
}

.panel-header h2 {
  margin: 0;
  font-size: 28px;
  color: #333;
}

.game-description {
  text-align: center;
  color: #666;
  font-size: 16px;
  margin-bottom: 30px;
}

.persona-section h3 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #333;
  text-align: center;
}

/* 角色列表样式 */
.persona-section {
  margin-bottom: 30px;
}

.persona-section h2 {
  margin: 0 0 20px 0;
  font-size: 24px;
  color: #333;
}

.persona-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.persona-list {
  max-height: 300px;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.persona-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.persona-item:hover {
  border-color: #667eea;
  background-color: #f5f7ff;
}

.persona-item.active {
  border-color: #667eea;
  background-color: #f5f7ff;
}

.persona-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  margin-right: 12px;
}

.persona-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.persona-model {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.persona-model.cloud {
  background-color: #e3f2fd;
  color: #1565c0;
}

.persona-model.local {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.no-personas {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* 开始游戏按钮 */
  .start-game-btn {
    width: 100%;
    padding: 20px;
    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
    color: white;
    border: none;
    border-radius: 16px;
    font-size: 24px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 25px rgba(255, 107, 107, 0.4);
    z-index: 1;
  }

  .start-game-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #ee5a24, #ff6b6b);
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: -1;
  }

  .start-game-btn:hover:not(:disabled) {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 15px 30px rgba(255, 107, 107, 0.5);
    animation: pulse 1.5s infinite;
  }

  .start-game-btn:hover:not(:disabled)::before {
    opacity: 1;
  }

  @keyframes pulse {
    0% { box-shadow: 0 15px 30px rgba(255, 107, 107, 0.5); }
    50% { box-shadow: 0 15px 30px rgba(255, 107, 107, 0.7); }
    100% { box-shadow: 0 15px 30px rgba(255, 107, 107, 0.5); }
  }

  .start-game-btn:active:not(:disabled) {
    transform: translateY(-1px) scale(0.98);
  }

  .start-game-btn:disabled {
    background: #cccccc;
    cursor: not-allowed;
    transform: none;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    animation: none;
  }
  
  /* 剧情体验特定按钮样式 */
  .start-game-btn.scene-btn {
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    box-shadow: 0 10px 25px rgba(79, 172, 254, 0.4);
  }
  
  .start-game-btn.scene-btn::before {
    background: linear-gradient(135deg, #00f2fe, #4facfe);
  }
  
  .start-game-btn.scene-btn:hover:not(:disabled) {
    box-shadow: 0 15px 30px rgba(79, 172, 254, 0.5);
    animation: pulseScene 1.5s infinite;
  }
  
  @keyframes pulseScene {
    0% { box-shadow: 0 15px 30px rgba(79, 172, 254, 0.5); }
    50% { box-shadow: 0 15px 30px rgba(79, 172, 254, 0.7); }
    100% { box-shadow: 0 15px 30px rgba(79, 172, 254, 0.5); }
  }
  
  /* 场景描述优化样式 */
  .scene-description.improved {
    margin-bottom: 40px;
    padding: 30px;
    background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(240,248,255,0.9));
    border-radius: 16px;
    border-left: 4px solid #4facfe;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
  }
  
  .feature-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-bottom: 20px;
  }
  
  .feature-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: white;
    border-radius: 12px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  }
  
  .feature-item:hover {
    transform: translateX(5px);
    box-shadow: 0 4px 12px rgba(79, 172, 254, 0.2);
  }
  
  .feature-icon {
    font-size: 24px;
    animation: float 3s ease-in-out infinite;
  }
  
  .feature-icon:nth-child(1) {
    animation-delay: 0s;
  }
  
  .feature-icon:nth-child(2) {
    animation-delay: 1s;
  }
  
  .feature-icon:nth-child(3) {
    animation-delay: 2s;
  }
  
  .feature-text {
    font-size: 16px;
    color: #333;
    font-weight: 500;
  }
  
  .scene-preview {
    display: flex;
    justify-content: center;
  }
  
  .preview-indicator {
    display: flex;
    gap: 8px;
  }
  
  .preview-indicator .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #4facfe;
    opacity: 0.5;
    animation: bounce 1.4s infinite ease-in-out both;
  }
  
  .preview-indicator .dot:nth-child(1) {
    animation-delay: -0.32s;
  }
  
  .preview-indicator .dot:nth-child(2) {
    animation-delay: -0.16s;
  }
  
  @keyframes float {
    0% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-5px);
    }
    100% {
      transform: translateY(0px);
    }
  }
  
  @keyframes bounce {
    0%, 80%, 100% {
      transform: scale(0);
      opacity: 0.5;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }
  
  /* 动画图标效果 */
  .animated-icon {
    animation: iconSpin 8s ease-in-out infinite;
  }
  
  @keyframes iconSpin {
    0% {
      transform: rotate(0deg) scale(1);
    }
    5% {
      transform: rotate(10deg) scale(1.05);
    }
    10% {
      transform: rotate(0deg) scale(1);
    }
    15% {
      transform: rotate(-10deg) scale(1.05);
    }
    20% {
      transform: rotate(0deg) scale(1);
    }
    100% {
      transform: rotate(0deg) scale(1);
    }
  }

/* 响应式设计 */
@media (max-width: 768px) {
  .game-selection-card {
    padding: 20px;
  }
  
  .persona-list {
    grid-template-columns: 1fr;
  }
}
</style>