<template>
  <div class="story-dialog-container" :style="backgroundStyle">
    <!-- 对话内容区域 - 全屏展示 -->
    <div class="dialog-content" ref="dialogContentRef">
      <!-- 错误提示 - 保持必要的错误提示但调整样式 -->
      <div v-if="connectionError" class="error-message">
        <span>{{ connectionError }}</span>
        <button class="reconnect-btn" @click="connectWebSocket">重新连接</button>
      </div>
      
      <!-- 欢迎消息 - 改进为剧情介绍样式 -->
      <div v-if="messages.length === 0" class="welcome-message story-intro">
        <h1>{{ scene.name }}</h1>
        <p>{{ scene.description }}</p>
        <p>开始你的剧情体验...</p>
      </div>

      <!-- 消息列表 -->
      <div v-for="(msg, index) in messages" :key="index">
        <!-- 用户消息 -->
        <div v-if="msg.role === 'user'" class="message-wrapper user-message">
          <div class="message-content">
            <div v-if="msg.content" class="message-text">{{ msg.content }}</div>
          </div>
        </div>
        
        <!-- AI回复消息 -->
        <div v-else class="message-wrapper ai-message">
          <div class="message-content">
            <div v-if="msg.content" class="message-text">{{ msg.content }}</div>
            <!-- 剧情选项 -->
            <div v-if="msg.options && msg.options.length > 0" class="story-options">
              <button 
                v-for="option in msg.options" 
                :key="option.id" 
                class="story-option-btn"
                @click="handleStoryOptionClick(option)"
                :class="{ selected: selectedOptionId === option.id }"
              >
                {{ option.text }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 背景设置按钮 -->
    <div class="background-controls">
      <button 
        class="bg-setting-btn" 
        @click="toggleBackgroundPicker"
        :class="{ 'bg-active': backgroundImage }"
        :disabled="isLoadingBackground"
      >
        {{ isLoadingBackground ? '⏳' : '🖼️' }} {{ backgroundImage ? '背景 ✓' : '背景' }}
      </button>
      
      <!-- 背景图片选择器 -->
      <transition name="fade">
        <div v-if="showBackgroundPicker" class="background-picker">
          <input
            type="file"
            ref="fileInput"
            style="display: none"
            accept="image/*"
            @change="handleFileSelect"
          />
          <button 
            class="select-bg-btn" 
            @click="triggerFileSelect"
            :disabled="isLoadingBackground"
          >
            {{ isLoadingBackground ? '加载中...' : '选择图片' }}
          </button>
          
          <div v-if="backgroundImage" class="bg-controls-section">
            <!-- 亮度控制 -->
            <div class="brightness-control">
              <label class="brightness-label">亮度调节</label>
              <input
                type="range"
                min="30"
                max="100"
                :value="brightnessLevel"
                @input="updateBrightness($event.target.value)"
                class="brightness-slider"
                :disabled="isLoadingBackground"
              />
              <span class="brightness-value">{{ brightnessLevel }}%</span>
            </div>
          </div>
          
          <button 
            v-if="backgroundImage" 
            class="clear-bg-btn" 
            @click="clearBackground"
            :disabled="isLoadingBackground"
          >
            清除背景
          </button>
          
          <div v-if="backgroundImage" class="bg-preview-container">
            <div class="bg-preview-title">当前背景</div>
            <div 
              class="bg-preview" 
              :style="{backgroundImage: `url(${backgroundImage})`, filter: `brightness(${brightnessLevel}%)`}"
            ></div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 输入区域 - 固定在底部 -->
    <div class="dialog-input">
      <textarea
        v-model="inputMessage"
        class="input"
        placeholder="输入你的回复..."
        @keydown.enter.exact.prevent="handleSendMessage"
        :disabled="!wsConnected || sending"
      ></textarea>
      <button 
        class="btn send-btn" 
        @click="handleSendMessage"
        :disabled="!inputMessage.trim() || !wsConnected || sending"
      >
        {{ sending ? '发送中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useTokenStore } from '../utils/tokenStore'
import { createSceneWebSocket } from '../utils/api'

export default {
  name: 'StoryDialog',
  props: {
    sceneId: {
      type: String,
      required: true
    },
    token: {
      type: String,
      required: true
    },
    scene: {
      type: Object,
      default: null
    },
    initialBackground: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    // Token is now received directly from props
    
    const messages = ref([])
    const inputMessage = ref('')
    const ws = ref(null)
    const wsConnected = ref(false)
    const sending = ref(false)
    const dialogContentRef = ref(null)
    const connectionError = ref('')
    const selectedOptionId = ref(null)
    // 背景相关状态
    const backgroundImage = ref(props.initialBackground || '')
    const showBackgroundPicker = ref(false)
    const fileInput = ref(null)
    const isLoadingBackground = ref(false)
    const brightnessLevel = ref(localStorage.getItem('storyDialogBrightness') || '80') // 默认80%亮度
    const backgroundStyle = ref({
      backgroundImage: backgroundImage.value ? `url(${backgroundImage.value})` : 'none',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      backgroundAttachment: 'fixed', // 固定背景，实现滚动时背景不动
      filter: `brightness(${brightnessLevel.value}%)`,
    })

    // 连接WebSocket
    const connectWebSocket = () => {
      if (!props.sceneId || !props.token) return
      
      // 关闭现有连接
      if (ws.value) {
        ws.value.close()
      }
      
      wsConnected.value = false
      
      // 建立新连接，只传递场景ID和token
      ws.value = createSceneWebSocket(
        props.sceneId,
        props.token,
        handleSceneMessage,
        handleSceneError,
        handleSceneClose,
        handleSceneOpen
      )
    }

    // 处理WebSocket打开
    const handleSceneOpen = () => {
      wsConnected.value = true
      // 不再自动发送初始消息，等待用户主动发起对话
      connectionError.value = '' // 清除错误信息
    }

    // 发送初始消息
    const sendInitialMessage = () => {
      if (ws.value && wsConnected.value) {
        // 发送一个初始消息开始对话
        const initialMessage = "开始对话"
        ws.value.sendMessage(initialMessage)
        sending.value = true
      }
    }

    // 处理剧情消息
    const handleSceneMessage = (data) => {
      sending.value = false
      connectionError.value = '' // 清除错误信息
      
      // 处理不同类型的消息
      if (data.type === 'text' && data.data) {
        const messageData = data.data
        console.log('处理剧情数据:', messageData)
        
        // 根据options_included字段确定是否显示选项
        let options = []
        if (messageData.options_included && messageData.options && Array.isArray(messageData.options)) {
          options = messageData.options
        } else if (!messageData.options_included) {
          options = []
        } else if (messageData.options && Array.isArray(messageData.options)) {
          // 兼容情况：有options但没有options_included字段
          options = messageData.options
        }
        
        // 添加AI回复到消息列表
        messages.value.push({
          role: 'assistant',
          content: messageData.reply || '',
          options: options,
          // 保存原始数据用于调试
          rawData: messageData
        })
      } else {
        // 兼容其他格式
        messages.value.push({
          role: 'assistant',
          content: data.reply || JSON.stringify(data),
          options: data.options || [],
          rawData: data
        })
      }
      
      // 滚动到底部
      nextTick(() => scrollToBottom())
    }

    // 处理WebSocket错误
    const handleSceneError = (error) => {
      sending.value = false
      console.error('WebSocket错误:', error)
      connectionError.value = '连接失败，请检查网络或服务器状态'
    }

    // 处理WebSocket关闭
    const handleSceneClose = () => {
      wsConnected.value = false
      sending.value = false
      console.log('WebSocket连接已关闭')
      connectionError.value = '连接已关闭'
    }

    // 发送消息
    const handleSendMessage = () => {
      const message = inputMessage.value.trim()
      if (!message || !ws.value || !wsConnected.value || sending.value) return
      
      // 添加用户消息到列表
      messages.value.push({
        role: 'user',
        content: message
      })
      
      // 清空输入框
      inputMessage.value = ''
      
      // 发送消息
      sending.value = true
      try {
        console.log('发送消息:', message)
        ws.value.sendMessage(message)
      } catch (error) {
        console.error('发送消息失败:', error)
        sending.value = false
        messages.value.push({
          role: 'assistant',
          content: '消息发送失败，请重试'
        })
        nextTick(() => scrollToBottom())
      }
      
      // 滚动到底部
      nextTick(() => scrollToBottom())
    }

    // 处理剧情选项点击
    const handleStoryOptionClick = (option) => {
      console.log('用户选择了剧情选项:', option)
      // 设置选中状态
      selectedOptionId.value = option.id
      
      // 创建用户消息
      messages.value.push({
        role: 'user',
        content: option.text
      })
      
      // 发送选项，直接发送选项文本内容，不带选项编号
      sending.value = true
      if (ws.value && wsConnected.value) {
        // 直接发送选项文本内容
        console.log('发送选项:', option.text)
        ws.value.sendMessage(option.text)
      }
      
      // 滚动到底部
      nextTick(() => scrollToBottom())
    }

    // 模拟回复（开发测试用）
    const simulateResponse = (userMessage) => {
      setTimeout(() => {
        // 随机决定是否带选项
        const hasOptions = Math.random() > 0.5
        
        let responseMessage
        if (hasOptions) {
          responseMessage = {
            type: 'text',
            data: {
              user_message: userMessage,
              reply: '这是一个模拟回复，包含选项供你选择：',
              options: [{id:"1",text:"继续聊天"},{id:"2",text:"查看更多"},{id:"3",text:"切换话题"},{id:"4",text:"结束对话"}],
              scene_included: false,
              memory_included: false,
              options_included: true
            }
          }
        } else {
          responseMessage = {
            type: 'text',
            data: {
              user_message: userMessage,
              reply: '这是一个不包含选项的模拟回复。你可以继续输入内容进行交流。',
              options: "",
              scene_included: false,
              memory_included: false,
              options_included: false
            }
          }
        }
        
        handleSceneMessage(responseMessage)
      }, 1000 + Math.random() * 1000)
    }

    // 背景相关函数
    const toggleBackgroundPicker = () => {
      showBackgroundPicker.value = !showBackgroundPicker.value
      // 如果打开选择器，点击其他区域时自动关闭
      if (showBackgroundPicker.value) {
        setTimeout(() => {
          const handleClickOutside = (event) => {
            const bgControls = event.target.closest('.background-controls')
            if (!bgControls && showBackgroundPicker.value) {
              showBackgroundPicker.value = false
              document.removeEventListener('click', handleClickOutside)
            }
          }
          document.addEventListener('click', handleClickOutside)
        }, 100)
      }
    }
    
    const triggerFileSelect = () => {
      if (fileInput.value) {
        fileInput.value.click()
      }
    }
    
    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (!file) return
      
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        alert('请选择有效的图片文件')
        return
      }
      
      // 验证文件大小（限制为10MB）
      if (file.size > 10 * 1024 * 1024) {
        alert('图片文件不能超过10MB')
        return
      }
      
      isLoadingBackground.value = true
      
      const reader = new FileReader()
      
      reader.onload = (e) => {
        // 验证base64内容
        if (!e.target.result || typeof e.target.result !== 'string') {
          alert('图片加载失败，请重试')
          isLoadingBackground.value = false
          return
        }
        
        // 预加载图片以确保它能正确显示
        const img = new Image()
        img.onload = () => {
          backgroundImage.value = e.target.result
          updateBackgroundStyle()
          // 保存到本地存储以便刷新后保持背景
          try {
            localStorage.setItem('storyDialogBackground', backgroundImage.value)
          } catch (err) {
            console.warn('无法保存背景图片到本地存储：', err)
          }
          isLoadingBackground.value = false
          showBackgroundPicker.value = false // 选择完成后自动关闭选择器
        }
        
        img.onerror = () => {
          alert('图片加载失败，请选择其他图片')
          isLoadingBackground.value = false
        }
        
        img.src = e.target.result
      }
      
      reader.onerror = () => {
        alert('文件读取失败，请重试')
        isLoadingBackground.value = false
      }
      
      reader.readAsDataURL(file)
      
      // 清空input，允许选择相同的文件
      event.target.value = ''
    }
    
    const clearBackground = () => {
      // 平滑过渡到无背景
      backgroundStyle.value.opacity = 0
      setTimeout(() => {
        backgroundImage.value = ''
        updateBackgroundStyle()
        try {
          localStorage.removeItem('storyDialogBackground')
        } catch (err) {
          console.warn('无法从本地存储中移除背景图片：', err)
        }
        // 恢复透明度
        setTimeout(() => {
          backgroundStyle.value.opacity = 1
        }, 100)
      }, 300)
    }
    
    const updateBackgroundStyle = () => {
      backgroundStyle.value = {
        backgroundImage: backgroundImage.value ? `url(${backgroundImage.value})` : 'none',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
        // 移除固定opacity设置，让用户通过亮度滑块完全控制
        filter: `brightness(${brightnessLevel.value}%)`,
      }
    }
    
    const updateBrightness = (value) => {
      brightnessLevel.value = value
      backgroundStyle.value.filter = `brightness(${value}%)`
      // 保存亮度设置到本地存储
      try {
        localStorage.setItem('storyDialogBrightness', value)
      } catch (err) {
        console.warn('无法保存亮度设置到本地存储：', err)
      }
    }
    
    // 滚动到底部 - 更健壮的实现
    const scrollToBottom = () => {
      if (dialogContentRef.value) {
        // 使用setTimeout确保DOM已更新
        setTimeout(() => {
          if (dialogContentRef.value) {
            const { scrollHeight, clientHeight } = dialogContentRef.value;
            // 确保滚动到底部的最底部位置
            dialogContentRef.value.scrollTop = scrollHeight - clientHeight;
          }
        }, 100);
      }
    }

    // 监听sceneId和token变化
    watch([() => props.sceneId, () => props.token], () => {
      messages.value = []
      connectWebSocket()
    }, { immediate: true })
    
    // 监听初始背景变化
    watch(() => props.initialBackground, (newVal) => {
      if (newVal && newVal !== backgroundImage.value) {
        backgroundImage.value = newVal
        updateBackgroundStyle()
      }
    })

    onMounted(() => {
      // 从本地存储恢复背景
      const savedBg = localStorage.getItem('storyDialogBackground')
      if (savedBg) {
        backgroundImage.value = savedBg
        updateBackgroundStyle()
      }
      
      // 如果是开发环境，添加模拟数据测试
      if (import.meta.env.DEV && !wsConnected.value) {
        console.log('开发环境：使用模拟数据进行测试')
        setTimeout(() => {
          simulateResponse('开始对话')
        }, 1000)
      }
    })

    onBeforeUnmount(() => {
      if (ws.value) {
        ws.value.close()
      }
    })

    return {
        messages,
        inputMessage,
        wsConnected,
        sending,
        dialogContentRef,
        selectedOptionId,
        backgroundImage,
        showBackgroundPicker,
        fileInput,
        backgroundStyle,
        isLoadingBackground,
        brightnessLevel,
        handleSendMessage,
        handleStoryOptionClick,
        toggleBackgroundPicker,
        triggerFileSelect,
        handleFileSelect,
        clearBackground,
        updateBrightness
      }
  }
}
</script>

<style scoped>
.story-dialog-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  position: relative;
  /* 移除固定背景色，让背景图片能够完全显示 */
  background-color: transparent;
  overflow: hidden;
  transition: background-image 0.3s ease-in-out, background-color 0.3s ease-in-out;
}

.dialog-content {
  flex: 1;
  overflow-y: auto;
  padding: 40px;
  display: flex;
  flex-direction: column;
  position: relative;
  font-size: 16px;
  padding-bottom: 200px; /* 增加底部padding以适应上移的输入框 */
  /* 调整滚动条样式而不是完全隐藏 */
  -ms-overflow-style: auto;  /* IE and Edge - 使用默认滚动条 */
  scrollbar-width: thin;     /* Firefox - 使用细滚动条 */
  scrollbar-color: #e0e0e0 transparent; /* Firefox - 滚动条颜色 */
  /* 降低背景不透明度，确保背景图片可见的同时保持文字可读性 */
  background: rgba(255, 255, 255, 0.8); /* 降低不透明度 */
  backdrop-filter: blur(3px); /* 降低模糊效果，让背景图片更清晰可见 */
  transition: background-color 0.3s ease, backdrop-filter 0.3s ease;
}

/* 当有背景图片时略微增加对话内容的对比度，但保持背景图片可见 */
.story-dialog-container[style*="background-image"] .dialog-content {
  background: rgba(255, 255, 255, 0.85);
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.05);
}

/* 美化滚动条 - Chrome, Safari and Opera */
.dialog-content::-webkit-scrollbar {
  width: 6px; /* 显示细滚动条 */
}

.dialog-content::-webkit-scrollbar-track {
  background: transparent;
}

.dialog-content::-webkit-scrollbar-thumb {
  background-color: #e0e0e0;
  border-radius: 3px;
}

.dialog-content::-webkit-scrollbar-thumb:hover {
  background-color: #d0d0d0;
}

/* 错误提示样式 - 简化版 */
.error-message {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background-color: rgba(255, 242, 240, 0.95);
  border: 1px solid #ffccc7;
  border-radius: 12px;
  color: #ff4d4f;
  margin-bottom: 20px;
  font-size: 16px;
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.1);
}

.reconnect-btn {
  padding: 8px 16px;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.reconnect-btn:hover {
  background-color: #ff7875;
}

.welcome-message {
  background: rgba(255, 255, 255, 0.98);
  padding: 20px;
  border-radius: 12px;
  margin: 20px auto;
  max-width: 600px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.story-intro {
  background: rgba(255, 255, 255, 0.98);
  padding: 40px;
  border-radius: 16px;
  margin: 100px auto;
  max-width: 800px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  animation: fadeIn 1s ease-in;
  transition: all 0.3s ease;
}

/* 有背景图片时增强卡片效果 */
.story-dialog-container[style*="background-image"] .story-intro {
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.story-intro h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
  color: #333;
  font-weight: 700;
}

.story-intro p {
  font-size: 1.2em;
  margin: 12px 0;
  color: #444;
  line-height: 1.8;
}

/* 消息样式 - 完全复刻图片效果 */
.message-wrapper {
  display: flex;
  align-items: flex-start;
  margin-bottom: 30px;
  animation: fadeIn 0.3s ease;
}

.user-message {
  justify-content: flex-end;
}

.ai-message {
  justify-content: center;
}

.ai-message .message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.user-message .message-content {
  max-width: 60%;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

/* AI消息气泡 - 完全复刻图片中的圆角矩形样式 */
.ai-message .message-text {
  background: rgba(255, 255, 255, 0.98);
  padding: 16px 24px;
  border-radius: 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  line-height: 1.6;
  word-wrap: break-word;
  position: relative;
  font-size: 16px;
  color: #333;
  border: 1px solid #f0f0f0;
}

/* 有背景图片时增强AI消息气泡的对比度 */
.story-dialog-container[style*="background-image"] .ai-message .message-text {
  background: rgba(255, 255, 255, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

/* 添加聊天气泡的三角形 */
.ai-message .message-text::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 12px solid transparent;
  border-right: 12px solid transparent;
  border-top: 12px solid #ffffff;
}

/* 用户消息气泡 */
.user-message .message-text {
  background: rgba(240, 240, 240, 0.98);
  padding: 16px 24px;
  border-radius: 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  line-height: 1.6;
  word-wrap: break-word;
  font-size: 16px;
  color: #333;
}

/* 有背景图片时增强用户消息气泡的对比度 */
.story-dialog-container[style*="background-image"] .user-message .message-text {
  background: rgba(240, 240, 240, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 剧情选项样式 - 复刻图片中的圆角卡片效果 */
.story-options {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 30px;
  justify-content: center;
  max-width: 100%;
}

.story-option-btn {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  padding: 12px 24px;
  cursor: pointer;
  text-align: center;
  transition: all 0.3s ease;
  font-size: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
  min-width: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-weight: 500;
}

/* 有背景图片时增强选项按钮的对比度 */
.story-dialog-container[style*="background-image"] .story-option-btn {
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

/* 选项前面的圆形样式 */
.story-option-btn::before {
  content: '';
  display: inline-block;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #d0d0d0;
  margin-right: 10px;
  transition: all 0.3s ease;
}

/* 选中状态 - 完全复刻图片中的实心圆点效果 */
.story-option-btn.selected {
  border-color: #000000;
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.story-option-btn.selected::before {
  background: #000000;
  border-color: #000000;
}

/* 悬停效果 */
.story-option-btn:hover {
  border-color: #000000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 背景控制按钮 */
.background-controls {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 200;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.bg-setting-btn {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #e0e0e0;
    border-radius: 20px;
    padding: 8px 16px;
    cursor: pointer;
    font-size: 14px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 4px;
    min-width: 80px;
    justify-content: center;
    font-weight: 500;
  }
  
  /* 有背景图片时增强背景设置按钮的对比度 */
  .story-dialog-container[style*="background-image"] .bg-setting-btn {
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .bg-setting-btn:hover:not(:disabled) {
    background: #ffffff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-1px);
  }
  
  .bg-setting-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
  }
  
  .bg-setting-btn.bg-active {
    background: rgba(240, 240, 240, 0.95);
    border-color: #c0c0c0;
  }

/* 背景选择器面板 */
.background-picker {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-width: 180px;
    position: relative;
  }
  
  /* 背景控制区域 */
  .bg-controls-section {
    border-top: 1px solid #f0f0f0;
    padding-top: 12px;
    margin-top: 8px;
  }
  
  /* 亮度控制 */
  .brightness-control {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
  }
  
  .brightness-label {
    font-size: 12px;
    color: #666;
    font-weight: 500;
    min-width: 70px;
  }
  
  .brightness-slider {
    flex: 1;
    -webkit-appearance: none;
    appearance: none;
    height: 4px;
    background: #e0e0e0;
    border-radius: 2px;
    outline: none;
    transition: background 0.3s ease;
  }
  
  .brightness-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    background: #000000;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .brightness-slider::-webkit-slider-thumb:hover {
    transform: scale(1.2);
    background: #333333;
  }
  
  .brightness-slider::-moz-range-thumb {
    width: 16px;
    height: 16px;
    background: #000000;
    border-radius: 50%;
    cursor: pointer;
    border: none;
    transition: all 0.3s ease;
  }
  
  .brightness-slider::-moz-range-thumb:hover {
    transform: scale(1.2);
    background: #333333;
  }
  
  .brightness-slider:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .brightness-value {
    font-size: 12px;
    color: #666;
    min-width: 40px;
    text-align: right;
  }
  
  /* 背景预览 */
  .bg-preview-container {
    margin-top: 12px;
    border-top: 1px solid #f0f0f0;
    padding-top: 12px;
  }
  
  .bg-preview-title {
    font-size: 12px;
    color: #666;
    margin-bottom: 6px;
    font-weight: 500;
  }
  
  .bg-preview {
    width: 100%;
    height: 70px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
  }

.select-bg-btn,
  .clear-bg-btn {
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s ease;
    font-weight: 500;
  }

  .select-bg-btn {
    background: #000000;
    color: white;
  }

  .select-bg-btn:hover:not(:disabled) {
    background: #333333;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .select-bg-btn:disabled {
    background: #666666;
    cursor: not-allowed;
    transform: none;
  }

  .clear-bg-btn {
    background: #f0f0f0;
    color: #333;
  }

  .clear-bg-btn:hover:not(:disabled) {
    background: #e0e0e0;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .clear-bg-btn:disabled {
    background: #e0e0e0;
    cursor: not-allowed;
    transform: none;
  }

/* 输入区域 - 固定在底部上方 */
  .dialog-input {
    display: flex;
    gap: 12px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.98);
    border-top: 1px solid #eee;
    position: fixed;
    bottom: 30px; /* 将输入框向上移动30px */
    left: 0;
    right: 0;
    z-index: 100;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
    backdrop-filter: blur(5px);
    transition: background-color 0.3s ease;
  }
  
  /* 有背景图片时增强输入区域的对比度 */
  .story-dialog-container[style*="background-image"] .dialog-input {
    background: rgba(255, 255, 255, 0.99);
    box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.1);
    border-top: 1px solid rgba(255, 255, 255, 0.8);
  }

.input {
  flex: 1;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px 24px;
  font-size: 1.1em;
  resize: none;
  min-height: 80px;
  max-height: 160px;
  font-family: inherit;
  transition: border-color 0.3s ease;
  background: #ffffff;
}

/* 有背景图片时增强输入框的对比度 */
.story-dialog-container[style*="background-image"] .input {
  border-color: #d0d0d0;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.input:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

.send-btn {
  align-self: flex-end;
  padding: 16px 32px;
  background: #000000;
  color: #fff;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1.1em;
  font-weight: 500;
  transition: all 0.3s ease;
}

.send-btn:hover:not(:disabled) {
  background: #333333;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 添加动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-message .message-content,
  .user-message .message-content {
    max-width: 85%;
  }
  
  .dialog-content {
    padding: 20px;
    padding-bottom: 100px;
    background: rgba(255, 255, 255, 0.95); /* 在移动端增加不透明度 */
  }
  
  .story-options {
    flex-direction: column;
    align-items: center;
  }
  
  .story-option-btn {
    width: 100%;
    max-width: 300px;
  }
  
  /* 移动端背景控制按钮样式 */
  .background-controls {
    top: 10px;
    right: 10px;
  }
  
  .bg-setting-btn {
    font-size: 12px;
    padding: 6px 12px;
  }
  
  .background-picker {
    min-width: 150px;
    padding: 12px;
  }
  
  /* 过渡动画 */
  .fade-enter-active, .fade-leave-active {
    transition: opacity 0.3s, transform 0.3s;
    transform-origin: top right;
  }
  .fade-enter-from {
    opacity: 0;
    transform: scale(0.9, 0.9);
  }
  .fade-leave-to {
    opacity: 0;
    transform: scale(0.9, 0.9);
  }
}
</style>