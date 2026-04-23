<template>
  <div class="family-dashboard">
    <div class="role-indicator family">
      <span class="role-icon">👨‍👩‍👧</span>
      <span class="role-text">老人家属</span>
    </div>

    <div class="welcome-banner">
      <div class="banner-content">
        <h1>您好，{{ familyName }}</h1>
        <p v-if="bindingElder">您关心的 {{ bindingElder.name }} 健康状况一切正常</p>
        <p v-else>请先绑定要关心的老人</p>
      </div>
      <div class="elder-select" v-if="!bindingElder">
        <el-button type="primary" size="large" @click="showBindDialog = true">
          绑定老人
        </el-button>
      </div>
    </div>

    <!-- 未绑定时显示绑定引导 -->
    <div v-if="!bindingElder" class="bind-guide">
      <el-empty description="您还没有绑定老人" :image-size="100">
        <el-button type="primary" @click="showBindDialog = true">
          立即绑定
        </el-button>
      </el-empty>
    </div>

    <div v-else class="family-content">
      <el-row :gutter="20">
        <el-col :span="16">
          <div class="main-section">
            <div class="section-header">
              <span class="section-title">{{ bindingElder.name }}的健康状况</span>
              <div class="header-actions">
                <el-button type="danger" size="small" link @click="unbindElder">解除绑定</el-button>
                <el-button type="primary" link @click="refreshData">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
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
                <el-button type="danger" @click="showEvaluateDialog = true">
                  <el-icon><Star /></el-icon>
                  评价护工
                </el-button>
                <el-button type="info" @click="$router.push('/ai-chat')">
                  <el-icon><ChatDotRound /></el-icon>
                  AI助手
                </el-button>
                <el-button type="primary" @click="$router.push('/orders')">
                  <el-icon><ShoppingCart /></el-icon>
                  我的订单
                </el-button>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 绑定老人对话框 -->
    <el-dialog v-model="showBindDialog" title="绑定老人" width="500px">
      <el-form :model="bindForm" label-width="80px">
        <el-form-item label="选择老人">
          <el-select v-model="bindForm.elder_id" placeholder="请选择老人" style="width: 100%">
            <el-option
              v-for="elder in elderList"
              :key="elder.id"
              :label="`${elder.name} ${elder.age ? '(' + elder.age + '岁)' : ''}`"
              :value="elder.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="老人账号">
          <el-input v-model="bindForm.username" placeholder="请输入老人的账号" />
        </el-form-item>
        <el-form-item label="老人密码">
          <el-input v-model="bindForm.password" type="password" placeholder="请输入老人的密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBindDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmBind" :loading="binding">确定绑定</el-button>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/store/auth'
import type { Elder } from '@/types'

// 家属名称
const familyName = computed(() => {
  const info = localStorage.getItem('userInfo')
  return info ? JSON.parse(info).name || '家人' : '家人'
})

// 绑定的老人信息
const bindingElder = ref<Elder | null>(null)
const selectedElderId = ref<number | null>(null)

// 老人列表
const elderList = ref<Elder[]>([])

// 绑定对话框
const showBindDialog = ref(false)
const binding = ref(false)
const bindForm = reactive({
  elder_id: null as number | null,
  username: '',
  password: ''
})

const healthData = reactive({
  heartRate: '--',
  bloodPressure: '--/--',
  bloodStatus: 'normal',
  sleepHours: '--',
  steps: '--'
})

const nursingRecords = ref<any[]>([])

const weeklyPlans = ref([
  { id: 1, day: '11', week: '周六', name: '日常护理', time: '09:00-11:00', nurse: '李护理' },
  { id: 2, day: '12', week: '周日', name: '健康监测', time: '10:00-11:00', nurse: '王护理' },
  { id: 3, day: '13', week: '周一', name: '日常护理', time: '09:00-11:00', nurse: '李护理' }
])

const alerts = ref<any[]>([])

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
  if (!bindingElder.value) {
    ElMessage.warning('请先绑定老人')
    return
  }
  if (!evaluateForm.worker_id) {
    ElMessage.warning('请选择要评价的护工')
    return
  }

  evaluating.value = true
  try {
    const res: any = await api.post('/evaluations/worker', {
      elder_id: bindingElder.value.id,
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

// 加载绑定的老人信息
const loadBindingElder = async () => {
  console.log('开始加载绑定老人信息...')
  try {
    const res: any = await api.get('/users/binding-elder')
    console.log('绑定老人API响应:', res)

    if (res.code === 200) {
      bindingElder.value = res.data
      if (res.data) {
        selectedElderId.value = res.data.id
        console.log('已绑定老人信息:', res.data)
      } else {
        console.log('当前用户未绑定任何老人')
      }
    } else {
      console.error('获取绑定老人信息失败:', res.message)
    }
  } catch (error: any) {
    console.error('获取绑定老人信息失败', error)
    if (error.response) {
      console.error('错误状态码:', error.response.status)
      console.error('错误数据:', error.response.data)
    }
  }
}

// 加载老人列表
const loadElderList = async () => {
  try {
    const res: any = await api.get('/users/elder/list')
    if (res.code === 200) {
      elderList.value = res.data
    }
  } catch (error) {
    console.error('获取老人列表失败', error)
  }
}

const getHealthData = async () => {
  if (!bindingElder.value) {
    console.warn('未绑定老人，跳过获取健康数据')
    return
  }

  const elderId = bindingElder.value.id
  console.log('正在获取老人健康数据, elderId:', elderId)

  try {
    const res: any = await api.get(`/health/metrics/latest/${elderId}`)
    console.log('健康数据API响应:', res)

    if (res.code === 200 && res.data) {
      console.log('健康数据内容:', res.data)

      // 检查数据类型，处理可能的单位转换
      const heartRate = res.data['心率']
      const systolic = res.data['血压-收缩压']
      const diastolic = res.data['血压-舒张压']
      const sleepHours = res.data['睡眠时长']
      const steps = res.data['今日步数']

      // 心率 - 整数
      healthData.heartRate = heartRate?.value !== undefined 
        ? String(Math.round(heartRate.value)) 
        : '--'

      // 血压 - 整数（收缩压/舒张压）
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

      console.log('解析后的健康数据:', healthData)
    } else {
      console.warn('API返回数据为空或格式错误')
    }
  } catch (error: any) {
    console.error('获取健康数据失败', error)
    if (error.response) {
      console.error('错误状态码:', error.response.status)
      console.error('错误数据:', error.response.data)
    }
  }
}

const getNursingRecords = async () => {
  if (!bindingElder.value) return

  try {
    const res: any = await api.get(`/nursing/records?elder_id=${bindingElder.value.id}&page_size=5`)
    if (res.code === 200) {
      nursingRecords.value = (res.data.items || []).map((record: any) => ({
        id: record.id,
        time: new Date(record.created_at).toLocaleString(),
        title: record.nursing_type_name,
        content: record.description,
        nurse: record.staff_name || '未知',
        color: '#409eff'
      }))
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

// 切换绑定的老人（如果有多绑定功能）
const onElderChange = (value: number) => {
  // 重新加载数据
  selectedElderId.value = value
  // 重新加载健康数据和护理记录
  bindingElder.value = elderList.value.find(e => e.id === value) || null
  getHealthData()
  getNursingRecords()
}

// 绑定老人
const confirmBind = async () => {
  if (!bindForm.elder_id) {
    ElMessage.warning('请选择老人')
    return
  }
  if (!bindForm.username) {
    ElMessage.warning('请输入老人账号')
    return
  }
  if (!bindForm.password) {
    ElMessage.warning('请输入老人密码')
    return
  }

  binding.value = true
  try {
    const res: any = await api.post('/users/binding-elder', {
      elder_id: bindForm.elder_id,
      username: bindForm.username,
      password: bindForm.password
    })
    if (res.code === 200) {
      ElMessage.success('绑定成功')
      showBindDialog.value = false
      // 重置表单
      bindForm.username = ''
      bindForm.password = ''
      // 重新加载绑定信息和数据
      await loadBindingElder()
      await getHealthData()
      await getNursingRecords()
    } else {
      ElMessage.error(res.message || '绑定失败')
    }
  } catch (error) {
    console.error('绑定失败', error)
  } finally {
    binding.value = false
  }
}

// 解绑老人
const unbindElder = () => {
  ElMessageBox.confirm('确定要解除与当前老人的绑定吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res: any = await api.delete('/users/binding-elder')
      if (res.code === 200) {
        ElMessage.success('解绑成功')
        bindingElder.value = null
        selectedElderId.value = null
        // 清空数据
        healthData.heartRate = '--'
        healthData.bloodPressure = '--/--'
        healthData.sleepHours = '--'
        healthData.steps = '--'
        nursingRecords.value = []
        alerts.value = []
      } else {
        ElMessage.error(res.message || '解绑失败')
      }
    } catch (error) {
      console.error('解绑失败', error)
    }
  }).catch(() => {})
}

onMounted(async () => {
  await loadElderList()
  await loadBindingElder()
  await loadWorkerList()
  if (bindingElder.value) {
    getHealthData()
    getNursingRecords()
  }
})
</script>

<style scoped lang="scss">
.family-dashboard {
  position: relative;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 50%, #f0f4f8 100%);

  &::before {
    content: '';
    position: fixed;
    top: -100%;
    left: -100%;
    width: 300%;
    height: 300%;
    background: 
      radial-gradient(ellipse at 20% 20%, rgba(64, 158, 255, 0.08) 0%, transparent 45%),
      radial-gradient(ellipse at 80% 80%, rgba(102, 177, 255, 0.05) 0%, transparent 45%),
      radial-gradient(ellipse at 40% 60%, rgba(64, 158, 255, 0.06) 0%, transparent 55%),
      radial-gradient(ellipse at 60% 40%, rgba(102, 177, 255, 0.04) 0%, transparent 55%);
    animation: familyBgFloat 28s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
  }

  &::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: 
      linear-gradient(rgba(64, 158, 255, 0.01) 1px, transparent 1px),
      linear-gradient(90deg, rgba(64, 158, 255, 0.01) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: gridMove 30s linear infinite;
    pointer-events: none;
    z-index: 0;
  }
}

@keyframes familyBgFloat {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(2%, -2%) rotate(1deg); }
  50% { transform: translate(-2%, 2%) rotate(-1deg); }
  75% { transform: translate(1%, -1%) rotate(0.5deg); }
}

@keyframes gridMove {
  0% { background-position: 0 0; }
  100% { background-position: 60px 60px; }
}

@keyframes bannerOrb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(-30px, 30px) scale(1.1); }
}

@keyframes bannerOrb2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(20px, -20px) scale(1.15); }
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
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

  &.family {
    background: linear-gradient(135deg, #409eff, #66b1ff);
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

.welcome-banner {
  position: relative;
  z-index: 1;
  background: linear-gradient(135deg, #409eff, #66b1ff);
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
    background: radial-gradient(circle, rgba(102, 177, 255, 0.15) 0%, transparent 70%);
    border-radius: 50%;
    animation: bannerOrb2 30s ease-in-out infinite reverse;
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

  :deep(.el-input__wrapper) {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    box-shadow: none;
    backdrop-filter: blur(10px);
  }

  :deep(.el-input__inner) {
    color: #fff;

    &::placeholder {
      color: rgba(255, 255, 255, 0.7);
    }
  }

  :deep(.el-select__caret) {
    color: rgba(255, 255, 255, 0.8);
  }
}

.family-content {
  position: relative;
  z-index: 1;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: #333333;
    padding-left: 10px;
    border-left: 4px solid #409eff;
  }
}

.health-cards {
  .health-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(64, 158, 255, 0.25);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: -50%;
      right: -50%;
      width: 100%;
      height: 200%;
      background: radial-gradient(circle, rgba(64, 158, 255, 0.1) 0%, transparent 70%);
      transform: rotate(45deg);
      transition: all 0.6s ease;
      opacity: 0;
    }

    &:hover {
      transform: translateY(-6px);
      box-shadow: 0 12px 32px rgba(64, 158, 255, 0.2);
      border-color: rgba(64, 158, 255, 0.5);

      &::before {
        opacity: 1;
        transform: rotate(45deg) scale(1.2);
      }
    }

    .card-icon {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 16px;
      font-size: 28px;
      color: #fff;
      position: relative;
      z-index: 1;
    }

    .card-value {
      font-size: 28px;
      font-weight: 700;
      color: #333333;
      margin-bottom: 6px;
      position: relative;
      z-index: 1;
    }

    .card-label {
      font-size: 14px;
      color: #666666;
      position: relative;
      z-index: 1;
    }

    .card-status {
      font-size: 12px;
      font-weight: 500;
      margin-top: 12px;
      padding: 4px 12px;
      border-radius: 12px;
      display: inline-block;
      position: relative;
      z-index: 1;

      &.normal {
        background: rgba(103, 194, 58, 0.2);
        color: #67c23a;
        border: 1px solid rgba(103, 194, 58, 0.3);
      }

      &.warning {
        background: rgba(245, 158, 11, 0.2);
        color: #e6a23c;
        border: 1px solid rgba(245, 158, 11, 0.3);
      }

      &.danger {
        background: rgba(245, 108, 108, 0.2);
        color: #f56c6c;
        border: 1px solid rgba(245, 108, 108, 0.3);
      }
    }

    &.heart .card-icon { background: linear-gradient(135deg, #409eff, #66b1ff); }
    &.blood .card-icon { background: linear-gradient(135deg, #409eff, #66b1ff); }
    &.sleep .card-icon { background: linear-gradient(135deg, #409eff, #66b1ff); }
    &.activity .card-icon { background: linear-gradient(135deg, #409eff, #66b1ff); }
  }
}

.nursing-records {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(64, 158, 255, 0.25);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
  }

  :deep(.el-card) {
    border: none;
    box-shadow: none;
    background: rgba(245, 247, 250, 0.9);
    border-radius: 12px;
    margin-bottom: 16px;
    padding: 20px;
    transition: all 0.3s ease;
    border-left: 4px solid #409eff;

    &:hover {
      transform: translateX(10px);
      box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
      background: rgba(235, 240, 245, 0.95);
    }
  }

  h4 {
    font-size: 16px;
    font-weight: 600;
    color: #409eff;
    margin-bottom: 10px;
  }

  p {
    font-size: 14px;
    color: #666666;
    margin-bottom: 6px;
    line-height: 1.5;
  }

  .record-nurse {
    color: #409eff;
    font-weight: 500;
  }
}

.side-section > div {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid rgba(64, 158, 255, 0.2);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 12px 32px rgba(64, 158, 255, 0.15);
  }
}

.plan-list {
  .plan-item {
    display: flex;
    align-items: center;
    padding: 16px;
    background: rgba(245, 247, 250, 0.9);
    border-radius: 12px;
    margin-bottom: 12px;
    border: 1px solid rgba(64, 158, 255, 0.15);
    transition: all 0.3s ease;

    &:hover {
      background: rgba(235, 240, 245, 0.95);
      border-color: rgba(64, 158, 255, 0.3);
      transform: translateX(8px);
    }

    .plan-date {
      width: 50px;
      text-align: center;
      margin-right: 15px;

      .day {
        display: block;
        font-size: 20px;
        font-weight: 600;
        color: #409eff;
      }

      .week {
        font-size: 12px;
        color: #666666;
      }
    }

    .plan-info {
      flex: 1;

      .plan-name {
        font-size: 14px;
        font-weight: 600;
        color: #333333;
        margin-bottom: 4px;
      }

      .plan-time {
        font-size: 12px;
        color: #666666;
      }
    }
  }
}

.alert-list {
  .alert-item {
    display: flex;
    align-items: flex-start;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 14px;
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid rgba(245, 158, 11, 0.25);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
      background: #f59e0b;
    }

    &.danger {
      background: rgba(239, 68, 68, 0.15);
      border-color: rgba(239, 68, 68, 0.25);

      &::before {
        background: #ef4444;
      }

      .el-icon {
        color: #ef4444;
      }
    }

    &:hover {
      transform: translateX(10px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }

    .el-icon {
      margin-right: 14px;
      margin-top: 4px;
      font-size: 22px;
      color: #f59e0b;
      position: relative;
      z-index: 1;
    }

    .alert-content {
      flex: 1;
      position: relative;
      z-index: 1;

      .alert-text {
        font-size: 14px;
        font-weight: 500;
        color: #ffffff;
        margin-bottom: 8px;
        line-height: 1.5;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
      }

      .alert-time {
        font-size: 12px;
        color: #9aafc0;
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
      background: rgba(30, 40, 50, 0.9);
      border: 1px solid rgba(64, 158, 255, 0.2);
      color: #e8eef5;
      padding: 16px 20px;
      border-radius: 12px;
      transition: all 0.3s ease;

      &:hover {
        background: rgba(50, 60, 70, 0.95);
        border-color: rgba(64, 158, 255, 0.4);
        transform: translateX(8px);
        box-shadow: 0 6px 16px rgba(64, 158, 255, 0.2);
      }
    }
  }
}

.bind-guide {
  position: relative;
  z-index: 1;
  background: rgba(40, 50, 60, 0.95);
  border-radius: 18px;
  padding: 80px;
  text-align: center;
  border: 1px solid rgba(64, 158, 255, 0.2);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.header-actions {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 10px;
  align-items: center;
}
</style>