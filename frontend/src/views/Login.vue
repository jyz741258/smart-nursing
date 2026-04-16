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

  // 粒子背景
  .particle-bg {
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;

    .particle {
      position: absolute;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.6) 0%, rgba(118, 75, 162, 0.6) 100%);
      filter: blur(1px);

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
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 0.6;
  }
  33% {
    transform: translateY(-80px) translateX(30px) rotate(120deg);
    opacity: 0.3;
  }
  66% {
    transform: translateY(-40px) translateX(-30px) rotate(240deg);
    opacity: 0.5;
  }
  100% {
    transform: translateY(0) translateX(0) rotate(360deg);
    opacity: 0.6;
  }
}

.login-background {
  position: absolute;
  inset: 0;
  z-index: 0;

  .bg-gradient {
    position: absolute;
    inset: 0;
    background-color: var(--bg-primary);
    background-image: 
      radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 70%, rgba(118, 75, 162, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 40% 80%, rgba(240, 147, 251, 0.05) 0%, transparent 50%);
    background-attachment: fixed;
  }

  .bg-shapes {
    position: absolute;
    inset: 0;
    overflow: hidden;

    .shape {
      position: absolute;
      border-radius: 50%;
      opacity: 0.1;
    }

    .shape-1 {
      width: 600px;
      height: 600px;
      background: var(--color-primary);
      top: -200px;
      right: -200px;
      animation: float 6s ease-in-out infinite;
    }

    .shape-2 {
      width: 400px;
      height: 400px;
      background: var(--color-secondary);
      bottom: -150px;
      left: -100px;
      animation: float 8s ease-in-out infinite reverse;
    }

    .shape-3 {
      width: 200px;
      height: 200px;
      background: var(--color-accent);
      top: 50%;
      left: 10%;
      animation: float 5s ease-in-out infinite;
    }
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-30px) rotate(10deg); }
}

// 登录框入场动画
.login-box {
  position: relative;
  z-index: 1;
  width: 420px;
  padding: 50px 40px;
  // 深色玻璃态背景
  background: rgba(28, 33, 40, 0.92);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid var(--border-color);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5),
              0 0 0 1px rgba(102, 126, 234, 0.1);

  // 全息效果
  &::before {
    content: '';
    position: absolute;
    inset: -2px;
    z-index: -1;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3), rgba(240, 147, 251, 0.3));
    background-size: 300% 300%;
    animation: holographicShift 4s ease-in-out infinite;
    border-radius: 26px;
    filter: blur(8px);
    opacity: 0.6;
  }

  // 顶部高光线
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    animation: topShine 3s ease-in-out infinite;
    animation-delay: 1s;
  }

  @keyframes topShine {
    0%, 100% { left: -100%; }
    50% { left: 100%; }
  }

  // 入场动画
  animation: loginBoxSlideIn 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
  opacity: 0;
  transform: translateY(40px) scale(0.95);
}

@keyframes loginBoxSlideIn {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

// Logo 独立动画
.login-header .logo {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin: 0 auto 20px;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
  animation: logoFloat 3s ease-in-out infinite, logoAppear 0.8s ease-out 0.3s forwards;
  opacity: 0;
}

@keyframes logoAppear {
  from {
    opacity: 0;
    transform: scale(0.5) rotate(-10deg);
  }
  to {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  animation: fadeInDown 0.6s ease-out 0.5s forwards;
  opacity: 0;

  h1 {
    font-size: 28px;
    color: var(--text-primary);
    margin-bottom: 8px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--text-primary), var(--color-primary-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  p {
    font-size: 14px;
    color: var(--text-secondary);
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
      color: #909399;
      z-index: 1;
    }

    :deep(.el-input__wrapper) {
      padding-left: 45px;
      height: 48px;
      border-radius: 12px;
      box-shadow: 0 0 0 1px #dcdfe6;
      transition: all 0.3s ease;

      &:hover, &.is-focus {
        box-shadow: 0 0 0 2px #667eea;
      }
    }

    :deep(.el-input__inner) {
      height: 48px;
    }
  }

  .login-btn {
    width: 100%;
    height: 48px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border: none;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;

    // 按钮悬停提升效果
    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 12px 24px rgba(102, 126, 234, 0.4);

      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
          90deg,
          transparent,
          rgba(255, 255, 255, 0.2),
          transparent
        );
        animation: buttonShine 0.6s ease;
      }
    }

    &:active {
      transform: translateY(-1px);
    }

    // 按钮点击波纹效果
    .ripple {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.4);
      transform: scale(0);
      animation: rippleEffect 0.6s ease-out;
      pointer-events: none;
    }
  }

  // 输入框依次入场
  .el-form-item {
    animation: slideInUp 0.5s ease-out both;

    &:nth-child(1) { animation-delay: 0.2s; }
    &:nth-child(2) { animation-delay: 0.3s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes buttonShine {
  from { left: -100%; }
  to { left: 100%; }
}

@keyframes rippleEffect {
  to {
    transform: scale(4);
    opacity: 0;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes rippleBtn {
  to {
    transform: translate(-50%, -50%) scale(4);
    opacity: 0;
  }
}

// 样例登录区域
.demo-login {
  margin-top: 20px;
  animation: fadeIn 0.6s ease-out 0.6s forwards;
  opacity: 0;

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
        background: var(--border-color);
      }

      span {
        position: relative;
        background: rgba(28, 33, 40, 0.92);
        padding: 0 15px;
        color: var(--text-secondary);
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
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    border: 1px solid transparent;
    animation: fadeInUp 0.5s ease-out both;
    position: relative;
    overflow: hidden;

    // 依次延迟显示
    &:nth-child(1) { animation-delay: 0.6s; }
    &:nth-child(2) { animation-delay: 0.7s; }
    &:nth-child(3) { animation-delay: 0.8s; }
    &:nth-child(4) { animation-delay: 0.9s; }

    &:hover {
      transform: translateY(-5px) scale(1.02);
      box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }

    // 点击波纹
    &:active .ripple-effect {
      position: absolute;
      width: 100px;
      height: 100px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      transform: translate(-50%, -50%) scale(0);
      animation: rippleBtn 0.6s ease-out;
      pointer-events: none;
    }

    .demo-role {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      position: relative;
      z-index: 1;
    }

    .demo-phone {
      font-size: 11px;
      color: var(--text-secondary);
      font-family: 'Courier New', monospace;
      position: relative;
      z-index: 1;
    }

    // 渐变背景
    &.elder {
      background: linear-gradient(135deg, rgba(103, 194, 58, 0.08), rgba(103, 194, 58, 0.02));
      border-color: rgba(103, 194, 58, 0.3);
      &:hover {
        background: linear-gradient(135deg, rgba(103, 194, 58, 0.15), rgba(103, 194, 58, 0.08));
        border-color: rgba(103, 194, 58, 0.5);
        box-shadow: 0 12px 24px rgba(103, 194, 58, 0.2);
      }
    }

    &.nurse {
      background: linear-gradient(135deg, rgba(64, 158, 255, 0.08), rgba(64, 158, 255, 0.02));
      border-color: rgba(64, 158, 255, 0.3);
      &:hover {
        background: linear-gradient(135deg, rgba(64, 158, 255, 0.15), rgba(64, 158, 255, 0.08));
        border-color: rgba(64, 158, 255, 0.5);
        box-shadow: 0 12px 24px rgba(64, 158, 255, 0.2);
      }
    }

    &.admin {
      background: linear-gradient(135deg, rgba(230, 162, 60, 0.08), rgba(230, 162, 60, 0.02));
      border-color: rgba(230, 162, 60, 0.3);
      &:hover {
        background: linear-gradient(135deg, rgba(230, 162, 60, 0.15), rgba(230, 162, 60, 0.08));
        border-color: rgba(230, 162, 60, 0.5);
        box-shadow: 0 12px 24px rgba(230, 162, 60, 0.2);
      }
    }

    &.family {
      background: linear-gradient(135deg, rgba(245, 108, 108, 0.08), rgba(245, 108, 108, 0.02));
      border-color: rgba(245, 108, 108, 0.3);
      &:hover {
        background: linear-gradient(135deg, rgba(245, 108, 108, 0.15), rgba(245, 108, 108, 0.08));
        border-color: rgba(245, 108, 108, 0.5);
        box-shadow: 0 12px 24px rgba(245, 108, 108, 0.2);
      }
    }
  }
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  animation: fadeIn 0.6s ease-out 0.7s forwards;
  opacity: 0;

  p {
    color: #909399;
    font-size: 14px;
    margin-bottom: 15px;
  }

  .back-home {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #606266;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s ease;

    &:hover {
      color: #667eea;
      transform: translateX(4px);
    }
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>