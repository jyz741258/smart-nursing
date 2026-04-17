<template>
  <div class="login-container">
    <!-- 粒子背景 -->
    <div class="particle-bg">
      <div class="particle"></div>
      <div class="particle"></div>
      <div class="particle"></div>
      <div class="particle"></div>
      <div class="particle"></div>
    </div>

    <div class="login-background">
      <div class="bg-gradient"></div>
      <div class="bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
    </div>

    <div class="login-box">
      <div class="login-header">
        <div class="logo">
          <el-icon :size="48"><FirstAidKit /></el-icon>
        </div>
        <h1>智慧养老系统</h1>
        <p>Smart Nursing Platform</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="phone">
          <div class="input-wrapper">
            <el-icon class="input-icon"><Iphone /></el-icon>
            <el-input
              v-model="form.phone"
              placeholder="请输入手机号"
              size="large"
            />
          </div>
        </el-form-item>
        <el-form-item prop="password">
          <div class="input-wrapper">
            <el-icon class="input-icon"><Lock /></el-icon>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              show-password
            />
          </div>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            native-type="submit"
          >
            <span v-if="!loading">登 录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 样例账号快速登录 -->
      <div class="demo-login">
        <div class="demo-divider">
          <span>或选择以下样例账号快速登录</span>
        </div>
        <div class="demo-users">
          <div
            v-for="user in demoUsers"
            :key="user.id"
            class="demo-user-item"
            :class="user.role"
            @click="quickLogin(user)"
          >
            <span class="demo-role">{{ user.roleName }}</span>
            <span class="demo-phone">{{ user.phone }}</span>
          </div>
        </div>
      </div>

      <div class="login-footer">
        <p>还没有账号？<el-link type="primary" @click="$router.push('/register')">立即注册</el-link></p>
        <div class="back-home" @click="$router.push('/')">
          <el-icon><House /></el-icon>
          <span>返回首页</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage } from 'element-plus'
import { Iphone, Lock, FirstAidKit, House } from '@element-plus/icons-vue'
import api from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  phone: '',
  password: ''
})

// 样例账号列表
const demoUsers = [
  { id: 1, role: 'elder', roleName: '老人', phone: '13900001001', password: '123456' },
  { id: 4, role: 'family', roleName: '家属', phone: '13900001004', password: '123456' },
  { id: 2, role: 'nurse', roleName: '护理员', phone: '13900001002', password: '123456' },
  { id: 3, role: 'admin', roleName: '管理员', phone: '13800138000', password: '123456' }
]

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 样例账号快速登录
const quickLogin = async (user: any) => {
  loading.value = true
  try {
    const res: any = await api.post('/users/login', {
      phone: user.phone,
      password: user.password
    })
    if (res.code === 200) {
      const loginData = res.data || {}

      const roleMap: Record<string, number> = {
        elder: 1,
        nurse: 2,
        admin: 3,
        family: 4
      }
      const userType = loginData.user_type || roleMap[user.role] || 3

      const userInfo = {
        id: loginData.user_id || loginData.id || 0,
        user_type: userType,
        name: loginData.name || user.roleName,
        phone: user.phone
      }
      localStorage.setItem('token', loginData.token || '')
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
      
      // 同时更新authStore
      authStore.userInfo = userInfo
      authStore.token = loginData.token || ''

      ElMessage.success(`以${user.roleName}身份登录成功`)

      const routeMap: Record<number, string> = {
        1: '/elder-dashboard',
        2: '/nurse-dashboard',
        3: '/admin-dashboard',
        4: '/family-dashboard'
      }
      router.push(routeMap[userType] || '/admin-dashboard')
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (error) {
    ElMessage.error('登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleLogin = async () => {
  try {
    await formRef.value.validate()
    loading.value = true

    const res = await authStore.login(form)

    if (res.code === 200) {
      ElMessage.success('登录成功')

      // 保存用户信息到 localStorage
      const userData = res.data || {}
      localStorage.setItem('userInfo', JSON.stringify(userData))

      // 根据用户类型跳转到对应页面
      const userType = userData.user_type || 3
      const routeMap: Record<number, string> = {
        1: '/elder-dashboard',
        2: '/nurse-dashboard',
        3: '/admin-dashboard',
        4: '/family-dashboard'
      }
      router.push(routeMap[userType] || '/admin-dashboard')
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (error) {
    console.error('登录失败', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;

  // 柔和的绿色粒子背景
  .particle-bg {
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;

    .particle {
      position: absolute;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(34, 197, 94, 0.3) 0%, rgba(6, 182, 212, 0.3) 100%);
      filter: blur(2px);

      &:nth-child(1) {
        width: 80px;
        height: 80px;
        top: 20%;
        left: 10%;
        animation: particleFloat 25s ease-in-out infinite;
      }

      &:nth-child(2) {
        width: 60px;
        height: 60px;
        top: 60%;
        right: 10%;
        animation: particleFloat 30s ease-in-out infinite;
        animation-delay: -5s;
      }

      &:nth-child(3) {
        width: 100px;
        height: 100px;
        bottom: 20%;
        left: 30%;
        animation: particleFloat 28s ease-in-out infinite;
        animation-delay: -10s;
      }

      &:nth-child(4) {
        width: 40px;
        height: 40px;
        top: 10%;
        right: 30%;
        animation: particleFloat 22s ease-in-out infinite;
        animation-delay: -15s;
      }

      &:nth-child(5) {
        width: 70px;
        height: 70px;
        bottom: 10%;
        right: 20%;
        animation: particleFloat 26s ease-in-out infinite;
        animation-delay: -8s;
      }
    }
  }
}

@keyframes particleFloat {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0.3;
  }
  33% {
    transform: translateY(-30px) translateX(15px);
    opacity: 0.2;
  }
  66% {
    transform: translateY(-15px) translateX(-15px);
    opacity: 0.25;
  }
  100% {
    transform: translateY(0) translateX(0);
    opacity: 0.3;
  }
}

.login-background {
  position: absolute;
  inset: 0;
  z-index: 0;

  .bg-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #f8fafc 0%, #ffffff 50%, #f0fdf4 100%);
  }

  .bg-shapes {
    position: absolute;
    inset: 0;
    overflow: hidden;

    .shape {
      position: absolute;
      border-radius: 50%;
      opacity: 0.08;
    }

    .shape-1 {
      width: 600px;
      height: 600px;
      background: #22c55e;
      top: -200px;
      right: -200px;
    }

    .shape-2 {
      width: 400px;
      height: 400px;
      background: #0d9488;
      bottom: -150px;
      left: -100px;
    }

    .shape-3 {
      width: 200px;
      height: 200px;
      background: #06b6d4;
      top: 50%;
      left: 10%;
    }
  }
}

// 登录框 - 浅色玻璃态
.login-box {
  position: relative;
  z-index: 1;
  width: 420px;
  padding: 50px 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.1);

  // 绿色顶部边框
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 4px;
    background: linear-gradient(90deg, #22c55e, #0d9488);
    border-radius: 0 0 4px 4px;
  }

  // 入场动画
  animation: loginBoxSlideIn 0.6s ease-out forwards;
  opacity: 0;
  transform: translateY(30px);
}

@keyframes loginBoxSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Logo
.login-header .logo {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin: 0 auto 20px;
  box-shadow: 0 10px 30px rgba(34, 197, 94, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;

  h1 {
    font-size: 28px;
    color: #1e293b;
    margin-bottom: 8px;
    font-weight: 700;
  }

  p {
    font-size: 14px;
    color: #64748b;
  }
}

.login-form {
  .input-wrapper {
    position: relative;
    width: 100%;

    .input-icon {
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      color: #94a3b8;
      z-index: 1;
    }

    :deep(.el-input__wrapper) {
      padding-left: 45px;
      height: 48px;
      border-radius: 12px;
      box-shadow: 0 0 0 1px #e2e8f0;
      background: #ffffff;
      transition: all 0.3s ease;

      &:hover, &.is-focus {
        box-shadow: 0 0 0 2px #22c55e;
      }
    }

    :deep(.el-input__inner) {
      height: 48px;
      color: #1e293b;
      &::placeholder {
        color: #94a3b8;
      }
    }
  }

  .login-btn {
    width: 100%;
    height: 48px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(135deg, #22c55e, #16a34a);
    border: none;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(34, 197, 94, 0.3);
      background: linear-gradient(135deg, #16a34a, #15803d);
    }

    &:active {
      transform: translateY(0);
    }
  }

  .el-form-item {
    animation: slideInUp 0.5s ease-out both;

    &:nth-child(1) { animation-delay: 0.1s; }
    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.3s; }
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 样例登录区域
.demo-login {
  margin-top: 20px;

  .demo-divider {
    text-align: center;
    position: relative;
    margin-bottom: 15px;

    &::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 0;
      right: 0;
      height: 1px;
      background: #e2e8f0;
    }

    span {
      position: relative;
      background: #ffffff;
      padding: 0 15px;
      color: #64748b;
      font-size: 12px;
    }
  }

  .demo-users {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .demo-user-item {
    padding: 12px 15px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;

    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
    }

    .demo-role {
      font-size: 13px;
      font-weight: 600;
      color: #1e293b;
    }

    .demo-phone {
      font-size: 11px;
      color: #64748b;
      font-family: 'Courier New', monospace;
    }

    &.elder {
      border-color: rgba(34, 197, 94, 0.3);
      &:hover {
        border-color: #22c55e;
        background: #f0fdf4;
      }
    }

    &.nurse {
      border-color: rgba(59, 130, 246, 0.3);
      &:hover {
        border-color: #3b82f6;
        background: #eff6ff;
      }
    }

    &.admin {
      border-color: rgba(245, 158, 11, 0.3);
      &:hover {
        border-color: #f59e0b;
        background: #fffbeb;
      }
    }

    &.family {
      border-color: rgba(168, 85, 247, 0.3);
      &:hover {
        border-color: #a855f7;
        background: #faf5ff;
      }
    }
  }
}

.login-footer {
  text-align: center;
  margin-top: 30px;

  p {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 15px;
  }

  .back-home {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #64748b;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s ease;

    &:hover {
      color: #22c55e;
      transform: translateX(4px);
    }
  }
}
</style>