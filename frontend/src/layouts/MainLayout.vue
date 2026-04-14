<template>
  <el-container class="layout-container">
    <!-- 侧边栏（桌面端） -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar" v-show="!isMobile">
      <div class="logo">
        <el-icon v-if="isCollapse"><UserFilled /></el-icon>
        <span v-else>智慧养老系统</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item :index="dashboardPath">
          <el-icon><component :is="dashboardIcon" /></el-icon>
          <template #title>{{ dashboardTitle }}</template>
        </el-menu-item>

        <!-- 老人用户菜单 -->
        <template v-if="userType === 1">
          <el-sub-menu index="elder">
            <template #title>
              <el-icon><User /></el-icon>
              <span>我的服务</span>
            </template>
            <el-menu-item index="/services"><el-icon><Collection /></el-icon>服务列表</el-menu-item>
            <el-menu-item index="/health"><el-icon><TrendCharts /></el-icon>健康与护理</el-menu-item>
            <el-menu-item index="/notifications"><el-icon><Bell /></el-icon>消息通知</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/ai-chat"><el-icon><ChatDotRound /></el-icon>AI健康助手</el-menu-item>
        </template>

        <!-- 护理人员菜单 -->
        <template v-if="userType === 2">
          <el-sub-menu index="nurse">
            <template #title>
              <el-icon><FirstAidKit /></el-icon>
              <span>护理工作</span>
            </template>
            <el-menu-item index="/services"><el-icon><Collection /></el-icon>服务列表</el-menu-item>
            <el-menu-item index="/nursing"><el-icon><Document /></el-icon>护理记录</el-menu-item>
            <el-menu-item index="/health"><el-icon><TrendCharts /></el-icon>健康与护理</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/ai-chat"><el-icon><ChatDotRound /></el-icon>AI健康助手</el-menu-item>
        </template>

        <!-- 家属菜单 -->
        <template v-if="userType === 4">
          <el-sub-menu index="family">
            <template #title>
              <el-icon><House /></el-icon>
              <span>家属服务</span>
            </template>
            <el-menu-item index="/services"><el-icon><Collection /></el-icon>服务列表</el-menu-item>
            <el-menu-item index="/health"><el-icon><TrendCharts /></el-icon>健康与护理</el-menu-item>
            <el-menu-item index="/nursing"><el-icon><Document /></el-icon>护理记录</el-menu-item>
            <el-menu-item index="/notifications"><el-icon><Bell /></el-icon>消息通知</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/ai-chat"><el-icon><ChatDotRound /></el-icon>AI健康助手</el-menu-item>
        </template>

        <!-- 管理员菜单 -->
        <template v-if="userType === 3">
          <el-menu-item index="/elders"><el-icon><User /></el-icon>老人管理</el-menu-item>
          <el-menu-item index="/nursing"><el-icon><Document /></el-icon>护理记录</el-menu-item>
          <el-menu-item index="/health"><el-icon><TrendCharts /></el-icon>健康与护理</el-menu-item>
          <el-menu-item index="/service-management"><el-icon><Collection /></el-icon>服务管理</el-menu-item>
          <el-menu-item index="/accounting"><el-icon><Document /></el-icon>账目管理</el-menu-item>
          <el-menu-item index="/statistics"><el-icon><PieChart /></el-icon>数据统计</el-menu-item>
          <el-menu-item index="/ai-chat"><el-icon><ChatDotRound /></el-icon>AI健康助手</el-menu-item>
        </template>

        <el-menu-item index="/notifications">
          <el-icon><Bell /></el-icon>
          <template #title>消息通知</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <!-- 移动端菜单按钮 -->
          <el-icon class="menu-btn" @click="showMobileMenu = !showMobileMenu" v-show="isMobile">
            <Menu />
          </el-icon>
          <!-- 桌面端折叠按钮 -->
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse" v-show="!isMobile">
            <Expand v-if="isCollapse" />
            <Fold v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="badge-item">
            <el-icon class="header-icon" @click="$router.push('/notifications')">
              <Bell />
            </el-icon>
          </el-badge>
          <div class="user-type-badge" :class="'type-' + userType" v-show="!isMobile">
            {{ userTypeName }}
          </div>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :src="userInfo?.avatar || ''">
                {{ userInfo?.name?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="username" v-show="!isMobile">{{ userInfo?.name || '用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 移动端菜单 -->
    <el-drawer
      v-model="showMobileMenu"
      direction="ltr"
      size="80%"
      v-show="isMobile"
    >
      <div class="mobile-menu">
        <div class="mobile-logo">
          <el-icon><UserFilled /></el-icon>
          <span>智慧养老系统</span>
        </div>
        <el-menu
          :default-active="route.path"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
          @select="showMobileMenu = false"
        >
          <el-menu-item :index="dashboardPath">
            <el-icon><component :is="dashboardIcon" /></el-icon>
            <template #title>{{ dashboardTitle }}</template>
          </el-menu-item>

          <!-- 老人用户菜单 -->
          <template v-if="userType === 1">
            <el-sub-menu index="elder">
              <template #title>
                <el-icon><User /></el-icon>
                <span>我的服务</span>
              </template>
              <el-menu-item index="/services"><el-icon><Collection /></el-icon>服务列表</el-menu-item>
              <el-menu-item index="/health"><el-icon><TrendCharts /></el-icon>健康与护理</el-menu-item>
              <el-menu-item index="/notifications"><el-icon><Bell /></el-icon>消息通知</el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/ai-chat"><el-icon><ChatDotRound /></el-icon>AI健康助手</el-menu-item>
          </template>

          <!-- 护理人员菜单 -->
          <template v-if="userType === 2">
            <el-sub-menu index="nurse">
              <template #title>
                <el-icon><FirstAidKit /></el-icon>
                <span>护理工作</span>
              </template>
              <el-menu-item index="/services"><el-icon><Collection /></el-icon>服务列表</el-menu-item>
              <el-menu-item index="/nursing"><el-icon><Document /></el-icon>护理记录</el-menu-item>
              <el-menu-item index="/health"><el-icon><TrendCharts /></el-icon>健康与护理</el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/ai-chat"><el-icon><ChatDotRound /></el-icon>AI健康助手</el-menu-item>
          </template>

          <!-- 家属菜单 -->
          <template v-if="userType === 4">
            <el-sub-menu index="family">
              <template #title>
                <el-icon><House /></el-icon>
                <span>家属服务</span>
              </template>
              <el-menu-item index="/services"><el-icon><Collection /></el-icon>服务列表</el-menu-item>
              <el-menu-item index="/health"><el-icon><TrendCharts /></el-icon>健康与护理</el-menu-item>
              <el-menu-item index="/nursing"><el-icon><Document /></el-icon>护理记录</el-menu-item>
              <el-menu-item index="/notifications"><el-icon><Bell /></el-icon>消息通知</el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/ai-chat"><el-icon><ChatDotRound /></el-icon>AI健康助手</el-menu-item>
          </template>

          <!-- 管理员菜单 -->
          <template v-if="userType === 3">
            <el-menu-item index="/elders"><el-icon><User /></el-icon>老人管理</el-menu-item>
            <el-menu-item index="/nursing"><el-icon><Document /></el-icon>护理记录</el-menu-item>
            <el-menu-item index="/health"><el-icon><TrendCharts /></el-icon>健康与护理</el-menu-item>
            <el-menu-item index="/service-management"><el-icon><Collection /></el-icon>服务管理</el-menu-item>
            <el-menu-item index="/accounting"><el-icon><Document /></el-icon>账目管理</el-menu-item>
            <el-menu-item index="/statistics"><el-icon><PieChart /></el-icon>数据统计</el-menu-item>
            <el-menu-item index="/ai-chat"><el-icon><ChatDotRound /></el-icon>AI健康助手</el-menu-item>
          </template>

          <el-menu-item index="/notifications">
            <el-icon><Bell /></el-icon>
            <template #title>消息通知</template>
          </el-menu-item>
        </el-menu>
      </div>
    </el-drawer>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onMounted as onMountedRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/store/auth'
import {
  DataAnalysis, User, Document, TrendCharts, Collection, Bell, PieChart,
  Fold, Expand, SwitchButton, FirstAidKit, House, Sunny, Menu, ChatDotRound
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapse = ref(false)
const unreadCount = ref(0)
const userType = ref(3)
const isMobile = ref(false)
const showMobileMenu = ref(false)

const dashboardPath = computed(() => {
  const paths: Record<number, string> = { 1: '/elder-dashboard', 2: '/nurse-dashboard', 3: '/admin-dashboard', 4: '/family-dashboard' }
  return paths[userType.value] || '/admin-dashboard'
})

const dashboardIcon = computed(() => {
  const icons: Record<number, any> = { 1: Sunny, 2: FirstAidKit, 3: DataAnalysis, 4: House }
  return icons[userType.value] || DataAnalysis
})

const dashboardTitle = computed(() => {
  const titles: Record<number, string> = { 1: '我的主页', 2: '工作台', 3: '管理中心', 4: '家属首页' }
  return titles[userType.value] || '工作台'
})

const userInfo = computed(() => {
  if (authStore.userInfo) return authStore.userInfo
  const stored = localStorage.getItem('userInfo')
  if (stored) {
    try {
      return JSON.parse(stored)
    } catch {
      return null
    }
  }
  return null
})

const userTypeName = computed(() => {
  const names: Record<number, string> = { 1: '老人', 2: '护理人员', 3: '管理员', 4: '家属' }
  return names[userType.value] || '用户'
})

const handleCommand = (command: string) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}

const getUserType = () => {
  const info = userInfo.value
  if (info) {
    userType.value = info.user_type || 3
  }
}

const getUnreadCount = async () => {
  try {
    const res: any = await api.get('/notifications/unread-count')
    if (res.code === 200) {
      unreadCount.value = res.data.count
    }
  } catch (error) {
    console.error('获取未读消息数失败', error)
  }
}

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  authStore.getProfile()
  getUserType()
  getUnreadCount()
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

// 组件卸载时移除事件监听器
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    background-color: #2b3a4d;
  }
}

.header {
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);

  .header-left {
    display: flex;
    align-items: center;
    gap: 15px;

    .collapse-btn {
      font-size: 20px;
      cursor: pointer;
      color: #606266;
    }

    .menu-btn {
      font-size: 20px;
      cursor: pointer;
      color: #606266;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 15px;

    .header-icon {
      font-size: 20px;
      cursor: pointer;
      color: #606266;

      &:hover {
        color: #409eff;
      }
    }

    .user-type-badge {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      color: #fff;

      &.type-1 { background: #67c23a; }
      &.type-2 { background: #409eff; }
      &.type-3 { background: #e6a23c; }
      &.type-4 { background: #f56c6c; }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;

      .username {
        color: #606266;
      }
    }
  }
}

.main-content {
  background-color: #f5f7fa;
  overflow-y: auto;
}

/* 移动端菜单样式 */
.mobile-menu {
  height: 100%;
  display: flex;
  flex-direction: column;

  .mobile-logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    background-color: #2b3a4d;
    margin-bottom: 20px;
  }

  :deep(.el-menu) {
    flex: 1;
  }
}

/* 响应式样式 */
@media (max-width: 768px) {
  .header {
    padding: 0 10px;
  }

  .header-left {
    gap: 10px;
  }

  .header-right {
    gap: 10px;
  }

  .el-breadcrumb {
    display: none;
  }

  .main-content {
    padding: 10px;
  }
}
</style>