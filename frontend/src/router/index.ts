import { createRouter, createWebHistory } from 'vue-router'
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
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
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