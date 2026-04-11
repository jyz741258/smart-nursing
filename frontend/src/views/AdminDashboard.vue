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
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '@/store/auth'

const chartPeriod = ref('week')
const nursingChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
let nursingChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

const userName = ref('管理员')
const stats = reactive({ elderCount: 45, nurseCount: 12, familyCount: 38, todayOrders: 28 })

const pendingTasks = ref([
  { task_name: '日常护理', elder_name: '张三', nurse_name: '李护理', status: '待执行' },
  { task_name: '健康监测', elder_name: '李四', nurse_name: '王护理', status: '待执行' }
])

const refreshData = () => {
  ElMessage.success('数据已刷新')
  updateCharts()
}

const updateCharts = () => {
  if (nursingChartRef.value) {
    nursingChart = echarts.init(nursingChartRef.value)
    nursingChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [12, 15, 10, 18, 14, 8, 6], itemStyle: { color: '#409eff' } }]
    })
  }

  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: 45, name: '日常照护' },
          { value: 25, name: '医疗护理' },
          { value: 15, name: '康复训练' },
          { value: 15, name: '健康监测' }
        ]
      }]
    })
  }
}

const handleResize = () => {
  nursingChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
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
</style>