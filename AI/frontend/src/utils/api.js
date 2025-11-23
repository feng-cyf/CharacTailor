import axios from 'axios'
import { useTokenStore } from './tokenStore'
import { useSessionStore } from './sessionStore'

// 场景对话专用的WebSocket连接函数
const createSceneWebSocket = (sceneId, token, onMessage, onError, onClose, onOpen, personaId = '') => {
  // 根据规则：只有带api的路由使用5000端口（此URL包含/api路径）
  // 修改为大写的Scene以匹配C#后端控制器的路由
  let wsUrl = `ws://localhost:5000/api/Scene/ws?token=${token}&sceneId=${sceneId}`
  // 如果提供了角色ID，则添加到URL参数中
  if (personaId) {
    wsUrl += `&persona_id=${personaId}`
  }
  
  const ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('剧情WebSocket连接已建立')
    onOpen && onOpen()
  }

    ws.onmessage = (event) => {
      try {
        // 直接处理后端返回的原始数据
        const rawData = event.data
        
        try {
          // 尝试解析JSON
          const data = JSON.parse(rawData)
          onMessage && onMessage(data)
        } catch (parseError) {
          onMessage && onMessage({ type: 'text', data: { reply: rawData } })
        }
      } catch (e) {
        onError && onError(e)
      }
    }

    ws.onerror = (error) => {
      onError && onError(error)
    }

    ws.onclose = () => {
      onClose && onClose()
    }

    // 发送消息方法
    ws.sendMessage = (userMessage) => {
      const payload = {
        userMessage: userMessage
      }
      ws.send(JSON.stringify(payload))
    }

    return ws
}

// 获取场景列表
const getSceneList = async () => {
  try {
    console.log('调用GetScene接口获取场景列表...')
    // 使用已配置的api实例，确保使用正确的baseURL和拦截器
    const response = await axios.get('http://localhost:5000/api/Scene/GetScene', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
    console.log('GetScene接口返回数据:', response)
    return response.data // 返回response.data而不是整个response对象
  } catch (error) {
    console.error('获取场景列表失败:', error)
    throw error
  }
}

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

// 响应拦截器：总是返回 response.data
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API错误:', error)
    if (error.response && error.response.status === 401) {
      const tokenStore = useTokenStore()
      tokenStore.clearToken()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 请求拦截器：注入 Authorization
api.interceptors.request.use(
  config => {
    const tokenStore = useTokenStore()
    const token = tokenStore.getToken()
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  error => Promise.reject(error)
)

// 解析上传响应（严格按照后端：resp.data.{cloud_url,local_url,...}）
const normalizeUploadResponse = (resp, fallbackFile) => {
  const d = resp?.data || resp // 兼容意外结构
  const cloud_url = d?.cloud_url ?? null
  const local_url = d?.local_url ?? null
  const file_name = d?.file_name ?? fallbackFile?.name ?? null
  const file_size = d?.file_size ?? fallbackFile?.size ?? null
  return {
    success: !!(cloud_url || local_url),
    cloud_url, local_url, file_name, file_size, raw: resp
  }
}

// 文件上传（image / video）
const uploadFile = async (file, fileType) => {
  console.log('开始文件上传:', { fileName: file.name, fileSize: file.size, fileType })
  const formData = new FormData()
  formData.append('file', file)

  const resp = await api.post(`/file/upload/${fileType}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total) {
        const progress = Math.round((e.loaded * 100) / e.total)
        console.log(`上传进度: ${progress}%`)
      }
    }
  })

  console.log('上传响应数据(已过拦截器):', resp)
  const normalized = normalizeUploadResponse(resp, file)
  if (!normalized.success) {
    console.warn('上传成功但未找到cloud_url/local_url:', resp)
  }

  return {
    success: normalized.success,
    cloud_url: normalized.cloud_url,   // 发给AI
    local_url: normalized.local_url,   // 前端预览
    file_name: normalized.file_name,
    file_size: normalized.file_size,
    original_response: resp
  }
}

// 登录
const login = async (credentials) => {
  try {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    return await api.post('/user/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  } catch (error) {
    console.error('登录API错误详情:', error)
    if (error.response) {
      return { code: error.response.status, message: error.response.data.message || '服务器错误', data: error.response.data }
    } else if (error.request) {
      return { code: 0, message: '网络连接失败，请检查您的网络', error: 'network_error' }
    } else {
      return { code: 0, message: '请求配置错误', error: error.message }
    }
  }
}

// Persona APIs
const getUserPersonas = async (userId) => {
  try {
    console.log('调用API获取角色列表，用户ID:', userId)
    // 确保URL格式正确，后端路由参数是_id
    const response = await api.post(`/user/get_persona/${encodeURIComponent(userId)}`)
    console.log('获取角色列表响应:', response)
    
    // 更新浏览器存储中的会话映射
    const sessionStore = useSessionStore()
    if (response && response.code === 200 && response.data && Array.isArray(response.data)) {
      console.log('开始更新会话映射')
      response.data.forEach(persona => {
        if (persona.persona_id && persona.session_id) {
          console.log(`更新角色 ${persona.persona_id} 的会话ID: ${persona.session_id}`)
          // 添加或更新会话信息
          sessionStore.addOrUpdateSession({
            session_id: persona.session_id,
            persona_id: persona.persona_id,
            persona_name: persona.persona_name,
            last_activity: new Date().toISOString(),
            lastActivityTime: Date.now()
          })
        }
      })
      console.log('会话映射更新完成')
    }
    
    return response
  } catch (error) {
    console.error('获取角色列表错误:', error)
    console.error('错误详情:', error.response || error.message)
    if (error.response) return error.response.data
    throw error
  }
}

const getPersonaDetail = async (personaId) => api.get(`/persona/get_persona/${personaId}`)

const createPersona = async (personaData) => {
  try {
    const tokenStore = useTokenStore()
    const sessionStore = useSessionStore()
    const token = tokenStore.getToken()

    const userInfo = tokenStore.getUserInfo()
    const userId = userInfo?.user_id || 'default_user'
    const sessionId = `${userId}_${personaData.persona_id}`
    sessionStore.setCurrentSessionId(sessionId)

    const userAgent = navigator.userAgent
    let browserPrefix = 'unknown'
    if (userAgent.includes('Edg') && !userAgent.includes('Edge')) browserPrefix = 'edge'
    else if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) browserPrefix = 'chrome'
    else if (userAgent.includes('Firefox')) browserPrefix = 'firefox'
    else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) browserPrefix = 'safari'

    let deviceId = localStorage.getItem('deviceId')
    if (!deviceId) {
      const randomId = crypto.randomUUID ? crypto.randomUUID() : `uuid_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      deviceId = `${browserPrefix}_${randomId}`
      localStorage.setItem('deviceId', deviceId)
    }

    let deviceType = 'pc'
    if (navigator.platform.includes('Mac')) deviceType = 'mac'
    else if (/iPad|iPhone|iPod|Android/i.test(userAgent)) {
      if (/iPad|tablet/i.test(userAgent) || (window.innerWidth >= 768 && window.innerHeight >= 1024)) deviceType = 'pad'
      else deviceType = 'phone'
    }

    const requestData = {
      persona: {
        persona_id: personaData.persona_id,
        persona_name: personaData.persona_name,
        description: personaData.description || '',
        tone: personaData.tone || 'neutral',
        functional_scene: personaData.functional_scene || 'general',
        deploy_type: personaData.is_cloud_model ? 'cloud' : 'local',
        speech_characteristics: personaData.speech_characteristics || null,
        emotional_bias: personaData.emotional_bias || null
      },
      session: {
        session_id: sessionId,
        device: { device_id: deviceId, device_type: deviceType, browser: browserPrefix, user_agent: userAgent }
      }
    }

    console.log('创建角色请求数据:', requestData)
    const response = await api.post('/persona/create', requestData, { headers: { Authorization: `Bearer ${token}` } })
    console.log('创建角色响应:', response)
    return response
  } catch (error) {
    console.error('创建角色错误:', error)
    if (error.response) return error.response.data
    throw error
  }
}

const updatePersona = async (personaData) => api.post('/persona/update_person', personaData)
const deletePersona = async (personaId) => api.post(`/persona/delete_person?id=${personaId}`)

// 工具：按 MIME 推断文件类型
const detectFileType = (file) => {
  if (file?.type?.startsWith('image/')) return 'image'
  if (file?.type === 'video/mp4') return 'video'
  return null // 后端仅支持 image / video
}

// 构建附件对象
const buildAttachment = (file, uploadResult, kind) => ({
  kind, // 'image' | 'video'
  name: uploadResult.file_name || file.name,
  size: uploadResult.file_size || file.size,
  mime: file.type,
  cloud_url: uploadResult.cloud_url || null,
  local_url: uploadResult.local_url || null
})

// 批量上传（支持图片/视频混合）
const uploadFilesAsAttachments = async (files) => {
  const list = Array.from(files || [])
  const tasks = list.map(async (f) => {
    const ft = detectFileType(f)
    if (!ft) {
      console.warn(`不支持的文件类型: ${f.type || f.name}`)
      return null
    }
    const r = await uploadFile(f, ft)
    return buildAttachment(f, r, ft)
  })
  const results = await Promise.all(tasks)
  return results.filter(Boolean)
}

// 创建WebSocket（并在实例上挂载发送方法，兼容多字段）
const createChatWebSocket = (personaInfo, onMessage, onError, onClose, useCloudModel = false) => {
  const tokenStore = useTokenStore()
  const sessionStore = useSessionStore()
  const token = tokenStore.getToken()
  
  // 获取personaId（兼容字符串ID或对象）
  const personaId = typeof personaInfo === 'string' || typeof personaInfo === 'number' ? personaInfo : personaInfo.persona_id
  
  // 关键修改：首先确保会话已正确切换
  // 无论传入什么参数，都先确保获取或创建正确的会话ID
  let sessionId
  if (typeof personaInfo === 'object' && personaInfo !== null) {
    // 如果传入了完整的personaInfo，使用自动切换功能
    sessionId = sessionStore.autoSwitchToPersonaSession(personaInfo)
  } else {
    // 如果只传入了ID，先尝试找到对应的personaInfo
    // 这样可以确保即使只传入ID，也能创建与角色相关的会话
    const normalizedPersonaInfo = {
      persona_id: personaId,
      persona_name: 'AI助手',
      personaId: personaId,
      name: 'AI助手'
    }
    sessionId = sessionStore.autoSwitchToPersonaSession(normalizedPersonaInfo)
  }
  
  // 最后再获取一次最新的会话ID，确保使用的是最新值
  sessionId = sessionStore.getCurrentSessionId()
  console.log('createChatWebSocket - 最终使用的会话ID:', sessionId)

  const userAgent = navigator.userAgent
  let browserPrefix = 'unknown'
  if (userAgent.includes('Edg') && !userAgent.includes('Edge')) browserPrefix = 'edge'
  else if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) browserPrefix = 'chrome'
  else if (userAgent.includes('Firefox')) browserPrefix = 'firefox'
  else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) browserPrefix = 'safari'

  let deviceId = localStorage.getItem('deviceId')
  if (!deviceId) {
    const randomId = crypto.randomUUID ? crypto.randomUUID() : `uuid_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    deviceId = `${browserPrefix}_${randomId}`
    localStorage.setItem('deviceId', deviceId)
  }

  let deviceType = 'pc'
  if (navigator.platform.includes('Mac')) deviceType = 'mac'
  else if (/iPad|iPhone|iPod|Android/i.test(userAgent)) {
    if (/iPad|tablet/i.test(userAgent) || (window.innerWidth >= 768 && window.innerHeight >= 1024)) deviceType = 'pad'
    else deviceType = 'phone'
  }

  // 根据规则：只有带api的路由使用5000端口，其他使用8000端口（此路径不包含/api）
  const ws = new WebSocket(`ws://localhost:8000/AIChat/ws/${personaId}?token=${token}&use_cloud_model=${useCloudModel}&session_id=${sessionId}&device_id=${encodeURIComponent(deviceId)}&device_type=${deviceType}`)

  ws.onopen = () => console.log(`WebSocket连接已建立，模型类型: ${useCloudModel ? '云端模型' : '本地模型'}`)

  let accumulatedResponse = ''
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('WebSocket接收消息:', data)
      if (data.type === 'stream') {
        accumulatedResponse += data.message
        onMessage && onMessage(accumulatedResponse, event.data)
      } else if (data.type === 'end') {
        onMessage && onMessage(data.message, event.data)
        accumulatedResponse = ''
      } else if (data.type === 'error') {
        console.error('WebSocket错误消息:', data.message)
        onMessage && onMessage(`[错误] ${data.message}`, event.data)
        accumulatedResponse = ''
      } else if (data.type === 'start') {
        console.log('开始生成回复...')
      } else {
        onMessage && onMessage(data.message || data, event.data)
      }
    } catch (e) {
      console.error('解析WebSocket消息失败:', e)
      onMessage && onMessage(event.data, event.data)
    }
  }
  ws.onerror = (error) => { console.error('WebSocket错误:', error); onError && onError(error) }
  ws.onclose = () => { console.log('WebSocket连接已关闭'); onClose && onClose() }

  // 发送（文本 + 附件），兼容后端可能的字段命名
  ws.sendMessage = (content, attachments = []) => {
    const images = attachments.filter(a => a.kind === 'image' && a.cloud_url).map(a => a.cloud_url)
    const videos = attachments.filter(a => a.kind === 'video' && a.cloud_url).map(a => a.cloud_url)
    
    // 根据附件类型设置user_message_type
    let user_message_type = 'text';
    if (images.length > 0) {
      user_message_type = 'image';
    } else if (videos.length > 0) {
      user_message_type = 'video';
    }

    const payload = {
      // 文本双字段别名，后端可取其中之一
      content: content || '',
      message: content || '',
      // 文件字段别名：images/image_urls，videos/video_urls
      images,
      image_urls: images,
      videos,
      video_urls: videos,
      // 完整附件留作后端扩展
      attachments,
      // 会话标识
      session_id: sessionId,
      persona_id: personaId,
      // 类型与角色（如后端用到）
      type: 'message',
      role: 'user',
      // 添加user_message_type参数，后端可通过data.get("user_message_type", "")获取
      user_message_type,
      // 添加文件URL参数，与后端data.get("user_file_local_url", null)和data.get("user_file_cloud_url", null)对应
      user_file_local_url: attachments.length > 0 ? attachments[0].local_url : null,
      user_file_cloud_url: attachments.length > 0 ? attachments[0].cloud_url : null
    }
    ws.send(JSON.stringify(payload))
  }

  ws.sendText = (content) => ws.sendMessage(content, [])

  ws.sendFiles = async (content, files) => {
    const attachments = await uploadFilesAsAttachments(files)
    ws.sendMessage(content, attachments)
    return attachments
  }

  return ws
}

const getDialogHistory = async (sessionId, personaId) => {
  try {
    // 直接使用axios的全量响应，不依赖response.data
    const response = await api.get(`/dialog?session_id=${sessionId}&persona_id=${personaId}`)
    console.log('获取历史对话完整响应:', response)
    
    // 尝试不同的响应数据获取方式
    let data = response.data || response
    console.log('获取历史对话数据:', data)
    console.log('数据类型:', typeof data)
    console.log('是否包含bot_response:', data && 'bot_response' in data)
    console.log('是否包含user_msg:', data && 'user_msg' in data)
    
    // 处理情况1: 包含bot_response、user_msg和time数组的旧格式
    if (data && data.bot_response && data.user_msg && Array.isArray(data.bot_response) && Array.isArray(data.user_msg)) {
      console.log('检测到旧格式数据（数组形式），开始转换...')
      const transformedData = []
      
      // 假设bot_response和user_msg数组长度相同
      const messageCount = Math.min(data.bot_response.length, data.user_msg.length)
      console.log('消息数量:', messageCount)
      
      for (let i = 0; i < messageCount; i++) {
        console.log(`处理消息索引${i}`)
        
        // 添加用户消息
        const userMsg = data.user_msg[i]
        if (userMsg) {
          const userMessageObj = {
            role: 'user',
            content: userMsg.user_message || '',
            user_message_type: userMsg.user_type || 'text',
            user_file_url: userMsg.user_file_url || '',
            time: data.time && data.time[i] ? data.time[i] : new Date().toISOString()
          }
          console.log('添加用户消息:', userMessageObj)
          transformedData.push(userMessageObj)
        }
        
        // 添加AI回复消息 - 使用assistant作为角色名
        const botResponse = data.bot_response[i]
        if (botResponse) {
          const assistantMessageObj = {
            role: 'assistant',
            content: botResponse.bot_response || '',
            bot_response_type: botResponse.bot_type || 'text',
            bot_file_url: botResponse.bot_file_url || '',
            time: data.time && data.time[i] ? data.time[i] : new Date().toISOString()
          }
          console.log('添加AI消息:', assistantMessageObj)
          transformedData.push(assistantMessageObj)
        }
      }
      
      console.log('转换后的聊天历史数据数量:', transformedData.length)
      console.log('转换后的聊天历史数据:', transformedData)
      return transformedData
    }
    // 处理情况2: 已经是消息对象数组的格式
    else if (Array.isArray(data)) {
      console.log('检测到已格式化的消息数组，确保角色名称正确...')
      const normalizedData = data.map(item => ({
        ...item,
        role: item.role === 'bot' ? 'assistant' : item.role
      }))
      return normalizedData
    }
    // 处理情况3: 标准API响应格式（有code和data字段）
    else if (data && data.code && data.data) {
      console.log('检测到标准API响应格式...')
      if (Array.isArray(data.data)) {
        const normalizedData = data.data.map(item => ({
          ...item,
          role: item.role === 'bot' ? 'assistant' : item.role
        }))
        return normalizedData
      }
      return data.data
    }
    
    // 兜底方案：如果不是预期格式，尝试把整个对象包装成数组返回
    console.log('未识别的数据格式，返回原始数据...')
    return data ? [data] : []
  } catch (error) {
    console.error('获取历史对话错误:', error)
    if (error.response && error.response.data) {
      console.log('错误响应数据:', error.response.data)
      return error.response.data
    }
    return []
  }
}

// 便捷方法：直接上传并发送
const sendTextAndFiles = async (ws, content, files) => {
  const attachments = await uploadFilesAsAttachments(files)
  ws.sendMessage(content, attachments)
  return attachments
}

export {
  api,
  login,
  getUserPersonas,
  createPersona,
  createChatWebSocket,
  createSceneWebSocket,
  getDialogHistory,
  getSceneList,
  uploadFile,
  sendTextAndFiles
}