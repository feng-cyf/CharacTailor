<template>
  <div class="gomoku-container">
    <!-- 游戏头部 -->
    <div class="game-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">返回</button>
        <h1>五子棋对战</h1>
      </div>
      <div class="game-info">
        <div class="player-info">
          <div class="player">
            <span class="player-icon">👤</span>
            <span class="player-name">我</span>
            <span class="player-piece black"></span>
          </div>
          <div class="vs">VS</div>
          <div class="player">
            <span class="player-icon">🤖</span>
            <span class="player-name">{{ personaName || 'AI' }}</span>
            <span class="player-piece white"></span>
          </div>
        </div>
        <div class="game-status" :class="gameStatusClass">
          {{ gameStatusText }}
        </div>
      </div>
    </div>

    <!-- 游戏内容区域 -->
    <div class="game-content">
      <!-- 棋盘区域 -->
      <div class="board-container">
        <div 
          class="gomoku-board"
          @click="handleBoardClick"
        >
          <div 
            v-for="(cell, index) in boardCells" 
            :key="index"
            class="board-cell"
            :class="{
              'has-piece': cell.piece !== null,
              'piece-black': cell.piece === 'black',
              'piece-white': cell.piece === 'white',
              'last-move': cell.isLastMove
            }"
            :style="{
              left: `${(cell.col - 1) * cellSize}px`,
              top: `${(cell.row - 1) * cellSize}px`
            }"
            @click.stop="handleCellClick(cell.row, cell.col)"
          >
            <div class="piece" v-if="cell.piece"></div>
          </div>
          <!-- 棋盘网格线 -->
          <div class="grid-lines">
            <div 
              v-for="i in 14" 
              :key="`h-${i}`"
              class="grid-line horizontal"
              :style="{ top: `${i * cellSize}px` }"
            ></div>
            <div 
              v-for="i in 14" 
              :key="`v-${i}`"
              class="grid-line vertical"
              :style="{ left: `${i * cellSize}px` }"
            ></div>
          </div>
        </div>
      </div>

      <!-- 聊天区域 -->
      <div class="chat-container">
        <div class="chat-header">
          <h3>聊天记录</h3>
        </div>
        <div class="chat-messages" ref="chatMessagesRef">
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            class="message"
            :class="message.sender === 'user' ? 'user-message' : 'ai-message'"
          >
            <div class="message-avatar">
              {{ message.sender === 'user' ? '👤' : '🤖' }}
            </div>
            <div class="message-content">
              <div class="message-sender">{{ message.sender === 'user' ? '我' : (personaName || 'AI') }}</div>
              <div class="message-text">{{ message.content }}</div>
            </div>
          </div>
          <div v-if="messages.length === 0" class="no-messages">
            <p>暂无消息</p>
          </div>
        </div>
        <div class="chat-input">
          <input 
            type="text" 
            v-model="messageInput"
            placeholder="输入消息..."
            @keyup.enter="sendMessage"
            :disabled="!isConnected || isGameOver"
          />
          <button 
            @click="sendMessage"
            :disabled="!isConnected || isGameOver || !messageInput.trim()"
          >
            发送
          </button>
        </div>
      </div>
    </div>

    <!-- 游戏结束弹窗 -->
    <div v-if="isGameOver" class="game-over-modal">
      <div class="modal-content">
        <h2>{{ gameResultText }}</h2>
        <p>{{ gameResultDescription }}</p>
        <div class="modal-buttons">
          <button @click="restartGame">再来一局</button>
          <button @click="goBack">返回选择</button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>{{ loadingText }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTokenStore } from '../utils/tokenStore'

export default {
  name: 'GomokuGame',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const tokenStore = useTokenStore()
    
    // 从路由参数获取信息
    const personaId = route.query.persona_id
    const personaName = route.query.persona_name
    
    // 游戏状态
    const isConnected = ref(false)
    const isGameOver = ref(false)
    const currentPlayer = ref('black') // 黑棋先行
    const gameStatus = ref('waiting') // waiting, playing, gameOver
    const gameWinner = ref(null)
    const isLoading = ref(true)
    const loadingText = ref('正在连接游戏...')
    
    // WebSocket连接
    let ws = null
    const chatMessagesRef = ref(null)
    
    // 棋盘配置
    const boardSize = 15 // 15x15棋盘
    const cellSize = 30 // 每个格子大小
    const boardCells = ref([])
    
    // 消息相关
    const messages = ref([])
    const messageInput = ref('')
    
    // 初始化棋盘
    const initializeBoard = () => {
      const cells = []
      for (let row = 1; row <= boardSize; row++) {
        for (let col = 1; col <= boardSize; col++) {
          cells.push({
            row,
            col,
            piece: null, // null, 'black', 'white'
            isLastMove: false
          })
        }
      }
      boardCells.value = cells
    }
    
    // 获取棋盘单元格
    const getCell = (row, col) => {
      return boardCells.value.find(cell => cell.row === row && cell.col === col)
    }
    
    // 计算属性
    const gameStatusText = computed(() => {
      switch (gameStatus.value) {
        case 'waiting':
          return '准备中...'
        case 'playing':
          return currentPlayer.value === 'black' ? '轮到你落子' : 'AI思考中...'
        case 'gameOver':
          return gameWinner.value ? `${gameWinner.value === 'black' ? '你赢了！' : 'AI赢了！'}` : '游戏结束'
        default:
          return '未知状态'
      }
    })
    
    const gameStatusClass = computed(() => {
      return gameStatus.value
    })
    
    const gameResultText = computed(() => {
      return gameWinner.value === 'black' ? '🎉 你赢了！' : '🎮 AI赢了！'
    })
    
    const gameResultDescription = computed(() => {
      return gameWinner.value === 'black' ? '恭喜你取得了胜利！' : '再接再厉，下次一定可以赢！'
    })
    
    // WebSocket连接
    const connectWebSocket = () => {
      try {
        const token = tokenStore.getToken()
        // 连接到.NET后端的WebSocket服务
        const wsUrl = `ws://localhost:5000/api/Gomoku/ws?token=${token}&persona_id=${personaId}`
        
        ws = new WebSocket(wsUrl)
        
        ws.onopen = () => {
          console.log('WebSocket连接已建立')
          isConnected.value = true
          isLoading.value = false
          gameStatus.value = 'playing'
        }
        
        ws.onmessage = (event) => {
          handleWebSocketMessage(event.data)
        }
        
        ws.onerror = (error) => {
          console.error('WebSocket错误:', error)
          isLoading.value = false
          showError('连接出错，请重试')
        }
        
        ws.onclose = () => {
          console.log('WebSocket连接已关闭')
          isConnected.value = false
          if (!isGameOver.value) {
            showError('连接已断开')
          }
        }
      } catch (error) {
        console.error('WebSocket连接失败:', error)
        isLoading.value = false
        showError('无法连接到游戏服务器')
      }
    }
    
    // 处理WebSocket消息
    const handleWebSocketMessage = (data) => {
      try {
        console.log('收到后端消息:', data);
        // 先检查是否是字符串消息（游戏结束消息）
        if (typeof data === 'string' && data.includes('获胜')) {
          // 游戏结束消息
          const winner = data.includes('玩家1') ? 'black' : 'white'
          handleGameOver(winner)
          return
        }
        
        // 解析JSON格式的消息（AI落子响应）
        const message = JSON.parse(data)
        console.log('解析后的AI落子消息:', message);
        
        // 处理AI落子响应
        if (message.BestX !== undefined && message.BestY !== undefined) {
          // 计算棋盘坐标（从0-based转为1-based）
          const row = message.BestY + 1
          const col = message.BestX + 1
          console.log('AI落子位置:', {row, col});
          
          // 更新棋盘
          const cell = getCell(row, col)
          if (cell) {
            // 清除之前的最后落子标记
            boardCells.value.forEach(c => c.isLastMove = false)
            
            // 设置新的棋子（AI是白棋）
            cell.piece = 'white'
            cell.isLastMove = true
            console.log('成功更新棋盘，设置AI白棋');
          } else {
            console.error('未找到对应的棋盘单元格:', {row, col});
          }
          
          // 如果有聊天内容，添加到聊天记录
          if (message.chat) {
            addMessage('ai', message.chat)
          }
          
          // 切换回玩家回合
          currentPlayer.value = 'black'
        }
        // 处理错误消息
        else {
          // 显示错误消息
          console.error('无效的AI落子消息:', message);
          showError(data)
        }
      } catch (error) {
        console.error('解析WebSocket消息失败:', error, '原始数据:', data)
      }
    }
    
    // 处理游戏结束
    const handleGameOver = (winner) => {
      gameStatus.value = 'gameOver'
      gameWinner.value = winner
      isGameOver.value = true
      isConnected.value = false
      
      if (ws) {
        ws.close()
        ws = null
      }
    }
    
    // 处理棋盘点击
    const handleBoardClick = (event) => {
      // 防止点击空白区域触发
      if (event.target === event.currentTarget) {
        return
      }
    }
    
    // 处理单元格点击（落子）
    const handleCellClick = (row, col) => {
      // 检查是否可以落子
      if (!isConnected.value || gameStatus.value !== 'playing' || currentPlayer.value !== 'black' || isGameOver.value) {
        return
      }
      
      // 检查单元格是否已有棋子
      const cell = getCell(row, col)
      if (!cell || cell.piece !== null) {
        return
      }
      
      // 发送落子请求
      const userMessage = messageInput.value.trim()
      const moveData = {
        x: col - 1, // 调整为0-based索引
        y: row - 1, // 调整为0-based索引
        userMessage: userMessage
      }
      
      // 立即在前端更新棋盘，显示用户落子
      // 清除之前的最后落子标记
      boardCells.value.forEach(c => c.isLastMove = false)
      // 设置新的棋子（用户是黑棋）
      cell.piece = 'black'
      cell.isLastMove = true
      
      ws.send(JSON.stringify(moveData))
      
      // 清空消息输入框
      messageInput.value = ''
      
      // 如果有消息，添加到聊天记录
      if (userMessage) {
        addMessage('user', userMessage)
      }
      
      // 切换到AI回合
      gameStatus.value = 'playing'
      currentPlayer.value = 'white'
    }
    
    // 发送聊天消息
    const sendMessage = () => {
      const message = messageInput.value.trim()
      if (!message || !isConnected.value || isGameOver.value) {
        return
      }
      
      const chatData = {
        type: 'chat',
        content: message
      }
      
      ws.send(JSON.stringify(chatData))
      addMessage('user', message)
      messageInput.value = ''
    }
    
    // 添加消息到聊天记录
    const addMessage = (sender, content) => {
      messages.value.push({
        sender,
        content,
        timestamp: new Date()
      })
      
      // 滚动到底部
      nextTick(() => {
        if (chatMessagesRef.value) {
          chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
        }
      })
    }
    
    // 显示错误信息
    const showError = (message) => {
      // 简单的错误提示，实际项目中可以使用更好的提示组件
      console.error(message)
      alert(message)
    }
    
    // 重新开始游戏
    const restartGame = () => {
      // 重置游戏状态
      initializeBoard()
      isGameOver.value = false
      gameStatus.value = 'waiting'
      gameWinner.value = null
      currentPlayer.value = 'black'
      messages.value = []
      
      // 重新连接WebSocket
      if (ws) {
        ws.close()
        ws = null
      }
      
      isLoading.value = true
      loadingText.value = '正在重新连接...'
      connectWebSocket()
    }
    
    // 返回游戏选择页面
    const goBack = () => {
      if (ws) {
        ws.close()
        ws = null
      }
      router.push('/game')
    }
    
    // 组件挂载时
    onMounted(() => {
      initializeBoard()
      connectWebSocket()
    })
    
    // 组件卸载时
    onBeforeUnmount(() => {
      if (ws) {
        ws.close()
        ws = null
      }
    })
    
    return {
      // 游戏信息
      personaId,
      personaName,
      
      // 游戏状态
      isConnected,
      isGameOver,
      gameStatusText,
      gameStatusClass,
      gameResultText,
      gameResultDescription,
      isLoading,
      loadingText,
      
      // 棋盘
      boardCells,
      cellSize,
      
      // 消息
      messages,
      messageInput,
      chatMessagesRef,
      
      // 方法
      handleBoardClick,
      handleCellClick,
      sendMessage,
      restartGame,
      goBack
    }
  }
}
</script>

<style scoped>
.gomoku-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
  overflow: hidden;
}

/* 游戏头部 */
.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.game-header h1 {
  margin: 0;
  font-size: 24px;
}

.game-info {
  text-align: right;
}

.player-info {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 15px;
  margin-bottom: 5px;
}

.player {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
}

.player-icon {
  font-size: 18px;
}

.player-name {
  font-weight: 500;
}

.player-piece {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.5);
}

.player-piece.black {
  background-color: #000;
}

.player-piece.white {
  background-color: #fff;
}

.vs {
  font-weight: bold;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
}

.game-status {
  font-size: 14px;
  opacity: 0.9;
  padding: 5px 10px;
  border-radius: 12px;
  display: inline-block;
}

.game-status.waiting {
  background: rgba(255, 255, 255, 0.2);
}

.game-status.playing {
  background: rgba(46, 204, 113, 0.3);
}

.game-status.gameOver {
  background: rgba(155, 89, 182, 0.3);
}

/* 游戏内容区域 */
.game-content {
  flex: 1;
  display: flex;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

/* 棋盘区域 */
.board-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.gomoku-board {
  position: relative;
  width: 450px;
  height: 450px;
  background-color: #e9c97a;
  border: 2px solid #a87c32;
  border-radius: 4px;
  cursor: pointer;
}

.board-cell {
  position: absolute;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.piece {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  animation: placePiece 0.3s ease;
}

.piece-black .piece {
  background-color: #000;
}

.piece-white .piece {
  background-color: #fff;
  border: 1px solid #ccc;
}

.board-cell.last-move::after {
  content: '';
  position: absolute;
  width: 8px;
  height: 8px;
  background-color: #ff4d4d;
  border-radius: 50%;
  z-index: 3;
}

/* 网格线 */
.grid-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.grid-line {
  position: absolute;
  background-color: #000;
}

.grid-line.horizontal {
  width: 100%;
  height: 1px;
}

.grid-line.vertical {
  width: 1px;
  height: 100%;
}

/* 聊天区域 */
.chat-container {
  width: 350px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.chat-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.chat-messages {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  max-height: calc(100vh - 300px);
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.user-message {
  flex-direction: row;
}

.ai-message {
  flex-direction: row;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-sender {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.message-text {
  background-color: #f0f0f0;
  padding: 10px 12px;
  border-radius: 8px;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.4;
}

.user-message .message-text {
  background-color: #667eea;
  color: white;
}

.no-messages {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.chat-input {
  padding: 15px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 10px;
}

.chat-input input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.chat-input input:focus {
  border-color: #667eea;
}

.chat-input input:disabled {
  background-color: #f5f5f5;
  color: #999;
}

.chat-input button {
  padding: 10px 20px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.chat-input button:hover:not(:disabled) {
  background-color: #5a5fd8;
}

.chat-input button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 游戏结束弹窗 */
.game-over-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
}

.modal-content h2 {
  margin: 0 0 15px 0;
  font-size: 28px;
  color: #333;
}

.modal-content p {
  margin: 0 0 30px 0;
  font-size: 16px;
  color: #666;
}

.modal-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.modal-buttons button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.modal-buttons button:first-child {
  background-color: #667eea;
  color: white;
}

.modal-buttons button:first-child:hover {
  background-color: #5a5fd8;
}

.modal-buttons button:last-child {
  background-color: #f0f0f0;
  color: #333;
}

.modal-buttons button:last-child:hover {
  background-color: #e0e0e0;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content {
  text-align: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes placePiece {
  from {
    transform: scale(0.5);
    opacity: 0.5;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .game-content {
    flex-direction: column;
  }
  
  .chat-container {
    width: 100%;
    height: 300px;
  }
  
  .gomoku-board {
    width: 400px;
    height: 400px;
  }
}

@media (max-width: 768px) {
  .game-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .header-left {
    order: 2;
  }
  
  .game-info {
    order: 1;
    text-align: center;
  }
  
  .player-info {
    justify-content: center;
  }
  
  .gomoku-board {
    width: 300px;
    height: 300px;
  }
  
  .board-cell {
    width: 20px;
    height: 20px;
  }
  
  .piece {
    width: 16px;
    height: 16px;
  }
}
</style>