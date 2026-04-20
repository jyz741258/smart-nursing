<template>
  <div class="register-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <div class="register-box">
      <!-- 标题区域 -->
      <div class="register-header">
        <div class="logo">
          <el-icon :size="40"><FirstAidKit /></el-icon>
        </div>
        <h1>智慧养老系统</h1>
        <p>Smart Nursing Platform</p>
      </div>

      <!-- 注册表单 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="register-form"
        @submit.prevent="handleRegister"
        size="large"
      >
        <!-- 用户类型 -->
        <el-form-item prop="user_type">
          <el-select
            v-model="form.user_type"
            placeholder="请选择用户类型"
            class="full-select"
          >
            <el-option :value="1" label="老人" />
            <el-option :value="4" label="家属" />
          </el-select>
        </el-form-item>

        <!-- 手机号 -->
        <el-form-item prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="请输入手机号"
            prefix-icon="Phone"
          />
        </el-form-item>

        <!-- 邮箱 -->
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="请输入邮箱地址"
            prefix-icon="Message"
          />
        </el-form-item>

        <!-- 验证码 -->
        <el-form-item prop="email_code">
          <el-input
            v-model="form.email_code"
            placeholder="请输入验证码"
            prefix-icon="Key"
            class="code-input"
          >
            <template #append>
              <el-button
                :disabled="smsSending || countdown > 0"
                @click="sendEmailCode"
                class="code-btn"
              >
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>

        <!-- 密码 -->
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码（6-20位）"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <!-- 确认密码 -->
        <el-form-item prop="confirm_password">
          <el-input
            v-model="form.confirm_password"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <!-- 姓名 -->
        <el-form-item prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入姓名（可选）"
            prefix-icon="User"
          />
        </el-form-item>

        <!-- 身份证 -->
        <el-form-item prop="id_card">
          <el-input
            v-model="form.id_card"
            placeholder="请输入身份证号（可选）"
            prefix-icon="Document"
          />
        </el-form-item>

        <!-- 性别 -->
        <el-form-item prop="gender" class="gender-item">
          <template #label><span class="field-label">性别</span></template>
          <div class="gender-buttons">
            <el-radio-group v-model="form.gender">
              <el-radio-button :value="0">未知</el-radio-button>
              <el-radio-button :value="1">男</el-radio-button>
              <el-radio-button :value="2">女</el-radio-button>
            </el-radio-group>
          </div>
        </el-form-item>

        <!-- 年龄 -->
        <el-form-item prop="age">
          <el-input
            v-model.number="form.age"
            placeholder="年龄（必须大于0）"
            prefix-icon="Calendar"
            type="number"
            min="1"
          />
        </el-form-item>

        <!-- 家属关系 -->
        <template v-if="form.user_type === 4">
          <div class="relation-section">
            <el-form-item prop="relation_with_elder">
              <template #label><span class="field-label">与老人关系</span></template>
              <el-select
                v-model="form.relation_with_elder"
                placeholder="请选择与老人的关系"
                class="full-select"
              >
                <el-option :value="1" label="子女" />
                <el-option :value="2" label="配偶" />
                <el-option :value="3" label="兄弟姐妹" />
                <el-option :value="4" label="孙子女" />
                <el-option :value="5" label="其他亲属" />
                <el-option :value="6" label="朋友/邻居" />
              </el-select>
            </el-form-item>
          </div>
        </template>

        <!-- 注册按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            class="register-btn"
            native-type="submit"
          >
            {{ loading ? '注册中...' : '注 册' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 底部链接 -->
      <div class="register-footer">
        <span>已有账号？</span>
        <el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { FirstAidKit } from '@element-plus/icons-vue'
import api from '@/store/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const smsSending = ref(false)
const countdown = ref(0)

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
      ElMessage.success('验证码已发送至邮箱，请查收')
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
// 配色方案 - 绿色、浅蓝、白色
$primary-green: #22c55e;
$primary-green-dark: #16a34a;
$primary-green-light: #4ade80;
$light-blue: #3b82f6;
$light-blue-light: #60a5fa;
$white: #ffffff;
$gray-50: #f8fafc;
$gray-100: #f1f5f9;
$gray-200: #e2e8f0;
$gray-300: #cbd5e1;
$gray-400: #94a3b8;
$gray-500: #64748b;
$gray-600: #475569;
$gray-700: #334155;
$gray-800: #1e293b;

.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 50%, #f0fdf4 100%);
  position: relative;
  overflow: hidden;
}

// 背景装饰
.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;

  .circle {
    position: absolute;
    border-radius: 50%;
    opacity: 0.5;
  }

  .circle-1 {
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(34, 197, 94, 0.15) 0%, transparent 70%);
    top: -100px;
    right: -100px;
  }

  .circle-2 {
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
    bottom: -50px;
    left: -50px;
  }

  .circle-3 {
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(34, 197, 94, 0.1) 0%, transparent 70%);
    top: 50%;
    left: 10%;
  }
}

.register-box {
  width: 100%;
  max-width: 420px;
  background: $white;
  border-radius: 20px;
  padding: 40px 36px;
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.05),
    0 10px 15px -3px rgba(0, 0, 0, 0.08),
    0 20px 25px -5px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 1;
}

// 标题区域
.register-header {
  text-align: center;
  margin-bottom: 32px;

  .logo {
    width: 72px;
    height: 72px;
    background: linear-gradient(135deg, $primary-green 0%, $light-blue 100%);
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: $white;
    margin: 0 auto 16px;
    box-shadow: 0 8px 20px rgba(34, 197, 94, 0.3);
  }

  h1 {
    font-size: 26px;
    font-weight: 700;
    color: $gray-800;
    margin-bottom: 6px;
  }

  p {
    font-size: 14px;
    color: $gray-500;
  }
}

// 表单样式
.register-form {
  :deep(.el-form-item) {
    margin-bottom: 18px;
  }

  :deep(.el-form-item__label) {
    color: $gray-700;
    font-weight: 500;
    padding-bottom: 8px;
  }

  :deep(.el-input__wrapper) {
    padding: 4px 16px;
    border-radius: 12px;
    box-shadow: 0 0 0 1px $gray-200 inset;
    transition: all 0.2s ease;

    &:hover {
      box-shadow: 0 0 0 1px $primary-green inset;
    }

    &.is-focus {
      box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2), 0 0 0 1px $primary-green inset;
    }
  }

  :deep(.el-input__inner) {
    height: 44px;
    color: $gray-800;

    &::placeholder {
      color: $gray-400;
    }
  }

  :deep(.el-input__prefix) {
    color: $gray-400;
  }

  // 下拉框样式
  :deep(.el-select) {
    width: 100%;

    .el-select__wrapper {
      min-height: 52px;
      padding: 6px 16px;
      border-radius: 12px;
      box-shadow: 0 0 0 1px $gray-200 inset;

      &:hover {
        box-shadow: 0 0 0 1px $primary-green inset;
      }

      &.is-focused {
        box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2), 0 0 0 1px $primary-green inset !important;
      }

      .el-select__placeholder {
        color: $gray-400;
      }

      .el-select__selected-item {
        color: $gray-800;
      }
    }
  }

  :deep(.el-select-dropdown) {
    border-radius: 12px;
    border: 1px solid $gray-200;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);

    .el-select-dropdown__item {
      color: $gray-700;
      padding: 12px 16px;

      &:hover {
        background-color: $gray-50;
      }

      &.is-selected {
        color: $primary-green;
        background-color: rgba(34, 197, 94, 0.08);
        font-weight: 600;
      }
    }
  }

  // 验证码输入框
  .code-input {
    :deep(.el-input-group__append) {
      background: linear-gradient(135deg, $primary-green 0%, $primary-green-dark 100%);
      border: none;
      border-radius: 0 12px 12px 0;
      padding: 0;
      margin: 0;
      box-shadow: none;

      .code-btn {
        background: transparent;
        border: none;
        color: $white;
        font-weight: 500;
        font-size: 14px;
        padding: 0 18px;
        height: 44px;
        margin: 3px 0;
        border-radius: 0 9px 9px 0;
        transition: all 0.2s ease;
        white-space: nowrap;

        &:hover:not(:disabled) {
          background: rgba(255, 255, 255, 0.15);
        }

        &:disabled {
          background: rgba(255, 255, 255, 0.5);
          color: $primary-green-dark;
          cursor: not-allowed;
        }
      }
    }

    :deep(.el-input__wrapper) {
      border-radius: 12px 0 0 12px;
    }
  }

  // 字段标签
  .field-label {
    font-weight: 500;
    color: $gray-700;
  }

  // 性别选择
  .gender-item {
    :deep(.el-form-item__content) {
      justify-content: flex-start;
    }
  }

  .gender-buttons {
    :deep(.el-radio-group) {
      display: flex;
      gap: 12px;
    }

    :deep(.el-radio-button) {
      .el-radio-button__inner {
        border: 2px solid $gray-200;
        border-radius: 10px;
        padding: 10px 24px;
        font-size: 14px;
        font-weight: 500;
        color: $gray-500;
        background: $gray-50;
        box-shadow: none !important;
        transition: all 0.2s ease;

        &:hover {
          border-color: $primary-green;
          color: $primary-green;
        }
      }

      &.is-active {
        .el-radio-button__inner {
          border-color: $primary-green;
          background: linear-gradient(135deg, $primary-green 0%, $primary-green-dark 100%);
          color: $white;
          box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3) !important;
        }
      }

      .el-radio-button__original-radio:checked + .el-radio-button__inner {
        border-color: $primary-green;
        background: linear-gradient(135deg, $primary-green 0%, $primary-green-dark 100%);
        color: $white;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3) !important;
      }
    }
  }

  // 关系选择区域
  .relation-section {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(34, 197, 94, 0.05) 100%);
    border: 1px solid rgba(34, 197, 94, 0.2);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 18px;
  }

  // 注册按钮
  .register-btn {
    width: 100%;
    height: 52px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(135deg, $primary-green 0%, $light-blue 100%);
    border: none;
    color: $white;
    margin-top: 8px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 14px rgba(34, 197, 94, 0.35);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(34, 197, 94, 0.4);
    }

    &:active {
      transform: translateY(0);
    }
  }
}

// 底部链接
.register-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid $gray-100;

  span {
    color: $gray-500;
    font-size: 14px;
  }

  :deep(.el-link) {
    font-weight: 500;

    &:hover {
      color: $primary-green;
    }
  }
}

// 响应式
@media (max-width: 480px) {
  .register-box {
    padding: 30px 24px;
  }

  .register-header h1 {
    font-size: 22px;
  }

  .gender-buttons :deep(.el-radio-button__inner) {
    padding: 8px 16px;
    font-size: 13px;
  }
}
</style>
