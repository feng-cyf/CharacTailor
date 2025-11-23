<template>
  <div class="chat-container">
    <!-- 右键菜单 -->
    <div v-if="contextMenu.visible" class="context-menu" :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }">
      <div class="context-menu-item" @click="handleContextMenuPlayAudio">播放音频</div>
    </div>
    <!-- 顶部导航栏 -->
    <div class="chat-header">
      <h2>AI聊天助手</h2>
      <div v-if="selectedPersona" class="model-type-badge" :class="{ 'cloud': selectedPersona.is_cloud_model, 'local': !selectedPersona.is_cloud_model }">
        {{ selectedPersona.is_cloud_model ? '云端模型' : '本地模型' }}
      </div>
      <div class="header-actions">
        <!-- 游戏入口按钮 -->
        <button class="btn game-entry-btn" @click="goToGame">
          🎮 游戏入口
        </button>
        <!-- 角色选择下拉框 -->
        <select 
          v-model="selectedPersona" 
          @change="handlePersonaChange()" 
          :disabled="isLoadingPersonas"
          class="persona-select"
        >
          <option v-if="personas.length === 0" :value="null">默认角色</option>
          <option v-else v-for="persona in personas" :key="persona.persona_id" :value="persona">
            {{ persona.persona_name }} {{ persona.is_cloud_model ? '[云]' : '[本]' }}
          </option>
        </select>
        <button class="btn" @click="handleCreatePersona">添加人设</button>
        <button class="btn" @click="handleLogout">退出登录</button>
      </div>
    </div>

    <!-- 聊天内容区域 -->
    <div class="chat-content" ref="chatContentRef">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message">
        <p>欢迎使用AI聊天助手！</p>
        <p>请输入您的问题或上传文件开始对话</p>
      </div>

      <!-- 消息列表 -->
      <div v-for="(msg, index) in messages" :key="index">
        <!-- 用户消息 -->
        <div v-if="msg.role === 'user'" class="message-wrapper user-message">
          <!-- 消息内容区域 -->
          <div class="message-content">
            <div v-if="msg.content" class="message-text">{{ msg.content }}</div>
            <!-- 用户上传的图片/视频 -->
            <div class="attachments" v-if="msg.attachments && msg.attachments.length">
              <div v-for="(att, idx) in msg.attachments" :key="idx" class="attachment">
                <template v-if="att.kind === 'image'">
                  <img :src="att.local_url || att.cloud_url" alt="上传图片" />
                </template>
                <template v-else-if="att.kind === 'video'">
                  <video :src="att.local_url || att.cloud_url" controls></video>
                </template>
              </div>
            </div>
          </div>
          <!-- 用户头像容器 -->
          <div class="message-avatar">👤</div>
        </div>
        
        <!-- AI回复消息 -->
          <div v-else class="message-wrapper ai-message" 
            style="display: flex; flex-direction: row !important; justify-content: flex-start !important;"
            @contextmenu.prevent="handleContextMenu($event, msg)"
          >
          <!-- AI头像容器 - 确保在最左侧 -->
          <div class="message-avatar" style="order: 1 !important; margin-right: 8px !important; margin-left: 0 !important; width: 32px; height: 32px; border-radius: 50%; background-color: #1677ff; color: white; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 16px; z-index: 999; position: relative;">🤖</div>
          <!-- 消息内容区域 - 在头像右侧 -->
          <div class="message-content" style="order: 2; flex-grow: 1; position: relative;">
            <!-- 音频播放按钮或生成提示 -->
            <div v-if="generatingAudioIds.value && generatingAudioIds.value.has(msg.id)" class="audio-play-button generating">
              <span class="generating-text">生成中...</span>
            </div>
            <div 
              v-else-if="msg.bot_audio_url || (audioUrls.value && audioUrls.value.has(msg.id) && audioUrls.value.get(msg.id))" 
              class="audio-play-button"
              @click="playAudio(msg)"
              :class="{ 'playing': currentPlayingMessageId && currentPlayingMessageId.value === msg.id }"
            ></div>
              <div v-if="msg.content" class="message-text">{{ msg.content }}</div>
              <!-- 剧情选项列表 -->
              <div v-if="msg.options_included && msg.options && msg.options.length > 0" class="story-options">
                <button 
                  v-for="(option, optIndex) in msg.options" 
                  :key="optIndex" 
                  class="story-option-btn"
                  @click="handleStoryOptionClick(option)"
                >
                  {{ option }}
                </button>
              </div>
              <!-- AI回复的图片/视频 -->
              <div class="attachments" v-if="msg.attachments && msg.attachments.length">
                <div v-for="(att, idx) in msg.attachments" :key="idx" class="attachment">
                  <template v-if="att.kind === 'image'">
                    <img :src="att.local_url || att.cloud_url" alt="AI回复图片" />
                  </template>
                  <template v-else-if="att.kind === 'video'">
                    <video :src="att.local_url || att.cloud_url" controls></video>
                  </template>
                </div>
              </div>
            </div>
        </div>
      </div>

      <!-- 正在输入指示器 -->
      <div v-if="isLoading" class="typing-indicator-container">
        <div class="message-avatar">🤖</div>
        <div class="typing-indicator">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    </div>

    <!-- 消息输入区域 -->
    <div class="chat-input">
      <ChatComposer
          :persona-id="currentPersonaId"
          :persona-info="currentPersonaInfo"
          :use-cloud-model="selectedPersona?.is_cloud_model || false"
          @message="handleMessageReceived"
          @userMessage="handleSendMessage"
          @error="handleError"
          @close="handleConnectionClose"
          @open="handleConnectionOpen"
        />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useTokenStore } from '../utils/tokenStore'
import { useSessionStore } from '../utils/sessionStore'
import { getDialogHistory, getUserPersonas, createChatWebSocket, uploadFile } from '../utils/api'
import ChatComposer from '../components/ChatComposer.vue'

export default {
  name: 'Chat',
  components: {
    ChatComposer
  },
  setup() {
    // 右键菜单状态
    const contextMenu = ref({
      visible: false,
      x: 0,
      y: 0,
      message: null
    })
    const router = useRouter()
    const tokenStore = useTokenStore()
    const sessionStore = useSessionStore()
    
    const messages = ref([])
    // 音频URL映射，用于存储每个消息的音频URL
    const audioUrls = ref(new Map())
    // 音频播放状态管理
    const currentPlayingAudio = ref(null)
    const currentPlayingMessageId = ref(null)
    // 音频生成状态管理 - 用于显示"正在生成音频"提示
    const generatingAudioIds = ref(new Set())
    const isLoading = ref(false)
    const personas = ref([])
    const isLoadingPersonas = ref(false)
    const chatContentRef = ref(null)
    const currentPersonaId = ref('default') // 默认使用default persona
    const currentPersonaInfo = ref(null) // 存储当前选中的完整persona信息
    const selectedPersona = ref(null) // 直接存储选中的完整persona对象
    
    // 获取用户角色列表
    const fetchUserPersonas = async () => {
      try {
        isLoadingPersonas.value = true
        const userInfo = tokenStore.getUserInfo()
        const userId = userInfo?.user_id || 'default_user'
        console.log('获取用户角色列表，用户ID:', userId)
        const response = await getUserPersonas(userId)
        
        console.log('获取角色列表响应数据:', response)
        if (response && response.code === 200 && response.data) {
          // 确保数据是数组
          const personaData = Array.isArray(response.data) ? response.data : []
          console.log('角色数据数量:', personaData.length)
          
          // 显示每个角色的详细信息
          personaData.forEach((persona, index) => {
            console.log(`角色 ${index + 1}:`, {
              persona_id: persona.persona_id,
              persona_name: persona.persona_name,
              session_id: persona.session_id,
              其他字段: Object.keys(persona)
            })
          })
          
          personas.value = personaData
          
          // 如果有角色且当前角色不是默认角色，则不修改；否则设置第一个角色为当前角色
          if (personas.value.length > 0 && currentPersonaId.value === 'default') {
            const firstPersona = personas.value[0]
            console.log('设置默认角色:', firstPersona)
            currentPersonaId.value = firstPersona.persona_id
            currentPersonaInfo.value = {
              persona_id: firstPersona.persona_id,
              persona_name: firstPersona.persona_name,
              session_id: firstPersona.session_id,
              personaId: firstPersona.persona_id,
              name: firstPersona.persona_name,
              sessionId: firstPersona.session_id
            }
            
            // 设置选中的persona对象
            selectedPersona.value = firstPersona
            
            // 直接切换到第一个角色的会话
            if (firstPersona.session_id) {
              console.log('直接设置第一个角色的会话ID:', firstPersona.session_id)
              sessionStore.setCurrentSessionId(firstPersona.session_id)
            }
          }
        } else {
          console.warn('获取角色列表失败:', response?.message || '未知错误')
        }
      } catch (error) {
        console.error('获取角色列表异常:', error)
        console.error('错误详情:', error.message)
      } finally {
        isLoadingPersonas.value = false
      }
    }
    
    // 初始化聊天历史
    const initChatHistory = async () => {
      try {
        // 确保总是获取最新的会话ID
        const sessionId = sessionStore.getCurrentSessionId()
        console.log('初始化聊天历史 - 使用会话ID:', sessionId)
        console.log('初始化聊天历史 - 当前角色ID:', currentPersonaId.value)
        console.log('初始化聊天历史 - 当前角色信息:', currentPersonaInfo.value)
        
        if (sessionId) {
          isLoading.value = true
          console.log('开始获取对话历史，会话ID:', sessionId, '角色ID:', currentPersonaId.value)
          // 确保传入正确的会话ID和角色ID
          const history = await getDialogHistory(sessionId, currentPersonaId.value)
          console.log('获取到聊天历史结果类型:', typeof history)
          console.log('获取到聊天历史结果:', history)
          console.log('获取到聊天历史结果是否为数组:', Array.isArray(history))
          
          // 简化处理逻辑：直接检查是否为数组，如果不是数组则尝试转换
          let chatMessages = []
          
          if (Array.isArray(history)) {
            // 如果已经是数组，直接使用
            console.log('直接使用返回的数组:', history.length, '条消息')
            chatMessages = history
          } else if (history && typeof history === 'object') {
            // 如果是对象，检查是否包含旧格式数据
            if (history.bot_response && history.user_msg && Array.isArray(history.bot_response) && Array.isArray(history.user_msg)) {
              console.log('发现旧格式数据，在前端进行转换...')
              // 直接包装整个history对象，让后续的处理函数来处理
              chatMessages = [history]
            } else {
              // 其他对象类型，包装成数组
              console.log('包装单条消息对象为数组')
              chatMessages = [history]
            }
          }
          
          console.log('最终处理前的聊天消息数组长度:', chatMessages.length)
          console.log('最终处理前的聊天消息数组:', chatMessages)
          
          // 创建临时数组存储处理后的消息
          const processedMessages = []
          
          for (let i = 0; i < chatMessages.length; i++) {
            const item = chatMessages[i]
            console.log(`处理第${i}项数据:`, item)
            
            // 检查是否为旧格式的整个对象
            if (item && item.bot_response && item.user_msg && Array.isArray(item.bot_response) && Array.isArray(item.user_msg)) {
              console.log('检测到旧格式数据块，内部进行转换...')
              const messageCount = Math.min(item.bot_response.length, item.user_msg.length)
              
              for (let j = 0; j < messageCount; j++) {
                // 处理用户消息
                const userMsg = item.user_msg[j]
                if (userMsg) {
                  const userMessageObj = {
                    role: 'user',
                    content: userMsg.user_message || '',
                    user_message_type: userMsg.user_type || 'text',
                    user_file_url: userMsg.user_file_url || '',
                    time: item.time && item.time[j] ? item.time[j] : new Date().toISOString()
                  }
                  processedMessages.push(userMessageObj)
                }
                
                // 处理AI消息
                const botResponse = item.bot_response[j]
                if (botResponse) {
                  const assistantMessageObj = {
                    role: 'assistant',
                    content: botResponse.bot_response || '',
                    bot_response_type: botResponse.bot_type || 'text',
                    bot_file_url: botResponse.bot_file_url || '',
                    bot_audio_url: botResponse.bot_audio_url || '',
                    time: item.time && item.time[j] ? item.time[j] : new Date().toISOString()
                  }
                  processedMessages.push(assistantMessageObj)
                }
              }
            } else {
              // 处理单条消息对象
              console.log('处理单条消息对象')
              const message = {
                role: item.role === 'bot' ? 'assistant' : (item.role || 'unknown'),
                content: item.content || (item.bot_response || item.user_message || ''),
                bot_audio_url: item.bot_audio_url || '',
                attachments: []
              }
              
              // 处理附件
              if (message.role === 'user') {
                const fileUrl = item.user_file_url || item.file_url || item.url
                const messageType = item.user_message_type || item.message_type || 'text'
                
                if (fileUrl) {
                  message.attachments = [{
                    kind: messageType === 'image' ? 'image' : (messageType === 'video' ? 'video' : 'file'),
                    local_url: fileUrl,
                    cloud_url: fileUrl
                  }]
                }
              } else if (message.role === 'assistant') {
                const fileUrl = item.bot_file_url || item.file_url || item.url
                const responseType = item.bot_response_type || item.response_type || 'text'
                
                if (fileUrl) {
                  message.attachments = [{
                    kind: responseType === 'image' ? 'image' : (responseType === 'video' ? 'video' : 'file'),
                    local_url: fileUrl,
                    cloud_url: fileUrl
                  }]
                }
              }
              
              processedMessages.push(message)
            }
          }
          
          console.log('处理后的消息数量:', processedMessages.length)
          console.log('处理后的消息数组:', processedMessages)
          messages.value = processedMessages
        } else {
          console.warn('没有有效的会话ID，无法加载聊天历史')
          // 尝试从当前角色信息中获取会话ID
          if (currentPersonaInfo.value && currentPersonaInfo.value.session_id) {
            console.log('从角色信息中获取会话ID:', currentPersonaInfo.value.session_id)
            sessionStore.setCurrentSessionId(currentPersonaInfo.value.session_id)
            return initChatHistory()
          }
        }
      } catch (error) {
        console.error('加载聊天历史异常:', error)
        console.error('异常详情:', error.message)
        messages.value = []
      } finally {
        isLoading.value = false
        // 滚动到底部
        await nextTick()
        scrollToBottom()
      }
    }
    
    // 处理persona选择变化
    const handlePersonaChange = async () => {
      if (!selectedPersona.value) return
      
      // 直接使用选中的persona对象中的persona_id
      await switchPersona(selectedPersona.value.persona_id)
    }
    
    // 切换角色
    const switchPersona = async (personaId) => {
      console.log('开始切换角色，目标角色ID:', personaId)
      
      // 如果是当前角色，不执行切换
      if (personaId === currentPersonaId.value) {
        console.log('目标角色与当前角色相同，跳过切换')
        return
      }
      
      // 直接从selectedPersona获取完整信息，如果不存在则从personas数组查找
      const personaInfo = selectedPersona.value || personas.value.find(p => 
        p.id === personaId || 
        p.persona_id === personaId || 
        p.personaId === personaId
      ) || {} // 提供默认空对象以避免undefined
      
      console.log('获取到的角色信息:', personaInfo)
      console.log('角色信息中的会话ID:', personaInfo.session_id || personaInfo.sessionId)
      
      // 规范化personaInfo对象，同时包含两种命名格式
      // 关键修改：保留原始的session_id信息
      const normalizedPersonaInfo = {
        // 带下划线格式
        persona_id: personaInfo.persona_id || personaInfo.id || personaId,
        persona_name: personaInfo.persona_name || personaInfo.name || personaInfo.personaName || 'AI助手',
        // 保留session_id信息
        session_id: personaInfo.session_id || personaInfo.sessionId,
        // 驼峰格式
        personaId: personaInfo.persona_id || personaInfo.id || personaId,
        name: personaInfo.persona_name || personaInfo.name || personaInfo.personaName || 'AI助手',
        sessionId: personaInfo.session_id || personaInfo.sessionId,
        // 保存原始对象的所有其他属性
        ...personaInfo
      }
      
      console.log('规范化后的角色信息:', normalizedPersonaInfo)
      console.log('角色对应的会话ID:', normalizedPersonaInfo.session_id)
      
      // 清空当前消息列表
      messages.value = []
      
      try {
        // 尝试使用自动切换功能
        console.log('使用自动切换会话功能')
        
        // 记录切换前的状态
        console.log('切换前 - 当前会话ID:', sessionStore.getCurrentSessionId())
        console.log('切换前 - 所有会话列表:', sessionStore.getSessions())
        
        // 直接从personaInfo中获取session_id
        const personaSessionId = normalizedPersonaInfo.session_id || normalizedPersonaInfo.sessionId
        console.log('从personaInfo获取的会话ID:', personaSessionId)
        
        // 优先使用personaInfo中的session_id
        if (personaSessionId) {
          console.log('直接使用personaInfo中的会话ID:', personaSessionId)
          sessionStore.setCurrentSessionId(personaSessionId)
        } else {
          // 否则使用自动切换功能
          const sessionId = sessionStore.autoSwitchToPersonaSession(normalizedPersonaInfo)
          
          // 验证会话ID是否有效
          if (!sessionId) {
            console.error('获取会话ID失败，生成新会话')
            // 直接创建新会话
            const userInfo = tokenStore.getUserInfo()
            const userId = userInfo?.user_id || 'default_user'
            const newSessionId = `${userId}_${personaId}_${Date.now()}`
            sessionStore.setCurrentSessionId(newSessionId)
            console.log('手动创建会话ID:', newSessionId)
          }
        }
        
        // 验证当前会话ID是否已更新
        const updatedSessionId = sessionStore.getCurrentSessionId()
        console.log('当前会话ID验证:', updatedSessionId)
        
        // 记录切换后的状态
        console.log('切换后 - 所有会话列表:', sessionStore.getSessions())
        console.log('切换后 - localStorage中的currentSessionId:', localStorage.getItem('currentSessionId'))
        
        // 关键修改：确保在更新currentPersonaId和currentPersonaInfo之前，会话已经切换
        // 这样ChatComposer的watch监听器可以捕获到角色变化并重新创建WebSocket连接
        await nextTick()
        
        // 最后更新当前角色信息，触发ChatComposer的重新渲染和连接创建
        currentPersonaId.value = personaId
        currentPersonaInfo.value = normalizedPersonaInfo
        
        // 确保selectedPersona也被正确设置
        selectedPersona.value = personaInfo
        
        console.log('角色信息已更新，触发组件更新')
        
        // 等待组件更新完成后再加载聊天历史
        await nextTick()
        
        // 加载新会话的聊天历史
        console.log('开始加载新会话的聊天历史')
        await initChatHistory()
        console.log('聊天历史加载完成')
      } catch (error) {
        console.error('自动切换会话失败:', error)
        // 降级方案：手动生成sessionId并直接切换
        try {
          const userInfo = tokenStore.getUserInfo()
          const userId = userInfo?.user_id || 'default_user'
          const newSessionId = `${userId}_${personaId}_${Date.now()}` // 增加时间戳确保唯一性
          
          console.log('降级到手动会话ID生成:', newSessionId)
          sessionStore.setCurrentSessionId(newSessionId)
          
          // 降级情况下也更新角色信息
          currentPersonaId.value = personaId
          currentPersonaInfo.value = normalizedPersonaInfo
          
          // 加载聊天历史
          await nextTick()
          await initChatHistory()
        } catch (fallbackError) {
          console.error('降级方案也失败:', fallbackError)
        }
      }
      
      console.log('角色切换完成')
    }
    
    // 滚动到底部
    const scrollToBottom = () => {
      if (chatContentRef.value) {
        chatContentRef.value.scrollTop = chatContentRef.value.scrollHeight
      }
    }
    
    // 处理接收到的消息
    const handleMessageReceived = (content, rawData) => {
      if (!content) return
      
      try {
        const data = JSON.parse(rawData)
        // 检查是否是剧情数据格式
        if (data.type === 'text' && data.data) {
          const storyData = data.data
          isLoading.value = false
          
          // 创建剧情消息对象
          const storyMessage = {
            role: 'assistant',
            content: storyData.reply || content,
            scene_included: storyData.scene_included || false,
            options_included: storyData.options_included || false,
            options: storyData.options || []
          }
          
          messages.value.push(storyMessage)
        } else if (data.type === 'end') {
          isLoading.value = false
          // 更新最后一条AI消息为完整内容
          const lastMessage = messages.value[messages.value.length - 1]
          if (lastMessage && lastMessage.role !== 'user') {
            lastMessage.content = content
          } else {
            messages.value.push({
              role: 'assistant',
              content: content
            })
          }
        } else if (data.type === 'stream') {
          // 更新或添加流式消息
          isLoading.value = true
          const lastMessage = messages.value[messages.value.length - 1]
          if (lastMessage && lastMessage.role !== 'user') {
            lastMessage.content = content
          } else {
            messages.value.push({
              role: 'assistant',
              content: content
            })
          }
        } else if (data.type === 'error') {
          isLoading.value = false
          messages.value.push({
            role: 'assistant',
            content: `[错误] ${content}`
          })
        } else {
          isLoading.value = false
          messages.value.push({
            role: 'assistant',
            content: content
          })
        }
        
        // 滚动到底部
        nextTick(() => scrollToBottom())
      } catch (error) {
        console.error('处理消息失败:', error)
        messages.value.push({
          role: 'assistant',
          content: content
        })
        nextTick(() => scrollToBottom())
      }
    }
    
    // 处理连接打开
    const handleConnectionOpen = () => {
      console.log('聊天连接已建立')
    }
    
    // 处理发送消息
    const handleSendMessage = async (userMessage) => {
      if (!userMessage) return
      
      // 设置正在加载状态，显示"正在输入"指示器
      isLoading.value = true
      
      // 直接添加用户消息到列表
      messages.value.push(userMessage)
      
      // 滚动到底部
      await nextTick()
      scrollToBottom()
      
      console.log('收到用户消息:', userMessage)
    }
    
    // 处理剧情选项点击
    const handleStoryOptionClick = (option) => {
      console.log('用户选择了剧情选项:', option)
      // 创建用户消息对象
      const userMessage = {
        role: 'user',
        content: option
      }
      // 发送消息
      handleSendMessage(userMessage)
    }
    
    // 处理文件上传
    const handleUploadFile = async (file) => {
      console.log('上传文件:', file)
      // 这里应该实现文件上传逻辑
      messages.value.push({
        role: 'user',
        content: `[文件上传] ${file.name}`,
        attachments: [{ type: file.type, name: file.name, size: file.size }]
      })
      
      await nextTick()
      scrollToBottom()
    }
    
    // 处理连接关闭
    const handleConnectionClose = () => {
      console.log('聊天连接已关闭')
    }
    
    // 处理错误
    const handleError = (error) => {
      // 发生错误时清除加载状态
      isLoading.value = false
      console.error('聊天错误:', error)
      messages.value.push({
        role: 'assistant',
        content: '[错误] 连接失败，请刷新页面重试'
      })
      nextTick(() => scrollToBottom())
    }
    
    // 退出登录
    const handleLogout = () => {
      tokenStore.clearToken()
      sessionStore.clearAllSessions()
      router.push('/login')
    }
    
    // 跳转到游戏页面
    const goToGame = () => {
      // 跳转到游戏选择页面
      router.push('/game')
    }
    
    // 处理创建人设
    const handleCreatePersona = () => {
      router.push('/persona/create')
    }
    
    // 处理右键菜单
    const handleContextMenu = (event, message) => {
      // 确保消息有唯一ID
      if (!message.id) {
        message.id = Date.now().toString() + '_' + Math.random().toString(36).substr(2, 9)
      }
      contextMenu.value.visible = true
      contextMenu.value.x = event.clientX
      contextMenu.value.y = event.clientY
      contextMenu.value.message = message
    }
    
    // 处理右键菜单播放音频选项
    const handleContextMenuPlayAudio = async () => {
      if (contextMenu.value.message) {
        await handlePlayAudio(contextMenu.value.message)
      }
      contextMenu.value.visible = false
    }
    
    // 处理播放语音请求
    const handlePlayAudio = async (message) => {
      // 如果消息ID不存在，先生成一个
      if (!message.id) {
        message.id = Date.now().toString() + '_' + Math.random().toString(36).substr(2, 9);
      }
      
      console.log('开始处理音频请求', message);
      const sessionId = sessionStore.getCurrentSessionId();
      console.log('会话ID:', sessionId);
      
      // 添加到正在生成音频的集合中，显示提示
      generatingAudioIds.value.add(message.id);
      
      try {
        const response = await fetch(`http://127.0.0.1:8000/file/upload/audio/audio/${sessionId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${tokenStore.getToken()}`
          },
          body: JSON.stringify({ text: message.content })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('获取音频URL成功:', data);
        
        const audioUrl = data.audio_url || data.data?.local_url;
        
        // 直接更新消息对象的bot_audio_url字段，确保播放按钮持续显示
        message.bot_audio_url = audioUrl;
        
        // 同时更新messages数组中的对应消息
        const messageIndex = messages.value.findIndex(msg => msg.id === message.id);
        if (messageIndex !== -1) {
          messages.value[messageIndex] = { ...messages.value[messageIndex], bot_audio_url: audioUrl };
        }
        
        // 保存音频URL到Map中作为备份
        audioUrls.value.set(message.id, audioUrl);
        
        // 立即播放音频
        playAudio(message);
      } catch (error) {
        console.error('获取音频URL失败:', error);
        // 可以添加错误提示给用户
      } finally {
        // 无论成功失败，都从生成集合中移除，隐藏提示
        generatingAudioIds.value.delete(message.id);
      }
    };
    
    // 处理播放语音请求 - 用于右键菜单触发音频生成
    
    // 右键菜单相关处理函数可以在这里添加
    
    // 播放音频 - 支持点击正在播放的音频时关闭重置
    const playAudio = (message) => {
      // 检查是否正在播放该消息的音频
      if (currentPlayingMessageId.value === message.id && currentPlayingAudio.value) {
        // 如果是同一个消息，停止并重置音频
        currentPlayingAudio.value.pause()
        currentPlayingAudio.value.currentTime = 0
        currentPlayingAudio.value = null
        currentPlayingMessageId.value = null
        return
      }
      
      // 如果有其他音频正在播放，先停止
      if (currentPlayingAudio.value) {
        currentPlayingAudio.value.pause()
        currentPlayingAudio.value.currentTime = 0
      }
      
      // 优先使用消息中的bot_audio_url
      let audioUrl = message.bot_audio_url
      
      // 如果没有bot_audio_url，则从audioUrls中获取
      if (!audioUrl && message.id) {
        audioUrl = audioUrls.value.get(message.id)
        
        // 如果从audioUrls获取到了URL，同步更新到消息对象和messages数组中
        if (audioUrl) {
          message.bot_audio_url = audioUrl;
          const messageIndex = messages.value.findIndex(msg => msg.id === message.id);
          if (messageIndex !== -1) {
            messages.value[messageIndex] = { ...messages.value[messageIndex], bot_audio_url: audioUrl };
          }
        }
      }
      
      if (audioUrl) {
        // 保存音频URL到Map中，确保按钮持续显示
        if (message.id) {
          audioUrls.value.set(message.id, audioUrl)
        }
        
        // 创建并播放音频
        const audio = new Audio(audioUrl)
        
        // 存储当前播放状态
        currentPlayingAudio.value = audio
        currentPlayingMessageId.value = message.id
        
        // 播放结束时重置状态
        audio.onended = () => {
          currentPlayingAudio.value = null
          currentPlayingMessageId.value = null
        }
        
        // 播放音频
        audio.play().catch(error => {
          console.error('播放音频失败:', error)
          // 播放失败时重置状态
          currentPlayingAudio.value = null
          currentPlayingMessageId.value = null
        })
      } else {
        console.warn('没有找到音频URL')
      }
    }
    
    // 全局点击关闭右键菜单
    const handleGlobalClick = () => {
      contextMenu.value.visible = false
    }
    
    // 检查登录状态
    const checkLogin = () => {
      if (!tokenStore.isLoggedIn()) {
        router.push('/login')
        return false
      }
      return true
    }
    
    onMounted(async () => {
      if (checkLogin()) {
        // 先获取角色列表
        await fetchUserPersonas()
        // 再初始化聊天历史
        await initChatHistory()
      }
      // 添加全局点击事件监听
      document.addEventListener('click', handleGlobalClick)
    })
    
    onBeforeUnmount(() => {
      // 清理全局点击事件
      document.removeEventListener('click', handleGlobalClick)
      // 清理资源
    })
    
    return {
      messages,
      isLoading,
      personas,
      isLoadingPersonas,
      chatContentRef,
      currentPersonaId,
      currentPersonaInfo,
      selectedPersona,
      contextMenu,
      audioUrls,
      currentPlayingMessageId,
      generatingAudioIds,
      handlePersonaChange,
      handleMessageReceived,
      handleError,
      handleConnectionOpen,
      handleConnectionClose,
      handleLogout,
      handleCreatePersona,
      goToGame,
      switchPersona,
      handleSendMessage,
      handleUploadFile,
      handleContextMenu,
      handleContextMenuPlayAudio,
      handlePlayAudio,
      playAudio,
      handleStoryOptionClick
    }
  }
}
</script>

<style scoped>
.model-type-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: bold;
  margin-right: 16px;
}

.model-type-badge.cloud {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.model-type-badge.local {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
}

.header-actions {
  display: flex;
  align-items: center;
}
</style>

<style scoped>
/* 右键菜单样式 */
.context-menu {
  position: fixed;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  padding: 4px 0;
  z-index: 1000;
  min-width: 120px;
}

.context-menu-item {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: background-color 0.2s;
}

.context-menu-item:hover {
  background-color: #f5f5f5;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.chat-header h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #333;
  }

  .header-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }
  
  .persona-select {
    padding: 6px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    background-color: #fff;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s;
  }
  
  .persona-select:hover {
    border-color: #1677ff;
  }
  
  .persona-select:disabled {
    cursor: not-allowed;
    opacity: 0.6;
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
  color: white;
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(64, 150, 255, 0.3);
}

.story-option-btn:active {
  transform: translateX(3px);
}

.btn:hover {
  background-color: #f5f5f5;
}

/* 游戏入口按钮样式 */
.game-entry-btn {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: white;
  border: none;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}

.game-entry-btn:hover {
  background: linear-gradient(135deg, #ee5a24, #ff6b6b);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 107, 107, 0.4);
}

.game-entry-btn:active {
  transform: translateY(0);
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  /* 优化滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f0f0f0;
}

/* WebKit浏览器滚动条样式 */
.chat-content::-webkit-scrollbar {
  width: 6px;
}

.chat-content::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.welcome-message {
  text-align: center;
  color: #666;
  margin-top: 100px;
}

.welcome-message p {
  margin: 8px 0;
  font-size: 16px;
}

.message-wrapper {
  display: flex;
  margin-bottom: 12px;
  width: 100%;
}

.user-message {
  justify-content: flex-end;
  flex-direction: row;
}

.ai-message {
  justify-content: flex-start;
  flex-direction: row !important;
}

/* 为头像预留位置 */
.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.user-message .message-avatar {
  order: 2;
  margin-left: 8px;
  margin-right: 0;
  background-color: #52c41a;
  color: white;
}

/* 强制AI头像在左侧 */
.ai-message .message-avatar {
  order: 1 !important;
  margin-right: 8px !important;
  margin-left: 0 !important;
  background-color: #1677ff;
  color: white;
  position: relative;
  z-index: 999; /* 极高的层级确保在最上层 */
}

/* 专门为AI头像添加样式，确保在最左侧 */
.ai-avatar {
  flex-shrink: 0 !important;
  z-index: 999 !important;
  position: relative !important;
  margin-right: 8px !important;
  margin-left: 0 !important;
  order: 1 !important;
}

/* 已移除message-bubble类，直接在message-wrapper中布局 */

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  background-color: #fff;
  box-shadow: none;
  max-width: 75%;
  word-wrap: break-word;
}

.user-message .message-content {
  background-color: #52c41a;
  color: #fff;
  border-radius: 16px 16px 4px 16px;
  padding: 12px 16px;
  font-weight: normal;
}

.ai-message .message-content {
  background-color: #ffffff;
  color: #333;
  border-radius: 16px 16px 16px 4px;
  border: 1px solid #e8e8e8;
  padding: 12px 16px;
  box-shadow: none;
}

/* 移除悬停效果，保持简洁 */
.message-content:hover {
  box-shadow: none;
}

.user-message .message-content:hover {
  box-shadow: none;
}

.message-text {
  /* 确保消息文本使用包含中文字体的字体族 */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    'Microsoft YaHei', '微软雅黑', 'SimHei', '黑体', 'sans-serif';
  line-height: 1.5;
  font-size: 15px;
  white-space: pre-wrap;
  word-break: break-word;
  /* 优化中文显示 */
  letter-spacing: 0.5px;
}

.attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.attachment {
  max-width: 200px;
  max-height: 200px;
  border-radius: 8px;
  overflow: hidden;
}

.attachment img,
.attachment video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.typing-indicator-container {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background-color: #fff;
  border-radius: 12px;
  border-bottom-left-radius: 4px;
  max-width: 200px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.typing-dot {
  width: 10px;
  height: 10px;
  background-color: #1677ff;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }
.typing-dot:nth-child(3) { animation-delay: 0s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.chat-input {
  border-top: 1px solid #ddd;
  background-color: #fff;
  padding: 16px 24px;
}

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 120px;
  padding: 4px 0;
}

.context-menu-item {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: background-color 0.2s;
}

.context-menu-item:hover {
  background-color: #f5f5f5;
}

/* 三角形播放按钮样式 */
.audio-play-button {
  position: absolute;
  top: -8px;
  left: -8px;
  width: 0;
  height: 0;
  border-left: 12px solid #1677ff;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  cursor: pointer;
  z-index: 10;
  transition: transform 0.2s;
}

.audio-play-button:hover {
  transform: scale(1.1);
}

.audio-play-button.generating {
  background-color: rgba(236, 249, 255, 0.8);
  border: 1px solid #93c5fd;
  border-left: none;
  width: auto;
  height: auto;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
}

.audio-play-button.generating .generating-text {
  font-size: 10px;
  color: #2563eb;
  font-weight: 500;
}
</style>