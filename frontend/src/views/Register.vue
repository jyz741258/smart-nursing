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
                :value="4"
                label="家属"
              />
            </el-select>
          </div>
        </el-form-item>

        <!-- 邮箱 -->
        <el-form-item prop="email">
          <div class="input-wrapper">
            <el-icon class="input-icon"><Message /></el-icon>
            <el-input
              v-model="form.email"
              placeholder="请输入邮箱地址"
              size="large"
            />
          </div>
        </el-form-item>

        <!-- 邮箱验证码 -->
        <el-form-item prop="email_code">
          <div class="input-wrapper sms-wrapper">
            <el-icon class="input-icon"><Key /></el-icon>
            <el-input
              v-model="form.email_code"
              placeholder="请输入验证码"
              size="large"
              class="sms-input"
            />
            <el-button
              size="large"
              :disabled="smsSending || countdown > 0"
              @click="sendEmailCode"
              class="sms-btn"
            >
              {{ countdown > 0 ? `${countdown}秒后重发` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <!-- 验证码显示区域 -->
        <div v-if="showCodeDisplay" class="code-display">
          <div class="code-box">
            <div class="code-label">
              <el-icon><Key /></el-icon>
              <span>您的验证码</span>
            </div>
            <div class="code-value">{{ displayCode }}</div>
            <div class="code-tips">请在下方输入此验证码</div>
          </div>
        </div>

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
              v-model.number="form.age"
              placeholder="年龄（必须大于0）"
              size="large"
              class="half-input"
              type="number"
              min="1"
            />
          </el-form-item>
        </div>

        <!-- 家属与老人关系（仅家属显示） -->
        <div v-if="form.user_type === 4" class="relation-section">
          <el-alert
            title="请选择与老人的关系"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 15px"
          />
          <el-form-item prop="relation_with_elder">
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <el-select
                v-model="form.relation_with_elder"
                placeholder="请选择与老人的关系"
                size="large"
                class="full-width"
              >
                <el-option :value="1" label="子女" />
                <el-option :value="2" label="配偶" />
                <el-option :value="3" label="兄弟姐妹" />
                <el-option :value="4" label="孙子女" />
                <el-option :value="5" label="其他亲属" />
                <el-option :value="6" label="朋友/邻居" />
              </el-select>
            </div>
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
  FirstAidKit,
  Key
} from '@element-plus/icons-vue'
import api from '@/store/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const smsSending = ref(false)
const countdown = ref(0)
const showCodeDisplay = ref(false)
const displayCode = ref('')

const form = reactive({
  user_type: 1,
  phone: '',
  email: '',
  email_code: '',
  password: '',
  confirm_password: '',
  name: '',
  id_card: '',
  gender: null as number | null,
  age: null as number | null,
  relation_with_elder: null as number | null
})

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

// 验证邮箱格式
const validateEmail = (rule: any, value: string, callback: any) => {
  if (!value) {
    return callback(new Error('请输入邮箱地址'))
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value)) {
    return callback(new Error('请输入有效的邮箱地址'))
  }
  callback()
}

// 验证年龄为正数
const validateAge = (rule: any, value: number | null, callback: any) => {
  if (value !== null && value !== undefined) {
    if (value <= 0) {
      return callback(new Error('年龄必须大于0'))
    }
    if (value > 150) {
      return callback(new Error('年龄不能超过150岁'))
    }
  }
  callback()
}

// 验证家属与老人关系
const validateRelation = (rule: any, value: number | null, callback: any) => {
  if (form.user_type === 4 && !value) {
    return callback(new Error('请选择与老人的关系'))
  }
  callback()
}

const rules = {
  user_type: [
    { required: true, message: '请选择用户类型', trigger: 'change' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入11位有效手机号', trigger: 'blur' }
  ],
  email: [
    { required: true, validator: validateEmail, trigger: 'blur' }
  ],
  email_code: [
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
  age: [
    { validator: validateAge, trigger: 'blur' }
  ],
  relation_with_elder: [
    { validator: validateRelation, trigger: 'change' }
  ]
}

// 发送邮箱验证码
const sendEmailCode = async () => {
  try {
    await formRef.value.validateField('email')
    smsSending.value = true

    const res: any = await api.post('/users/send-email-code', {
      email: form.email
    })

    if (res.code === 200) {
      ElMessage.success('验证码已发送至邮箱')
      if (res.data && res.data.code) {
        displayCode.value = res.data.code
        showCodeDisplay.value = true
      }
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

    loading.value = true

    const registerData: any = {
      phone: form.phone,
      password: form.password,
      email_code: form.email_code,
      user_type: form.user_type,
      name: form.name || null,
      id_card: form.id_card || null,
      gender: form.gender || 0,
      age: form.age || null,
      email: form.email
    }

    // 如果是家属注册，添加关系字段
    if (form.user_type === 4) {
      registerData.relation_with_elder = form.relation_with_elder
    }

    const res: any = await api.post('/users/register', registerData)

    if (res.code === 200) {
      ElMessage.success('注册成功，请登录')

      localStorage.setItem('token', res.data.token)
      localStorage.setItem('userInfo', JSON.stringify({
        id: res.data.user_id,
        user_type: form.user_type,
        name: form.name || '新用户',
        phone: form.phone
      }))

      const routeMap: Record<number, string> = {
        1: '/elder-dashboard',
        4: '/family-dashboard'
      }
      router.push(routeMap[form.user_type] || '/login')
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

  .relation-section {
    background: rgba(64, 158, 255, 0.08);
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    border: 1px solid rgba(64, 158, 255, 0.3);
  }

  .full-width {
    width: 100%;
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

.code-display {
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;

  .code-box {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border: 2px dashed #409eff;
    border-radius: 16px;
    padding: 20px;
    text-align: center;

    .code-label {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      color: #409eff;
      font-size: 14px;
      margin-bottom: 10px;

      .el-icon {
        font-size: 18px;
      }
    }

    .code-value {
      font-size: 36px;
      font-weight: 700;
      color: #1565c0;
      letter-spacing: 8px;
      font-family: 'Courier New', monospace;
      padding: 10px 20px;
      background: rgba(255, 255, 255, 0.8);
      border-radius: 8px;
      display: inline-block;
    }

    .code-tips {
      font-size: 12px;
      color: #64b5f6;
      margin-top: 10px;
    }
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
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
