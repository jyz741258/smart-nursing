<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">个人中心</h2>
    </div>

    <div class="card-container">
      <el-form ref="formRef" :model="form" label-width="100px" style="max-width: 600px">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" disabled />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio :label="1">男</el-radio>
            <el-radio :label="2">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="form.age" :min="0" :max="150" />
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="form.id_card" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="紧急联系人">
          <el-input v-model="form.emergency_contact" placeholder="请输入紧急联系人" />
        </el-form-item>
        <el-form-item label="紧急联系电话">
          <el-input v-model="form.emergency_phone" placeholder="请输入紧急联系电话" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="updateProfile">保存修改</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card-container" style="margin-top: 20px">
      <h4 class="card-title">修改密码</h4>
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="100px" style="max-width: 600px">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="changePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import api from '@/store/auth'

const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const pwdFormRef = ref<FormInstance>()

const form = reactive({
  phone: '',
  name: '',
  gender: 1,
  age: null as number | null,
  id_card: '',
  address: '',
  emergency_contact: '',
  emergency_phone: ''
})

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== pwdForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const pwdRules: FormRules = {
  old_password: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const getProfile = async () => {
  try {
    const res: any = await api.get('/users/profile')
    if (res.code === 200) {
      Object.assign(form, res.data)
    }
  } catch (error) {
    console.error('获取个人信息失败', error)
  }
}

const updateProfile = async () => {
  try {
    const res: any = await api.put('/users/profile', form)
    if (res.code === 200) {
      ElMessage.success('保存成功')
      authStore.getProfile()
    }
  } catch (error) {
    console.error('保存失败', error)
  }
}

const changePassword = async () => {
  try {
    await pwdFormRef.value?.validate()
    const res: any = await api.post('/users/change-password', {
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    if (res.code === 200) {
      ElMessage.success('密码修改成功')
      pwdFormRef.value?.resetFields()
    }
  } catch (error) {
    console.error('修改密码失败', error)
  }
}

onMounted(() => {
  getProfile()
})
</script>