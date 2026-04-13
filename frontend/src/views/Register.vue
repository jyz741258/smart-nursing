<template>
  <div class="register-container">
    <div class="register-background">
      <div class="bg-gradient"></div>
      <div class="bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
    </div>

    <div class="register-box">
      <div class="register-header">
        <div class="logo">
          <el-icon :size="48"><FirstAidKit /></el-icon>
        </div>
        <h1>智慧养老系统</h1>
        <p>Smart Nursing Platform - 用户注册</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="register-form"
        @submit.prevent="handleRegister"
      >
        <!-- 用户类型选择 -->
        <el-form-item prop="user_type">
          <div class="input-wrapper">
            <el-icon class="input-icon"><User /></el-icon>
            <el-select
              v-model="form.user_type"
              placeholder="请选择用户类型"
              size="large"
              class="user-type-select"
            >
              <el-option
                :value="1"
                label="老人"
              />
              <el-option
                :value="2"
                label="护理人员"
              />
              <el-option
                :value="4"
                label="家属"
              />
              <el-option
                v-if="showAdminOption"
                :value="3"
                label="管理员"
              />
            </el-select>
          </div>
        </el-form-item>

        <!-- 管理员注册验证（当选择管理员时显示） -->
        <div v-if="form.user_type === 3" class="admin-validation">
          <el-alert
            title="管理员注册需要验证权限"
            type="warning"
            :closable="false"
            show-icon
          />
          <el-form-item prop="admin_password">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input
                v-model="form.admin_password"
                type="password"
                placeholder="请输入管理员密码进行验证"
                size="large"
                show-password
              />
            </div>
          </el-form-item>
        </div>

        <!-- 基本信息 -->
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

        <!-- 短信验证码 -->
        <el-form-item prop="sms_code">
          <div class="input-wrapper sms-wrapper">
            <el-icon class="input-icon"><Message /></el-icon>
            <el-input
              v-model="form.sms_code"
              placeholder="请输入验证码"
              size="large"
              class="sms-input"
            />
            <el-button
              size="large"
              :disabled="smsSending || countdown > 0"
              @click="sendSms"
              class="sms-btn"
            >
              {{ countdown > 0 ? `${countdown}秒后重发` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <!-- 密码 -->
        <el-form-item prop="password">
          <div class="input-wrapper">
            <el-icon class="input-icon"><Lock /></el-icon>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码（6-20位）"
              size="large"
              show-password
            />
          </div>
        </el-form-item>

        <!-- 确认密码 -->
        <el-form-item prop="confirm_password">
          <div class="input-wrapper">
            <el-icon class="input-icon"><Lock /></el-icon>
            <el-input
              v-model="form.confirm_password"
              type="password"
              placeholder="请再次输入密码"
              size="large"
              show-password
            />
          </div>
        </el-form-item>

        <!-- 姓名（可选） -->
        <el-form-item prop="name">
          <div class="input-wrapper">
            <el-icon class="input-icon"><User /></el-icon>
            <el-input
              v-model="form.name"
              placeholder="请输入姓名（可选）"
              size="large"
            />
          </div>
        </el-form-item>

        <!-- 身份证号（可选） -->
        <el-form-item prop="id_card">
          <div class="input-wrapper">
            <el-icon class="input-icon"><Document /></el-icon>
            <el-input
              v-model="form.id_card"
              placeholder="请输入身份证号（可选）"
              size="large"
            />
          </div>
        </el-form-item>

        <!-- 性别和年龄 -->
        <div class="form-row">
          <el-form-item prop="gender">
            <el-select v-model="form.gender" placeholder="性别" size="large" class="half-input">
              <el-option :value="0" label="未知" />
              <el-option :value="1" label="男" />
              <el-option :value="2" label="女" />
            </el-select>
          </el-form-item>

          <el-form-item prop="age">
            <el-input
              v-model="form.age"
              placeholder="年龄（可选）"
              size="large"
              class="half-input"
              type="number"
            />
          </el-form-item>
        </div>

        <!-- 注册按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="register-btn"
            native-type="submit"
          >
            <span v-if="!loading">注 册</span>
            <span v-else>注册中...</span>
          </el-button>
        </el-form-item>
      </el-form>

      <div class="register-footer">
        <p>已有账号？<el-link type="primary" @click="$router.push('/login')">立即登录</el-link></p>
        <div class="back-login" @click="$router.push('/login')">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回登录</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Iphone,
  Lock,
  Message,
  User,
  Document,
  ArrowLeft,
  FirstAidKit
} from '@element-plus/icons-vue'
import api from '@/store/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const smsSending = ref(false)
const countdown = ref(0)

const form = reactive({
  user_type: 1,
  phone: '',
  sms_code: '',
  password: '',
  confirm_password: '',
  name: '',
  id_card: '',
  gender: null as number | null,
  age: null as number | null,
  admin_password: '' // 管理员注册验证密码
})

// 管理员注册专用密码验证API密钥（仅后端知晓，前端传递用于验证）
// 在实际应用中，应该由已登录的管理员通过界面创建新管理员
// 这里为简化实现，使用一个预设的管理员密码进行验证
const ADMIN_REGISTRATION_KEY = 'ADMIN_REGISTER_2024'

// 是否显示管理员选项（默认隐藏，需要通过特定方式显示）
// 为了演示，我们始终显示，但需要密码验证
const showAdminOption = ref(true)

// 验证确认密码
const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (!value) {
    return callback(new Error('请再次输入密码'))
  }
  if (value !== form.password) {
    return callback(new Error('两次输入的密码不一致'))
  }
  callback()
}

// 验证管理员密码（仅当选择管理员类型时）
const validateAdminPassword = (rule: any, value: string, callback: any) => {
  if (form.user_type === 3) {
    if (!value) {
      return callback(new Error('管理员注册需要验证密码'))
    }
    if (value !== ADMIN_REGISTRATION_KEY) {
      return callback(new Error('管理员验证密码错误'))
    }
  }
  callback()
}

const rules = {
  user_type: [
    { required: true, message: '请选择用户类型', trigger: 'change' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  sms_code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
    { max: 20, message: '密码长度不能超过20位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ],
  admin_password: [
    { validator: validateAdminPassword, trigger: 'blur' }
  ]
}

// 发送短信验证码
const sendSms = async () => {
  try {
    await formRef.value.validateField('phone')
    smsSending.value = true

    const res: any = await api.post('/users/send-sms', {
      phone: form.phone
    })

    if (res.code === 200) {
      ElMessage.success('验证码已发送')
      startCountdown()
    } else {
      ElMessage.error(res.message || '发送失败')
    }
  } catch (error: any) {
    if (error.fields) return
    ElMessage.error('发送失败，请稍后重试')
  } finally {
    smsSending.value = false
  }
}

// 倒计时
const startCountdown = () => {
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 注册处理
const handleRegister = async () => {
  try {
    await formRef.value.validate()

    // 管理员类型需要额外的验证（已经在validator中验证admin_password）
    // 但为了安全，后端也需要验证

    loading.value = true

    const registerData = {
      phone: form.phone,
      password: form.password,
      sms_code: form.sms_code,
      user_type: form.user_type,
      name: form.name || null,
      id_card: form.id_card || null,
      gender: form.gender || 0,
      age: form.age || null
    }

    // 如果是管理员注册，传递验证密码
    if (form.user_type === 3) {
      registerData.admin_verify_code = form.admin_password
    }

    const res: any = await api.post('/users/register', registerData)

    if (res.code === 200) {
      ElMessage.success('注册成功，请登录')

      // 保存登录信息
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('userInfo', JSON.stringify({
        id: res.data.user_id,
        user_type: form.user_type,
        name: form.name || '新用户',
        phone: form.phone
      }))

      // 跳转到对应仪表盘
      const routeMap: Record<number, string> = {
        1: '/elder-dashboard',
        2: '/nurse-dashboard',
        3: '/admin-dashboard',
        4: '/family-dashboard'
      }
      router.push(routeMap[form.user_type] || '/admin-dashboard')
    } else {
      ElMessage.error(res.message || '注册失败')
    }
  } catch (error: any) {
    console.error('注册失败', error)
    if (error.fields) return
    ElMessage.error('注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.register-background {
  position: absolute;
  inset: 0;
  z-index: 0;

  .bg-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
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
      background: #fff;
      top: -200px;
      right: -200px;
      animation: float 6s ease-in-out infinite;
    }

    .shape-2 {
      width: 400px;
      height: 400px;
      background: #fff;
      bottom: -150px;
      left: -100px;
      animation: float 8s ease-in-out infinite reverse;
    }

    .shape-3 {
      width: 200px;
      height: 200px;
      background: #fff;
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

.register-box {
  position: relative;
  z-index: 1;
  width: 460px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 50px 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;

  .logo {
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
  }

  h1 {
    font-size: 28px;
    color: #303133;
    margin-bottom: 8px;
    font-weight: 700;
  }

  p {
    font-size: 14px;
    color: #909399;
  }
}

.register-form {
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

      &:hover, &.is-focus {
        box-shadow: 0 0 0 2px #667eea;
      }
    }

    :deep(.el-input__inner) {
      height: 48px;
    }

    &.sms-wrapper {
      display: flex;
      gap: 10px;

      .sms-input {
        flex: 1;
      }

      .sms-btn {
        width: 140px;
        height: 48px;
        border-radius: 12px;
        flex-shrink: 0;
      }
    }

    &.user-type-select {
      :deep(.el-input__wrapper) {
        padding-left: 45px;
        cursor: pointer;
      }
    }
  }

  .form-row {
    display: flex;
    gap: 15px;

    .half-input {
      flex: 1;
    }
  }

  .admin-validation {
    background: rgba(230, 162, 60, 0.08);
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    border: 1px solid rgba(230, 162, 60, 0.3);
  }

  .register-btn {
    width: 100%;
    height: 48px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border: none;
    transition: all 0.3s ease;
    margin-top: 10px;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
  }
}

.register-footer {
  text-align: center;
  margin-top: 25px;

  p {
    color: #909399;
    font-size: 14px;
    margin-bottom: 15px;
  }

  .back-login {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #606266;
    cursor: pointer;
    font-size: 14px;
    transition: color 0.3s;

    &:hover {
      color: #667eea;
    }
  }
}
</style>
