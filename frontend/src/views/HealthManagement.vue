<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">健康管理与护理计划</h2>
      <div class="header-buttons">
        <el-button v-if="isAdminOrNurse" type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增记录
        </el-button>
        <el-button type="success" @click="exportCSV">
          <el-icon><Download /></el-icon>
          导出CSV
        </el-button>
        <el-button @click="showChartDialog = true">
          <el-icon><DataAnalysis /></el-icon>
          可视化图表
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 健康监测 -->
      <el-tab-pane label="健康监测" name="health">
        <div class="card-container">
          <div class="search-form">
            <el-select v-model="healthSearch.elder_id" placeholder="选择老人" clearable style="width: 150px">
              <el-option v-for="elder in elders" :key="elder.id" :label="elder.name" :value="elder.id" />
            </el-select>
            <el-select v-model="healthSearch.metric_type" placeholder="指标类型" clearable style="width: 150px">
              <el-option label="体温" :value="1" />
              <el-option label="血压-收缩压" :value="2" />
              <el-option label="血压-舒张压" :value="3" />
              <el-option label="心率" :value="4" />
              <el-option label="血氧" :value="5" />
              <el-option label="血糖" :value="6" />
              <el-option label="体重" :value="7" />
              <el-option label="身高" :value="8" />
            </el-select>
            <el-button type="primary" @click="getMetrics">搜索</el-button>
            <el-button @click="resetHealthSearch">重置</el-button>
          </div>

          <!-- 最新指标卡片 -->
          <el-row :gutter="20" class="latest-metrics" v-if="latestMetrics && Object.keys(latestMetrics).length > 0">
            <el-col :span="6" v-for="(value, key) in latestMetrics" :key="key">
              <div class="metric-card">
                <div class="metric-label">{{ key }}</div>
                <div class="metric-value">{{ value.value }} {{ value.unit }}</div>
                <div class="metric-time">{{ value.recorded_at }}</div>
              </div>
            </el-col>
          </el-row>

          <!-- 指标记录列表 -->
          <el-table :data="metrics" v-loading="healthLoading" style="margin-top: 20px">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="elder_name" label="老人" />
            <el-table-column prop="metric_type_name" label="指标类型" />
            <el-table-column prop="metric_value" label="数值" />
            <el-table-column prop="unit" label="单位" width="100" />
            <el-table-column prop="recorded_at" label="记录时间" width="180" />
            <el-table-column prop="notes" label="备注" show-overflow-tooltip />
          </el-table>

          <el-pagination
            v-model:current-page="healthPagination.page"
            v-model:page-size="healthPagination.page_size"
            :total="healthPagination.total"
            layout="total, prev, pager, next"
            @current-change="getMetrics"
            style="margin-top: 20px; justify-content: flex-end"
          />
        </div>
      </el-tab-pane>

      <!-- 护理计划 -->
      <el-tab-pane label="护理计划" name="plan">
        <div class="card-container">
          <el-table :data="plans" v-loading="planLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="计划标题" />
            <el-table-column prop="elder_name" label="老人" />
            <el-table-column prop="status_name" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status_name }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="end_date" label="结束日期" width="120" />
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewPlan(row)">查看</el-button>
                <el-button v-if="isAdminOrNurse" type="success" size="small" @click="addTask(row)">添加任务</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="planPagination.page"
            v-model:page-size="planPagination.page_size"
            :total="planPagination.total"
            layout="total, prev, pager, next"
            @current-change="getPlans"
            style="margin-top: 20px; justify-content: flex-end"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 健康记录对话框 -->
    <el-dialog v-model="showHealthDialog" title="记录健康指标" width="500px">
      <el-form ref="healthFormRef" :model="healthForm" label-width="100px">
        <el-form-item label="老人">
          <el-select v-model="healthForm.elder_id" placeholder="选择老人" style="width: 100%">
            <el-option v-for="elder in elders" :key="elder.id" :label="elder.name" :value="elder.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="指标类型">
          <el-select v-model="healthForm.metric_type" placeholder="选择类型" style="width: 100%">
            <el-option label="体温" :value="1" />
            <el-option label="血压-收缩压" :value="2" />
            <el-option label="血压-舒张压" :value="3" />
            <el-option label="心率" :value="4" />
            <el-option label="血氧" :value="5" />
            <el-option label="血糖" :value="6" />
            <el-option label="体重" :value="7" />
            <el-option label="身高" :value="8" />
          </el-select>
        </el-form-item>
        <el-form-item label="数值">
          <el-input v-model="healthForm.value" placeholder="请输入数值" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="healthForm.notes" type="textarea" rows="3" placeholder="备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showHealthDialog = false">取消</el-button>
        <el-button type="primary" @click="submitHealthRecord">提交</el-button>
      </template>
    </el-dialog>

    <!-- 护理计划对话框 -->
    <el-dialog v-model="showPlanDialog" title="创建护理计划" width="600px">
      <el-form ref="planFormRef" :model="planForm" label-width="100px">
        <el-form-item label="计划标题">
          <el-input v-model="planForm.title" placeholder="请输入计划标题" />
        </el-form-item>
        <el-form-item label="老人">
          <el-select v-model="planForm.elder_id" placeholder="选择老人" style="width: 100%">
            <el-option v-for="elder in elders" :key="elder.id" :label="elder.name" :value="elder.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="planForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="planForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="计划描述">
          <el-input v-model="planForm.description" type="textarea" rows="3" placeholder="请输入计划描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPlanDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPlan">创建</el-button>
      </template>
    </el-dialog>

    <!-- 计划详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="护理计划详情" width="800px">
      <el-descriptions :column="2" border style="margin-bottom: 20px">
        <el-descriptions-item label="标题">{{ currentPlan.title }}</el-descriptions-item>
        <el-descriptions-item label="老人">{{ currentPlan.elder_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentPlan.status)">{{ currentPlan.status_name }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="开始日期">{{ currentPlan.start_date }}</el-descriptions-item>
        <el-descriptions-item label="结束日期">{{ currentPlan.end_date }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentPlan.description }}</el-descriptions-item>
      </el-descriptions>

      <div class="tasks-section">
        <h4>护理任务</h4>
        <el-table :data="currentPlan.tasks" size="small">
          <el-table-column prop="task_name" label="任务名称" />
          <el-table-column prop="task_type" label="任务类型" width="100" />
          <el-table-column prop="scheduled_time" label="计划时间" width="120" />
          <el-table-column prop="status_name" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getTaskStatusType(row.status)" size="small">{{ row.status_name }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 添加任务对话框 -->
    <el-dialog v-model="showTaskDialog" title="添加护理任务" width="500px">
      <el-form ref="taskFormRef" :model="taskForm" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="taskForm.task_name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="taskForm.task_type" placeholder="选择类型" style="width: 100%">
            <el-option label="日常照护" :value="1" />
            <el-option label="医疗护理" :value="2" />
            <el-option label="康复训练" :value="3" />
            <el-option label="健康监测" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划时间">
          <el-date-picker v-model="taskForm.scheduled_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="taskForm.notes" type="textarea" rows="3" placeholder="备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTaskDialog = false">取消</el-button>
        <el-button type="primary" @click="submitTask">添加</el-button>
      </template>
    </el-dialog>

    <!-- 可视化图表对话框 -->
    <el-dialog v-model="showChartDialog" title="健康数据可视化" width="800px">
      <div class="chart-container">
        <el-select v-model="chartElderId" placeholder="选择老人" style="width: 200px; margin-bottom: 20px">
          <el-option v-for="elder in elders" :key="elder.id" :label="elder.name" :value="elder.id" />
        </el-select>
        <el-select v-model="chartMetricType" placeholder="选择指标类型" style="width: 200px; margin-left: 10px; margin-bottom: 20px">
          <el-option label="体温" :value="1" />
          <el-option label="血压-收缩压" :value="2" />
          <el-option label="血压-舒张压" :value="3" />
          <el-option label="心率" :value="4" />
          <el-option label="血氧" :value="5" />
          <el-option label="血糖" :value="6" />
          <el-option label="体重" :value="7" />
          <el-option label="身高" :value="8" />
          <el-option label="睡眠时长" :value="9" />
          <el-option label="今日步数" :value="10" />
        </el-select>
        <el-button type="primary" @click="updateChart" style="margin-left: 10px">生成图表</el-button>
        <div ref="chartRef" style="height: 400px"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Download, DataAnalysis } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { FormInstance } from 'element-plus'
import api from '@/store/auth'
import { useAuthStore } from '@/store/auth'

const activeTab = ref('health')
const authStore = useAuthStore()

const isAdminOrNurse = computed(() => {
  const userType = authStore.userInfo?.user_type
  return userType === 2 || userType === 3
})

// 健康监测相关
const healthSearch = reactive({ elder_id: '', metric_type: '' })
const healthFormRef = ref<FormInstance>()
const healthForm = reactive({ elder_id: '', metric_type: null, value: '', notes: '' })
const metrics = ref<any[]>([])
const latestMetrics = ref<any>({})
const healthLoading = ref(false)
const healthPagination = reactive({ page: 1, page_size: 10, total: 0 })
const showHealthDialog = ref(false)
const elders = ref<any[]>([])

// 护理计划相关
const plans = ref<any[]>([])
const planLoading = ref(false)
const planPagination = reactive({ page: 1, page_size: 10, total: 0 })
const showPlanDialog = ref(false)
const showDetailDialog = ref(false)
const showTaskDialog = ref(false)
const showChartDialog = ref(false)
const planFormRef = ref<FormInstance>()
const taskFormRef = ref<FormInstance>()
const currentPlan = ref<any>({})
const planForm = reactive({ title: '', elder_id: '', start_date: '', end_date: '', description: '' })
const taskForm = reactive({ task_name: '', task_type: null, scheduled_time: '', notes: '' })

// 图表相关
const chartRef = ref<HTMLElement>()
const chartElderId = ref('')
const chartMetricType = ref('')
let healthChart: echarts.ECharts | null = null

const getElders = async () => {
  try {
    const res: any = await api.get('/users/elder/list')
    if (res.code === 200) elders.value = res.data || []
  } catch (error) {
    console.error('获取老人列表失���', error)
  }
}

const getMetrics = async () => {
  healthLoading.value = true
  try {
    const params: any = { page: healthPagination.page, page_size: healthPagination.page_size }
    if (healthSearch.elder_id) params.elder_id = healthSearch.elder_id
    if (healthSearch.metric_type) params.metric_type = healthSearch.metric_type

    const res: any = await api.get('/health/metrics', { params })
    if (res.code === 200) {
      metrics.value = res.data.items || []
      healthPagination.total = res.data.total || 0
    }
  } catch (error) {
    console.error('获取健康指标失败', error)
  } finally {
    healthLoading.value = false
  }
}

const getLatestMetrics = async () => {
  try {
    const res: any = await api.get('/health/latest')
    if (res.code === 200 && res.data) latestMetrics.value = res.data
  } catch (error) {
    console.error('获取最新指标失败', error)
  }
}

const resetHealthSearch = () => {
  healthSearch.elder_id = ''
  healthSearch.metric_type = ''
  getMetrics()
}

const submitHealthRecord = async () => {
  try {
    const res: any = await api.post('/health/metrics', healthForm)
    if (res.code === 200) {
      ElMessage.success('记录成功')
      showHealthDialog.value = false
      healthFormRef.value?.resetFields()
      getMetrics()
      getLatestMetrics()
    }
  } catch (error) {
    ElMessage.error('记录失败')
  }
}

const getPlans = async () => {
  planLoading.value = true
  try {
    const res: any = await api.get('/care/plans', { params: { page: planPagination.page, page_size: planPagination.page_size } })
    if (res.code === 200) {
      plans.value = res.data.items || []
      planPagination.total = res.data.total || 0
    }
  } catch (error) {
    console.error('获取护理计划失败', error)
  } finally {
    planLoading.value = false
  }
}

const submitPlan = async () => {
  try {
    const res: any = await api.post('/care/plans', planForm)
    if (res.code === 200) {
      ElMessage.success('创建成功')
      showPlanDialog.value = false
      planFormRef.value?.resetFields()
      getPlans()
    }
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const viewPlan = async (row: any) => {
  const res: any = await api.get(`/care/plans/${row.id}`)
  if (res.code === 200) {
    currentPlan.value = res.data
    showDetailDialog.value = true
  }
}

const addTask = (row: any) => {
  currentPlan.value = row
  taskFormRef.value?.resetFields()
  showTaskDialog.value = true
}

const submitTask = async () => {
  try {
    const res: any = await api.post(`/care/plans/${currentPlan.value.id}/tasks`, taskForm)
    if (res.code === 200) {
      ElMessage.success('添加成功')
      showTaskDialog.value = false
      taskFormRef.value?.resetFields()
    }
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const getStatusType = (status: number) => ({ 1: 'success', 2: 'warning', 3: 'info' }[status] || 'info')
const getTaskStatusType = (status: number) => ({ 1: 'warning', 2: 'success', 3: 'info' }[status] || 'info')

// 导出CSV
const exportCSV = () => {
  if (metrics.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }

  // 生成CSV内容
  const headers = ['ID', '老人', '指标类型', '数值', '单位', '记录时间', '备注']
  const rows = metrics.value.map(metric => [
    metric.id,
    metric.elder_name,
    metric.metric_type_name,
    metric.metric_value,
    metric.unit,
    metric.recorded_at,
    metric.notes || ''
  ])

  // 组合CSV内容
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')

  // 创建下载链接
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `健康指标_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 更新图表
const updateChart = async () => {
  if (!chartElderId.value || !chartMetricType.value) {
    ElMessage.warning('请选择老人和指标类型')
    return
  }

  try {
    const res: any = await api.get(`/health/metrics/history/${chartElderId.value}/${chartMetricType.value}`, {
      params: { days: 30 }
    })

    if (res.code === 200) {
      await nextTick()
      if (!chartRef.value) return

      healthChart = echarts.init(chartRef.value)
      const data = res.data || []
      const dates = data.map((item: any) => item.recorded_at.split('T')[0])
      const values = data.map((item: any) => item.value)

      healthChart.setOption({
        title: { text: '健康指标趋势', left: 'center' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45 } },
        yAxis: { type: 'value' },
        series: [{
          name: '指标值',
          type: 'line',
          data: values,
          smooth: true,
          itemStyle: { color: '#409eff' }
        }]
      })
    }
  } catch (error) {
    console.error('获取健康指标历史失败', error)
    ElMessage.error('获取数据失败')
  }
}

const handleAdd = () => {
  if (activeTab.value === 'health') {
    healthFormRef.value?.resetFields()
    showHealthDialog.value = true
  } else {
    planFormRef.value?.resetFields()
    showPlanDialog.value = true
  }
}

onMounted(() => {
  getElders()
  getMetrics()
  getLatestMetrics()
  getPlans()
})
</script>

<style scoped lang="scss">
.page-container { padding: 20px; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
  }

  .header-buttons {
    display: flex;
    gap: 10px;
  }
}

.main-tabs {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
}

.card-container { background: #fff; border-radius: 8px; }

.search-form {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.latest-metrics {
  margin-bottom: 20px;

  .metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    padding: 20px;
    border-radius: 12px;
    text-align: center;

    .metric-label {
      font-size: 14px;
      opacity: 0.9;
      margin-bottom: 8px;
    }

    .metric-value {
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 4px;
    }

    .metric-time {
      font-size: 12px;
      opacity: 0.7;
    }
  }
}

.tasks-section {
  margin-top: 20px;

  h4 {
    margin-bottom: 10px;
    color: #303133;
  }
}
</style>