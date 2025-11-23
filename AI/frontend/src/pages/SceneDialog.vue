<template>
  <div class="scene-dialog-container">
    <!-- 顶部导航栏 -->
    <div class="dialog-header">
      <button class="btn-icon btn-secondary" @click="goBack" aria-label="返回">
        ←
      </button>
      <h2>{{ currentScene?.name || '剧情对话' }}</h2>
      <div class="header-actions">
        <button class="btn-primary btn-sm" @click="startNewDialog" v-if="currentScene">
          🔄 重新开始
        </button>
      </div>
    </div>

    <!-- 情景选择区域 -->
    <div v-if="!currentScene" class="scene-selection">
      <div class="selection-header">
        <h3>🎭 选择对话场景</h3>
        <p class="scene-subtitle">探索不同的剧情世界，开始您的互动体验</p>
      </div>
      
      <div v-if="loadingScenes" class="loading-container">
        <div class="loading-spinner large"></div>
        <p class="loading-text">正在准备精彩场景...</p>
      </div>
      
      <div v-else-if="scenes.length === 0" class="empty-state improved">
        <div class="empty-icon">📖</div>
        <h4>暂无可用场景</h4>
        <p class="empty-hint">管理员正在准备精彩内容，敬请期待</p>
      </div>
      
      <div v-else class="scene-grid">
        <div 
          v-for="scene in scenes" 
          :key="scene.id" 
          class="scene-card improved"
          @click="selectScene(scene)"
          @mouseenter="onSceneHover(scene.id, true)"
          @mouseleave="onSceneHover(scene.id, false)"
        >
          <div class="scene-card-banner" :class="{ 'animated': hoveredScenes.includes(scene.id) }">
            <div class="scene-card-overlay"></div>
          </div>
          <div class="scene-card-content">
            <div class="scene-card-header">
              <h4 class="scene-card-title">{{ scene.name }}</h4>
              <div class="scene-date">{{ formatDate(scene.createdAt) }}</div>
            </div>
            <p class="scene-description">{{ scene.description }}</p>
            <div class="scene-card-footer">
              <span class="select-hint">开始体验</span>
              <svg class="arrow-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 18l6-6-6-6"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 引入StoryDialog组件 -->
    <div v-if="currentScene && token" class="story-dialog-wrapper">
      <StoryDialog 
        :scene-id="currentScene.id.toString()" 
        :token="token"
        :scene="currentScene"
      />
    </div>
    <div v-else-if="!currentScene" class="story-dialog-wrapper">
      <div class="empty-state">
        <p>请先选择一个场景</p>
      </div>
    </div>
    <div v-else class="story-dialog-wrapper">
      <div class="empty-state">
        <p>未登录或Token不存在</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTokenStore } from '../utils/tokenStore'
import { getSceneList } from '../utils/api'
import StoryDialog from '../components/StoryDialog.vue'

export default {
  name: 'SceneDialog',
  components: {
    StoryDialog
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const tokenStore = useTokenStore()
    // 使用响应式引用获取token，确保条件渲染能正确响应token变化
    const token = ref(tokenStore.getToken())
    
    const scenes = ref([])
    const currentScene = ref(null)
    const loadingScenes = ref(false)
    const hoveredScenes = ref([])
    // 不需要人设相关逻辑，直接使用场景进行对话

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }

    // 获取情景列表
    const fetchScenes = async () => {
      if (!token) {
        router.push('/login')
        return
      }
      
      loadingScenes.value = true
      try {
          // 调用 [HttpGet("GetScene")] 接口获取场景列表
          console.log('正在调用GetScene接口获取场景列表...')
          const data = await getSceneList()
          
          // 确保返回的数据是数组格式
          if (Array.isArray(data)) {
            // 直接使用后端返回的数据，确保保留所有字段，特别是id
            scenes.value = data.map(scene => ({
              id: scene.id || scene.Id, // 确保id字段存在
              name: scene.name || scene.Name || '未命名场景',
              description: scene.description || scene.Description || '暂无描述',
              createdAt: scene.createdAt || scene.CreatedAt || new Date().toISOString(),
              userId: scene.userId || scene.UserId || '',
              user: scene.user
            }))
            console.log('获取情景列表成功，共', scenes.value.length, '个场景', scenes.value)
          } else {
            console.warn('场景数据格式不正确，预期数组格式:', data)
            scenes.value = []
          }
      } catch (error) {
        console.error('获取情景列表失败:', error)
        console.error('获取情景列表失败，请重试')
        
        // 开发环境提供模拟数据，避免因接口问题无法进入界面
        if (import.meta.env.DEV) {
          console.log('开发环境：使用模拟场景数据')
          scenes.value = [
            {
              id: 1,
              name: '图书馆的午后阳光',
              description: '期末季的图书馆座无虚席，你在寻找空位时，发现暗恋已久的女生林溪身边刚好有一个空位。阳光透过窗户洒在她的侧脸上，她正低头认真复习，笔记本上画着可爱的小图案。',
              createdAt: '2025-11-18T18:44:25',
              userId: 'feng',
              user: null
            },
            {
              id: 2,
              name: '咖啡厅偶遇',
              description: '周末的午后，你在常去的咖啡厅看书，突然一个熟悉的身影推门而入。是你的大学同学小雯，她似乎也注意到了你，微笑着向你走来...',
              createdAt: '2025-11-17T14:30:00',
              userId: 'feng',
              user: null
            },
            {
              id: 3,
              name: '雨中送伞',
              description: '下班时突然下起了大雨，你站在公司楼下发愁。这时，一个撑着伞的身影出现了，是新同事雨桐，她微笑着说："一起走吧，我顺路。"',
              createdAt: '2025-11-16T18:00:00',
              userId: 'feng',
              user: null
            }
          ]
        }
      } finally {
        loadingScenes.value = false
      }
    }

    // 选择情景
    const selectScene = (scene) => {
      console.log('选择场景:', scene.id, scene.name)
      currentScene.value = scene
      // 保存选择的场景到会话存储
      sessionStorage.setItem('selectedScene', JSON.stringify(scene))
    }

    // 重新开始对话
    const startNewDialog = () => {
      // 重置当前场景，会触发重新连接
      const tempScene = currentScene.value
      currentScene.value = null
      setTimeout(() => {
        currentScene.value = tempScene
      }, 0)
    }

    // 返回上一页
    const goBack = () => {
      router.back()
    }
    
    // 处理场景悬停效果
    const onSceneHover = (sceneId, isHovered) => {
      if (isHovered) {
        hoveredScenes.value.push(sceneId)
      } else {
        hoveredScenes.value = hoveredScenes.value.filter(id => id !== sceneId)
      }
    }

    // 监听tokenStore中的token变化，更新本地响应式token
    watch(() => tokenStore.getToken(), (newToken) => {
      token.value = newToken
    })

    onMounted(() => {
      fetchScenes()
    })

    return {
      scenes,
      currentScene,
      loadingScenes,
      hoveredScenes,
      token,
      formatDate,
      selectScene,
      startNewDialog,
      goBack,
      onSceneHover
    }
  }
}
</script>

<style scoped>
.scene-dialog-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  z-index: 10;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.dialog-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn:hover {
  border-color: #1677ff;
  color: #1677ff;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 情景选择样式 */
.scene-selection {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
}

.selection-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(10px);
}

.selection-header h3 {
  margin: 0 0 12px 0;
  color: #1e293b;
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.scene-subtitle {
  color: #64748b;
  font-size: 18px;
  font-weight: 500;
  margin: 0;
  line-height: 1.5;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #64748b;
  min-height: 400px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e0e7ff;
  border-top: 4px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.loading-spinner.large {
  width: 80px;
  height: 80px;
  border-width: 6px;
  margin-bottom: 24px;
}

.loading-text {
  font-size: 18px;
  color: #6366f1;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.05); }
  100% { transform: rotate(360deg) scale(1); }
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

.empty-state.improved {
  padding: 80px 20px;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}

.empty-state.improved h4 {
  font-size: 24px;
  color: #475569;
  margin: 0 0 12px 0;
  font-weight: 600;
}

.empty-hint {
  font-size: 16px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
  max-width: 320px;
}

.scene-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 30px;
  margin-top: 20px;
}

.scene-card {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background-color: #ffffff;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  position: relative;
  height: 100%;
}

.scene-card.improved {
  border: none;
  transform-origin: center;
}

.scene-card.improved:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
}

.scene-card-banner {
  height: 120px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  position: relative;
  overflow: hidden;
  transition: all 0.5s ease;
}

.scene-card-banner.animated {
  height: 140px;
  background: linear-gradient(135deg, #8b5cf6, #3b82f6);
}

.scene-card-banner::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.15) 0%, transparent 30%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 40%);
  transition: opacity 0.3s ease;
}

.scene-card:hover .scene-card-banner::after {
  opacity: 0.8;
}

.scene-card-content {
  padding: 24px;
}

.scene-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.scene-card-title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  line-height: 1.3;
  transition: color 0.3s ease;
}

.scene-card:hover .scene-card-title {
  color: #3b82f6;
}

.scene-date {
  font-size: 12px;
  color: #94a3b8;
  background-color: #f1f5f9;
  padding: 4px 10px;
  border-radius: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.scene-card:hover .scene-date {
  background-color: #dbeafe;
  color: #3b82f6;
}

.scene-description {
  font-size: 16px;
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 20px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.3s ease;
}

.scene-card:hover .scene-description {
  color: #475569;
}

.scene-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
  transition: border-color 0.3s ease;
}

.scene-card:hover .scene-card-footer {
  border-color: #dbeafe;
}

.select-hint {
  font-weight: 600;
  color: #3b82f6;
  font-size: 14px;
  transition: color 0.3s ease;
}

.scene-card:hover .select-hint {
  color: #2563eb;
}

.arrow-icon {
  width: 20px;
  height: 20px;
  color: #3b82f6;
  transition: all 0.3s ease;
}

.scene-card:hover .arrow-icon {
  transform: translateX(6px) scale(1.1);
  color: #2563eb;
}

/* 卡片选择动画 */
@keyframes cardSelect {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(0.98);
  }
  100% {
    transform: scale(1);
  }
}

.scene-card:active {
  animation: cardSelect 0.2s ease-in-out;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .scene-selection {
    padding: 20px;
  }
  
  .selection-header h3 {
    font-size: 28px;
  }
  
  .scene-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .scene-card-content {
    padding: 20px;
  }
  
  .scene-card-title {
    font-size: 20px;
  }
  
  .scene-description {
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .selection-header h3 {
    font-size: 24px;
  }
  
  .scene-subtitle {
    font-size: 16px;
  }
  
  .scene-card-banner {
    height: 100px;
  }
  
  .scene-card-banner.animated {
    height: 120px;
  }
}

/* 对话样式 */
.scene-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.story-dialog-wrapper {
  flex: 1;
  height: 100%;
  min-height: 0;
}


.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.welcome-message p {
  margin: 8px 0;
  line-height: 1.6;
}

.message-wrapper {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.user-message {
  flex-direction: row-reverse;
}

.ai-message {
  flex-direction: row;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin: 0 12px;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  word-wrap: break-word;
  position: relative;
}

.user-message .message-content {
  background-color: #1677ff;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.ai-message .message-content {
  background-color: #fff;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-text {
  line-height: 1.6;
  white-space: pre-wrap;
}

/* 剧情选项样式 */
.story-options {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.story-option-btn {
  padding: 10px 16px;
  border: 1px solid #4096ff;
  border-radius: 8px;
  background-color: #f0f9ff;
  color: #1890ff;
  cursor: pointer;
  font-size: 14px;
  text-align: left;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.story-option-btn:hover {
  background-color: #4096ff;
  color: #fff;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(64, 150, 255, 0.3);
}

.story-option-btn:active {
  transform: translateX(2px);
  box-shadow: 0 1px 4px rgba(64, 150, 255, 0.3);
}

/* 输入区域样式 */
.dialog-input {
  display: flex;
  gap: 12px;
  padding: 20px;
  background-color: #fff;
  border-top: 1px solid #e8e8e8;
}

.input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  min-height: 44px;
  max-height: 120px;
}

.input:focus {
  outline: none;
  border-color: #1677ff;
}

.send-btn {
  padding: 0 20px;
  background-color: #1677ff;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.send-btn:hover:not(:disabled) {
  background-color: #4096ff;
}

/* 连接状态 */
.connection-status {
  position: fixed;
  bottom: 80px;
  right: 20px;
  padding: 6px 12px;
  border-radius: 16px;
  background-color: #f5f5f5;
  color: #666;
  font-size: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.connection-status.connected {
  background-color: #f0f9ff;
  color: #1890ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .scene-list {
    grid-template-columns: 1fr;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .dialog-content {
    padding: 16px;
  }
}
</style>