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
          <el-menu-item index="/elder-location-map"><el-icon><MapLocation /></el-icon>位置地图</el-menu-item>
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
          <el-menu-item index="/staff-location-map"><el-icon><MapLocation /></el-icon>位置地图</el-menu-item>
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
          <el-menu-item index="/staff-location-map"><el-icon><MapLocation /></el-icon>位置地图</el-menu-item>
        </template>

        <!-- 管理员菜单 -->
        <template v-if="userType === 3">
          <el-menu-item index="/elders"><el-icon><User /></el-icon>老人管理</el-menu-item>
          <el-menu-item index="/nursing"><el-icon><Document /></el-icon>护理记录</el-menu-item>
          <el-menu-item index="/health"><el-icon><TrendCharts /></el-icon>健康与护理</el-menu-item>
          <el-menu-item index="/staff-location-map"><el-icon><MapLocation /></el-icon>位置地图</el-menu-item>
          <el-menu-item index="/service-management"><el-icon><Collection /></el-icon>服务管理</el-menu-item>
          <el-menu-item index="/accounting"><el-icon><Document /></el-icon>账目管理</el-menu-item>
          <el-menu-item index="/statistics"><el-icon><PieChart /></el-icon>数据统计</el-menu-item>
          <el-menu-item index="/bigdata"><el-icon><DataAnalysis /></el-icon>大数据分析</el-menu-item>
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
          <!-- 字体大小切换按钮（仅老人用户显示） -->
          <el-tooltip :content="settingsStore.fontSizeMode === 'normal' ? '切换大字模式' : '切换普通字体'" placement="bottom">
            <el-button
              class="font-size-toggle"
              :type="settingsStore.fontSizeMode === 'large' ? 'primary' : 'default'"
              circle
              @click="settingsStore.toggleFontSize"
              v-if="userType === 1"
            >
              <el-icon :size="20">
                <ZoomIn v-if="settingsStore.fontSizeMode === 'normal'" />
                <ZoomOut v-else />
              </el-icon>
            </el-button>
          </el-tooltip>
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="badge-item">
            <el-icon class="header-icon" @click="$router.push('/notifications')">
              <Bell />
            </el-icon>
          </el-badge>
          <div class="user-type-badge" :class="'type-' + userType" v-show="!isMobile">
            {{ userTypeName }}
          </div>
          
          <!-- 字体大小控制 -->
          <div class="font-control" v-show="!isMobile">
            <el-tooltip content="调整字体大小" placement="bottom">
              <el-icon class="font-btn" @click="showFontMenu = !showFontMenu">
                <ZoomIn />
              </el-icon>
            </el-tooltip>
            <el-dropdown v-model="showFontMenu" @command="handleFontCommand">
              <span class="font-size-indicator" :class="settingsStore.fontSize">
                {{ fontSizeLabel }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="decrease" :disabled="settingsStore.fontSize === 'small'">
                    <el-icon><ZoomOut /></el-icon>减小字体
                  </el-dropdown-item>
                  <el-dropdown-item command="reset">
                    <el-icon><RefreshLeft /></el-icon>恢复默认
                  </el-dropdown-item>
                  <el-dropdown-item command="increase" :disabled="settingsStore.fontSize === 'xlarge'">
                    <el-icon><ZoomIn /></el-icon>增大字体
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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
            <el-menu-item index="/elder-location-map"><el-icon><MapLocation /></el-icon>位置地图</el-menu-item>
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
            <el-menu-item index="/staff-location-map"><el-icon><MapLocation /></el-icon>位置地图</el-menu-item>
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
            <el-menu-item index="/staff-location-map"><el-icon><MapLocation /></el-icon>位置地图</el-menu-item>
          </template>

          <!-- 管理员菜单 -->
          <template v-if="userType === 3">
            <el-menu-item index="/elders"><el-icon><User /></el-icon>老人管理</el-menu-item>
            <el-menu-item index="/nursing"><el-icon><Document /></el-icon>护理记录</el-menu-item>
            <el-menu-item index="/health"><el-icon><TrendCharts /></el-icon>健康与护理</el-menu-item>
            <el-menu-item index="/staff-location-map"><el-icon><MapLocation /></el-icon>位置地图</el-menu-item>
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
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useSettingsStore } from '@/store/settings'
import api from '@/store/auth'
import {
  DataAnalysis, User, Document, TrendCharts, Collection, Bell, PieChart,
  Fold, Expand, SwitchButton, FirstAidKit, House, Sunny, Menu, ChatDotRound,
  ZoomIn, ZoomOut, MapLocation
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()

const isCollapse = ref(false)
const unreadCount = ref(0)
const userType = ref(3)
const isMobile = ref(false)
const showMobileMenu = ref(false)
const showFontMenu = ref(false)

const fontSizeLabel = computed(() => {
  const labels: Record<string, string> = {
    small: '正常',
    medium: '中等',
    large: '大字',
    xlarge: '特大'
  }
  return labels[settingsStore.fontSize] || '中等'
})

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

// 字体大小控制
const increaseFontSize = () => {
  const sizes = ['small', 'medium', 'large', 'xlarge']
  const currentIndex = sizes.indexOf(settingsStore.fontSize)
  if (currentIndex < sizes.length - 1) {
    settingsStore.setFontSize(sizes[currentIndex + 1])
  }
}

const decreaseFontSize = () => {
  const sizes = ['small', 'medium', 'large', 'xlarge']
  const currentIndex = sizes.indexOf(settingsStore.fontSize)
  if (currentIndex > 0) {
    settingsStore.setFontSize(sizes[currentIndex - 1])
  }
}

const resetFontSize = () => {
  settingsStore.setFontSize('medium')
}

const handleFontCommand = (command: string) => {
  if (command === 'increase') {
    increaseFontSize()
  } else if (command === 'decrease') {
    decreaseFontSize()
  } else if (command === 'reset') {
    resetFontSize()
  }
}

const getUserType = () => {
  // 优先从 localStorage 读取，因为登录时已经保存了用户信息
  const storedUserInfo = localStorage.getItem('userInfo')
  if (storedUserInfo) {
    try {
      const user = JSON.parse(storedUserInfo)
      userType.value = Number(user.user_type) || 3
      console.log('[Layout] 从localStorage获取用户类型:', userType.value)
      return
    } catch (e) {
      console.error('[Layout] 解析用户信息失败', e)
    }
  }
  // 如果 localStorage 没有，则从 authStore 获取
  const info = authStore.userInfo
  if (info) {
    userType.value = Number(info.user_type) || 3
    console.log('[Layout] 从authStore获取用户类型:', userType.value)
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
  // 初始化字体设置
  settingsStore.initSettings()
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
  background: #f8fafc;
}

.sidebar {
  background-color: #ffffff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
  transition: width 0.3s;
  overflow: hidden;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
    background: linear-gradient(135deg, #22c55e, #16a34a);
  }
}

// 侧边栏菜单浅色主题
:deep(.el-menu) {
  background-color: #ffffff !important;
  border-right: none !important;

  .el-menu-item,
  .el-sub-menu__title {
    color: #475569 !important;

    &:hover {
      background-color: #f0fdf4 !important;
      color: #22c55e !important;
    }

    &.is-active {
      background-color: #dcfce7 !important;
      color: #22c55e !important;
    }
  }

  .el-sub-menu .el-menu-item {
    padding-left: 50px !important;
  }
}

.header {
  background-color: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 15px;

    .collapse-btn {
      font-size: 20px;
      cursor: pointer;
      color: #64748b;
    }

    .menu-btn {
      font-size: 20px;
      cursor: pointer;
      color: #64748b;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 15px;

    .header-icon {
      font-size: 20px;
      cursor: pointer;
      color: #64748b;

      &:hover {
        color: #22c55e;
      }
    }

    .font-size-toggle {
      font-weight: bold;

      &.el-button--primary {
        background: linear-gradient(135deg, #22c55e, #16a34a);
        border-color: #22c55e;
      }
    }

    .user-type-badge {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      color: #fff;

      &.type-1 { background: #22c55e; }
      &.type-2 { background: #3b82f6; }
      &.type-3 { background: #f59e0b; }
      &.type-4 { background: #8b5cf6; }
    }

  .user-info {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    padding: 6px 12px;
    border-radius: 20px;
    transition: all 0.2s ease;

    &:hover {
      background: #f0fdf4;
    }

    .username {
      color: #1e293b;
      font-weight: 500;
    }

    .el-dropdown__caret-button {
      .el-icon {
        color: #64748b;
      }
    }
  }

  // 字体控制样式
  .font-control {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-right: 5px;

    .font-btn {
      font-size: 18px;
      cursor: pointer;
      color: #64748b;
      padding: 4px;
      border-radius: 4px;
      transition: all 0.2s;

      &:hover {
        color: #22c55e;
        background: #f0fdf4;
      }
    }

    .font-size-indicator {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      background: #f0fdf4;
      color: #22c55e;
      border: 1px solid #dcfce7;
      transition: all 0.2s;

      &:hover {
        background: #dcfce7;
      }

      // 不同字体大小的指示器样式
      &.small {
        font-size: 12px;
        background: #f5f7fa;
        color: #909399;
        border-color: #e4e7ed;
      }

      &.medium {
        font-size: 13px;
      }

      &.large {
        font-size: 15px;
        background: #ecf5ff;
        color: #409eff;
        border-color: #d9ecff;
      }

      &.xlarge {
        font-size: 17px;
        background: #fef0f0;
        color: #f56c6c;
        border-color: #fde2e2;
      }
    }
  }
}
}

.main-content {
  background-color: #f8fafc;
  overflow-y: auto;
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu) {
  background-color: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
  padding: 8px 0 !important;

  .el-dropdown-menu__item {
    color: #1e293b !important;
    padding: 10px 20px !important;
    font-size: 14px !important;
    line-height: 1.5 !important;

    &:hover {
      background-color: #f0fdf4 !important;
      color: #22c55e !important;
    }

    &:focus {
      background-color: #f0fdf4 !important;
      color: #22c55e !important;
    }

    .el-icon {
      color: #64748b !important;
      margin-right: 8px !important;
    }
  }

  // 分隔线
  .el-dropdown-menu__item--divided {
    border-top: 1px solid #e2e8f0 !important;
    margin-top: 8px !important;
  }
}

// 确保下拉触发器文字可见
:deep(.el-dropdown) {
  .el-dropdown-selfdefine {
    color: #1e293b !important;
  }
}

/* 面包屑样式 */
:deep(.el-breadcrumb__item) {
  .el-breadcrumb__inner {
    color: #64748b !important;

    &:hover {
      color: #22c55e !important;
    }
  }

  .el-breadcrumb__separator {
    color: #94a3b8 !important;
  }
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
    color: #ffffff;
    font-size: 1.1em;
    font-weight: bold;
    background: linear-gradient(135deg, #22c55e, #16a34a);
    margin-bottom: 20px;
  }

  :deep(.el-menu) {
    flex: 1;
    background-color: #ffffff !important;
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