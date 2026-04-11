<template>
  <div v-if="loading" class="loading-container">
    <el-icon class="is-loading"><Loading /></el-icon>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(true)

onMounted(() => {
  const userInfoStr = localStorage.getItem('userInfo')
  if (userInfoStr) {
    try {
      const userInfo = JSON.parse(userInfoStr)
      const userType = userInfo.user_type || 3

      const routes: Record<number, string> = {
        1: '/elder-dashboard',
        2: '/nurse-dashboard',
        4: '/family-dashboard',
        3: '/admin-dashboard'
      }

      const redirectPath = routes[userType] || '/admin-dashboard'
      router.replace(redirectPath)
    } catch {
      router.replace('/admin-dashboard')
    }
  } else {
    router.replace('/admin-dashboard')
  }
  loading.value = false
})
</script>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 40px;
}
</style>