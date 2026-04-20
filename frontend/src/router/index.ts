import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台' }
      },
      {
        path: 'elder-dashboard',
        name: 'ElderDashboard',
        component: () => import('@/views/ElderDashboard.vue'),
        meta: { title: '工作台', roles: [1] }
      },
      {
        path: 'nurse-dashboard',
        name: 'NurseDashboard',
        component: () => import('@/views/NurseDashboard.vue'),
        meta: { title: '工作台', roles: [2] }
      },
      {
        path: 'family-dashboard',
        name: 'FamilyDashboard',
        component: () => import('@/views/FamilyDashboard.vue'),
        meta: { title: '工作台', roles: [4] }
      },
      {
        path: 'admin-dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/AdminDashboard.vue'),
        meta: { title: '管理中心', roles: [3] }
      },
      {
        path: 'elders',
        name: 'Elders',
        component: () => import('@/views/Elders.vue'),
        meta: { title: '老人管理' }
      },
      {
        path: 'nursing',
        name: 'Nursing',
        component: () => import('@/views/Nursing.vue'),
        meta: { title: '护理记录' }
      },
      {
        path: 'health',
        name: 'Health',
        component: () => import('@/views/HealthManagement.vue'),
        meta: { title: '健康管理与护理计划' }
      },
      {
        path: 'care-plan',
        name: 'CarePlan',
        component: () => import('@/views/CarePlan.vue'),
        meta: { title: '护理计划' }
      },
      {
        path: 'notifications',
        name: 'Notifications',
        component: () => import('@/views/Notifications.vue'),
        meta: { title: '消息通知' }
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/Statistics.vue'),
        meta: { title: '数据统计' }
      },
      {
        path: 'bigdata',
        name: 'BigDataAnalytics',
        component: () => import('@/views/BigDataAnalytics.vue'),
        meta: { title: '大数据分析' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心' }
      },
      {
        path: 'services',
        name: 'Services',
        component: () => import('@/views/Services.vue'),
        meta: { title: '服务列表' }
      },
      {
        path: 'service-management',
        name: 'ServiceManagement',
        component: () => import('@/views/ServiceManagement.vue'),
        meta: { title: '服务管理', roles: [3] }
      },
      {
        path: 'accounting',
        name: 'Accounting',
        component: () => import('@/views/Accounting.vue'),
        meta: { title: '账目管理', roles: [3] }
      },
      {
        path: 'ai-chat',
        name: 'AIChat',
        component: () => import('@/views/AIChat.vue'),
        meta: { title: 'AI健康助手' }
      },
      {
        path: 'location-map',
        name: 'LocationMap',
        component: () => import('@/views/LocationMap.vue'),
        meta: { title: '位置地图' }
      },
      {
        path: 'elder-location-map',
        name: 'ElderLocationMap',
        component: () => import('@/views/ElderLocationMap.vue'),
        meta: { title: '位置地图', roles: [1] }
      },
      {
        path: 'staff-location-map',
        name: 'StaffLocationMap',
        component: () => import('@/views/StaffLocationMap.vue'),
        meta: { title: '位置地图', roles: [2, 3, 4] }
      },
      {
        path: 'payment/mock',
        name: 'MockPayment',
        component: () => import('@/views/MockPayment.vue'),
        meta: { title: '模拟支付', requiresAuth: false }
      },
      {
        path: 'payment/result',
        name: 'PaymentResult',
        component: () => import('@/views/PaymentResult.vue'),
        meta: { title: '支付结果', requiresAuth: false }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router