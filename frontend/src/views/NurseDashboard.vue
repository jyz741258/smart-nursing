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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'

const taskDialog = ref(false)
const currentTask = ref<any>(null)
const taskForm = reactive({ content: '', status: '2' })

const currentDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
})

const currentDay = computed(() => String(new Date().getDate()).padStart(2, '0'))
const completedCount = ref(3)
const pendingCount = ref(5)
const stats = reactive({ completed: 3, pending: 5, totalHours: 12, rating: 4.8 })

const todayTasks = ref([
  { id: 1, time: '09:00', duration: 60, elderName: '张三', address: '朝阳区建国路88号', notes: '日常清洁护理', type: 1, status: 2 },
  { id: 2, time: '10:30', duration: 30, elderName: '李四', address: '海淀区中关村大街1号', notes: '血压监测', type: 4, status: 1 },
  { id: 3, time: '14:00', duration: 45, elderName: '王五', address: '西城区金融街8号', notes: '服药提醒', type: 4, status: 1 }
])

const getTypeName = (type: number) => ({ 1: '日常照护', 2: '医疗护理', 3: '康复训练', 4: '健康监测' }[type] || '其他')
const getTypeColor = (type: number) => ({ 1: 'success', 2: 'primary', 3: 'warning', 4: 'info' }[type] || 'info')

const startTask = (task: any) => {
  currentTask.value = task
  taskForm.content = task.notes
  taskForm.status = '2'
  taskDialog.value = true
}

const completeTask = async () => {
  ElMessage.success('任务已完成')
  taskDialog.value = false
}

const syncHealth = () => ElMessage.success('健康数据同步成功')

onMounted(() => {})
</script>

<style scoped lang="scss">
.nurse-dashboard {
  position: relative;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #0a0e14 0%, #12151c 50%, #0d1117 100%);

  // 多层动态背景效果
  &::before {
    content: '';
    position: fixed;
    top: -100%;
    left: -100%;
    width: 300%;
    height: 300%;
    background: 
      radial-gradient(ellipse at 20% 20%, rgba(64, 158, 255, 0.12) 0%, transparent 40%),
      radial-gradient(ellipse at 80% 80%, rgba(102, 126, 234, 0.08) 0%, transparent 40%),
      radial-gradient(ellipse at 50% 50%, rgba(64, 158, 255, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 10% 90%, rgba(102, 126, 234, 0.05) 0%, transparent 30%),
      radial-gradient(circle at 90% 10%, rgba(64, 158, 255, 0.05) 0%, transparent 30%);
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
      linear-gradient(rgba(64, 158, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(64, 158, 255, 0.03) 1px, transparent 1px);
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
  color: #ffffff;
  padding-left: 12px;
  border-left: 4px solid #409eff;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.task-list {
  background: rgba(40, 50, 60, 0.95);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(64, 158, 255, 0.2);

  .task-item {
    display: flex;
    align-items: center;
    padding: 20px;
    background: rgba(30, 40, 50, 0.9);
    border: 1px solid rgba(64, 158, 255, 0.15);
    border-radius: 14px;
    margin-bottom: 14px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);

    &:last-child {
      margin-bottom: 0;
    }

    &:hover {
      background: rgba(50, 60, 70, 0.95);
      border-color: rgba(64, 158, 255, 0.4);
      transform: translateX(8px);
      box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
    }

    &.completed {
      opacity: 0.5;

      .elder-name {
        text-decoration: line-through;
        color: #7a9ab5;
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
        text-shadow: 0 0 8px rgba(64, 158, 255, 0.3);
      }

      .duration {
        font-size: 12px;
        color: #7a9ab5;
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
          color: #e8eef5;
        }
      }

      .task-address {
        font-size: 13px;
        color: #9aafc0;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .task-notes {
        font-size: 13px;
        color: #7a9ab5;
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
  background: rgba(40, 50, 60, 0.95);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid rgba(64, 158, 255, 0.2);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 12px 32px rgba(64, 158, 255, 0.15);
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
    background: rgba(30, 40, 50, 0.9);
    border-radius: 12px;
    border: 1px solid rgba(64, 158, 255, 0.15);
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-4px);
      border-color: rgba(64, 158, 255, 0.4);
      box-shadow: 0 8px 20px rgba(64, 158, 255, 0.2);
    }

    .stat-value {
      font-size: 32px;
      font-weight: 700;
      color: #409eff;
      margin-bottom: 6px;
      text-shadow: 0 0 10px rgba(64, 158, 255, 0.3);
    }

    .stat-label {
      font-size: 13px;
      color: #9aafc0;
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
    background: rgba(30, 40, 50, 0.9);
    margin-bottom: 10px;
    border: 1px solid rgba(64, 158, 255, 0.15);

    .el-icon {
      font-size: 20px;
      color: #409eff;
      margin-right: 14px;
    }

    span {
      font-size: 15px;
      color: #e8eef5;
    }

    &:hover {
      background: rgba(64, 158, 255, 0.15);
      border-color: rgba(64, 158, 255, 0.4);
      transform: translateX(8px);
    }
  }
}
</style>