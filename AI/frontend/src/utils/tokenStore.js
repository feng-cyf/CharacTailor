import { ref, reactive } from 'vue'

// 创建响应式的token状态
const token = ref(localStorage.getItem('token') || '')
const userInfo = reactive(localStorage.getItem('userInfo') ? JSON.parse(localStorage.getItem('userInfo')) : {})

// Token存储管理
const tokenStore = {
  // 获取token
  getToken() {
    return token.value
  },
  
  // 设置token
  setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  },
  
  // 清除token
  clearToken() {
    token.value = ''
    localStorage.removeItem('token')
    this.clearUserInfo()
  },
  
  // 检查是否已登录
  isLoggedIn() {
    return !!token.value
  },
  
  // 获取用户信息
  getUserInfo() {
    return userInfo
  },
  
  // 设置用户信息
  setUserInfo(info) {
    Object.assign(userInfo, info)
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
  },
  
  // 清除用户信息
  clearUserInfo() {
    Object.keys(userInfo).forEach(key => {
      delete userInfo[key]
    })
    localStorage.removeItem('userInfo')
  }
}

// 导出useTokenStore组合式函数
export const useTokenStore = () => {
  return tokenStore
}