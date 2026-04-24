<template>
  <div class="nurse-dashboard">
    <div class="role-indicator nurse">
      <span class="role-icon">👩‍⚕️</span>
      <span class="role-text">护理人员</span>
    </div>

    <div class="welcome-banner">
      <div class="banner-left">
        <h1>您好，护理师</h1>
        <p>今日已服务 {{ completedCount }} 位老人，还需完成 {{ pendingCount }} 个任务</p>
      </div>
      <div class="banner-right">
        <div class="today-date">
          <div class="date-day">{{ currentDay }}</div>
          <div class="date-info">{{ currentDate }}</div>
        </div>
      </div>
    </div>

    <div class="nurse-content">
      <el-row :gutter="20">
        <el-col :span="16">
          <div class="main-section">
            <div class="section-header">
              <span class="section-title">今日任务</span>
              <el-tag type="warning">待执行 {{ pendingCount }}</el-tag>
            </div>
            <div class="task-list">
              <div v-for="task in todayTasks" :key="task.id" class="task-item" :class="{ completed: task.status === 2 }">
                <div class="task-time">
                  <span class="time">{{ task.time }}</span>
                  <span class="duration">{{ task.duration }}分钟</span>
                </div>
                <div class="task-info">
                  <div class="task-header">
                    <span class="elder-name">{{ task.elderName }}</span>
                    <el-tag v-if="task.type" size="small" :type="getTypeColor(task.type)">{{ getTypeName(task.type) }}</el-tag>
                  </div>
                  <div class="task-address"><el-icon><Location /></el-icon> {{ task.address }}</div>
                  <div class="task-notes">{{ task.notes }}</div>
                </div>
                <div class="task-actions">
                  <el-button v-if="task.status === 1" type="primary" size="small" @click="startTask(task)">开始服务</el-button>
                  <el-button v-else type="success" size="small" disabled>已完成</el-button>
                </div>
              </div>
              <el-empty v-if="todayTasks.length === 0" description="今日暂无任务" />
            </div>


          </div>
        </el-col>

        <el-col :span="8">
          <div class="side-section">
            <div class="stats-card">
              <div class="section-title">今日工作统计</div>
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value">{{ stats.completed }}</div>
                  <div class="stat-label">已完成</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ stats.pending }}</div>
                  <div class="stat-label">待执行</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ stats.totalHours }}</div>
                  <div class="stat-label">服务时长(h)</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ stats.rating }}</div>
                  <div class="stat-label">服务评分</div>
                </div>
              </div>
            </div>

            <!-- 服务老人 -->
            <div class="elder-list">
              <div class="section-title">服务老人</div>
              <div class="elder-items">
                <div v-for="elder in serviceElders" :key="elder.id" class="elder-item">
                  <div class="elder-info">
                    <div class="elder-name">{{ elder.name }}</div>
                    <div class="elder-phone">{{ elder.phone }}</div>
                  </div>
                  <el-button type="primary" size="small" @click="viewElderOrders(elder.id)">查看订单</el-button>
                </div>
              </div>
              <el-empty v-if="serviceElders.length === 0" description="暂无服务老人" />
            </div>

            <div class="quick-actions">
              <div class="section-title">快捷操作</div>
              <div class="action-list">
                <div class="action-item" @click="$router.push('/nursing')"><el-icon><Document /></el-icon><span>添加护理记录</span></div>
                <div class="action-item" @click="$router.push('/care-plan')"><el-icon><Calendar /></el-icon><span>护理计划</span></div>
                <div class="action-item" @click="syncHealth"><el-icon><Refresh /></el-icon><span>同步健康数据</span></div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="taskDialog" title="开始服务" width="500px">
      <el-form ref="formRef" :model="taskForm" label-width="100px">
        <el-form-item label="服务内容"><el-input v-model="taskForm.content" type="textarea" rows="3" placeholder="请输入服务内容" /></el-form-item>
        <el-form-item label="服务状态">
          <el-radio-group v-model="taskForm.status">
            <el-radio label="2">正常完成</el-radio>
            <el-radio label="3">异常/取消</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialog = false">取消</el-button>
        <el-button type="primary" @click="completeTask">确认完成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'
import { useAuthStore } from '@/store/auth'

const router = useRouter()

const authStore = useAuthStore()

const taskDialog = ref(false)
const currentTask = ref<any>(null)
const taskForm = reactive({ content: '', status: '2' })



// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '待定'
  return dateStr
}

const currentDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
})

const currentDay = computed(() => String(new Date().getDate()).padStart(2, '0'))
const completedCount = ref(0)
const pendingCount = ref(0)
const stats = reactive({ completed: 0, pending: 0, totalHours: 0, rating: 0 })

const todayTasks = ref<any[]>([])

// 加载今日任务
const loadTodayTasks = async () => {
  try {
    const res: any = await api.get('/nursing/records', {
      params: {
        page: 1,
        page_size: 50
      }
    })
    if (res.code === 200) {
      // 映射API返回的数据到前端需要的字段
      todayTasks.value = (res.data.items || []).map((item: any) => ({
        id: item.id,
        time: item.start_time ? new Date(item.start_time).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '待定',
        duration: 30, // 默认30分钟
        elderName: item.elder_name || '未知老人',
        address: '服务地址', // 暂时使用默认地址
        notes: item.description || '无备注',
        type: item.nursing_type || 1,
        status: item.status
      }))
      // 计算统计数据
      completedCount.value = todayTasks.value.filter(task => task.status === 2).length
      pendingCount.value = todayTasks.value.filter(task => task.status === 1).length
      stats.completed = completedCount.value
      stats.pending = pendingCount.value
    }
  } catch (error) {
    console.error('获取今日任务失败', error)
    // 模拟数据
    todayTasks.value = [
      { id: 1, time: '09:00', duration: 60, elderName: '张三', address: '朝阳区建国路88号', notes: '日常清洁护理', type: 1, status: 2 },
      { id: 2, time: '10:30', duration: 30, elderName: '李四', address: '海淀区中关村大街1号', notes: '血压监测', type: 4, status: 1 },
      { id: 3, time: '14:00', duration: 45, elderName: '王五', address: '西城区金融街8号', notes: '服药提醒', type: 4, status: 1 }
    ]
    completedCount.value = todayTasks.value.filter(task => task.status === 2).length
    pendingCount.value = todayTasks.value.filter(task => task.status === 1).length
    stats.completed = completedCount.value
    stats.pending = pendingCount.value
  }
}

// 服务老人列表
const serviceElders = ref<any[]>([])

const getTypeName = (type: number) => ({ 1: '日常照护', 2: '医疗护理', 3: '康复训练', 4: '健康监测' }[type] || '其他')
const getTypeColor = (type: number) => ({ 1: 'success', 2: 'primary', 3: 'warning', 4: 'info' }[type] || 'info')

// 加载服务老人列表
const loadServiceElders = async () => {
  try {
    const res: any = await api.get('/users/service-elders')
    if (res.code === 200) {
      serviceElders.value = res.data || []
    }
  } catch (error) {
    console.error('获取服务老人列表失败', error)
    // 模拟数据
    serviceElders.value = [
      { id: 1, name: '张三', phone: '13900001001' },
      { id: 3, name: '王五', phone: '13900001003' }
    ]
  }
}

// 查看老人订单
const viewElderOrders = (elderId: number) => {
  router.push({ path: '/orders', query: { elder_id: elderId } })
}

const startTask = (task: any) => {
  currentTask.value = task
  taskForm.content = task.notes
  taskForm.status = '2'
  taskDialog.value = true
}

const completeTask = async () => {
  if (currentTask.value) {
    try {
      // 调用API完成任务
      const res: any = await api.post(`/nursing/records/${currentTask.value.id}/complete`, {
        notes: taskForm.content
      })
      if (res.code === 200) {
        // 更新本地任务状态
        const taskIndex = todayTasks.value.findIndex(task => task.id === currentTask.value.id)
        if (taskIndex !== -1) {
          todayTasks.value[taskIndex].status = parseInt(taskForm.status)
        }
        // 更新统计数据
        if (taskForm.status === '2') {
          completedCount.value++
          pendingCount.value--
          stats.completed++
          stats.pending--
        }
        ElMessage.success('服务已完成')
        taskDialog.value = false
      } else {
        ElMessage.error('完成服务失败')
      }
    } catch (error) {
      console.error('完成服务失败', error)
      ElMessage.error('完成服务失败，请稍后重试')
    }
  }
}

const syncHealth = () => ElMessage.success('健康数据同步成功')

onMounted(() => {
  loadServiceElders()
  loadTodayTasks()
})

onUnmounted(() => {
})
</script>

<style scoped lang="scss">
.nurse-dashboard {
  position: relative;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 50%, #dee2e6 100%);

  // 多层动态背景效果
  &::before {
    content: '';
    position: fixed;
    top: -100%;
    left: -100%;
    width: 300%;
    height: 300%;
    background: 
      radial-gradient(ellipse at 20% 20%, rgba(64, 158, 255, 0.05) 0%, transparent 40%),
      radial-gradient(ellipse at 80% 80%, rgba(102, 126, 234, 0.05) 0%, transparent 40%),
      radial-gradient(ellipse at 50% 50%, rgba(64, 158, 255, 0.05) 0%, transparent 50%);
    animation: nurseBgFloat 25s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
  }

  // 科技网格背景
  &::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: 
      linear-gradient(rgba(64, 158, 255, 0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(64, 158, 255, 0.02) 1px, transparent 1px);
    background-size: 55px 55px;
    animation: gridMove 22s linear infinite;
    pointer-events: none;
    z-index: 0;
  }

  @keyframes nurseBgFloat {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    25% { transform: translate(2%, -2%) rotate(1deg); }
    50% { transform: translate(-2%, 2%) rotate(-1deg); }
    75% { transform: translate(1%, -1%) rotate(0.5deg); }
  }

  @keyframes gridMove {
    0% { background-position: 0 0; }
    100% { background-position: 55px 55px; }
  }
}

.role-indicator {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 24px;

  &.nurse {
    background: linear-gradient(135deg, #409eff, #5a9fff);
    color: #ffffff;
    box-shadow: 0 4px 24px rgba(64, 158, 255, 0.5), 0 0 0 2px rgba(64, 158, 255, 0.2);
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    animation: fadeInDown 0.6s var(--ease-bounce);
  }

  .role-icon {
    font-size: 20px;
  }

  .role-text {
    letter-spacing: 0.5px;
  }
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.welcome-banner {
  position: relative;
  z-index: 1;
  background: linear-gradient(135deg, #409eff, #5a9fff);
  border-radius: 18px;
  padding: 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  color: #fff;
  box-shadow: 0 10px 40px rgba(64, 158, 255, 0.4);
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -60%;
    right: -15%;
    width: 350px;
    height: 350px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, transparent 70%);
    border-radius: 50%;
    animation: bannerOrb 25s ease-in-out infinite;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: -40%;
    left: -10%;
    width: 250px;
    height: 250px;
    background: radial-gradient(circle, rgba(102, 126, 234, 0.15) 0%, transparent 70%);
    border-radius: 50%;
    animation: bannerOrb2 30s ease-in-out infinite reverse;
  }

  @keyframes bannerOrb {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(-30px, 30px) scale(1.1); }
  }

  @keyframes bannerOrb2 {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(20px, -20px) scale(1.15); }
  }

  h1 {
    font-size: 30px;
    margin-bottom: 10px;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    position: relative;
    z-index: 1;
  }

  p {
    font-size: 16px;
    opacity: 0.95;
    position: relative;
    z-index: 1;
  }

  .today-date {
    text-align: center;
    background: rgba(255, 255, 255, 0.15);
    padding: 18px 28px;
    border-radius: 14px;
    backdrop-filter: blur(10px);
    position: relative;
    z-index: 1;

    .date-day {
      font-size: 40px;
      font-weight: 700;
      line-height: 1;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    .date-info {
      font-size: 14px;
      opacity: 0.9;
      margin-top: 6px;
    }
  }
}

.nurse-content {
  position: relative;
  z-index: 1;
}

.section-title {
  font-size: 19px;
  font-weight: 700;
  color: #333333;
  padding-left: 12px;
  border-left: 4px solid #409eff;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.task-list {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(64, 158, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);

  .task-item {
    display: flex;
    align-items: center;
    padding: 20px;
    background: rgba(248, 249, 250, 0.9);
    border: 1px solid rgba(64, 158, 255, 0.1);
    border-radius: 14px;
    margin-bottom: 14px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);

    &:last-child {
      margin-bottom: 0;
    }

    &:hover {
      background: rgba(233, 236, 239, 0.9);
      border-color: rgba(64, 158, 255, 0.3);
      transform: translateX(8px);
      box-shadow: 0 8px 24px rgba(64, 158, 255, 0.15);
    }

    &.completed {
      opacity: 0.5;

      .elder-name {
        text-decoration: line-through;
        color: #6c757d;
      }
    }

    .task-time {
      width: 85px;
      text-align: center;
      margin-right: 22px;
      flex-shrink: 0;

      .time {
        font-size: 20px;
        font-weight: 700;
        color: #409eff;
        display: block;
      }

      .duration {
        font-size: 12px;
        color: #6c757d;
      }
    }

    .task-info {
      flex: 1;

      .task-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;

        .elder-name {
          font-size: 17px;
          font-weight: 600;
          color: #333333;
        }
      }

      .task-address {
        font-size: 13px;
        color: #6c757d;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .task-notes {
        font-size: 13px;
        color: #6c757d;
      }
    }

    .task-actions {
      margin-left: 22px;
    }
  }
}

.side-section > div {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid rgba(64, 158, 255, 0.1);
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);

  &:hover {
    box-shadow: 0 12px 32px rgba(64, 158, 255, 0.1);
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 18px;

  .stat-item {
    text-align: center;
    padding: 18px;
    background: rgba(248, 249, 250, 0.9);
    border-radius: 12px;
    border: 1px solid rgba(64, 158, 255, 0.1);
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-4px);
      border-color: rgba(64, 158, 255, 0.3);
      box-shadow: 0 8px 20px rgba(64, 158, 255, 0.15);
    }

    .stat-value {
      font-size: 32px;
      font-weight: 700;
      color: #409eff;
      margin-bottom: 6px;
    }

    .stat-label {
      font-size: 13px;
      color: #6c757d;
      font-weight: 500;
    }
  }
}

.action-list {
  .action-item {
    display: flex;
    align-items: center;
    padding: 14px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
    background: rgba(248, 249, 250, 0.9);
    margin-bottom: 10px;
    border: 1px solid rgba(64, 158, 255, 0.1);

    .el-icon {
      font-size: 20px;
      color: #409eff;
      margin-right: 14px;
    }

    span {
      font-size: 15px;
      color: #333333;
    }

    &:hover {
      background: rgba(64, 158, 255, 0.05);
      border-color: rgba(64, 158, 255, 0.3);
      transform: translateX(8px);
    }
  }
}

// 服务老人列表
.elder-list {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid rgba(64, 158, 255, 0.1);
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);

  &:hover {
    box-shadow: 0 12px 32px rgba(64, 158, 255, 0.1);
  }

  .section-title {
    font-size: 19px;
    font-weight: 700;
    color: #333333;
    padding-left: 12px;
    border-left: 4px solid #409eff;
    margin-bottom: 18px;
  }

  .elder-items {
    .elder-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px;
      background: rgba(248, 249, 250, 0.9);
      border: 1px solid rgba(64, 158, 255, 0.1);
      border-radius: 12px;
      margin-bottom: 12px;
      transition: all 0.3s ease;

      &:hover {
        background: rgba(233, 236, 239, 0.9);
        border-color: rgba(64, 158, 255, 0.3);
        transform: translateX(8px);
        box-shadow: 0 8px 24px rgba(64, 158, 255, 0.15);
      }

      .elder-info {
        flex: 1;

        .elder-name {
          font-size: 16px;
          font-weight: 600;
          color: #333333;
          margin-bottom: 4px;
        }

        .elder-phone {
          font-size: 13px;
          color: #6c757d;
        }
      }
    }
  }
}

.new-orders-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(64, 158, 255, 0.2);

  .order-list {
    .order-item {
      display: flex;
      align-items: center;
      padding: 15px;
      background: rgba(245, 108, 108, 0.1);
      border: 1px solid rgba(245, 108, 108, 0.3);
      border-radius: 10px;
      margin-bottom: 10px;

      .order-info {
        flex: 1;
        .order-service {
          font-weight: 600;
          color: #fff;
          margin-right: 15px;
        }
        .order-elder {
          color: #9aafc0;
          font-size: 13px;
        }
      }

      .order-time {
        color: #f56c6c;
        font-size: 13px;
        margin-right: 15px;
      }
    }
  }
}
</style>