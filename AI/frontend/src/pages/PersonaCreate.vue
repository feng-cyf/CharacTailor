<template>
  <div class="persona-create-container">
    <div class="persona-create-header">
      <h1>创建新的AI人设</h1>
      <p>为您的AI助手设置独特的性格和行为特征</p>
    </div>
    
    <form @submit.prevent="handleSubmit" class="persona-form">
      <div class="form-group">
        <label for="personaName">人设名称</label>
        <input 
          type="text" 
          id="personaName" 
          v-model="formData.persona_name" 
          required 
          placeholder="请输入人设名称"
        >
      </div>
      
      <div class="form-group">
        <label for="personaId">人设ID</label>
        <input 
          type="text" 
          id="personaId" 
          v-model="formData.persona_id" 
          required 
          placeholder="请输入人设ID (英文、数字、下划线组合)"
          pattern="[a-zA-Z0-9_]+"
        >
      </div>
      
      <div class="form-group">
        <label for="description">人设描述</label>
        <textarea 
          id="description" 
          v-model="formData.description" 
          rows="4" 
          placeholder="请描述这个人设的特点和背景"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label for="tone">语调风格</label>
        <input 
          type="text" 
          id="tone" 
          v-model="formData.tone" 
          required 
          placeholder="请输入语调风格（例如：neutral、friendly、professional、casual、serious、humorous）"
        >
      </div>
      
      <div class="form-group">
        <label for="functionalScene">应用场景</label>
        <input 
          type="text" 
          id="functionalScene" 
          v-model="formData.functional_scene" 
          required 
          placeholder="请输入应用场景（例如：general、education、entertainment、work、creative）"
        >
      </div>
      
      <div class="form-group">
        <label for="speechCharacteristics">语言特征 (JSON格式)</label>
        <textarea 
          id="speechCharacteristics" 
          v-model="formData.speech_characteristics" 
          rows="3" 
          placeholder='请输入语言特征的JSON格式数据，例如：{"vocabulary_level": "advanced", "sentence_structure": "complex"}'
        ></textarea>
        <small style="color: #666; display: block; margin-top: 5px;">可选字段，默认为空对象</small>
      </div>
      
      <div class="form-group">
        <label for="emotionalBias">情感倾向 (JSON格式)</label>
        <textarea 
          id="emotionalBias" 
          v-model="formData.emotional_bias" 
          rows="3" 
          placeholder='请输入情感倾向的JSON格式数据，例如：{"optimism": 0.7, "patience": 0.9}'
        ></textarea>
        <small style="color: #666; display: block; margin-top: 5px;">可选字段，默认为空对象</small>
      </div>
      
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="formData.is_active">
          激活人设
        </label>
        <small style="color: #666; display: block; margin-top: 5px;">默认已激活</small>
      </div>
      
      <div class="form-group">
        <label>模型类型</label>
        <div class="radio-group">
          <label>
            <input type="radio" value="cloud" v-model="formData.deploy_type" required>
            云端模型
          </label>
          <label>
            <input type="radio" value="local" v-model="formData.deploy_type" required>
            本地模型
          </label>
        </div>
      </div>
      
      <div class="form-actions">
        <button type="button" class="btn-cancel" @click="handleCancel">取消</button>
        <button type="submit" class="btn-submit" :disabled="isSubmitting">
          {{ isSubmitting ? '创建中...' : '创建人设' }}
        </button>
      </div>
    </form>
    
    <!-- 提示信息 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { createPersona } from '../utils/api.js'
import { useTokenStore } from '../utils/tokenStore.js'

export default {
  name: 'PersonaCreate',
  setup() {
    const router = useRouter()
    const tokenStore = useTokenStore()
    const isSubmitting = ref(false)
    const message = ref('')
    const messageType = ref('')
    
    // 表单数据
    const formData = reactive({
      persona_id: '',
      persona_name: '',
      description: '',
      tone: 'neutral',
      functional_scene: 'general',
      deploy_type: 'cloud',
      speech_characteristics: '',
      emotional_bias: '',
      is_active: true
    })
    
    // 生成随机的persona_id
    const generatePersonaId = () => {
      const timestamp = Date.now().toString(36)
      const randomStr = Math.random().toString(36).substring(2, 8)
      return `persona_${timestamp}_${randomStr}`
    }
    
    // 处理表单提交
    const handleSubmit = async () => {
      try {
        // 如果没有填写persona_id，自动生成一个
        if (!formData.persona_id.trim()) {
          formData.persona_id = generatePersonaId()
        }
        
        isSubmitting.value = true
        message.value = ''
        
        // 处理JSON格式字段
        let speechCharData = {}
        let emotionalBiasData = {}
        
        if (formData.speech_characteristics.trim()) {
          try {
            speechCharData = JSON.parse(formData.speech_characteristics)
          } catch (e) {
            message.value = '语言特征格式错误，请输入有效的JSON格式'
            messageType.value = 'error'
            isSubmitting.value = false
            return
          }
        }
        
        if (formData.emotional_bias.trim()) {
          try {
            emotionalBiasData = JSON.parse(formData.emotional_bias)
          } catch (e) {
            message.value = '情感倾向格式错误，请输入有效的JSON格式'
            messageType.value = 'error'
            isSubmitting.value = false
            return
          }
        }
        
        // 准备发送给API的数据
        const personaData = {
          ...formData,
          speech_characteristics: speechCharData,
          emotional_bias: emotionalBiasData
        }
        
        // 移除可能不需要的字段
        delete personaData.is_cloud_model
        
        console.log('提交的人设数据:', personaData)
        
        // 调用创建人设API
        const response = await createPersona(personaData)
        
        if (response && response.code === 200) {
          message.value = '人设创建成功！'
          messageType.value = 'success'
          
          // 延迟后跳转到聊天页面
          setTimeout(() => {
            router.push('/chat')
          }, 1500)
        } else {
          message.value = response?.message || '创建人设失败，请重试'
          messageType.value = 'error'
        }
      } catch (error) {
        console.error('创建人设错误:', error)
        message.value = '创建过程中出现错误，请重试'
        messageType.value = 'error'
      } finally {
        isSubmitting.value = false
      }
    }
    
    // 取消创建，返回聊天页面
    const handleCancel = () => {
      router.push('/chat')
    }
    
    return {
      formData,
      isSubmitting,
      message,
      messageType,
      handleSubmit,
      handleCancel
    }
  }
}
</script>

<style scoped>
.persona-create-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  max-height: 100vh;
  overflow-y: auto;
  background-color: #f5f5f5;
  box-sizing: border-box;
}

.persona-create-header {
  text-align: center;
  margin-bottom: 40px;
}

.persona-create-header h1 {
  color: #333;
  font-size: 28px;
  margin-bottom: 10px;
}

.persona-create-header p {
  color: #666;
  font-size: 16px;
}

.persona-form {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #4a90e2;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: normal;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
}

.btn-cancel,
.btn-submit {
  padding: 12px 24px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel {
  background-color: #f0f0f0;
  color: #333;
}

.btn-cancel:hover {
  background-color: #e0e0e0;
}

.btn-submit {
  background-color: #4a90e2;
  color: white;
}

.btn-submit:hover {
  background-color: #357abd;
}

.btn-submit:disabled {
  background-color: #90c4e8;
  cursor: not-allowed;
}

.message {
  margin-top: 20px;
  padding: 15px;
  border-radius: 5px;
  text-align: center;
  font-size: 16px;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .persona-create-container {
    padding: 10px;
  }
  
  .persona-form {
    padding: 20px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn-cancel,
  .btn-submit {
    width: 100%;
  }
}
</style>