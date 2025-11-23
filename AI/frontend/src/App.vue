<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 设置页面标题
const setPageTitle = () => {
  const title = route.meta.title || 'AI聊天助手'
  document.title = title
}

onMounted(() => {
  setPageTitle()
  
  // 监听路由变化，更新页面标题
  router.afterEach((to) => {
    const title = to.meta.title || 'AI聊天助手'
    document.title = title
  })
})
</script>

<template>
  <div class="app-container">
    <!-- 路由视图 -->
    <router-view />
  </div>
</template>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
