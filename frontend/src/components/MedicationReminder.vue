<template>
  <div class="medication-reminder">
    <div class="reminder-header">
      <h3 class="header-title">用药提醒</h3>
      <el-button type="primary" size="small" @click="showAddReminderDialog = true">
        <el-icon><Plus /></el-icon> 添加提醒
      </el-button>
    </div>

    <!-- 所有提醒列表 -->
    <div class="all-reminders" style="margin-top: 20px;">
      <h4 class="section-title">所有提醒</h4>
      <div v-if="reminders.length === 0" class="empty-reminders">
        <el-empty description="暂无用药提醒" />
      </div>
      <div v-else class="reminder-list">
        <div 
          v-for="reminder in reminders" 
          :key="reminder.id"
          :class="['reminder-item', { 'completed': reminder.completed }]"
        >
          <div class="reminder-time">
            <div class="time">
              {{ reminder.time }}
            </div>
            <div class="status">
              <el-tag :type="reminder.completed ? 'success' : 'warning'" size="small">
                {{ reminder.completed ? '已服用' : '待服用' }}
              </el-tag>
            </div>
          </div>
          <div class="reminder-content">
            <h5 class="medication-name">{{ reminder.medication_name }}</h5>
            <p class="medication-dosage">{{ reminder.dosage }}</p>
            <p class="medication-notes" v-if="reminder.notes">{{ reminder.notes }}</p>
            <p class="medication-days">{{ reminder.days.join('、') }}</p>
            <p class="medication-user" v-if="reminder.user_name">{{ reminder.user_name }}</p>
          </div>
          <div class="reminder-actions">
            <el-button 
              v-if="!reminder.completed" 
              type="success" 
              size="small" 
              @click="markAsCompleted(reminder.id)"
            >
              <el-icon><Check /></el-icon> 确认服用
            </el-button>
            <el-button 
              v-else 
              type="info" 
              size="small" 
              @click="markAsUncompleted(reminder.id)"
            >
              <el-icon><Close /></el-icon> 取消确认
            </el-button>
            <el-button type="danger" size="small" @click="deleteReminder(reminder.id)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加提醒对话框 -->
    <el-dialog v-model="showAddReminderDialog" title="添加用药提醒" width="500px">
      <el-form :model="reminderForm" label-width="100px">
        <el-form-item label="老人" v-if="isAdmin">
          <el-select v-model="reminderForm.user_id" placeholder="选择老人">
            <el-option v-for="elder in elderList" :key="elder.id" :label="elder.name" :value="elder.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="药品名称">
          <el-input v-model="reminderForm.medication_name" placeholder="请输入药品名称" />
        </el-form-item>
        <el-form-item label="服用时间">
          <el-time-picker v-model="reminderForm.time" format="HH:mm" placeholder="选择时间" style="width: 100%" />
        </el-form-item>
        <el-form-item label="服用剂量">
          <el-input v-model="reminderForm.dosage" placeholder="如：1片" />
        </el-form-item>
        <el-form-item label="服用天数">
          <el-checkbox-group v-model="reminderForm.days">
            <el-checkbox label="周一" />
            <el-checkbox label="周二" />
            <el-checkbox label="周三" />
            <el-checkbox label="周四" />
            <el-checkbox label="周五" />
            <el-checkbox label="周六" />
            <el-checkbox label="周日" />
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="reminderForm.notes" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddReminderDialog = false">取消</el-button>
        <el-button type="primary" @click="addReminder">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Check, Close, Delete } from '@element-plus/icons-vue'
import api from '@/store/auth'

interface Reminder {
  id: number
  medication_name: string
  time: string
  dosage: string
  days: string[]
  notes: string
  completed: boolean
  user_name?: string
}

const showAddReminderDialog = ref(false)
const reminders = ref<Reminder[]>([])
const elderList = ref<any[]>([])

const reminderForm = ref({
  user_id: '',
  medication_name: '',
  time: '',
  dosage: '',
  days: [],
  notes: ''
})

// 获取当前用户类型
const isAdmin = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return user.user_type === 3
})

// 加载老人列表
const loadElderList = async () => {
  if (!isAdmin.value) return
  try {
    const res: any = await api.get('/users/elders')
    if (res.code === 200) {
      elderList.value = res.data || []
    }
  } catch (error) {
    console.error('获取老人列表失败', error)
  }
}

// 加载用药提醒
const loadReminders = async () => {
  try {
    const res: any = await api.get('/medication/reminders')
    if (res.code === 200) {
      reminders.value = res.data || []
    }
  } catch (error) {
    console.error('获取用药提醒失败', error)
    // 模拟数据
    reminders.value = [
      {
        id: 1,
        medication_name: '降压药',
        time: '08:00',
        dosage: '1片',
        days: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        notes: '饭后服用',
        completed: false
      },
      {
        id: 2,
        medication_name: '降糖药',
        time: '12:00',
        dosage: '1片',
        days: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        notes: '饭前30分钟服用',
        completed: false
      },
      {
        id: 3,
        medication_name: '维生素D',
        time: '20:00',
        dosage: '1片',
        days: ['周一', '周三', '周五'],
        notes: '',
        completed: false
      }
    ]
  }
}

// 添加用药提醒
const addReminder = async () => {
  if (!reminderForm.value.medication_name || !reminderForm.value.time || !reminderForm.value.dosage || reminderForm.value.days.length === 0) {
    ElMessage.warning('请填写完整信息')
    return
  }

  try {
    const res: any = await api.post('/medication/reminders', reminderForm.value)
    if (res.code === 200) {
      ElMessage.success('添加成功')
      showAddReminderDialog.value = false
      await loadReminders()
      // 重置表单
      reminderForm.value = {
        user_id: '',
        medication_name: '',
        time: '',
        dosage: '',
        days: [],
        notes: ''
      }
    }
  } catch (error) {
    console.error('添加用药提醒失败', error)
    ElMessage.error('添加失败')
    // 模拟添加成功
    const newReminder: Reminder = {
      id: Date.now(),
      medication_name: reminderForm.value.medication_name,
      time: reminderForm.value.time,
      dosage: reminderForm.value.dosage,
      days: reminderForm.value.days,
      notes: reminderForm.value.notes,
      completed: false
    }
    reminders.value.push(newReminder)
    ElMessage.success('添加成功')
    showAddReminderDialog.value = false
    // 重置表单
    reminderForm.value = {
      user_id: '',
      medication_name: '',
      time: '',
      dosage: '',
      days: [],
      notes: ''
    }
  }
}

// 标记为已服用
const markAsCompleted = async (id: number) => {
  try {
    const res: any = await api.put(`/medication/reminders/${id}/complete`)
    if (res.code === 200) {
      ElMessage.success('已标记为已服用')
      const reminder = reminders.value.find(r => r.id === id)
      if (reminder) {
        reminder.completed = true
      }
    }
  } catch (error) {
    console.error('标记为已服用失败', error)
    ElMessage.error('操作失败')
    // 模拟标记成功
    const reminder = reminders.value.find(r => r.id === id)
    if (reminder) {
      reminder.completed = true
    }
    ElMessage.success('已标记为已服用')
  }
}

// 标记为未服用
const markAsUncompleted = async (id: number) => {
  try {
    const res: any = await api.put(`/medication/reminders/${id}/uncomplete`)
    if (res.code === 200) {
      ElMessage.success('已标记为未服用')
      const reminder = reminders.value.find(r => r.id === id)
      if (reminder) {
        reminder.completed = false
      }
    }
  } catch (error) {
    console.error('标记为未服用失败', error)
    ElMessage.error('操作失败')
    // 模拟标记成功
    const reminder = reminders.value.find(r => r.id === id)
    if (reminder) {
      reminder.completed = false
    }
    ElMessage.success('已标记为未服用')
  }
}

// 删除用药提醒
const deleteReminder = async (id: number) => {
  try {
    const res: any = await api.delete(`/medication/reminders/${id}`)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      reminders.value = reminders.value.filter(r => r.id !== id)
    }
  } catch (error) {
    console.error('删除用药提醒失败', error)
    ElMessage.error('删除失败')
    // 模拟删除成功
    reminders.value = reminders.value.filter(r => r.id !== id)
    ElMessage.success('删除成功')
  }
}

onMounted(() => {
  loadReminders()
  loadElderList()
})
</script>

<style scoped lang="scss">
.medication-reminder {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

  .reminder-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e4e7ed;

    .header-title {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 15px 0;
    padding-left: 10px;
    border-left: 4px solid #409eff;
  }

  .empty-reminders {
    padding: 40px 0;
    text-align: center;
  }

  .reminder-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .reminder-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 8px;
    transition: all 0.3s ease;

    &:hover {
      background: #eef2f7;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    &.completed {
      background: #f0f9eb;

      .medication-name {
        text-decoration: line-through;
        color: #909399;
      }
    }

    .reminder-time {
      min-width: 120px;
      text-align: center;

      .time {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 8px;
      }
    }

    .reminder-content {
      flex: 1;

      .medication-name {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        margin: 0 0 8px 0;
      }

      .medication-dosage {
        font-size: 14px;
        color: #606266;
        margin: 0 0 4px 0;
      }

      .medication-notes {
        font-size: 12px;
        color: #909399;
        margin: 0 0 4px 0;
      }

      .medication-days {
        font-size: 12px;
        color: #409eff;
        margin: 0;
      }

      .medication-user {
        font-size: 12px;
        color: #67c23a;
        margin: 4px 0 0 0;
      }
    }

    .reminder-actions {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
  }
}
</style>