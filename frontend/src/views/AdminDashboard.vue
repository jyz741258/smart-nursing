<template>
  <div class="admin-dashboard">
    <div class="role-indicator admin">
      <span class="role-icon">🔧</span>
      <span class="role-text">系统管理员</span>
    </div>

    <div class="page-header">
      <div>
        <h2 class="page-title">管理中心</h2>
        <p class="page-desc">欢迎回来</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData"><el-icon><Refresh /></el-icon>刷新数据</el-button>
        <el-button type="success" @click="showSendNotificationDialog = true"><el-icon><Bell /></el-icon>发送通知</el-button>
      </div>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card elder">
          <div class="card-icon"><el-icon><User /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ stats.elderCount }}</div>
            <div class="card-label">老人总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card nurse">
          <div class="card-icon"><el-icon><UserFilled /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ stats.nurseCount }}</div>
            <div class="card-label">护理人员</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card family">
          <div class="card-icon"><el-icon><House /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ stats.familyCount }}</div>
            <div class="card-label">家属数量</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card order">
          <div class="card-icon"><el-icon><Document /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ stats.todayOrders }}</div>
            <div class="card-label">今日订单</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="16">
        <div class="card-container">
          <div class="card-header">
            <span class="card-title">护理记录统计</span>
            <el-radio-group v-model="chartPeriod" size="small">
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="nursingChartRef" style="height: 300px"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="card-container">
          <div class="card-header"><span class="card-title">服务类型分布</span></div>
          <div ref="pieChartRef" style="height: 300px"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <div class="card-container">
          <div class="card-header"><span class="card-title">待处理任务</span></div>
          <el-table :data="pendingTasks" style="width: 100%">
            <el-table-column prop="task_name" label="任务名称" />
            <el-table-column prop="elder_name" label="老人" />
            <el-table-column prop="nurse_name" label="护理人员" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === '待执行' ? 'warning' : 'info'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card-container">
          <div class="card-header"><span class="card-title">快速入口</span></div>
          <div class="quick-links">
            <div class="link-item" @click="$router.push('/elders')"><el-icon><User /></el-icon><span>老人管理</span></div>
            <div class="link-item" @click="$router.push('/statistics')"><el-icon><DataAnalysis /></el-icon><span>数据统计</span></div>
            <div class="link-item" @click="$router.push('/nursing')"><el-icon><Document /></el-icon><span>护理记录</span></div>
            <div class="link-item" @click="$router.push('/care-plan')"><el-icon><Calendar /></el-icon><span>护理计划</span></div>
            <div class="link-item" @click="showEvaluationDialog = true"><el-icon><Star /></el-icon><span>护工评价</span></div>
            <div class="link-item" @click="$router.push('/ai-chat')"><el-icon><ChatDotRound /></el-icon><span>AI助手</span></div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 护工评价管理对话框 -->
    <el-dialog v-model="showEvaluationDialog" title="护工评价管理" width="900px">
      <el-tabs v-model="evaluationTab">
        <el-tab-pane label="评价列表" name="list">
          <div class="evaluation-filters">
            <el-select v-model="selectedWorkerId" placeholder="选择护工" clearable style="width: 200px; margin-right: 10px">
              <el-option v-for="w in workerList" :key="w.id" :label="w.name" :value="w.id" />
            </el-select>
            <el-button @click="loadEvaluations">查询</el-button>
          </div>
          <el-table :data="evaluationList" style="width: 100%; margin-top: 15px" v-loading="loadingEvaluations">
            <el-table-column prop="elder_name" label="评价老人" width="100">
              <template #default="{ row }">
                {{ row.is_anonymous ? '匿名' : (row.elder_name || '未知') }}
              </template>
            </el-table-column>
            <el-table-column prop="worker_name" label="护工" width="100" />
            <el-table-column prop="overall_rating" label="总体评分" width="100">
              <template #default="{ row }">
                <el-rate v-model="row.overall_rating" disabled size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="professionalism_rating" label="专业" width="80">
              <template #default="{ row }">{{ row.professionalism_rating || '-' }}</template>
            </el-table-column>
            <el-table-column prop="attitude_rating" label="态度" width="80">
              <template #default="{ row }">{{ row.attitude_rating || '-' }}</template>
            </el-table-column>
            <el-table-column prop="punctuality_rating" label="准时" width="80">
              <template #default="{ row }">{{ row.punctuality_rating || '-' }}</template>
            </el-table-column>
            <el-table-column prop="content" label="评价内容" min-width="150" show-overflow-tooltip />
            <el-table-column prop="tags" label="标签" width="120">
              <template #default="{ row }">
                <el-tag v-for="tag in (row.tags_list || [])" :key="tag" size="small" type="info" style="margin-right: 4px">{{ tag }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="评价时间" width="160">
              <template #default="{ row }">
                {{ row.created_at ? new Date(row.created_at).toLocaleString() : '-' }}
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="evaluationPage"
            v-model:page-size="evaluationPageSize"
            :total="evaluationTotal"
            layout="total, prev, pager, next"
            style="margin-top: 15px; justify-content: center"
            @current-change="loadEvaluations"
          />
        </el-tab-pane>

        <el-tab-pane label="评分统计" name="stats">
          <div class="stats-filters">
            <el-select v-model="selectedWorkerId" placeholder="选择护工" clearable style="width: 200px; margin-right: 10px" @change="loadWorkerStats">
              <el-option v-for="w in workerList" :key="w.id" :label="w.name" :value="w.id" />
            </el-select>
            <el-button @click="loadWorkerStats">查询</el-button>
          </div>
          <div v-if="workerStats" class="worker-stats-container">
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="stats-card-display">
                  <div class="big-score">{{ workerStats.average_rating || 0 }}</div>
                  <div class="score-label">平均评分</div>
                  <div class="total-count">共 {{ workerStats.total_count }} 条评价</div>
                </div>
              </el-col>
              <el-col :span="16">
                <div class="dimension-stats">
                  <div class="dimension-item">
                    <span class="dim-label">专业程度</span>
                    <el-progress :percentage="((workerStats.dimension_avg?.professionalism || 0) / 5 * 100)" :stroke-width="10" />
                    <span class="dim-score">{{ workerStats.dimension_avg?.professionalism || 0 }}</span>
                  </div>
                  <div class="dimension-item">
                    <span class="dim-label">服务态度</span>
                    <el-progress :percentage="((workerStats.dimension_avg?.attitude || 0) / 5 * 100)" :stroke-width="10" />
                    <span class="dim-score">{{ workerStats.dimension_avg?.attitude || 0 }}</span>
                  </div>
                  <div class="dimension-item">
                    <span class="dim-label">准时性</span>
                    <el-progress :percentage="((workerStats.dimension_avg?.punctuality || 0) / 5 * 100)" :stroke-width="10" />
                    <span class="dim-score">{{ workerStats.dimension_avg?.punctuality || 0 }}</span>
                  </div>
                  <div class="dimension-item">
                    <span class="dim-label">技能水平</span>
                    <el-progress :percentage="((workerStats.dimension_avg?.skill || 0) / 5 * 100)" :stroke-width="10" />
                    <span class="dim-score">{{ workerStats.dimension_avg?.skill || 0 }}</span>
                  </div>
                </div>
              </el-col>
            </el-row>
            <div class="rating-distribution">
              <div class="dist-title">评分分布</div>
              <div class="dist-bars">
                <div v-for="rating in [5, 4, 3, 2, 1]" :key="rating" class="dist-item">
                  <span class="dist-label">{{ rating }}星</span>
                  <div class="dist-bar-bg">
                    <div class="dist-bar-fill" :style="{ width: workerStats.total_count > 0 ? (workerStats.rating_distribution?.[rating] / workerStats.total_count * 100) + '%' : '0%' }"></div>
                  </div>
                  <span class="dist-count">{{ workerStats.rating_distribution?.[rating] || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="请选择护工查看评分统计" />
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <!-- 发送通知对话框 -->
    <el-dialog v-model="showSendNotificationDialog" title="发送通知" width="600px">
      <el-form :model="notificationForm" label-width="100px">
        <el-form-item label="通知类型">
          <el-select v-model="notificationForm.notification_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="系统通知" :value="1" />
            <el-option label="护理提醒" :value="2" />
            <el-option label="健康预警" :value="3" />
            <el-option label="任务通知" :value="4" />
            <el-option label="紧急通知" :value="5" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="notificationForm.priority">
            <el-radio :label="0">普通</el-radio>
            <el-radio :label="1">重要</el-radio>
            <el-radio :label="2">紧急</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="选择接收人">
          <el-select
            v-model="notificationForm.user_ids"
            multiple
            placeholder="请选择接收人"
            style="width: 100%"
            filterable
          >
            <el-option-group label="老人">
              <el-option
                v-for="user in userList.filter(u => u.user_type === 1)"
                :key="user.id"
                :label="user.name + ' (' + user.phone + ')'"
                :value="user.id"
              />
            </el-option-group>
            <el-option-group label="护理人员">
              <el-option
                v-for="user in userList.filter(u => u.user_type === 2)"
                :key="user.id"
                :label="user.name + ' (' + user.phone + ')'"
                :value="user.id"
              />
            </el-option-group>
            <el-option-group label="家属">
              <el-option
                v-for="user in userList.filter(u => u.user_type === 4)"
                :key="user.id"
                :label="user.name + ' (' + user.phone + ')'"
                :value="user.id"
              />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="通知标题">
          <el-input v-model="notificationForm.title" placeholder="请输入通知标题" />
        </el-form-item>
        <el-form-item label="通知内容">
          <el-input
            v-model="notificationForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入通知内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSendNotificationDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSendNotification" :loading="sendingNotification">
          发送通知
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '@/store/auth'

const chartPeriod = ref('week')
const nursingChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
let nursingChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

const userName = ref('管理员')
const stats = reactive({ elderCount: 0, nurseCount: 0, familyCount: 0, todayOrders: 0 })

// 发送通知相关
const showSendNotificationDialog = ref(false)
const sendingNotification = ref(false)
const userList = ref<any[]>([])
const notificationForm = reactive({
  notification_type: 1,
  priority: 0,
  user_ids: [] as number[],
  title: '',
  content: ''
})

const pendingTasks = ref([
  { task_name: '日常护理', elder_name: '张三', nurse_name: '李护理', status: '待执行' },
  { task_name: '健康监测', elder_name: '李四', nurse_name: '王护理', status: '待执行' }
])

// 加载用户列表
const loadUserList = async () => {
  try {
    const res: any = await api.get('/notifications/users')
    if (res.code === 200) {
      userList.value = res.data || []
    }
  } catch (error) {
    console.error('获取用户列表失败', error)
  }
}

// 发送通知
const handleSendNotification = async () => {
  if (!notificationForm.title.trim()) {
    ElMessage.warning('请输入通知标题')
    return
  }
  if (notificationForm.user_ids.length === 0) {
    ElMessage.warning('请选择至少一个接收人')
    return
  }

  sendingNotification.value = true
  try {
    const res: any = await api.post('/notifications/create', {
      user_ids: notificationForm.user_ids,
      title: notificationForm.title,
      content: notificationForm.content,
      notification_type: notificationForm.notification_type,
      priority: notificationForm.priority
    })
    if (res.code === 200) {
      ElMessage.success(res.message || '通知发送成功')
      showSendNotificationDialog.value = false
      // 重置表单
      notificationForm.title = ''
      notificationForm.content = ''
      notificationForm.user_ids = []
      notificationForm.notification_type = 1
      notificationForm.priority = 0
    } else {
      ElMessage.error(res.message || '发送失败')
    }
  } catch (error) {
    console.error('发送通知失败', error)
    ElMessage.error('发送通知失败')
  } finally {
    sendingNotification.value = false
  }
}

const getDashboardStats = async () => {
  try {
    const res: any = await api.get('/statistics/dashboard')
    if (res.code === 200) {
      stats.elderCount = res.data.elder_count || 0
      stats.nurseCount = res.data.staff_count || 0
      stats.familyCount = res.data.family_count || 0
      stats.todayOrders = res.data.today_orders || 0
    }
  } catch (error) {
    console.error('获取仪表盘数据失败', error)
  }
}

// 获取护理记录统计数据（支持本周/本月）
const getWeeklyNursingData = async () => {
  try {
    const period = chartPeriod.value  // 'week' 或 'month'
    const res: any = await api.get('/statistics/weekly-nursing', { params: { period } })
    console.log('[Debug] Nursing chart data (period:', period, '):', res)
    if (res.code === 200 && nursingChartRef.value) {
      const chartData = res.data || []
      const days = chartData.map((d: any) => d.day)  // 使用 day 字段作为X轴显示标签
      const counts = chartData.map((d: any) => d.count)
      console.log('[Debug] Chart data - days:', days, 'counts:', counts)
      nursingChart.setOption({
        xAxis: { type: 'category', data: days },
        series: [{ data: counts }]
      })
    }
  } catch (error) {
    console.error('获取护理记录数据失败', error)
  }
}

// 获取服务类型分布数据
const getServiceDistribution = async () => {
  try {
    const res: any = await api.get('/statistics/service-distribution')
    console.log('[Debug] Service distribution data:', res)
    if (res.code === 200 && pieChartRef.value) {
      const serviceData = res.data || []
      console.log('[Debug] Pie chart data:', serviceData)
      pieChart.setOption({
        series: [{
          data: serviceData
        }]
      })
    }
  } catch (error) {
    console.error('获取服务类型分布数据失败', error)
  }
}

const refreshData = async () => {
  await getDashboardStats()
  await updateCharts()
  ElMessage.success('数据已刷新')
}

// 清理图表实例
const disposeCharts = () => {
  if (nursingChart) {
    nursingChart.dispose()
    nursingChart = null
  }
  if (pieChart) {
    pieChart.dispose()
    pieChart = null
  }
}

const updateCharts = async () => {
  console.log('[Debug] updateCharts called')

  // 清理旧图表
  disposeCharts()

  // 等待DOM更新
  await nextTick()

  // 延迟初始化，确保容器有尺寸
  setTimeout(() => {
    let chartInitialized = false

    if (nursingChartRef.value) {
      const parent = nursingChartRef.value.parentElement
      console.log('[Debug] Nursing chart container:', {
        width: nursingChartRef.value.clientWidth,
        height: nursingChartRef.value.clientHeight,
        offsetWidth: nursingChartRef.value.offsetWidth,
        offsetHeight: nursingChartRef.value.offsetHeight,
        parentDisplay: parent ? getComputedStyle(parent).display : 'no-parent',
        parentWidth: parent ? parent.clientWidth : 'no-parent'
      })

      if (nursingChartRef.value.clientWidth > 0 && nursingChartRef.value.clientHeight > 0) {
        nursingChart = echarts.init(nursingChartRef.value)
        // 根据周期设置默认X轴标签
        const isWeek = chartPeriod.value === 'week'
        const defaultXAxis = isWeek
          ? ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
          : Array.from({length: 31}, (_, i) => `${i + 1}日`)
        nursingChart.setOption({
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'category', data: defaultXAxis },
          yAxis: { type: 'value' },
          series: [{ type: 'bar', data: new Array(defaultXAxis.length).fill(0), itemStyle: { color: '#409eff' } }]
        })
        getWeeklyNursingData()
        chartInitialized = true
      } else {
        console.warn('[Debug] Nursing chart container has zero dimensions')
      }
    }

    if (pieChartRef.value) {
      const parent = pieChartRef.value.parentElement
      console.log('[Debug] Pie chart container:', {
        width: pieChartRef.value.clientWidth,
        height: pieChartRef.value.clientHeight,
        offsetWidth: pieChartRef.value.offsetWidth,
        offsetHeight: pieChartRef.value.offsetHeight,
        parentDisplay: parent ? getComputedStyle(parent).display : 'no-parent',
        parentWidth: parent ? parent.clientWidth : 'no-parent'
      })

      if (pieChartRef.value.clientWidth > 0 && pieChartRef.value.clientHeight > 0) {
        pieChart = echarts.init(pieChartRef.value)
        pieChart.setOption({
          tooltip: { trigger: 'item' },
          legend: { bottom: 0, textStyle: { color: '#b8c5d6' } },
          series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            data: [],
            label: { color: '#b8c5d6' }
          }]
        })
        getServiceDistribution()
        chartInitialized = true
      } else {
        console.warn('[Debug] Pie chart container has zero dimensions')
      }
    }

    // 如果图表未初始化，延迟重试
    if (!chartInitialized) {
      console.log('[Debug] Charts not ready, retrying in 200ms...')
      setTimeout(updateCharts, 200)
    }
  }, 500)  // 增加到500ms确保布局完成
}

// 监听周期切换
watch(chartPeriod, () => {
  console.log('[Debug] chartPeriod changed to:', chartPeriod.value)
  // 重新初始化图表X轴
  if (nursingChart) {
    const isWeek = chartPeriod.value === 'week'
    const newXAxis = isWeek
      ? ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      : Array.from({length: 31}, (_, i) => `${i + 1}日`)
    nursingChart.setOption({
      xAxis: { data: newXAxis },
      series: [{ data: new Array(newXAxis.length).fill(0) }]
    })
  }
  getWeeklyNursingData()
})

const handleResize = () => {
  nursingChart?.resize()
  pieChart?.resize()
}

// 评价管理相关
const showEvaluationDialog = ref(false)
const evaluationTab = ref('list')
const workerList = ref<any[]>([])
const selectedWorkerId = ref<number | null>(null)
const evaluationList = ref<any[]>([])
const evaluationPage = ref(1)
const evaluationPageSize = ref(10)
const evaluationTotal = ref(0)
const loadingEvaluations = ref(false)
const workerStats = ref<any>(null)

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

// 加载评价列表
const loadEvaluations = async () => {
  loadingEvaluations.value = true
  try {
    const params: any = { page: evaluationPage.value, page_size: evaluationPageSize.value }
    if (selectedWorkerId.value) params.worker_id = selectedWorkerId.value
    const res: any = await api.get('/evaluations/worker', { params })
    if (res.code === 200) {
      evaluationList.value = (res.data.items || []).map((e: any) => ({
        ...e,
        tags_list: e.tags ? JSON.parse(e.tags) : []
      }))
      evaluationTotal.value = res.data.total || 0
    }
  } catch (error) {
    console.error('获取评价列表失败', error)
  } finally {
    loadingEvaluations.value = false
  }
}

// 加载护工评分统计
const loadWorkerStats = async () => {
  if (!selectedWorkerId.value) {
    workerStats.value = null
    return
  }
  try {
    const res: any = await api.get(`/evaluations/worker/stats/${selectedWorkerId.value}`)
    if (res.code === 200) {
      workerStats.value = res.data
    }
  } catch (error) {
    console.error('获取护工评分统计失败', error)
  }
}

// 监听对话框打开，加载护工列表
watch(showEvaluationDialog, (val) => {
  if (val) {
    loadWorkerList()
    loadEvaluations()
  }
})

onMounted(async () => {
  await getDashboardStats()
  await loadUserList()
  updateCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  nursingChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped lang="scss">
.admin-dashboard {
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
      radial-gradient(ellipse at 20% 20%, rgba(230, 162, 60, 0.12) 0%, transparent 40%),
      radial-gradient(ellipse at 80% 80%, rgba(245, 147, 251, 0.08) 0%, transparent 40%),
      radial-gradient(ellipse at 50% 50%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 10% 90%, rgba(240, 147, 251, 0.05) 0%, transparent 30%),
      radial-gradient(circle at 90% 10%, rgba(230, 162, 60, 0.05) 0%, transparent 30%);
    animation: adminBgFloat 25s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
  }

  // 网格背景
  &::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: 
      linear-gradient(rgba(102, 126, 234, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(102, 126, 234, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: gridMove 20s linear infinite;
    pointer-events: none;
    z-index: 0;
  }

  @keyframes adminBgFloat {
    0%, 100% { 
      transform: translate(0, 0) rotate(0deg);
    }
    25% { 
      transform: translate(2%, -2%) rotate(1deg);
    }
    50% { 
      transform: translate(-2%, 2%) rotate(-1deg);
    }
    75% { 
      transform: translate(1%, -1%) rotate(0.5deg);
    }
  }

  @keyframes gridMove {
    0% { background-position: 0 0; }
    100% { background-position: 50px 50px; }
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

  &.admin {
    background: linear-gradient(135deg, #e6a23c, #f0a030);
    color: #ffffff;
    box-shadow: 0 4px 24px rgba(230, 162, 60, 0.5), 0 0 0 2px rgba(230, 162, 60, 0.2);
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
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-header { 
  position: relative;
  z-index: 1;
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 28px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(230, 162, 60, 0.2);
  
  .page-title { 
    font-size: 26px; 
    font-weight: 700; 
    color: #ffffff;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }
  
  .page-desc { 
    font-size: 14px; 
    color: #a8b4c4;
    margin-top: 4px;
  }

  .header-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.stats-row { 
  position: relative;
  z-index: 1;
  margin-bottom: 24px;
}

.stats-card {
  position: relative;
  background: rgba(35, 45, 55, 0.95);
  border-radius: 16px;
  padding: 26px;
  display: flex;
  align-items: center;
  gap: 22px;
  border: 1px solid rgba(102, 126, 234, 0.2);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.5, 1);
  overflow: hidden;

  // 悬停顶部光效
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transform: scaleX(0);
    transition: transform 0.3s ease;
  }

  &:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 16px 40px rgba(102, 126, 234, 0.25);
    border-color: rgba(102, 126, 234, 0.4);

    &::before {
      transform: scaleX(1);
    }
  }

  .card-icon {
    width: 64px;
    height: 64px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    color: #fff;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  }

  .card-content {
    .card-value {
      font-size: 34px;
      font-weight: 800;
      color: #ffffff;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.3));
    }

    .card-label {
      font-size: 14px;
      color: #9aafc0;
      margin-top: 4px;
      font-weight: 500;
    }
  }

  &.elder .card-icon { 
    background: linear-gradient(135deg, #67c23a, #85ce61);
    box-shadow: 0 4px 20px rgba(103, 194, 58, 0.4);
  }

  &.nurse .card-icon { 
    background: linear-gradient(135deg, #409eff, #66b1ff);
    box-shadow: 0 4px 20px rgba(64, 158, 255, 0.4);
  }

  &.family .card-icon { 
    background: linear-gradient(135deg, #f56c6c, #fab6b6);
    box-shadow: 0 4px 20px rgba(245, 108, 108, 0.4);
  }

  &.order .card-icon { 
    background: linear-gradient(135deg, #e6a23c, #f0a030);
    box-shadow: 0 4px 20px rgba(230, 162, 60, 0.4);
  }
}

.card-container { 
  position: relative;
  z-index: 1;
  background: rgba(35, 45, 55, 0.95);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 12px 32px rgba(102, 126, 234, 0.15);
    border-color: rgba(102, 126, 234, 0.3);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;

    .card-title {
      font-size: 17px;
      font-weight: 600;
      color: #ffffff;
      padding-left: 12px;
      border-left: 3px solid #e6a23c;
    }
  }
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;

  .link-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 22px;
    background: rgba(30, 40, 50, 0.9);
    border-radius: 14px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
    border: 1px solid rgba(102, 126, 234, 0.15);

    .el-icon {
      font-size: 32px;
      color: #e6a23c;
      margin-bottom: 12px;
      transition: all 0.3s ease;
    }

    span {
      font-size: 14px;
      color: #b8c5d6;
      font-weight: 500;
      transition: all 0.3s ease;
    }

    &:hover {
      background: rgba(50, 60, 70, 0.95);
      border-color: rgba(230, 162, 60, 0.4);
      transform: translateY(-4px);
      box-shadow: 0 10px 24px rgba(230, 162, 60, 0.2);

      .el-icon {
        transform: scale(1.15);
        color: #f0a030;
      }

      span {
        color: #ffffff;
      }
    }
  }
}

.evaluation-filters, .stats-filters {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.worker-stats-container { 
  margin-top: 24px; 
}

.stats-card-display {
  background: linear-gradient(135deg, #e6a23c, #f0a030, #f6b040);
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  color: #ffffff;
  box-shadow: 0 8px 32px rgba(230, 162, 60, 0.4);

  .big-score {
    font-size: 64px;
    font-weight: 700;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }

  .score-label {
    font-size: 17px;
    opacity: 0.95;
    margin-top: 6px;
  }

  .total-count {
    font-size: 14px;
    opacity: 0.85;
    margin-top: 12px;
    background: rgba(0, 0, 0, 0.2);
    padding: 6px 14px;
    border-radius: 20px;
    display: inline-block;
  }
}

.dimension-stats {
  .dimension-item {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    padding: 10px 12px;
    background: rgba(30, 40, 50, 0.8);
    border-radius: 10px;
    transition: all 0.3s ease;

    &:hover {
      background: rgba(40, 50, 60, 0.9);
      transform: translateX(4px);
    }

    .dim-label {
      width: 90px;
      font-size: 14px;
      color: #b8c5d6;
      font-weight: 500;
    }

    .el-progress {
      flex: 1;
      margin: 0 12px;
    }

    .dim-score {
      width: 35px;
      text-align: right;
      font-weight: 700;
      color: #e6a23c;
      font-size: 15px;
    }
  }
}

.rating-distribution {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(102, 126, 234, 0.15);

  .dist-title {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 16px;
    padding-left: 10px;
    border-left: 3px solid #e6a23c;
  }

  .dist-bars {
    .dist-item {
      display: flex;
      align-items: center;
      margin-bottom: 12px;

      .dist-label {
        width: 45px;
        font-size: 13px;
        color: #9aafc0;
        font-weight: 500;
      }

      .dist-bar-bg {
        flex: 1;
        height: 22px;
        background: rgba(30, 40, 50, 0.9);
        border-radius: 11px;
        overflow: hidden;
        margin: 0 12px;
        border: 1px solid rgba(102, 126, 234, 0.1);
      }

      .dist-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #e6a23c, #f0a030);
        border-radius: 11px;
        transition: width 0.5s cubic-bezier(0.25, 0.8, 0.5, 1);
        box-shadow: 0 0 12px rgba(230, 162, 60, 0.4);
      }

      .dist-count {
        width: 45px;
        text-align: right;
        font-size: 14px;
        color: #b8c5d6;
        font-weight: 600;
      }
    }
  }
}
</style>