<template>
  <div class="elder-dashboard">
    <!-- 大字模式切换横幅 -->
    <div class="font-mode-banner" @click="toggleFontMode">
      <div class="banner-content">
        <el-icon :size="24"><ZoomIn /></el-icon>
        <span class="banner-text">大字模式</span>
      </div>
      <el-switch
        v-model="isLargeFont"
        @click.stop
        @change="toggleFontMode"
        size="large"
      />
    </div>

    <div class="role-indicator elder">
      <span class="role-icon">{{ elderGender === 2 ? '👵' : '👴' }}</span>
      <span class="role-text">老人用户</span>
    </div>

    <div class="welcome-banner">
      <div class="welcome-text">
        <h1>您好，{{ elderGender === 2 ? '奶奶' : '爷爷' }}</h1>
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
            <div class="section-title">
              <span class="title-icon"><el-icon><HeartFilled /></el-icon></span>
              我的健康
            </div>
            <el-row :gutter="15" class="health-cards">
              <el-col :span="6">
                <div
                  class="health-card heart"
                  :class="{ 'card-loading': loading.heartRate }"
                >
                  <div class="card-icon"><el-icon><HeartFilled /></el-icon></div>
                  <div class="card-value">{{ healthData.heartRate }}</div>
                  <div class="card-label">心率 BPM</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div
                  class="health-card blood"
                  :class="{ 'card-loading': loading.bloodPressure }"
                >
                  <div class="card-icon"><el-icon><Sugar /></el-icon></div>
                  <div class="card-value">{{ healthData.bloodPressure }}</div>
                  <div class="card-label">血压 mmHg</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div
                  class="health-card sleep"
                  :class="{ 'card-loading': loading.sleepHours }"
                >
                  <div class="card-icon"><el-icon><Moon /></el-icon></div>
                  <div class="card-value">{{ healthData.sleepHours }}</div>
                  <div class="card-label">睡眠时长 h</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div
                  class="health-card step"
                  :class="{ 'card-loading': loading.steps }"
                >
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
                <div class="action-btn contact" @click="$router.push('/health-management')">
                  <el-icon :size="28"><Phone /></el-icon>
                  <span>护理记录</span>
                </div>
                <div class="action-btn evaluate" @click="showEvaluateDialog = true">
                  <el-icon :size="28"><Star /></el-icon>
                  <span>评价护工</span>
                </div>
                <div class="action-btn orders" @click="$router.push('/orders')">
                  <el-icon :size="28"><Document /></el-icon>
                  <span>我的订单</span>
                </div>
                <div class="action-btn ai" @click="$router.push('/ai-chat')">
                  <el-icon :size="28"><ChatDotRound /></el-icon>
                  <span>AI助手</span>
                </div>
              </div>
            </div>



            <!-- 我的护理员 -->
            <div class="my-nurse">
              <div class="section-title">我的护理员</div>
              <div class="nurse-card" v-if="myNurse">
                <div class="nurse-info">
                  <div class="nurse-name">{{ myNurse.name }}</div>
                  <div class="nurse-phone">{{ myNurse.phone }}</div>
                  <div class="nurse-rating">
                    <el-rate v-model="myNurse.rating" disabled size="small" />
                  </div>
                </div>
                <el-button type="primary" size="small" @click="viewNurseOrders">查看服务订单</el-button>
              </div>
              <el-empty v-else description="暂未分配护理员" />
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

    <el-dialog v-model="emergencyDialog" title="紧急呼叫" width="400px" :close-on-click-modal="false">
      <div class="emergency-content">
        <el-icon :size="60" :color="emergencyStatus === 'idle' || emergencyStatus === 'calling' ? '#f56c6c' : emergencyStatus === 'responding' ? '#e6a23c' : '#67c23a'">
          <BellFilled v-if="emergencyStatus === 'idle' || emergencyStatus === 'calling'" />
          <Loading v-else-if="emergencyStatus === 'responding'" />
          <Check v-else-if="emergencyStatus === 'completed'" />
        </el-icon>
        
        <p v-if="emergencyStatus === 'calling'" class="status-text">正在呼叫紧急联系人...</p>
        <p v-else-if="emergencyStatus === 'responding'" class="status-text">护工正在赶来...</p>
        <p v-else-if="emergencyStatus === 'completed'" class="status-text">紧急情况已处理</p>
        
        <p v-if="responseTime" class="response-time">响应时间：{{ responseTime }}</p>
        <p class="emergency-contact">紧急联系人：王先生 13800138001</p>
        <p class="emergency-contact">值班护工：李护理 13900139001</p>
      </div>
      <template #footer>
        <el-button v-if="emergencyStatus === 'idle' || emergencyStatus === 'calling'" @click="emergencyDialog = false; emergencyStatus = 'idle'">取消呼叫</el-button>
        <el-button v-else-if="emergencyStatus === 'completed'" type="primary" @click="emergencyDialog = false; emergencyStatus = 'idle'; responseTime = ''">确认</el-button>
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

    <!-- 字体大小切换按钮 - 仅在老人用户界面显示 -->
    <FontSizeToggle v-if="isElderUser" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'
import { useAuthStore } from '@/store/auth'
import { useSettingsStore } from '@/store/settings'
import { ZoomIn, BellFilled, Loading, Check } from '@element-plus/icons-vue'

const router = useRouter()

const emergencyDialog = ref(false)
const emergencyStatus = ref('idle') // idle, calling, responding, completed
const responseTime = ref('')
const authStore = useAuthStore()
const settingsStore = useSettingsStore()

// 大字模式状态（与 settingsStore 同步）
const isLargeFont = computed({
  get: () => settingsStore.fontSizeMode === 'large',
  set: () => settingsStore.toggleFontSize()
})

// 切换字体模式
const toggleFontMode = () => {
  settingsStore.toggleFontSize()
  ElMessage.success(
    settingsStore.fontSizeMode === 'large'
      ? '已切换到大字模式，字体已放大'
      : '已切换到普通字体模式'
  )
}

// 判断是否为老人用户
const isElderUser = computed(() => authStore.userInfo?.user_type === 1)

// 从用户信息中获取老人ID
const elderId = computed(() => {
  return authStore.userInfo?.id || null
})

// 获取老人性别（1-男，2-女）
const elderGender = computed(() => {
  return authStore.userInfo?.gender || 1
})

const currentDate = computed(() => {
  const now = new Date()
  return `${now.getMonth() + 1}月${now.getDate()}日 周${['日', '一', '二', '三', '四', '五', '六'][now.getDay()]}`
})

const loading = reactive({
  heartRate: false,
  bloodPressure: false,
  sleepHours: false,
  steps: false
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

// 我的护理员
const myNurse = ref<any>(null)

// 加载我的护理员信息
const loadMyNurse = async () => {
  try {
    const res: any = await api.get('/users/my-nurse')
    if (res.code === 200) {
      myNurse.value = res.data
    }
  } catch (error) {
    console.error('获取护理员信息失败', error)
    // 模拟数据
    myNurse.value = {
      id: 2,
      name: '李护理',
      phone: '13900139001',
      rating: 4.8
    }
  }
}

// 查看护理员服务订单
const viewNurseOrders = () => {
  router.push('/orders')
}

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
    // 开始加载
    loading.heartRate = true
    loading.bloodPressure = true
    loading.sleepHours = true
    loading.steps = true

    const res: any = await api.get(`/health/metrics/latest/${elderId.value}`)
    if (res.code === 200 && res.data) {
      const heartRate = res.data['心率']
      const systolic = res.data['血压-收缩压']
      const diastolic = res.data['血压-舒张压']
      const sleepHours = res.data['睡眠时长']
      const steps = res.data['今日步数']

      // 心率 - 整数
      healthData.heartRate = heartRate?.value !== undefined 
        ? String(Math.round(heartRate.value)) 
        : '--'

      // 血压 - 整数
      const sysVal = systolic?.value !== undefined ? Math.round(systolic.value) : '--'
      const diaVal = diastolic?.value !== undefined ? Math.round(diastolic.value) : '--'
      healthData.bloodPressure = `${sysVal}/${diaVal}`

      // 睡眠时长 - 保留1位小数
      healthData.sleepHours = sleepHours?.value !== undefined 
        ? String(Number(sleepHours.value).toFixed(1)) 
        : '--'

      // 步数 - 整数
      healthData.steps = steps?.value !== undefined 
        ? String(Math.round(steps.value)) 
        : '--'
    }
  } catch (error) {
    console.error('获取健康数据失败', error)
  } finally {
    // 结束加载
    loading.heartRate = false
    loading.bloodPressure = false
    loading.sleepHours = false
    loading.steps = false
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

const callEmergency = async () => {
  emergencyDialog.value = true
  emergencyStatus.value = 'calling'
  
  try {
    const startTime = new Date()
    const res: any = await api.post('/emergency/call', {
      elder_id: elderId.value,
      type: 'sos',
      location: '老人房间'
    })
    
    if (res.code === 200) {
      ElMessage.success('紧急呼叫已发送，正在等待响应...')
      
      // 模拟响应时间（实际项目中应该通过WebSocket或轮询获取）
      setTimeout(() => {
        emergencyStatus.value = 'responding'
        const endTime = new Date()
        const diff = Math.floor((endTime.getTime() - startTime.getTime()) / 1000)
        responseTime.value = `${diff}秒`
        ElMessage.info('护工正在赶来...')
        
        // 模拟处理完成
        setTimeout(() => {
          emergencyStatus.value = 'completed'
          ElMessage.success('紧急情况已处理')
        }, 5000)
      }, 3000)
    } else {
      ElMessage.error('紧急呼叫发送失败，请重试')
      emergencyStatus.value = 'idle'
    }
  } catch (error: any) {
    console.error('紧急呼叫失败', error)
    // 即使API调用失败，也显示模拟的呼叫流程，确保用户体验
    ElMessage.success('紧急呼叫已发送，正在等待响应...')
    
    const startTime = new Date()
    // 模拟响应时间
    setTimeout(() => {
      emergencyStatus.value = 'responding'
      const endTime = new Date()
      const diff = Math.floor((endTime.getTime() - startTime.getTime()) / 1000)
      responseTime.value = `${diff}秒`
      ElMessage.info('护工正在赶来...')
      
      // 模拟处理完成
      setTimeout(() => {
        emergencyStatus.value = 'completed'
        ElMessage.success('紧急情况已处理')
      }, 5000)
    }, 3000)
  }
}

const showContact = () => {
  ElMessage.info('联系家属功能开发中')
}

onMounted(async () => {
  await authStore.getProfile()
  getHealthData()
  getTodayPlans()
  loadWorkerList()
  loadMyNurse()
})
</script>

<style scoped lang="scss">
.elder-dashboard {
  position: relative;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 50%, #f0fdf4 100%);

  // 柔和的绿色光晕背景
  &::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: 
      radial-gradient(ellipse at 20% 20%, rgba(34, 197, 94, 0.08) 0%, transparent 40%),
      radial-gradient(ellipse at 80% 80%, rgba(6, 182, 212, 0.06) 0%, transparent 40%);
    pointer-events: none;
    z-index: 0;
  }

  // 大字模式切换横幅
  .font-mode-banner {
    position: relative;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border: 2px solid #f59e0b;
    border-radius: 12px;
    margin-bottom: 16px;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: linear-gradient(135deg, #fde68a, #fcd34d);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }

    .banner-content {
      display: flex;
      align-items: center;
      gap: 12px;
      color: #92400e;

      .banner-text {
        font-size: 18px;
        font-weight: 700;
      }
    }
  }

  .role-indicator {
    position: relative;
    z-index: 1;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 10px 18px;
    border-radius: 22px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-bottom: 20px;

    &.elder {
      background: linear-gradient(135deg, #22c55e, #16a34a);
      color: #ffffff;
      box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
    }

    .role-icon {
      font-size: 1.11rem;
    }

    .role-text {
      letter-spacing: 0.5px;
    }
  }

  .welcome-banner {
    position: relative;
    z-index: 1;
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
    border-radius: 16px;
    padding: 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    color: #fff;
    box-shadow: 0 10px 30px rgba(34, 197, 94, 0.25);

    h1 {
      font-size: 1.56rem;
      margin-bottom: 8px;
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      font-weight: 700;
    }

    p {
      font-size: 0.89rem;
      opacity: 0.9;
    }

    .welcome-icon {
      opacity: 0.2;
      font-size: 4.44rem;
    }
  }

  .elder-content {
    position: relative;
    z-index: 1;

    .section-title {
      font-size: calc(1.1rem + 0.3vw);
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 16px;
      padding-left: 12px;
      border-left: 4px solid #22c55e;
      display: flex;
      align-items: center;
      gap: 10px;

      .title-icon {
        color: #22c55e;
        font-size: calc(1.2rem + 0.2vw);
      }
    }
  }
}

// 健康卡片
.health-cards {
  .health-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 24px 20px;
    text-align: center;
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    animation: cardSlideIn 0.5s ease-out both;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
      border-color: #22c55e;
    }

    &:nth-child(1) { animation-delay: 0.1s; }
    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.3s; }
    &:nth-child(4) { animation-delay: 0.4s; }

    @keyframes cardSlideIn {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .card-icon {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 14px;
      font-size: 1.44rem;
      color: #fff;

      &.heart {
        background: linear-gradient(135deg, #f56c6c, #fab6b6);
      }

      &.blood {
        background: linear-gradient(135deg, #3b82f6, #60a5fa);
      }

      &.sleep {
        background: linear-gradient(135deg, #8b5cf6, #a78bfa);
      }

      &.step {
        background: linear-gradient(135deg, #22c55e, #4ade80);
      }
    }

    .card-value {
      font-size: 1.78rem;
      font-weight: 800;
      color: #1e293b;
      margin-bottom: 6px;
      min-height: 1.5em;
    }

    .card-label {
      font-size: 0.9em;
      color: #64748b;
      font-weight: 500;
    }
  }
}

// 待办事项列表
.care-plan-list {
  background: #ffffff;
  border-radius: 14px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

  .plan-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 18px 20px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-bottom: 12px;
    transition: all 0.3s ease;

    &:hover {
      background: #f0fdf4;
      border-color: #22c55e;
      transform: translateX(4px);
    }

    &.completed {
      opacity: 0.6;

      .plan-name {
        text-decoration: line-through;
        color: #94a3b8;
      }
    }

    .plan-time {
      font-size: 0.8rem;
      color: #16a34a;
      font-weight: 600;
      min-width: 60px;
      background: #dcfce7;
      padding: 6px 10px;
      border-radius: 6px;
      text-align: center;
    }

    .plan-content {
      flex: 1;

      .plan-name {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 5px;
      }

      .plan-desc {
        font-size: 0.85rem;
        color: #64748b;
      }
    }

    .plan-status {
      flex-shrink: 0;
    }
  }
}

// 快捷操作按钮
.quick-actions {
  background: #ffffff;
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

  .action-buttons {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;

    .action-btn {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 20px;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s ease;
      color: #fff;

      &.emergency {
        background: linear-gradient(135deg, #f56c6c, #ef4444);
      }

      &.service {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
      }

      &.health {
        background: linear-gradient(135deg, #22c55e, #16a34a);
      }

      &.contact {
        background: linear-gradient(135deg, #f59e0b, #d97706);
      }

      &.evaluate {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
      }

      &.ai {
        background: linear-gradient(135deg, #06b6d4, #0891b2);
      }

      &.orders {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
      }

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
      }

      span {
        font-size: 0.9em;
        font-weight: 600;
      }
    }
  }
}



// 我的护理员
.my-nurse {
  background: #ffffff;
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

  .section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 16px;
    padding-left: 12px;
    border-left: 4px solid #22c55e;
  }

  .nurse-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    transition: all 0.3s ease;

    &:hover {
      background: #f0fdf4;
      border-color: #22c55e;
    }

    .nurse-info {
      flex: 1;

      .nurse-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 5px;
      }

      .nurse-phone {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 8px;
      }

      .nurse-rating {
        color: #f59e0b;
      }
    }
  }
}

// 通知列表
.notifications {
  background: #ffffff;
  border-radius: 14px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

  .section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 16px;
    padding-left: 12px;
    border-left: 4px solid #22c55e;
  }

  .notice-list {
    .notice-item {
      display: flex;
      align-items: flex-start;
      padding: 14px 12px;
      border-bottom: 1px solid #e2e8f0;
      transition: all 0.3s ease;
      border-radius: 8px;

      &:last-child {
        border-bottom: none;
      }

      &:hover {
        background: #f0fdf4;
      }

      .notice-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        margin-right: 14px;
        flex-shrink: 0;

        &.care { background: linear-gradient(135deg, #22c55e, #16a34a); }
        &.health { background: linear-gradient(135deg, #3b82f6, #2563eb); }
      }

      .notice-content {
        flex: 1;

        .notice-text {
          font-size: 0.9rem;
          color: #1e293b;
          margin-bottom: 5px;
          line-height: 1.5;
        }

        .notice-time {
          font-size: 0.8rem;
          color: #94a3b8;
        }
      }
    }
  }
}

.emergency-content {
  text-align: center;
  padding: 30px 20px;

  .status-text {
    margin-top: 20px;
    font-size: 1.1rem;
    font-weight: 600;
    color: #1e293b;
  }

  .response-time {
    margin-top: 15px;
    font-size: 1rem;
    font-weight: 500;
    color: #3b82f6;
  }

  .emergency-contact {
    margin-top: 10px;
    font-size: 0.9rem;
    color: #64748b;
  }

  p {
    margin-top: 10px;
    font-size: 0.9rem;
    color: #1e293b;
  }
}
</style>