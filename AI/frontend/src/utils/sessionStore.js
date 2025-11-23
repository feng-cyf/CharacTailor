import { ref, reactive } from 'vue'
import { useTokenStore } from './tokenStore'

// 创建响应式的session状态
const currentSessionId = ref(localStorage.getItem('currentSessionId') || '')
const sessions = reactive(localStorage.getItem('sessions') ? JSON.parse(localStorage.getItem('sessions')) : [])
// 记录每个角色的会话历史映射
const personaSessionsMap = reactive({})

// 初始化会话映射
const initPersonaSessionsMap = () => {
  sessions.forEach(session => {
    const personaId = session.persona_id || session.personaId
    const sessionId = session.session_id || session.sessionId
    if (!personaSessionsMap[personaId]) {
      personaSessionsMap[personaId] = []
    }
    personaSessionsMap[personaId].push(sessionId)
  })
}

// 初始化
initPersonaSessionsMap()

// Session存储管理
const sessionStore = {
  // 获取当前会话ID
  getCurrentSessionId() {
    return currentSessionId.value
  },
  
  // 设置当前会话ID
  setCurrentSessionId(sessionId) {
    currentSessionId.value = sessionId
    localStorage.setItem('currentSessionId', sessionId)
  },
  
  // 获取所有会话列表
  getSessions() {
    return [...sessions]
  },
  
  // 添加或更新会话
  addOrUpdateSession(sessionInfo) {
    const index = sessions.findIndex(s => s.session_id === sessionInfo.session_id)
    if (index > -1) {
      // 更新现有会话
      Object.assign(sessions[index], sessionInfo)
    } else {
      // 添加新会话
      sessions.push(sessionInfo)
      
      // 更新角色会话映射
      const personaId = sessionInfo.persona_id || sessionInfo.personaId
      const sessionId = sessionInfo.session_id || sessionInfo.sessionId
      if (!personaSessionsMap[personaId]) {
        personaSessionsMap[personaId] = []
      }
      if (!personaSessionsMap[personaId].includes(sessionId)) {
        personaSessionsMap[personaId].push(sessionId)
      }
    }
    // 保存到localStorage
    localStorage.setItem('sessions', JSON.stringify(sessions))
  },
  
  // 更新会话活动时间
  updateSessionActivity(sessionId) {
    const session = this.getSession(sessionId)
    if (session) {
      session.last_activity = new Date().toISOString()
      session.lastActivityTime = Date.now()
      this.addOrUpdateSession(session)
    }
  },
  
  // 获取角色的所有会话
  getPersonaSessions(personaId) {
    if (!personaId) return []
    
    // 如果映射中没有，从sessions中查找
    if (!personaSessionsMap[personaId]) {
      personaSessionsMap[personaId] = sessions
        .filter(s => s.persona_id === personaId || s.personaId === personaId)
        .map(s => s.session_id || s.sessionId)
    }
    
    // 返回按最后活动时间排序的会话
    return sessions
      .filter(s => s.persona_id === personaId || s.personaId === personaId)
      .sort((a, b) => {
        const timeA = a.lastActivityTime || new Date(a.last_activity).getTime() || 0
        const timeB = b.lastActivityTime || new Date(b.last_activity).getTime() || 0
        return timeB - timeA
      })
  },
  
  // 自动切换到角色的最新会话，如果没有则创建新会话
  autoSwitchToPersonaSession(personaInfo) {
    console.log('开始自动切换会话:', personaInfo)
    const personaId = personaInfo.persona_id || personaInfo.personaId
    const personaName = personaInfo.persona_name || personaInfo.name || 'AI助手'
    
    // 确保personaId有效
    if (!personaId) {
      console.error('无效的角色ID:', personaId)
      return null
    }
    
    // 记录当前状态
    console.log('autoSwitch前 - 当前会话ID:', this.getCurrentSessionId())
    console.log('autoSwitch前 - personaSessionsMap状态:', JSON.stringify(personaSessionsMap))
    
    // 重新初始化personaSessionsMap，确保映射正确
    initPersonaSessionsMap()
    
    // 首先检查personaInfo中是否直接包含session_id
    if (personaInfo.session_id) {
      console.log(`从personaInfo中直接获取会话ID: ${personaInfo.session_id}`)
      const sessionId = personaInfo.session_id
      
      // 确保会话ID被正确设置为当前会话
      console.log(`设置当前会话ID为: ${sessionId}`)
      this.setCurrentSessionId(sessionId)
      this.updateSessionActivity(sessionId)
      
      // 验证会话ID是否已正确设置
      const updatedSessionId = this.getCurrentSessionId()
      console.log(`验证 - 更新后的会话ID: ${updatedSessionId}`)
      console.log(`会话ID设置${sessionId === updatedSessionId ? '成功' : '失败'}`)
      
      console.log(`使用personaInfo中的会话ID切换到角色 ${personaName}`)
      return sessionId
    }
    
    // 获取角色的所有会话
    const personaSessions = this.getPersonaSessions(personaId)
    console.log(`找到 ${personaSessions?.length || 0} 个与角色 ${personaId} 相关的会话`)
    
    let sessionId = null
    
    if (personaSessions.length > 0) {
      // 有现有会话，使用最新的一个
      const latestSession = personaSessions[0]
      sessionId = latestSession.session_id || latestSession.sessionId
      console.log(`切换到最近使用的会话: ${sessionId}`)
    } else {
      // 没有现有会话，创建新会话
      console.log('没有找到相关会话，创建新会话')
      sessionId = this.createNewSession(personaInfo)
      console.log(`为角色 ${personaName} 创建新会话: ${sessionId}`)
    }
    
    // 确保会话ID被正确设置为当前会话
    if (sessionId) {
      console.log(`设置当前会话ID为: ${sessionId}`)
      this.setCurrentSessionId(sessionId)
      this.updateSessionActivity(sessionId)
      
      // 验证会话ID是否已正确设置
      const updatedSessionId = this.getCurrentSessionId()
      console.log(`验证 - 更新后的会话ID: ${updatedSessionId}`)
      console.log(`会话ID设置${sessionId === updatedSessionId ? '成功' : '失败'}`)
    }
    
    console.log(`自动切换到角色 ${personaName} ${personaSessions.length > 0 ? '的现有会话' : '并创建新会话'}: ${sessionId}`)
    return sessionId
  },
  
  // 为角色创建新会话并自动切换
  createNewSessionAndSwitch(personaInfo) {
    console.log('创建新会话:', personaInfo)
    const newSessionId = this.createNewSession(personaInfo)
    this.setCurrentSessionId(newSessionId)
    console.log(`创建并切换到新会话: ${newSessionId}`)
    return newSessionId
  },
  
  // 获取特定会话信息
  getSession(sessionId) {
    return sessions.find(s => s.session_id === sessionId || s.sessionId === sessionId) || null
  },
  
  // 删除会话
  deleteSession(sessionId) {
    const index = sessions.findIndex(s => s.session_id === sessionId || s.sessionId === sessionId)
    if (index > -1) {
      // 清除角色会话映射
      const session = sessions[index]
      const personaId = session.persona_id || session.personaId
      if (personaId && personaSessionsMap[personaId]) {
        const mapIndex = personaSessionsMap[personaId].indexOf(sessionId)
        if (mapIndex > -1) {
          personaSessionsMap[personaId].splice(mapIndex, 1)
        }
      }
      
      sessions.splice(index, 1)
      localStorage.setItem('sessions', JSON.stringify(sessions))
      // 如果删除的是当前会话，清除当前会话ID
      if (currentSessionId.value === sessionId) {
        this.clearCurrentSession()
      }
    }
  },
  
  // 清除当前会话
  clearCurrentSession() {
    currentSessionId.value = ''
    localStorage.removeItem('currentSessionId')
  },
  
  // 清除所有会话
  clearAllSessions() {
    sessions.splice(0, sessions.length)
    currentSessionId.value = ''
    localStorage.removeItem('sessions')
    localStorage.removeItem('currentSessionId')
  },
  
  // 从服务器获取会话列表（用于同步）
  async syncSessionsFromServer() {
    try {
      const tokenStore = useTokenStore()
      const token = tokenStore.getToken()
      if (!token) return
      
      // 这里可以实现从服务器同步会话的逻辑
      // 例如：
      // const response = await api.get('/session/list')
      // if (response && response.code === 200) {
      //   sessions.splice(0, sessions.length)
      //   response.data.forEach(session => sessions.push(session))
      //   localStorage.setItem('sessions', JSON.stringify(sessions))
      // }
    } catch (error) {
      console.error('同步会话失败:', error)
    }
  },
  
  // 创建新会话（用于需要主动创建新会话的场景）
  createNewSession(personaInfo) {
    // 使用user_id和persona_id生成固定的session_id
    const tokenStore = useTokenStore()
    const userInfo = tokenStore.getUserInfo()
    const userId = userInfo?.user_id || 'default_user'
    
    const personaId = personaInfo.persona_id || personaInfo.personaId
    const personaName = personaInfo.persona_name || personaInfo.name || 'AI助手'
    
    // 使用user_id + persona_id + 时间戳的格式生成session_id，确保唯一性
    const newSessionId = `${userId}_${personaId}_${Date.now()}`
    
    // 创建会话信息，同时支持两种命名格式
    const sessionInfo = {
      // 带下划线格式
      session_id: newSessionId,
      persona_id: personaId,
      persona_name: personaName,
      created_at: new Date().toISOString(),
      last_activity: new Date().toISOString(),
      session_name: `与${personaName}的对话`,
      // 驼峰格式
      sessionId: newSessionId,
      personaId: personaId,
      lastActivityTime: Date.now()
    }
    
    // 添加并设置为当前会话
    this.addOrUpdateSession(sessionInfo)
    this.setCurrentSessionId(newSessionId)
    
    return newSessionId
  }
}

// 导出useSessionStore组合式函数
export const useSessionStore = () => {
  return sessionStore
}