import { createRouter, createWebHistory } from 'vue-router'
import { useTokenStore } from '../utils/tokenStore'

// 懒加载路由组件
const Login = () => import('../pages/Login.vue')
const Chat = () => import('../pages/Chat.vue')
const Game = () => import('../pages/Game.vue') // 游戏选择页面
const GomokuGame = () => import('../pages/GomokuGame.vue') // 五子棋游戏页面
const PersonaCreate = () => import('../pages/PersonaCreate.vue') // 人设创建页面
const SceneDialog = () => import('../pages/SceneDialog.vue') // 剧情对话页面

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresAuth: false,
      title: '登录 - AI聊天助手'
    }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat,
    meta: {
      requiresAuth: true,
      title: 'AI聊天 - AI聊天助手'
    }
  },
  {
    path: '/game',
    name: 'Game',
    component: Game,
    meta: {
      requiresAuth: true,
      title: '游戏功能 - AI聊天助手'
    }
  },
  {
    path: '/game/gomoku',
    name: 'GomokuGame',
    component: GomokuGame,
    meta: {
      requiresAuth: true,
      title: '五子棋 - AI聊天助手'
    }
  },
  {
    path: '/persona/create',
    name: 'PersonaCreate',
    component: PersonaCreate,
    meta: {
      requiresAuth: true,
      title: '创建人设 - AI聊天助手'
    }
  },
  {
    path: '/scene/dialog',
    name: 'SceneDialog',
    component: SceneDialog,
    meta: {
      requiresAuth: true,
      title: '剧情对话 - AI聊天助手'
    }
  },
  {
    // 404页面
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || 'AI聊天助手'
  
  const tokenStore = useTokenStore()
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !tokenStore.isLoggedIn()) {
    // 需要登录但未登录，重定向到登录页
    next('/login')
  } else if (to.path === '/login' && tokenStore.isLoggedIn()) {
    // 已登录访问登录页，重定向到聊天页
    next('/chat')
  } else {
    // 正常访问
    next()
  }
})

export default router