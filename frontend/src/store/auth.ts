import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import type { UserInfo, LoginForm } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
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