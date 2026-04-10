<template>
  <div class="dashboard">
    <div class="page-header">
      <h2 class="page-title">工作台</h2>
      <el-button type="primary" @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card">
          <el-icon class="stats-icon"><User /></el-icon>
          <div class="stats-content">
            <div class="stats-value">{{ stats.elder_count }}</div>
            <div class="stats-label">老人总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card success">
          <el-icon class="stats-icon"><Document /></el-icon>
          <div class="stats-content">
            <div class="stats-value">{{ stats.today_nursing_count }}</div>
            <div class="stats-label">今日护理记录</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card warning">
          <el-icon class="stats-icon"><Finished /></el-icon>
          <div class="stats-content">
            <div class="stats-value">{{ stats.today_completed_tasks }}</div>
            <div class="stats-label">今日完成任务</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card info">
          <el-icon class="stats-icon"><Clock /></el-icon>
          <div class="stats-content">
            <div class="stats-value">{{ stats.pending_tasks }}</div>
            <div class="stats-label">待处理任务</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <div class="card-container">
          <div class="card-title">护理记录统计</div>
          <div ref="nursingChartRef" style="height: 300px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card-container">
          <div class="card-title">护理人员工作量</div>
          <div ref="workloadChartRef" style="height: 300px"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 待办任务 -->
    <div class="card-container todo-section">
      <div class="card-title">待办任务</div>
      <el-table :data="pendingTasks" style="width: 100%">
        <el-table-column prop="task_name" label="任务名称" />
        <el-table-column prop="elder_name" label="老人姓名" />
        <el-table-column prop="task_type" label="任务类型" />
        <el-table-column prop="scheduled_time" label="计划时间" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="completeTask(row)">
              完成
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '@/store/auth'
import type { DashboardStats } from '@/types'

const stats = reactive<DashboardStats>({
  today_nursing_count: 0,
  today_completed_tasks: 0,
  elder_count: 0,
  staff_count: 0,
  pending_tasks: 0
})

const pendingTasks = ref<any[]>([])
const nursingChartRef = ref<HTMLElement>()
const workloadChartRef = ref<HTMLElement>()

let nursingChart: echarts.ECharts | null = null
let workloadChart: echarts.ECharts | null = null

const getDashboardData = async () => {
  try {
    const res: any = await api.get('/statistics/dashboard')
    if (res.code === 200) {
      Object.assign(stats, res.data)
    }
  } catch (error) {
    console.error('获取仪表盘数据失败', error)
  }
}

const getTodayTasks = async () => {
  try {
    const res: any = await api.get('/care/tasks/today')
    if (res.code === 200) {
      pendingTasks.value = res.data.filter((t: any) => t.status === 1)
    }
  } catch (error) {
    console.error('获取今日任务失败', error)
  }
}

const getNursingSummary = async () => {
  try {
    const res: any = await api.get('/statistics/nursing-summary')
    if (res.code === 200) {
      updateNursingChart(res.data)
    }
  } catch (error) {
    console.error('获取护理统计失败', error)
  }
}

const getWorkload = async () => {
  try {
    const res: any = await api.get('/statistics/workload')
    if (res.code === 200) {
      updateWorkloadChart(res.data)
    }
  } catch (error) {
    console.error('获取工作量统计失败', error)
  }
}

const updateNursingChart = (data: any[]) => {
  if (!nursingChartRef.value) return

  nursingChart = echarts.init(nursingChartRef.value)
  const nursingTypes = ['日常照护', '医疗护理', '康复训练', '心理疏导', '饮食护理', '清洁护理', '安全护理']
  const values = new Array(7).fill(0)

  data.forEach((item: any) => {
    if (item.nursing_type >= 1 && item.nursing_type <= 7) {
      values[item.nursing_type - 1] = item.count
    }
  })

  nursingChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: nursingTypes },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: { color: '#409eff' }
    }]
  })
}

const updateWorkloadChart = (data: any[]) => {
  if (!workloadChartRef.value) return

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

const completeTask = async (task: any) => {
  try {
    const res: any = await api.post(`/care/tasks/${task.id}/complete`)
    if (res.code === 200) {
      ElMessage.success('任务已完成')
      getTodayTasks()
      getDashboardData()
    }
  } catch (error) {
    console.error('完成任务失败', error)
  }
}

const refreshData = () => {
  getDashboardData()
  getTodayTasks()
  getNursingSummary()
  getWorkload()
}

const handleResize = () => {
  nursingChart?.resize()
  workloadChart?.resize()
}

onMounted(() => {
  getDashboardData()
  getTodayTasks()
  getNursingSummary()
  getWorkload()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  nursingChart?.dispose()
  workloadChart?.dispose()
})
</script>

<style scoped lang="scss">
.dashboard {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.chart-row {
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

.todo-section {
  margin-top: 20px;
}
</style>