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
      <el-button type="primary" @click="refreshData"><el-icon><Refresh /></el-icon>刷新数据</el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
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

const pendingTasks = ref([
  { task_name: '日常护理', elder_name: '张三', nurse_name: '李护理', status: '待执行' },
  { task_name: '健康监测', elder_name: '李四', nurse_name: '王护理', status: '待执行' }
])

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

// 获取本周护理记录统计数据
const getWeeklyNursingData = async () => {
  try {
    const res: any = await api.get('/statistics/weekly-nursing')
    if (res.code === 200 && nursingChartRef.value) {
      const weekData = res.data || []
      const days = weekData.map((d: any) => d.day)
      const counts = weekData.map((d: any) => d.count)
      nursingChart.setOption({
        xAxis: { type: 'category', data: days },
        series: [{ data: counts }]
      })
    }
  } catch (error) {
    console.error('获取本周护理记录数据失败', error)
  }
}

// 获取服务类型分布数据
const getServiceDistribution = async () => {
  try {
    const res: any = await api.get('/statistics/service-distribution')
    if (res.code === 200 && pieChartRef.value) {
      const serviceData = res.data || []
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
  updateCharts()
  ElMessage.success('数据已刷新')
}

const updateCharts = () => {
  if (nursingChartRef.value) {
    nursingChart = echarts.init(nursingChartRef.value)
    nursingChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [], itemStyle: { color: '#409eff' } }]
    })
    getWeeklyNursingData()
  }

  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: []
      }]
    })
    getServiceDistribution()
  }
}

// 监听周期切换
watch(chartPeriod, () => {
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
.admin-dashboard { padding: 20px; }

.role-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 16px;

  &.admin {
    background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
    color: #fff;
  }

  .role-icon {
    font-size: 18px;
  }
}

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; .page-title { font-size: 24px; font-weight: 600; color: #303133; } .page-desc { font-size: 14px; color: #909399; } }
.stats-row { margin-bottom: 20px; }
.stats-card {
  background: #fff; border-radius: 12px; padding: 24px; display: flex; align-items: center; gap: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  .card-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 28px; color: #fff; }
  .card-content { .card-value { font-size: 32px; font-weight: 700; color: #303133; } .card-label { font-size: 14px; color: #909399; } }
  &.elder .card-icon { background: linear-gradient(135deg, #67c23a, #85ce61); }
  &.nurse .card-icon { background: linear-gradient(135deg, #409eff, #66b1ff); }
  &.family .card-icon { background: linear-gradient(135deg, #f56c6c, #fab6b6); }
  &.order .card-icon { background: linear-gradient(135deg, #e6a23c, #f3d19e); }
}
.card-container { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; .card-title { font-size: 16px; font-weight: 600; color: #303133; } } }
.quick-links { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; .link-item { display: flex; flex-direction: column; align-items: center; padding: 20px; background: #f5f7fa; border-radius: 12px; cursor: pointer; transition: all 0.3s; .el-icon { font-size: 28px; color: #409eff; margin-bottom: 10px; } span { font-size: 14px; color: #606266; } &:hover { background: #ecf5ff; transform: translateY(-3px); } } }

.evaluation-filters, .stats-filters { display: flex; align-items: center; }

.worker-stats-container { margin-top: 20px; }
.stats-card-display { background: linear-gradient(135deg, #409eff, #66b1ff); border-radius: 12px; padding: 30px; text-align: center; color: #fff; .big-score { font-size: 60px; font-weight: 700; } .score-label { font-size: 16px; opacity: 0.9; margin-top: 5px; } .total-count { font-size: 14px; opacity: 0.8; margin-top: 10px; } }
.dimension-stats { .dimension-item { display: flex; align-items: center; margin-bottom: 15px; .dim-label { width: 80px; font-size: 14px; color: #606266; } .el-progress { flex: 1; margin: 0 10px; } .dim-score { width: 30px; text-align: right; font-weight: 600; color: #409eff; } } }
.rating-distribution { margin-top: 20px; .dist-title { font-size: 16px; font-weight: 600; color: #303133; margin-bottom: 15px; } .dist-bars { .dist-item { display: flex; align-items: center; margin-bottom: 10px; .dist-label { width: 40px; font-size: 14px; color: #606266; } .dist-bar-bg { flex: 1; height: 20px; background: #f5f7fa; border-radius: 10px; overflow: hidden; margin: 0 10px; } .dist-bar-fill { height: 100%; background: linear-gradient(90deg, #409eff, #66b1ff); border-radius: 10px; transition: width 0.3s; } .dist-count { width: 40px; text-align: right; font-size: 14px; color: #909399; } } } }
</style>