<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">数据统计</h2>
      <el-select v-model="dateRange" style="width: 200px" @change="handleDateChange">
        <el-option label="最近7天" :value="7" />
        <el-option label="最近30天" :value="30" />
        <el-option label="最近90天" :value="90" />
      </el-select>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <div class="card-container stats-card">
          <div ref="nursingPieChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="16">
        <div class="card-container stats-card">
          <div ref="nursingTrendChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="12">
        <div class="card-container">
          <h4 class="card-title">护理人员工作量</h4>
          <div ref="workloadChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card-container">
          <h4 class="card-title">护理计划执行进度</h4>
          <el-table :data="planProgress" style="margin-top: 15px">
            <el-table-column prop="title" label="计划名称" />
            <el-table-column prop="elder_name" label="老人" />
            <el-table-column prop="completed_tasks" label="已完成" width="80" />
            <el-table-column prop="total_tasks" label="总数" width="80" />
            <el-table-column prop="progress_rate" label="进度" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.progress_rate" />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <div class="card-container" style="margin-top: 20px">
      <h4 class="card-title">健康预警</h4>
      <el-table :data="healthAlerts" v-loading="loading">
        <el-table-column prop="elder_name" label="老人" />
        <el-table-column prop="metric_type_name" label="指标类型" />
        <el-table-column prop="metric_value" label="数值" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="recorded_at" label="时间" width="180" />
        <el-table-column prop="notes" label="备注" show-overflow-tooltip />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '@/store/auth'

const dateRange = ref(7)
const loading = ref(false)

const nursingPieChartRef = ref<HTMLElement>()
const nursingTrendChartRef = ref<HTMLElement>()
const workloadChartRef = ref<HTMLElement>()

let nursingPieChart: echarts.ECharts | null = null
let nursingTrendChart: echarts.ECharts | null = null
let workloadChart: echarts.ECharts | null = null

const planProgress = ref<any[]>([])
const healthAlerts = ref<any[]>([])

const nursingTypes = ['日常照护', '医疗护理', '康复训练', '心理疏导', '饮食护理', '清洁护理', '安全护理']

const getNursingSummary = async () => {
  try {
    const res: any = await api.get('/statistics/nursing-summary', {
      params: { days: dateRange.value }
    })
    if (res.code === 200) {
      await updatePieChart(res.data)
    }
  } catch (error) {
    console.error('获取护理统计失败', error)
  }
}

const getWorkload = async () => {
  try {
    const res: any = await api.get('/statistics/workload', {
      params: { days: dateRange.value }
    })
    if (res.code === 200) {
      await updateWorkloadChart(res.data)
    }
  } catch (error) {
    console.error('获取工作量失败', error)
  }
}

const getPlanProgress = async () => {
  try {
    const res: any = await api.get('/statistics/care-plan-progress')
    if (res.code === 200) {
      planProgress.value = res.data
    }
  } catch (error) {
    console.error('获取计划进度失败', error)
  }
}

const getHealthAlerts = async () => {
  loading.value = true
  try {
    const res: any = await api.get('/statistics/alerts', {
      params: { days: dateRange.value }
    })
    if (res.code === 200) {
      healthAlerts.value = res.data
    }
  } catch (error) {
    console.error('获取健康预警失败', error)
  } finally {
    loading.value = false
  }
}

const updatePieChart = async (data: any[]) => {
  if (!nursingPieChartRef.value) return

  console.log('[Debug] updatePieChart called, data:', data)

  // 等待DOM更新
  await nextTick()

  // 循环等待容器有尺寸
  let retryCount = 0
  const maxRetries = 10
  while (nursingPieChartRef.value && (nursingPieChartRef.value.clientWidth === 0 || nursingPieChartRef.value.clientHeight === 0) && retryCount < maxRetries) {
    console.log('[Debug] Pie chart container not ready, waiting...', retryCount)
    await new Promise(resolve => setTimeout(resolve, 100))
    retryCount++
  }

  if (!nursingPieChartRef.value) return

  console.log('[Debug] Pie chart dimensions:', nursingPieChartRef.value.clientWidth, nursingPieChartRef.value.clientHeight)

  // 清理旧实例
  if (nursingPieChart) {
    nursingPieChart.dispose()
  }

  nursingPieChart = echarts.init(nursingPieChartRef.value)
  const values = new Array(7).fill(0)

  data.forEach((item: any) => {
    if (item.nursing_type >= 1 && item.nursing_type <= 7) {
      values[item.nursing_type - 1] = item.count
    }
  })

  nursingPieChart.setOption({
    title: {
      text: '护理类型分布',
      left: 'center',
      top: 5,
      textStyle: {
        fontSize: 12,
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      left: 'center',
      itemGap: 8,
      icon: 'circle',
      textStyle: {
        fontSize: 10,
        color: '#666'
      }
    },
    series: [{
      type: 'pie',
      radius: ['30%', '50%'],  // 进一步减小半径
      center: ['50%', '42%'],  // 调整中心点位置
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 3,
        borderColor: '#fff',
        borderWidth: 1.5
      },
      label: {
        show: true,
        position: 'outside',
        formatter: '{b}\n{d}%',
        fontSize: 9,
        color: '#333'
      },
      labelLine: {
        show: true,
        length: 6,
        length2: 10,
        lineStyle: {
          width: 1
        }
      },
      data: nursingTypes.map((name, index) => ({
        name,
        value: values[index]
      }))
    }]
  })
}

const updateWorkloadChart = async (data: any[]) => {
  if (!workloadChartRef.value) return

  console.log('[Debug] updateWorkloadChart called, data:', data)

  // 等待DOM更新
  await nextTick()

  // 循环等待容器有尺寸
  let retryCount = 0
  const maxRetries = 10
  while (workloadChartRef.value && (workloadChartRef.value.clientWidth === 0 || workloadChartRef.value.clientHeight === 0) && retryCount < maxRetries) {
    console.log('[Debug] Workload chart container not ready, waiting...', retryCount)
    await new Promise(resolve => setTimeout(resolve, 100))
    retryCount++
  }

  if (!workloadChartRef.value) return

  console.log('[Debug] Workload chart dimensions:', workloadChartRef.value.clientWidth, workloadChartRef.value.clientHeight)

  // 清理旧实例
  if (workloadChart) {
    workloadChart.dispose()
  }

  workloadChart = echarts.init(workloadChartRef.value)
  const names = data.map((item: any) => item.staff_name)
  const counts = data.map((item: any) => item.record_count)

  workloadChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: names },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: counts,
      itemStyle: { color: '#67c23a' }
    }]
  })
}

const updateTrendChart = async () => {
  if (!nursingTrendChartRef.value) return

  console.log('[Debug] updateTrendChart called')

  // 等待DOM更新
  await nextTick()

  // 循环等待容器有尺寸
  let retryCount = 0
  const maxRetries = 10
  while (nursingTrendChartRef.value && (nursingTrendChartRef.value.clientWidth === 0 || nursingTrendChartRef.value.clientHeight === 0) && retryCount < maxRetries) {
    console.log('[Debug] Trend chart container not ready, waiting...', retryCount)
    await new Promise(resolve => setTimeout(resolve, 100))
    retryCount++
  }

  if (!nursingTrendChartRef.value) return

  console.log('[Debug] Trend chart dimensions:', nursingTrendChartRef.value.clientWidth, nursingTrendChartRef.value.clientHeight)

  // 清理旧实例
  if (nursingTrendChart) {
    nursingTrendChart.dispose()
  }

  nursingTrendChart = echarts.init(nursingTrendChartRef.value)
  const dates = []
  const now = new Date()
  for (let i = dateRange.value - 1; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])
  }

  nursingTrendChart.setOption({
    title: { text: '护理记录趋势', left: 'center', top: 10 },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 10, left: 'center' },
    xAxis: { type: 'category', data: dates },
    yAxis: { type: 'value' },
    series: [{
      name: '护理记录',
      type: 'line',
      data: dates.map(() => Math.floor(Math.random() * 20) + 5),
      smooth: true,
      itemStyle: { color: '#409eff' }
    }]
  })
}

const handleDateChange = async () => {
  await getNursingSummary()
  await getWorkload()
  getHealthAlerts()
  await updateTrendChart()
}

const handleResize = () => {
  nursingPieChart?.resize()
  nursingTrendChart?.resize()
  workloadChart?.resize()
}

onMounted(async () => {
  await getNursingSummary()
  await getWorkload()
  getPlanProgress()
  getHealthAlerts()
  await updateTrendChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  nursingPieChart?.dispose()
  nursingTrendChart?.dispose()
  workloadChart?.dispose()
})
</script>

<style scoped lang="scss">
.stats-row {
  margin-bottom: 20px;
}

.card-container {
  .card-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
  }
}

// 图表容器必须有明确的宽高
.chart-container {
  width: 100%;
  height: 400px;  // 增加到400px提供更多空间
  min-height: 400px;
}
</style>