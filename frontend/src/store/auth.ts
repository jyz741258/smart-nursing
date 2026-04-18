import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import type { UserInfo, LoginForm } from '@/types'

// 创建 axios 实例，添加请求拦截器用于调试
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器 - 打印请求信息
api.interceptors.request.use(config => {
  console.log('[API Request]', {
    method: config.method?.toUpperCase(),
    url: config.url,
    params: config.params,
    headers: config.headers
  })
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('[API Response]', {
      url: response.config.url,
      status: response.status,
      data: response.data
    })
    return response.data
  },
  error => {
    console.error('[API Error]', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.response?.data?.message || error.message,
      fullError: error
    })
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)

  const login = async (data: LoginForm) => {
    const res: any = await api.post('/users/login', data)
    if (res.code === 200) {
      token.value = res.data.token
      localStorage.setItem('token', res.data.token)
      userInfo.value = res.data
    }
    return res
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  const getProfile = async () => {
    const res: any = await api.get('/users/profile')
    if (res.code === 200) {
      userInfo.value = res.data
    }
    return res
  }

  return { token, userInfo, login, logout, getProfile }
})

export default api
