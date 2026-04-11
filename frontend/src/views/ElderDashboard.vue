<template>
  <div class="elder-dashboard">
    <div class="role-indicator elder">
      <span class="role-icon">👴</span>
      <span class="role-text">老人用户</span>
    </div>

    <div class="welcome-banner">
      <div class="welcome-text">
        <h1>您好，爷爷/奶奶</h1>
        <p>今天是 {{ currentDate }}，愿您身体健康，生活愉快</p>
      </div>
      <div class="welcome-icon">
        <el-icon :size="60"><Sunny /></el-icon>
      </div>
    </div>

    <div class="elder-content">
      <el-row :gutter="20">
        <el-col :span="16">
          <div class="main-section">
            <div class="section-title">我的健康</div>
            <el-row :gutter="15" class="health-cards">
              <el-col :span="6">
                <div class="health-card heart">
                  <div class="card-icon"><el-icon><HeartFilled /></el-icon></div>
                  <div class="card-value">{{ healthData.heartRate }}</div>
                  <div class="card-label">心率 BPM</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="health-card blood">
                  <div class="card-icon"><el-icon><Sugar /></el-icon></div>
                  <div class="card-value">{{ healthData.bloodPressure }}</div>
                  <div class="card-label">血压 mmHg</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="health-card sleep">
                  <div class="card-icon"><el-icon><Moon /></el-icon></div>
                  <div class="card-value">{{ healthData.sleepHours }}</div>
                  <div class="card-label">睡眠时长 h</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="health-card step">
                  <div class="card-icon"><el-icon><Footprinter /></el-icon></div>
                  <div class="card-value">{{ healthData.steps }}</div>
                  <div class="card-label">今日步数</div>
                </div>
              </el-col>
            </el-row>

            <div class="section-title" style="margin-top: 30px">今日待办</div>
            <div class="care-plan-list">
              <div
                v-for="plan in todayPlans"
                :key="plan.id"
                class="plan-item"
                :class="{ completed: plan.status === 2 }"
              >
                <div class="plan-time">{{ plan.time }}</div>
                <div class="plan-content">
                  <div class="plan-name">{{ plan.name }}</div>
                  <div class="plan-desc">{{ plan.description }}</div>
                </div>
                <div class="plan-status">
                  <el-tag v-if="plan.status === 1" type="warning" size="small">待执行</el-tag>
                  <el-tag v-else-if="plan.status === 2" type="success" size="small">已完成</el-tag>
                </div>
              </div>
              <el-empty v-if="todayPlans.length === 0" description="今日暂无待办" />
            </div>
          </div>
        </el-col>

        <el-col :span="8">
          <div class="side-section">
            <div class="quick-actions">
              <div class="section-title">快捷服务</div>
              <div class="action-buttons">
                <div class="action-btn emergency" @click="callEmergency">
                  <el-icon :size="28"><Bell /></el-icon>
                  <span>紧急呼叫</span>
                </div>
                <div class="action-btn service" @click="$router.push('/notifications')">
                  <el-icon :size="28"><Calendar /></el-icon>
                  <span>消息通知</span>
                </div>
                <div class="action-btn health" @click="$router.push('/health')">
                  <el-icon :size="28"><TrendCharts /></el-icon>
                  <span>健康数据</span>
                </div>
                <div class="action-btn contact" @click="$router.push('/health')">
                  <el-icon :size="28"><Phone /></el-icon>
                  <span>护理记录</span>
                </div>
              </div>
            </div>

            <div class="notifications">
              <div class="section-title">最新通知</div>
              <div class="notice-list">
                <div v-for="notice in notices" :key="notice.id" class="notice-item">
                  <div class="notice-icon" :class="notice.type">
                    <el-icon v-if="notice.type === 'care'"><FirstAidKit /></el-icon>
                    <el-icon v-else-if="notice.type === 'health'"><TrendCharts /></el-icon>
                    <el-icon v-else><Bell /></el-icon>
                  </div>
                  <div class="notice-content">
                    <div class="notice-text">{{ notice.content }}</div>
                    <div class="notice-time">{{ notice.time }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="emergencyDialog" title="紧急呼叫" width="400px">
      <div class="emergency-content">
        <el-icon :size="60" color="#f56c6c"><BellFilled /></el-icon>
        <p>正在呼叫紧急联系人...</p>
        <p class="emergency-contact">紧急联系人：王先生 13800138001</p>
      </div>
      <template #footer>
        <el-button @click="emergencyDialog = false">取消呼叫</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'

const emergencyDialog = ref(false)

const currentDate = computed(() => {
  const now = new Date()
  return `${now.getMonth() + 1}月${now.getDate()}日 周${['日', '一', '二', '三', '四', '五', '六'][now.getDay()]}`
})

const healthData = reactive({
  heartRate: '--',
  bloodPressure: '--/--',
  sleepHours: '--',
  steps: '--'
})

const todayPlans = ref<any[]>([])

const notices = ref([
  { id: 1, type: 'care', content: '李护理师将于明日上午10点上门服务', time: '刚刚' },
  { id: 2, type: 'health', content: '您的血压记录已更新，请查看', time: '2小时前' },
  { id: 3, type: 'system', content: '系统升级通知', time: '昨天' }
])

const getHealthData = async () => {
  try {
    const res: any = await api.get('/health/latest')
    if (res.code === 200 && res.data) {
      healthData.heartRate = res.data.heart_rate || '--'
      healthData.bloodPressure = `${res.data.blood_pressure_high || '--'}/${res.data.blood_pressure_low || '--'}`
      healthData.sleepHours = res.data.sleep_hours || '--'
      healthData.steps = res.data.steps || '--'
    }
  } catch (error) {
    console.error('获取健康数据失败', error)
  }
}

const getTodayPlans = async () => {
  try {
    const res: any = await api.get('/care/plans/today')
    if (res.code === 200) {
      todayPlans.value = res.data || []
    }
  } catch (error) {
    console.error('获取护理计划失败', error)
  }
}

const callEmergency = () => {
  emergencyDialog.value = true
}

const showContact = () => {
  ElMessage.info('联系家属功能开发中')
}

onMounted(() => {
  getHealthData()
  getTodayPlans()
})
</script>

<style scoped lang="scss">
.elder-dashboard {
  padding: 20px;
}

.role-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 16px;

  &.elder {
    background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
    color: #fff;
  }

  .role-icon {
    font-size: 18px;
  }
}

.welcome-banner {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  border-radius: 16px;
  padding: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  color: #fff;

  h1 {
    font-size: 28px;
    margin-bottom: 8px;
  }

  p {
    font-size: 16px;
    opacity: 0.9;
  }

  .welcome-icon {
    opacity: 0.3;
  }
}

.elder-content {
  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 16px;
    padding-left: 10px;
    border-left: 4px solid #67c23a;
  }
}

.health-cards {
  .health-card {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

    .card-icon {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 12px;
      font-size: 24px;
      color: #fff;
    }

    .card-value {
      font-size: 28px;
      font-weight: 700;
      color: #303133;
      margin-bottom: 4px;
    }

    .card-label {
      font-size: 13px;
      color: #909399;
    }

    &.heart .card-icon { background: linear-gradient(135deg, #f56c6c, #fab6b6); }
    &.blood .card-icon { background: linear-gradient(135deg, #e6a23c, #f3d19e); }
    &.sleep .card-icon { background: linear-gradient(135deg, #909399, #c0c4cc); }
    &.step .card-icon { background: linear-gradient(135deg, #409eff, #66b1ff); }
  }
}

.care-plan-list {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

  .plan-item {
    display: flex;
    align-items: center;
    padding: 15px;
    border-bottom: 1px solid #ebeef5;

    &:last-child {
      border-bottom: none;
    }

    &.completed {
      opacity: 0.6;

      .plan-name {
        text-decoration: line-through;
      }
    }

    .plan-time {
      width: 60px;
      font-size: 14px;
      color: #67c23a;
      font-weight: 500;
    }

    .plan-content {
      flex: 1;
      padding: 0 15px;

      .plan-name {
        font-size: 15px;
        color: #303133;
        margin-bottom: 4px;
      }

      .plan-desc {
        font-size: 13px;
        color: #909399;
      }
    }
  }
}

.quick-actions {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

  .action-buttons {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;

    .action-btn {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s;
      color: #fff;

      span {
        margin-top: 8px;
        font-size: 13px;
      }

      &.emergency {
        background: linear-gradient(135deg, #f56c6c, #fab6b6);
      }

      &.service {
        background: linear-gradient(135deg, #409eff, #66b1ff);
      }

      &.health {
        background: linear-gradient(135deg, #67c23a, #85ce61);
      }

      &.contact {
        background: linear-gradient(135deg, #e6a23c, #f3d19e);
      }

      &:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
      }
    }
  }
}

.notifications {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

  .notice-list {
    .notice-item {
      display: flex;
      align-items: flex-start;
      padding: 12px 0;
      border-bottom: 1px solid #ebeef5;

      &:last-child {
        border-bottom: none;
      }

      .notice-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        margin-right: 12px;
        background: #909399;

        &.care { background: #67c23a; }
        &.health { background: #409eff; }
      }

      .notice-content {
        flex: 1;

        .notice-text {
          font-size: 14px;
          color: #303133;
          margin-bottom: 4px;
        }

        .notice-time {
          font-size: 12px;
          color: #c0c4cc;
        }
      }
    }
  }
}

.emergency-content {
  text-align: center;
  padding: 20px;

  p {
    margin-top: 15px;
    font-size: 16px;
  }

  .emergency-contact {
    font-size: 14px;
    color: #909399;
  }
}
</style>