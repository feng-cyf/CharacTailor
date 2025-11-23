AI/frontend/src/components/ChatComposer.vue
<template>
  <div class="chat-composer">
    <div class="attachments" v-if="previews.length">
      <div v-for="(p, idx) in previews" :key="idx" class="preview">
        <template v-if="p.kind === 'image'">
          <img :src="p.url" alt="preview" />
        </template>
        <template v-else-if="p.kind === 'video'">
          <video :src="p.url" controls></video>
        </template>
        <button class="remove" @click="removeFile(idx)">×</button>
      </div>
    </div>

    <textarea
      v-model="message"
      class="input"
      :placeholder="`向 ${personaInfo?.name || personaId || 'AI助手'} 发送消息...`"
      @keydown.enter.exact.prevent="handleSend"
    ></textarea>

    <div class="toolbar">
      <label class="btn">
        选择文件
        <input
          type="file"
          accept="image/*,video/mp4"
          multiple
          hidden
          @change="onSelectFiles"
        />
      </label>
      <span class="status" v-if="uploading">正在上传...</span>
      <button class="btn primary" :disabled="sending || !canSend" @click="handleSend">
        <span v-if="sending" class="loading-spinner"></span>
        {{ sending ? '发送中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { createChatWebSocket, uploadFile } from '../utils/api'

const props = defineProps({
  personaId: { type: [String, Number], required: false },
  personaInfo: { type: Object, required: false },
  useCloudModel: { type: Boolean, default: false }
})
const emit = defineEmits(['message', 'error', 'close', 'open'])

const message = ref('')
// 上传的文件信息 cloud_url/local_url等
const attachments = ref([]) // { kind, name, size, mime, cloud_url, local_url }
const previews = ref([])    // { url, kind }
const wsRef = ref(null)
const sending = ref(false)
const uploading = ref(false)
const fileInputRef = ref(null)

const canSend = computed(() => message.value.trim().length > 0 || attachments.value.length > 0)

// 仅支持 image / mp4类型(第一步)
const detectFileType = (file) => {
  if (file?.type?.startsWith('image/')) return 'image'
  if (file?.type === 'video/mp4') return 'video'
  return null
}

const onSelectFiles = async (e) => {
  const selected = Array.from(e.target.files || [])
  e.target.value = ''
  if (selected.length === 0) return

  uploading.value = true
  try {
    for (const f of selected) {
      const kind = detectFileType(f)
      if (!kind) {
        console.warn(`不支持的文件类型: ${f.type || f.name}`)
        continue
      }
      console.log('[上传] 调用接口:', `/file/upload/${kind}`, f.name)
      // 调用上传接口获取 cloud_url/local_url
      const r = await uploadFile(f, kind)
      console.log('[上传] 结果:', r)

      // 传给后端发送给AI的 cloud_url，预览用 local_url
      attachments.value.push({
        kind,
        name: r.file_name || f.name,
        size: r.file_size || f.size,
        mime: f.type,
        cloud_url: r.cloud_url || null,
        local_url: r.local_url || null
      })

      // 预览优先使用 local_url，没有的话使用 ObjectURL
      const previewUrl = r.local_url || URL.createObjectURL(f)
      previews.value.push({ url: previewUrl, kind })
    }
  } catch (err) {
    console.error('文件上传失败:', err)
  } finally {
    uploading.value = false
  }
}

const removeFile = (idx) => {
  const p = previews.value[idx]
  if (p?.url && p.url.startsWith('blob:')) URL.revokeObjectURL(p.url)
  previews.value.splice(idx, 1)
  attachments.value.splice(idx, 1)
}

const clearAll = () => {
  previews.value.forEach(p => {
    if (p.url && p.url.startsWith('blob:')) URL.revokeObjectURL(p.url)
  })
  previews.value = []
  attachments.value = []
}

const handleSend = async () => {
  if (!wsRef.value || wsRef.value.readyState !== WebSocket.OPEN) {
    console.warn('WebSocket 未连接')
    return
  }
  if (!canSend.value) return

  try {
    sending.value = true
    const text = message.value.trim()
    console.log('[发送] 文本+附件:', { text, attachments: attachments.value })
    
    // 创建用户消息对象，以便在前端渲染
    const userMessage = {
      role: 'user',
      content: text,
      // 设置用户消息类型
      user_message_type: attachments.value.length > 0 ? 
        (attachments.value[0].kind === 'image' ? 'image' : 'video') : 'text',
      // 添加附件信息
      attachments: [...attachments.value]
    }
    
    // 向父组件发送用户消息事件，以便渲染到页面上
    emit('userMessage', userMessage)
    
    // 直接使用已上传的文件信息，避免重复上传
    wsRef.value.sendMessage(text, attachments.value)
    message.value = ''
    clearAll()
  } catch (err) {
    console.error('发送失败:', err)
  } finally {
    sending.value = false
  }
}

// 创建WebSocket连接的函数
const createConnection = () => {
  console.log('ChatComposer - 创建WebSocket连接，参数:', props.personaInfo || props.personaId)
  
  // 关闭现有连接
  if (wsRef.value) {
    try {
      wsRef.value.close()
    } catch (e) {
      console.warn('关闭旧WebSocket连接时出错:', e)
    }
    wsRef.value = null
  }
  
  // 优先使用personaInfo对象（支持自动切换session），如果没有则使用personaId
  const ws = createChatWebSocket(
    props.personaInfo || props.personaId,
    (msg, raw) => emit('message', msg, raw),
    (err) => emit('error', err),
    () => emit('close'),
    props.useCloudModel
  )
  wsRef.value = ws
  ws.addEventListener('open', () => emit('open'))
}

onMounted(() => {
  createConnection()
})

// 监听personaId和personaInfo变化，重新创建连接
watch(
  () => [props.personaId, props.personaInfo],
  () => {
    console.log('ChatComposer - 检测到角色信息变化，重新创建连接')
    createConnection()
  },
  { deep: true }
)

onBeforeUnmount(() => {
  try {
    if (wsRef.value) {
      wsRef.value.close()
      wsRef.value = null
    }
  } catch {}
  clearAll()
})
</script>

<style scoped>
.chat-composer { display: flex; flex-direction: column; gap: 8px; }
.attachments { display: flex; flex-wrap: wrap; gap: 8px; }
.preview { position: relative; width: 120px; height: 120px; border: 1px solid #ddd; border-radius: 6px; overflow: hidden; background: #fafafa; }
.preview img, .preview video { width: 100%; height: 100%; object-fit: cover; }
.preview .remove { position: absolute; top: 2px; right: 2px; border: none; background: rgba(0,0,0,.55); color: #fff; border-radius: 50%; width: 20px; height: 20px; cursor: pointer; }
.input { width: 100%; min-height: 80px; padding: 8px; resize: vertical; border: 1px solid #ddd; border-radius: 6px; }
.toolbar { display: flex; gap: 12px; align-items: center; }
.btn { padding: 6px 12px; border: 1px solid #ddd; background: #fff; border-radius: 6px; cursor: pointer; }
.btn.primary { background: #1677ff; color: #fff; border-color: #1677ff; }
.btn:disabled { opacity: .6; cursor: not-allowed; }
.status { color: #666; font-size: 13px; }

/* 加载动画样式 */
.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 6px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>