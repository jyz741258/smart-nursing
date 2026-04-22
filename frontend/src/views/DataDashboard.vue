<template>
  <div class="data-dashboard">
    <div class="role-indicator admin">
      <span class="role-icon">📊</span>
      <span class="role-text">数据统计大屏</span>
    </div>

    <div class="page-header">
      <div>
        <h2 class="page-title">智慧护理平台数据中心</h2>
        <p class="page-desc">实时监控系统运行状态和关键指标</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData"><el-icon><Refresh /></el-icon>刷新数据</el-button>
        <el-button type="success" @click="exportData"><el-icon><Download /></el-icon>导出数据</el-button>
      </div>
    </div>

    <!-- 关键指标卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card elder">
          <div class="card-icon"><el-icon><User /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ stats.elderCount }}</div>
            <div class="card-label">老人总数</div>
            <div class="card-trend positive">
              <el-icon><ArrowUp /></el-icon>
              <span>5.2%</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card nurse">
          <div class="card-icon"><el-icon><UserFilled /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ stats.nurseCount }}</div>
            <div class="card-label">护理人员</div>
            <div class="card-trend positive">
              <el-icon><ArrowUp /></el-icon>
              <span>3.8%</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card family">
          <div class="card-icon"><el-icon><House /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ stats.familyCount }}</div>
            <div class="card-label">家属数量</div>
            <div class="card-trend positive">
              <el-icon><ArrowUp /></el-icon>
              <span>8.1%</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card order">
          <div class="card-icon"><el-icon><Document /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ stats.todayOrders }}</div>
            <div class="card-label">今日订单</div>
            <div class="card-trend positive">
              <el-icon><ArrowUp /></el-icon>
              <span>12.5%</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 主要图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 护理记录统计 -->
      <el-col :span="16">
        <div class="card-container">
          <div class="card-header">
            <span class="card-title">护理记录统计</span>
            <el-radio-group v-model="chartPeriod" size="small">
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
              <el-radio-button label="year">全年</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="nursingChartRef" style="height: 400px"></div>
        </div>
      </el-col>
      
      <!-- 服务类型分布 -->
      <el-col :span="8">
        <div class="card-container">
          <div class="card-header"><span class="card-title">服务类型分布</span></div>
          <div ref="pieChartRef" style="height: 400px"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 次要图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 健康指标趋势 -->
      <el-col :span="12">
        <div class="card-container">
          <div class="card-header"><span class="card-title">健康指标趋势</span></div>
          <div ref="healthChartRef" style="height: 350px"></div>
        </div>
      </el-col>
      
      <!-- 紧急呼叫分析 -->
      <el-col :span="12">
        <div class="card-container">
          <div class="card-header"><span class="card-title">紧急呼叫分析</span></div>
          <div ref="emergencyChartRef" style="height: 350px"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 数据表格区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 最近护理记录 -->
      <el-col :span="12">
        <div class="card-container">
          <div class="card-header"><span class="card-title">最近护理记录</span></div>
          <el-table :data="recentRecords" style="width: 100%" stripe>
            <el-table-column prop="elder_name" label="老人" width="120" />
            <el-table-column prop="type" label="护理类型" width="120" />
            <el-table-column prop="content" label="护理内容" />
            <el-table-column prop="created_at" label="护理时间" width="180">
              <template #default="{ row }">
                {{ row.created_at ? new Date(row.created_at).toLocaleString() : '-' }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      
      <!-- 紧急呼叫记录 -->
      <el-col :span="12">
        <div class="card-container">
          <div class="card-header"><span class="card-title">紧急呼叫记录</span></div>
          <el-table :data="emergencyCalls" style="width: 100%" stripe>
            <el-table-column prop="elder_name" label="老人" width="120" />
            <el-table-column prop="type" label="呼叫类型" width="100" />
            <el-table-column prop="location" label="位置" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag 
                  :type="row.status === 'pending' ? 'warning' : row.status === 'responding' ? 'info' : row.status === 'completed' ? 'success' : 'danger'" 
                  size="small"
                >
                  {{ row.status === 'pending' ? '待处理' : row.status === 'responding' ? '处理中' : row.status === 'completed' ? '已完成' : '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="呼叫时间" width="180">
              <template #default="{ row }">
                {{ row.created_at ? new Date(row.created_at).toLocaleString() : '-' }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '@/store/auth'

// 图表引用
const chartPeriod = ref('week')
const nursingChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
const healthChartRef = ref<HTMLElement>()
const emergencyChartRef = ref<HTMLElement>()

// 图表实例
let nursingChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null
let healthChart: echarts.ECharts | null = null
let emergencyChart: echarts.ECharts | null = null

// 统计数据
const stats = reactive({ 
  elderCount: 128, 
  nurseCount: 32, 
  familyCount: 216, 
  todayOrders: 45 
})

// 最近护理记录
const recentRecords = ref([
  { id: 1, elder_name: '张三', type: '日常护理', content: '协助老人进行日常活动', created_at: new Date().toISOString() },
  { id: 2, elder_name: '李四', type: '健康监测', content: '测量血压和心率', created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: 3, elder_name: '王五', type: '康复训练', content: '进行肢体康复训练', created_at: new Date(Date.now() - 7200000).toISOString() },
  { id: 4, elder_name: '赵六', type: '饮食护理', content: '协助准备营养餐食', created_at: new Date(Date.now() - 10800000).toISOString() },
  { id: 5, elder_name: '孙七', type: '安全护理', content: '检查房间安全设施', created_at: new Date(Date.now() - 14400000).toISOString() }
])

// 紧急呼叫记录
const emergencyCalls = ref([
  { id: 1, elder_id: 1, elder_name: '张三', type: 'sos', location: '老人房间', status: 'completed', created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: 2, elder_id: 2, elder_name: '李四', type: 'sos', location: '卫生间', status: 'responding', created_at: new Date(Date.now() - 1800000).toISOString() },
  { id: 3, elder_id: 3, elder_name: '王五', type: 'help', location: '客厅', status: 'completed', created_at: new Date(Date.now() - 7200000).toISOString() }
])

// 加载仪表盘数据
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

// 获取护理记录统计数据
const getWeeklyNursingData = async () => {
  try {
    const period = chartPeriod.value
    const res: any = await api.get('/statistics/weekly-nursing', { params: { period } })
    if (res.code === 200 && nursingChartRef.value) {
      const chartData = res.data || []
      const days = chartData.map((d: any) => d.day)
      const counts = chartData.map((d: any) => d.count)
      nursingChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: days, axisLabel: { color: '#b8c5d6' } },
        yAxis: { type: 'value', axisLabel: { color: '#b8c5d6' } },
        series: [{
          type: 'bar', 
          data: counts,
          itemStyle: { 
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#409eff' },
              { offset: 1, color: '#66b1ff' }
            ])
          },
          emphasis: {
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#66b1ff' },
                { offset: 1, color: '#91c1ff' }
              ])
            }
          }
        }]
      })
    }
  } catch (error) {
    console.error('获取护理记录数据失败', error)
    // 模拟数据
    if (nursingChartRef.value) {
      const days = chartPeriod.value === 'week' 
        ? ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        : chartPeriod.value === 'month' 
          ? Array.from({length: 31}, (_, i) => `${i + 1}日`)
          : ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
      const counts = days.map(() => Math.floor(Math.random() * 50) + 10)
      nursingChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: days, axisLabel: { color: '#b8c5d6' } },
        yAxis: { type: 'value', axisLabel: { color: '#b8c5d6' } },
        series: [{
          type: 'bar', 
          data: counts,
          itemStyle: { 
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#409eff' },
              { offset: 1, color: '#66b1ff' }
            ])
          }
        }]
      })
    }
  }
}

// 获取服务类型分布数据
const getServiceDistribution = async () => {
  try {
    const res: any = await api.get('/statistics/service-distribution')
    if (res.code === 200 && pieChartRef.value) {
      const serviceData = res.data || []
      pieChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: 0, textStyle: { color: '#b8c5d6' } },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          data: serviceData,
          label: { color: '#b8c5d6' },
          itemStyle: {
            borderRadius: 10,
            borderColor: '#232d3b',
            borderWidth: 2
          }
        }]
      })
    }
  } catch (error) {
    console.error('获取服务类型分布数据失败', error)
    // 模拟数据
    if (pieChartRef.value) {
      const serviceData = [
        { value: 35, name: '日常护理' },
        { value: 25, name: '健康监测' },
        { value: 20, name: '康复训练' },
        { value: 15, name: '饮食护理' },
        { value: 5, name: '安全护理' }
      ]
      pieChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: 0, textStyle: { color: '#b8c5d6' } },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          data: serviceData,
          label: { color: '#b8c5d6' },
          itemStyle: {
            borderRadius: 10,
            borderColor: '#232d3b',
            borderWidth: 2
          }
        }]
      })
    }
  }
}

// 初始化健康指标趋势图表
const initHealthChart = () => {
  if (healthChartRef.value) {
    healthChart = echarts.init(healthChartRef.value)
    const option = {
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['血压', '心率', '血糖'],
        textStyle: { color: '#b8c5d6' }
      },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月'],
        axisLabel: { color: '#b8c5d6' }
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#b8c5d6' }
      },
      series: [
        {
          name: '血压',
          type: 'line',
          data: [120, 125, 118, 130, 122, 115],
          smooth: true,
          itemStyle: { color: '#409eff' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ])
          }
        },
        {
          name: '心率',
          type: 'line',
          data: [75, 78, 80, 72, 76, 74],
          smooth: true,
          itemStyle: { color: '#67c23a' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
              { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
            ])
          }
        },
        {
          name: '血糖',
          type: 'line',
          data: [5.6, 5.8, 6.0, 5.7, 5.9, 5.5],
          smooth: true,
          itemStyle: { color: '#e6a23c' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(230, 162, 60, 0.3)' },
              { offset: 1, color: 'rgba(230, 162, 60, 0.1)' }
            ])
          }
        }
      ]
    }
    healthChart.setOption(option)
  }
}

// 初始化紧急呼叫分析图表
const initEmergencyChart = () => {
  if (emergencyChartRef.value) {
    emergencyChart = echarts.init(emergencyChartRef.value)
    const option = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月'],
        axisLabel: { color: '#b8c5d6' }
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#b8c5d6' }
      },
      series: [
        {
          name: '紧急呼叫',
          type: 'bar',
          data: [5, 8, 12, 7, 10, 6],
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#f56c6c' },
              { offset: 1, color: '#fab6b6' }
            ])
          }
        },
        {
          name: '响应时间(分钟)',
          type: 'line',
          yAxisIndex: 1,
          data: [2.5, 3.2, 2.8, 3.5, 2.9, 2.7],
          itemStyle: { color: '#409eff' }
        }
      ],
      yAxis: [
        {
          type: 'value',
          name: '呼叫次数',
          axisLabel: { color: '#b8c5d6' }
        },
        {
          type: 'value',
          name: '响应时间',
          axisLabel: { color: '#b8c5d6' }
        }
      ]
    }
    emergencyChart.setOption(option)
  }
}

// 刷新数据
const refreshData = async () => {
  await getDashboardStats()
  await updateCharts()
  ElMessage.success('数据已刷新')
}

// 导出数据
const exportData = () => {
  ElMessage.info('数据导出功能开发中')
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
  if (healthChart) {
    healthChart.dispose()
    healthChart = null
  }
  if (emergencyChart) {
    emergencyChart.dispose()
    emergencyChart = null
  }
}

// 更新图表
const updateCharts = async () => {
  // 清理旧图表
  disposeCharts()

  // 等待DOM更新
  await nextTick()

  // 延迟初始化，确保容器有尺寸
  setTimeout(() => {
    let chartInitialized = false

    if (nursingChartRef.value && nursingChartRef.value.clientWidth > 0) {
      nursingChart = echarts.init(nursingChartRef.value)
      getWeeklyNursingData()
      chartInitialized = true
    }

    if (pieChartRef.value && pieChartRef.value.clientWidth > 0) {
      pieChart = echarts.init(pieChartRef.value)
      getServiceDistribution()
      chartInitialized = true
    }

    if (healthChartRef.value && healthChartRef.value.clientWidth > 0) {
      initHealthChart()
      chartInitialized = true
    }

    if (emergencyChartRef.value && emergencyChartRef.value.clientWidth > 0) {
      initEmergencyChart()
      chartInitialized = true
    }

    // 如果图表未初始化，延迟重试
    if (!chartInitialized) {
      setTimeout(updateCharts, 200)
    }
  }, 500)
}

// 监听周期切换
watch(chartPeriod, () => {
  getWeeklyNursingData()
})

// 处理窗口大小变化
const handleResize = () => {
  nursingChart?.resize()
  pieChart?.resize()
  healthChart?.resize()
  emergencyChart?.resize()
}

// 组件挂载
onMounted(async () => {
  await getDashboardStats()
  updateCharts()
  window.addEventListener('resize', handleResize)
})

// 组件卸载
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})
</script>

<style scoped lang="scss">
.data-dashboard {
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
      radial-gradient(ellipse at 20% 20%, rgba(64, 158, 255, 0.12) 0%, transparent 40%),
      radial-gradient(ellipse at 80% 80%, rgba(103, 194, 58, 0.08) 0%, transparent 40%),
      radial-gradient(ellipse at 50% 50%, rgba(230, 162, 60, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 10% 90%, rgba(245, 108, 108, 0.05) 0%, transparent 30%),
      radial-gradient(circle at 90% 10%, rgba(102, 126, 234, 0.05) 0%, transparent 30%);
    animation: dashboardBgFloat 25s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
  }

  // 网格背景
  &::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: 
      linear-gradient(rgba(64, 158, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(64, 158, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: gridMove 20s linear infinite;
    pointer-events: none;
    z-index: 0;
  }

  @keyframes dashboardBgFloat {
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
    background: linear-gradient(135deg, #409eff, #66b1ff);
    color: #ffffff;
    box-shadow: 0 4px 24px rgba(64, 158, 255, 0.5), 0 0 0 2px rgba(64, 158, 255, 0.2);
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    animation: fadeInDown 0.6s ease-out;
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
  border-bottom: 1px solid rgba(64, 158, 255, 0.2);
  
  .page-title { 
    font-size: 28px; 
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
  border: 1px solid rgba(64, 158, 255, 0.2);
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
    box-shadow: 0 16px 40px rgba(64, 158, 255, 0.25);
    border-color: rgba(64, 158, 255, 0.4);

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
    flex: 1;

    .card-value {
      font-size: 34px;
      font-weight: 800;
      color: #ffffff;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      filter: drop-shadow(0 0 8px rgba(64, 158, 255, 0.3));
    }

    .card-label {
      font-size: 14px;
      color: #9aafc0;
      margin-top: 4px;
      font-weight: 500;
    }

    .card-trend {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      margin-top: 8px;

      &.positive {
        color: #67c23a;
      }

      &.negative {
        color: #f56c6c;
      }
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
  border: 1px solid rgba(64, 158, 255, 0.2);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 12px 32px rgba(64, 158, 255, 0.15);
    border-color: rgba(64, 158, 255, 0.3);
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
      border-left: 3px solid #409eff;
    }
  }
}

// 表格样式
:deep(.el-table) {
  background: transparent;
  border-radius: 8px;

  th.el-table__cell {
    background: rgba(45, 55, 70, 0.9);
    color: #ffffff;
    font-weight: 600;
    border-bottom: 1px solid rgba(64, 158, 255, 0.2);
  }

  td.el-table__cell {
    color: #b8c5d6;
    border-bottom: 1px solid rgba(64, 158, 255, 0.1);
  }

  .el-table__row {
    transition: background-color 0.3s ease;

    &:hover {
      background-color: rgba(45, 55, 70, 0.7);
    }
  }

  .el-table__row.el-table__row--striped {
    background-color: rgba(45, 55, 70, 0.3);

    &:hover {
      background-color: rgba(45, 55, 70, 0.7);
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .data-dashboard {
    padding: 10px;
  }

  .page-title {
    font-size: 24px !important;
  }

  .stats-card {
    padding: 20px;
  }

  .card-container {
    padding: 16px;
  }

  .card-value {
    font-size: 28px !important;
  }
}
</style>