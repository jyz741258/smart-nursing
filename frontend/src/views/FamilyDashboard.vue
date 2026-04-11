<template>
  <div class="family-dashboard">
    <div class="role-indicator family">
      <span class="role-icon">👨‍👩‍👧</span>
      <span class="role-text">老人家属</span>
    </div>

    <div class="welcome-banner">
      <div class="banner-content">
        <h1>您好，家人</h1>
        <p>您关心的老人健康状况一切正常</p>
      </div>
      <div class="elder-select">
        <el-select v-model="selectedElder" placeholder="选择老人" size="large">
          <el-option label="张三 (父亲)" value="1" />
        </el-select>
      </div>
    </div>

    <div class="family-content">
      <el-row :gutter="20">
        <el-col :span="16">
          <div class="main-section">
            <div class="section-header">
              <span class="section-title">{{ elderName }}的健康状况</span>
              <el-button type="primary" link @click="refreshData">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>

            <el-row :gutter="15" class="health-cards">
              <el-col :span="6">
                <div class="health-card heart">
                  <div class="card-icon"><el-icon><HeartFilled /></el-icon></div>
                  <div class="card-value">{{ healthData.heartRate }}</div>
                  <div class="card-label">心率 BPM</div>
                  <div class="card-status normal">正常</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="health-card blood">
                  <div class="card-icon"><el-icon><Sugar /></el-icon></div>
                  <div class="card-value">{{ healthData.bloodPressure }}</div>
                  <div class="card-label">血压 mmHg</div>
                  <div class="card-status" :class="healthData.bloodStatus">偏高</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="health-card sleep">
                  <div class="card-icon"><el-icon><Moon /></el-icon></div>
                  <div class="card-value">{{ healthData.sleepHours }}</div>
                  <div class="card-label">睡眠时长 h</div>
                  <div class="card-status normal">良好</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="health-card activity">
                  <div class="card-icon"><el-icon><Footprinter /></el-icon></div>
                  <div class="card-value">{{ healthData.steps }}</div>
                  <div class="card-label">今日步数</div>
                  <div class="card-status normal">达标</div>
                </div>
              </el-col>
            </el-row>

            <div class="section-header" style="margin-top: 30px">
              <span class="section-title">护理记录</span>
              <el-button type="primary" link @click="$router.push('/nursing')">查看全部</el-button>
            </div>
            <div class="nursing-records">
              <el-timeline>
                <el-timeline-item
                  v-for="record in nursingRecords"
                  :key="record.id"
                  :timestamp="record.time"
                  placement="top"
                  :color="record.color"
                >
                  <el-card>
                    <h4>{{ record.title }}</h4>
                    <p>{{ record.content }}</p>
                    <p class="record-nurse">护理人员：{{ record.nurse }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
          </div>
        </el-col>

        <el-col :span="8">
          <div class="side-section">
            <div class="care-plan">
              <div class="section-header">
                <span class="section-title">本周护理计划</span>
              </div>
              <div class="plan-list">
                <div v-for="plan in weeklyPlans" :key="plan.id" class="plan-item">
                  <div class="plan-date">
                    <span class="day">{{ plan.day }}</span>
                    <span class="week">{{ plan.week }}</span>
                  </div>
                  <div class="plan-info">
                    <div class="plan-name">{{ plan.name }}</div>
                    <div class="plan-time">{{ plan.time }} - {{ plan.nurse }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="alerts">
              <div class="section-header">
                <span class="section-title">异常提醒</span>
              </div>
              <div class="alert-list">
                <el-empty v-if="alerts.length === 0" description="暂无异常提醒" :image-size="60" />
                <div v-for="alert in alerts" :key="alert.id" class="alert-item" :class="alert.level">
                  <el-icon><Warning /></el-icon>
                  <div class="alert-content">
                    <div class="alert-text">{{ alert.content }}</div>
                    <div class="alert-time">{{ alert.time }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="quick-actions">
              <div class="section-header">
                <span class="section-title">快捷操作</span>
              </div>
              <div class="action-buttons">
                <el-button type="primary" @click="$router.push('/health')">
                  <el-icon><TrendCharts /></el-icon>
                  健康报告
                </el-button>
                <el-button type="success" @click="contactNurse">
                  <el-icon><Message /></el-icon>
                  联系护理员
                </el-button>
                <el-button type="warning" @click="$router.push('/notifications')">
                  <el-icon><Bell /></el-icon>
                  消息通知
                </el-button>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'

const selectedElder = ref('1')
const elderName = ref('张三')

const healthData = reactive({
  heartRate: '72',
  bloodPressure: '145/92',
  bloodStatus: 'warning',
  sleepHours: '7.5',
  steps: '3200'
})

const nursingRecords = ref([
  { id: 1, time: '今天 10:30', title: '日常护理服务', content: '协助进行日常清洁，照料起居', nurse: '李护理', color: '#67c23a' },
  { id: 2, time: '昨天 15:00', title: '健康监测', content: '血压偏高，已提醒按时服药', nurse: '王护理', color: '#409eff' },
  { id: 3, time: '昨天 09:00', title: '康复训练', content: '协助进行肢体康复训练30分钟', nurse: '李护理', color: '#67c23a' }
])

const weeklyPlans = ref([
  { id: 1, day: '11', week: '周六', name: '日常护理', time: '09:00-11:00', nurse: '李护理' },
  { id: 2, day: '12', week: '周日', name: '健康监测', time: '10:00-11:00', nurse: '王护理' },
  { id: 3, day: '13', week: '周一', name: '日常护理', time: '09:00-11:00', nurse: '李护理' }
])

const alerts = ref<any[]>([])

const getHealthData = async () => {
  try {
    const res: any = await api.get(`/health/metrics/latest/${selectedElder.value}`)
    if (res.code === 200 && res.data) {
      healthData.heartRate = res.data.心率?.value || '72'
      healthData.bloodPressure = `${res.data['血压-收缩压']?.value || '--'}/${res.data['血压-舒张压']?.value || '--'}`
      healthData.sleepHours = res.data.睡眠时长?.value || '7.5'
      healthData.steps = res.data.今日步数?.value || '3200'
    }
  } catch (error) {
    console.error('获取健康数据失败', error)
  }
}

const getNursingRecords = async () => {
  try {
    const res: any = await api.get(`/nursing/records?elder_id=${selectedElder.value}`)
    if (res.code === 200) {
      nursingRecords.value = res.data || []
    }
  } catch (error) {
    console.error('获取护理记录失败', error)
  }
}

const refreshData = () => {
  getHealthData()
  getNursingRecords()
  ElMessage.success('数据已刷新')
}

const contactNurse = () => {
  ElMessage.info('联系护理员功能开发中')
}

onMounted(() => {
  getHealthData()
  getNursingRecords()
})
</script>

<style scoped lang="scss">
.family-dashboard {
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

  &.family {
    background: linear-gradient(135deg, #f56c6c 0%, #fab6b6 100%);
    color: #fff;
  }

  .role-icon {
    font-size: 18px;
  }
}

.welcome-banner {
  background: linear-gradient(135deg, #f56c6c 0%, #fab6b6 100%);
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

  :deep(.el-input__wrapper) {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    box-shadow: none;
  }

  :deep(.el-input__inner) {
    color: #fff;

    &::placeholder {
      color: rgba(255, 255, 255, 0.8);
    }
  }

  :deep(.el-select__caret) {
    color: rgba(255, 255, 255, 0.8);
  }
}

.family-content {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    padding-left: 10px;
    border-left: 4px solid #f56c6c;
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
      font-size: 24px;
      font-weight: 700;
      color: #303133;
      margin-bottom: 4px;
    }

    .card-label {
      font-size: 13px;
      color: #909399;
    }

    .card-status {
      font-size: 12px;
      margin-top: 8px;
      padding: 2px 8px;
      border-radius: 10px;
      display: inline-block;

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

    &.heart .card-icon { background: linear-gradient(135deg, #f56c6c, #fab6b6); }
    &.blood .card-icon { background: linear-gradient(135deg, #e6a23c, #f3d19e); }
    &.sleep .card-icon { background: linear-gradient(135deg, #909399, #c0c4cc); }
    &.activity .card-icon { background: linear-gradient(135deg, #409eff, #66b1ff); }
  }
}

.nursing-records {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

  :deep(.el-card) {
    border: none;
    box-shadow: none;
    background: #fafafa;
  }

  h4 {
    font-size: 15px;
    color: #303133;
    margin-bottom: 8px;
  }

  p {
    font-size: 13px;
    color: #606266;
    margin-bottom: 4px;
  }

  .record-nurse {
    color: #909399;
  }
}

.side-section > div {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.plan-list {
  .plan-item {
    display: flex;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #ebeef5;

    &:last-child {
      border-bottom: none;
    }

    .plan-date {
      width: 50px;
      text-align: center;
      margin-right: 15px;

      .day {
        display: block;
        font-size: 20px;
        font-weight: 600;
        color: #f56c6c;
      }

      .week {
        font-size: 12px;
        color: #909399;
      }
    }

    .plan-info {
      flex: 1;

      .plan-name {
        font-size: 14px;
        color: #303133;
        margin-bottom: 4px;
      }

      .plan-time {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}

.alert-list {
  .alert-item {
    display: flex;
    align-items: flex-start;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 10px;
    background: #fdf6ec;

    &.danger {
      background: #fef0f0;
      color: #f56c6c;
    }

    .el-icon {
      margin-right: 10px;
      margin-top: 2px;
    }

    .alert-content {
      flex: 1;

      .alert-text {
        font-size: 13px;
        color: #303133;
        margin-bottom: 4px;
      }

      .alert-time {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}

.quick-actions {
  .action-buttons {
    display: flex;
    flex-direction: column;
    gap: 10px;

    :deep(.el-button) {
      width: 100%;
      justify-content: flex-start;
    }
  }
}
</style>