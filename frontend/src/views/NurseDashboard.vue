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
.nurse-dashboard { padding: 20px; }

.role-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 16px;

  &.nurse {
    background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
    color: #fff;
  }

  .role-icon {
    font-size: 18px;
  }
}

.welcome-banner {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-radius: 16px;
  padding: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  color: #fff;
  h1 { font-size: 28px; margin-bottom: 8px; }
  p { font-size: 16px; opacity: 0.9; }
  .today-date {
    text-align: center;
    background: rgba(255,255,255,0.2);
    padding: 15px 25px;
    border-radius: 12px;
    .date-day { font-size: 36px; font-weight: 700; }
    .date-info { font-size: 14px; opacity: 0.8; }
  }
}
.section-title { font-size: 18px; font-weight: 600; color: #303133; padding-left: 10px; border-left: 4px solid #409eff; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.task-list {
  background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  .task-item {
    display: flex; align-items: center; padding: 20px; border-bottom: 1px solid #ebeef5;
    &.completed { opacity: 0.6; }
    .task-time { width: 80px; text-align: center; margin-right: 20px; .time { font-size: 18px; font-weight: 600; color: #409eff; display: block; } .duration { font-size: 12px; color: #909399; } }
    .task-info { flex: 1; .task-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; .elder-name { font-size: 16px; font-weight: 600; color: #303133; } } .task-address { font-size: 13px; color: #909399; margin-bottom: 4px; } .task-notes { font-size: 13px; color: #606266; } }
    .task-actions { margin-left: 20px; }
  }
}
.side-section > div { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; .stat-item { text-align: center; padding: 15px; background: #f5f7fa; border-radius: 8px; .stat-value { font-size: 28px; font-weight: 700; color: #409eff; margin-bottom: 4px; } .stat-label { font-size: 12px; color: #909399; } } }
.action-list { .action-item { display: flex; align-items: center; padding: 12px; border-radius: 8px; cursor: pointer; transition: all 0.3s; .el-icon { font-size: 18px; color: #409eff; margin-right: 12px; } span { font-size: 14px; color: #606266; } &:hover { background: #ecf5ff; } } }
</style>