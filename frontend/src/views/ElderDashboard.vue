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
                <div class="action-btn evaluate" @click="showEvaluateDialog = true">
                  <el-icon :size="28"><Star /></el-icon>
                  <span>评价护工</span>
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

    <!-- 评价护工对话框 -->
    <el-dialog v-model="showEvaluateDialog" title="评价护工服务" width="600px">
      <el-form :model="evaluateForm" label-width="90px">
        <el-form-item label="选择护工">
          <el-select v-model="evaluateForm.worker_id" placeholder="请选择要评价的护工" style="width: 100%">
            <el-option
              v-for="worker in workerList"
              :key="worker.id"
              :label="worker.name"
              :value="worker.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="总体评分">
          <el-rate v-model="evaluateForm.overall_rating" show-text :texts="['很差', '较差', '一般', '满意', '非常满意']" />
        </el-form-item>

        <el-form-item label="专业程度">
          <el-rate v-model="evaluateForm.professionalism_rating" />
        </el-form-item>

        <el-form-item label="服务态度">
          <el-rate v-model="evaluateForm.attitude_rating" />
        </el-form-item>

        <el-form-item label="准时性">
          <el-rate v-model="evaluateForm.punctuality_rating" />
        </el-form-item>

        <el-form-item label="技能水平">
          <el-rate v-model="evaluateForm.skill_rating" />
        </el-form-item>

        <el-form-item label="评价内容">
          <el-input
            v-model="evaluateForm.content"
            type="textarea"
            :rows="3"
            placeholder="请分享您的服务体验..."
          />
        </el-form-item>

        <el-form-item label="评价标签">
          <el-checkbox-group v-model="evaluateForm.selectedTags">
            <el-checkbox label="专业">专业</el-checkbox>
            <el-checkbox label="耐心">耐心</el-checkbox>
            <el-checkbox label="细心">细心</el-checkbox>
            <el-checkbox label="热情">热情</el-checkbox>
            <el-checkbox label="准时">准时</el-checkbox>
            <el-checkbox label="负责">负责</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="匿名评价">
          <el-switch v-model="evaluateForm.isAnonymous" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEvaluateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitEvaluation" :loading="evaluating">提交评价</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'
import { useAuthStore } from '@/store/auth'

const emergencyDialog = ref(false)
const authStore = useAuthStore()

// 从用户信息中获取老人ID
const elderId = computed(() => {
  return authStore.userInfo?.id || null
})

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

// 评价护工
const showEvaluateDialog = ref(false)
const evaluating = ref(false)
const workerList = ref<any[]>([])
const evaluateForm = reactive({
  worker_id: null as number | null,
  overall_rating: 5,
  professionalism_rating: 5,
  attitude_rating: 5,
  punctuality_rating: 5,
  skill_rating: 5,
  content: '',
  selectedTags: [] as string[],
  isAnonymous: false
})

// 加载护工列表
const loadWorkerList = async () => {
  try {
    const res: any = await api.get('/users/workers')
    if (res.code === 200) {
      workerList.value = res.data || []
    }
  } catch (error) {
    console.error('获取护工列表失败', error)
  }
}

// 提交评价
const submitEvaluation = async () => {
  if (!elderId.value) {
    ElMessage.warning('未获取到用户信息')
    return
  }
  if (!evaluateForm.worker_id) {
    ElMessage.warning('请选择要评价的护工')
    return
  }

  evaluating.value = true
  try {
    const res: any = await api.post('/evaluations/worker', {
      elder_id: elderId.value,
      worker_id: evaluateForm.worker_id,
      overall_rating: evaluateForm.overall_rating,
      professionalism_rating: evaluateForm.professionalism_rating,
      attitude_rating: evaluateForm.attitude_rating,
      punctuality_rating: evaluateForm.punctuality_rating,
      skill_rating: evaluateForm.skill_rating,
      content: evaluateForm.content,
      tags: JSON.stringify(evaluateForm.selectedTags),
      is_anonymous: evaluateForm.isAnonymous ? 1 : 0
    })

    if (res.code === 200) {
      ElMessage.success('评价提交成功，感谢您的反馈！')
      showEvaluateDialog.value = false
      // 重置表单
      evaluateForm.worker_id = null
      evaluateForm.overall_rating = 5
      evaluateForm.professionalism_rating = 5
      evaluateForm.attitude_rating = 5
      evaluateForm.punctuality_rating = 5
      evaluateForm.skill_rating = 5
      evaluateForm.content = ''
      evaluateForm.selectedTags = []
      evaluateForm.isAnonymous = false
    } else {
      ElMessage.error(res.message || '评价提交失败')
    }
  } catch (error) {
    console.error('评价提交失败', error)
    ElMessage.error('评价提交失败，请稍后重试')
  } finally {
    evaluating.value = false
  }
}

const getHealthData = async () => {
  if (!elderId.value) return
  try {
    const res: any = await api.get(`/health/metrics/latest/${elderId.value}`)
    if (res.code === 200 && res.data) {
      healthData.heartRate = res.data.心率?.value || '--'
      healthData.bloodPressure = `${res.data['血压-收缩压']?.value || '--'}/${res.data['血压-舒张压']?.value || '--'}`
      healthData.sleepHours = res.data.睡眠时长?.value || '--'
      healthData.steps = res.data.今日步数?.value || '--'
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

onMounted(async () => {
  await authStore.getProfile()
  getHealthData()
  getTodayPlans()
  loadWorkerList()
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

      &.evaluate {
        background: linear-gradient(135deg, #909399, #c0c4cc);
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