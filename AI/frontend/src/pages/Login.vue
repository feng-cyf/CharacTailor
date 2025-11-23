<template>
  <div class="login-container">
    <div class="login-form">
      <h1 class="title">AI聊天助手</h1>
      <p class="subtitle">请登录您的账号</p>
      
      <div class="form-group">
        <label for="username">用户名</label>
        <input 
          type="text" 
          id="username" 
          v-model="formData.username" 
          placeholder="请输入用户名"
          class="form-input"
          @keyup.enter="handleLogin"
        />
      </div>
      
      <div class="form-group">
        <label for="password">密码</label>
        <input 
          type="password" 
          id="password" 
          v-model="formData.password" 
          placeholder="请输入密码"
          class="form-input"
          @keyup.enter="handleLogin"
        />
      </div>
      
      <button 
        class="login-button" 
        @click="handleLogin"
        :disabled="loading"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>
      
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../utils/api'
import { useTokenStore } from '../utils/tokenStore'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const tokenStore = useTokenStore()
    
    const formData = ref({
      username: '',
      password: ''
    })
    
    const loading = ref(false)
    const errorMessage = ref('')
    
    const handleLogin = async () => {
      // 表单验证
      if (!formData.value.username || !formData.value.password) {
        errorMessage.value = '请输入用户名和密码'
        return
      }
      
      loading.value = true
      errorMessage.value = ''
      
      try {
        console.log('发送登录请求...')
        const response = await login(formData.value)
        console.log('登录响应:', response)
        
        // 检查响应格式和状态
        if (response && response.code === 200) {
          // 保存token
          tokenStore.setToken(response.token || response.access_token)
          tokenStore.setUserInfo({
            user_id: response.user_id || response.id || formData.value.username,
            username: formData.value.username
          })
          
          // 跳转到聊天页面
          router.push('/chat')
        } else {
          // 显示错误信息
          errorMessage.value = response?.message || '登录失败，请重试'
          console.log('登录失败:', response?.message)
        }
      } catch (error) {
        console.error('登录错误:', error)
        errorMessage.value = '网络错误，请稍后重试'
      } finally {
        loading.value = false
      }
    }
    
    return {
      formData,
      loading,
      errorMessage,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-form {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.title {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #333;
  text-align: center;
}

.subtitle {
  margin: 0 0 30px 0;
  font-size: 16px;
  color: #666;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.login-button {
  width: 100%;
  padding: 14px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
  margin-top: 10px;
}

.login-button:hover:not(:disabled) {
  background: #5a5fd8;
}

.login-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  margin-top: 15px;
  padding: 10px;
  background: #fee;
  color: #c33;
  border-radius: 6px;
  font-size: 14px;
}
</style>