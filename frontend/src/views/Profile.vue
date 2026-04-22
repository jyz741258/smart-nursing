<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">个人中心</h2>
      <div class="user-badge" :class="userTypeClass">
        <el-icon><UserFilled /></el-icon>
        <span>{{ userTypeName }}</span>
      </div>
    </div>

    <div class="profile-content">
      <div class="profile-card info-section">
        <div class="card-header">
          <h3>基本信息</h3>
        </div>
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

      <div class="profile-card role-section">
        <div class="card-header">
          <h3>角色权限</h3>
        </div>
        <div class="role-info">
          <div class="role-icon" :class="userTypeClass">
            <el-icon :size="40"><UserFilled /></el-icon>
          </div>
          <div class="role-details">
            <h4>{{ userTypeName }}</h4>
            <p class="role-desc">{{ roleDescription }}</p>
          </div>
        </div>
        <div class="permissions">
          <h5>可使用功能</h5>
          <div class="permission-tags">
            <span v-for="perm in permissions" :key="perm" class="perm-tag">
              <el-icon><Check /></el-icon>
              {{ perm }}
            </span>
          </div>
        </div>
      </div>

      <div class="profile-card password-section">
        <div class="card-header">
          <h3>修改密码</h3>
        </div>
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

      <div v-if="userType === 1" class="profile-card health-section">
        <div class="card-header">
          <h3>健康信息</h3>
        </div>
        <div class="health-stats">
          <div class="stat-item">
            <div class="stat-value">--</div>
            <div class="stat-label">今日步数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">--</div>
            <div class="stat-label">睡眠时长</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">--</div>
            <div class="stat-label">心率</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">--</div>
            <div class="stat-label">血压</div>
          </div>
        </div>
        <el-button type="primary" plain @click="$router.push('/health')">查看健康详情</el-button>
      </div>

      <div v-if="userType === 2" class="profile-card work-section">
        <div class="card-header">
          <h3>工作统计</h3>
        </div>
        <div class="work-stats">
          <div class="stat-item">
            <div class="stat-value">--</div>
            <div class="stat-label">今日服务</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">--</div>
            <div class="stat-label">本周服务</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">--</div>
            <div class="stat-label">评分</div>
          </div>
        </div>
        <el-button type="primary" plain @click="$router.push('/nursing')">查看护理记录</el-button>
      </div>

      <div v-if="userType === 4" class="profile-card family-section">
        <div class="card-header">
          <h3>关注的老人</h3>
        </div>
        <div class="elder-list">
          <div v-for="elder in watchedElders" :key="elder.id" class="elder-item">
            <el-avatar :size="40" :style="{ background: elder.color }">{{ elder.name.charAt(0) }}</el-avatar>
            <div class="elder-info">
              <div class="elder-name">{{ elder.name }}</div>
              <div class="elder-relation">{{ elder.relation }}</div>
            </div>
            <div class="elder-status" :class="elder.healthStatus">{{ elder.healthStatusText }}</div>
          </div>
        </div>
        <el-button type="primary" plain @click="$router.push('/health')">查看健康详情</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled, Check } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import api from '@/store/auth'

const formRef = ref<FormInstance>()
const pwdFormRef = ref<FormInstance>()
const userType = ref(3)

const watchedElders = ref([
  { id: 1, name: '张三', relation: '父亲', healthStatus: 'normal', healthStatusText: '健康', color: '#67c23a' }
])

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

const userTypeName = computed(() => {
  const names = { 1: '老人用户', 2: '护理人员', 3: '管理员', 4: '老人家属' }
  return names[userType.value] || '未知'
})

const userTypeClass = computed(() => {
  const classes = { 1: 'elder', 2: 'nurse', 3: 'admin', 4: 'family' }
  return classes[userType.value] || ''
})

const roleDescription = computed(() => {
  const descs = {
    1: '享受专业护理服务，管理个人健康档案',
    2: '提供护理服务，管理护理计划和记录',
    3: '管理系统用户和数据，查看统计报表',
    4: '查看老人健康状况，联系护理人员'
  }
  return descs[userType.value] || ''
})

const permissions = computed(() => {
  const perms = {
    1: ['健康记录', '护理计划', '预约服务', '消息通知'],
    2: ['护理记录', '健康监测', '任务管理', '服务统计'],
    3: ['老人管理', '护理人员管理', '数据统计', '系统设置'],
    4: ['健康监测', '护理记录', '紧急求助', '联系护理']
  }
  return perms[userType.value] || []
})

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== pwdForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const pwdRules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
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
      userType.value = res.data.user_type || 3
    }
  } catch (error) {
    console.error('获取个人信息失败', error)
  }
}

const getStats = async () => {
  if (userType.value !== 3) return
  try {
    const res: any = await api.get('/statistics/overview')
    if (res.code === 200) {
      stats.value = res.data || {}
    }
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

const updateProfile = async () => {
  try {
    const res: any = await api.put('/users/profile', form)
    if (res.code === 200) {
      ElMessage.success('保存成功')
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
  getStats()
})
</script>

<style scoped lang="scss">
.page-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
  }

  .user-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;

    &.elder {
      background: #f0f9eb;
      color: #67c23a;
    }

    &.nurse {
      background: #ecf5ff;
      color: #409eff;
    }

    &.admin {
      background: #fdf6ec;
      color: #e6a23c;
    }

    &.family {
      background: #fef0f0;
      color: #f56c6c;
    }
  }
}

.profile-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.profile-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

  .card-header {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #ebeef5;

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.role-section {
  .role-info {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;

    .role-icon {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;

      &.elder { background: linear-gradient(135deg, #67c23a, #85ce61); }
      &.nurse { background: linear-gradient(135deg, #409eff, #66b1ff); }
      &.admin { background: linear-gradient(135deg, #e6a23c, #ebb563); }
      &.family { background: linear-gradient(135deg, #f56c6c, #fab6b6); }
    }

    .role-details {
      h4 {
        font-size: 20px;
        color: #303133;
        margin-bottom: 8px;
      }

      .role-desc {
        color: #909399;
        font-size: 14px;
      }
    }
  }

  .permissions {
    h5 {
      font-size: 14px;
      color: #606266;
      margin-bottom: 12px;
    }

    .permission-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .perm-tag {
        display: flex;
        align-items: center;
        gap: 4px;
        background: #f4f4f5;
        color: #606266;
        padding: 6px 12px;
        border-radius: 15px;
        font-size: 13px;

        .el-icon {
          color: #67c23a;
        }
      }
    }
  }
}

.health-section, .work-section, .admin-section {
  .health-stats, .work-stats, .admin-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    margin-bottom: 20px;

    .stat-item {
      text-align: center;
      padding: 15px;
      background: #f5f7fa;
      border-radius: 8px;

      .stat-value {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 5px;
      }

      .stat-label {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .admin-actions {
    display: flex;
    gap: 10px;
  }
}

.family-section {
  .elder-list {
    margin-bottom: 20px;

    .elder-item {
      display: flex;
      align-items: center;
      padding: 12px;
      border-radius: 8px;
      background: #f5f7fa;
      margin-bottom: 10px;

      .elder-info {
        flex: 1;
        margin-left: 12px;

        .elder-name {
          font-size: 15px;
          font-weight: 500;
          color: #303133;
        }

        .elder-relation {
          font-size: 12px;
          color: #909399;
        }
      }

      .elder-status {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;

        &.normal {
          background: #f0f9eb;
          color: #67c23a;
        }

        &.warning {
          background: #fdf6ec;
          color: #e6a23c;
        }

        &.danger {
          background: #fef0f0;
          color: #f56c6c;
        }
      }
    }
  }
}
</style>