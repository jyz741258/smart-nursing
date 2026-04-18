<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">健康监测</h2>
      <el-button v-if="isAdminOrNurse" type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        记录指标
      </el-button>
    </div>

    <div class="card-container">
      <div class="search-form">
        <el-select v-model="searchForm.elder_id" placeholder="选择老人" clearable style="width: 150px">
          <el-option v-for="elder in elders" :key="elder.id" :label="elder.name" :value="elder.id" />
        </el-select>
        <el-select v-model="searchForm.metric_type" placeholder="指标类型" clearable style="width: 150px">
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
        <el-button @click="resetSearch">重置</el-button>
      </div>

      <!-- 最新指标卡片 -->
      <el-row :gutter="20" class="latest-metrics" v-if="formattedLatestMetrics && Object.keys(formattedLatestMetrics).length > 0">
        <el-col :span="6" v-for="(value, key) in formattedLatestMetrics" :key="key">
          <div class="metric-card">
            <div class="metric-label">{{ key }}</div>
            <div class="metric-value">{{ value.value }} {{ value.unit }}</div>
            <div class="metric-time">{{ value.recorded_at }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 指标记录列表 -->
      <el-table :data="metrics" v-loading="loading" style="margin-top: 20px">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="elder_name" label="老人" />
        <el-table-column prop="metric_type_name" label="指标类型" />
        <el-table-column label="数值" width="120">
          <template #default="{ row }">
            {{ formatMetricValue(row.metric_value, row.metric_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="100" />
        <el-table-column prop="recorded_at" label="记录时间" width="180" />
        <el-table-column prop="notes" label="备注" show-overflow-tooltip />
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="getMetrics"
        @current-change="getMetrics"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </div>

    <!-- 添加指标对话框 -->
    <el-dialog v-model="showAddDialog" title="记录健康指标" width="500px">
      <el-form ref="formRef" :model="metricForm" label-width="100px">
        <el-form-item label="老人" prop="elder_id">
          <el-select v-model="metricForm.elder_id" placeholder="请选择老人">
            <el-option v-for="elder in elders" :key="elder.id" :label="elder.name" :value="elder.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="指标类型" prop="metric_type">
          <el-select v-model="metricForm.metric_type" placeholder="请选择指标类型">
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
        <el-form-item label="数值" prop="metric_value">
          <el-input-number v-model="metricForm.metric_value" :precision="1" :step="0.1" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="metricForm.notes" type="textarea" :rows="2" placeholder="备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'
import { useAuthStore } from '@/store/auth'
import type { HealthMetric, Elder } from '@/types'

const authStore = useAuthStore()

const isAdminOrNurse = computed(() => {
  const userType = authStore.userInfo?.user_type
  return userType === 2 || userType === 3
})

const loading = ref(false)
const showAddDialog = ref(false)

const metrics = ref<HealthMetric[]>([])
const elders = ref<Elder[]>([])
const latestMetrics = ref<any>(null)

const searchForm = reactive({
  elder_id: null as number | null,
  metric_type: null as number | null
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const metricForm = reactive({
  elder_id: null as number | null,
  metric_type: null as number | null,
  metric_value: 0,
  notes: ''
})

const getMetrics = async () => {
  loading.value = true
  try {
    const res: any = await api.get('/health/metrics', {
      params: {
        page: pagination.page,
        page_size: pagination.page_size,
        ...searchForm
      }
    })
    if (res.code === 200) {
      metrics.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('获取健康指标失败', error)
  } finally {
    loading.value = false
  }
}

const getLatestMetrics = async () => {
  if (!searchForm.elder_id) return
  try {
    const res: any = await api.get(`/health/metrics/latest/${searchForm.elder_id}`)
    if (res.code === 200) {
      latestMetrics.value = res.data
    }
  } catch (error) {
    console.error('获取最新指标失败', error)
  }
}

const getElders = async () => {
  try {
    const res: any = await api.get('/users/elder/list')
    if (res.code === 200) {
      elders.value = res.data
    }
  } catch (error) {
    console.error('获取老人列表失败', error)
  }
}

// 指标类型对应的单位映射
const metricUnitMap: Record<number, string> = {
  1: '℃',      // 体温
  2: 'mmHg',   // 血压-收缩压
  3: 'mmHg',   // 血压-舒张压
  4: '次/分',  // 心率
  5: '%',      // 血氧
  6: 'mmol/L', // 血糖
  7: 'kg',     // 体重
  8: 'cm',     // 身高
  9: 'h',      // 睡眠时长
  10: '步'     // 今日步数
}

// 指标类型显示名称映射
const metricTypeNameMap: Record<number, string> = {
  1: '体温',
  2: '血压-收缩压',
  3: '血压-舒张压',
  4: '心率',
  5: '血氧',
  6: '血糖',
  7: '体重',
  8: '身高',
  9: '睡眠时长',
  10: '今日步数'
}

// 格式化健康指标值（取整或保留小数）
const formatMetricValue = (value: number | undefined, metricType: number): string => {
  if (value === undefined || value === null) return '--'
  
  const numValue = Number(value)
  
  switch (metricType) {
    case 1: // 体温 - 保留1位小数
      return numValue.toFixed(1)
    case 2: // 收缩压 - 整数
    case 3: // 舒张压 - 整数
    case 4: // 心率 - 整数
    case 10: // 步数 - 整数
      return String(Math.round(numValue))
    case 5: // 血氧 - 保留1位小数
    case 6: // 血糖 - 保留1位小数（或2位）
      return numValue.toFixed(1)
    case 7: // 体重 - 保留1位小数
    case 8: // 身高 - 保留1位小数
      return numValue.toFixed(1)
    case 9: // 睡眠时长 - 保留1位小数
      return numValue.toFixed(1)
    default:
      return String(numValue)
  }
}

// 格式化后的最新指标（用于显示）
const formattedLatestMetrics = computed(() => {
  const formatted: Record<string, { value: string, unit: string, recorded_at: string }> = {}
  if (!latestMetrics.value || typeof latestMetrics.value !== 'object') return formatted
  
  for (const [key, data] of Object.entries(latestMetrics.value)) {
    const metricData = data as any
    const metricType = getMetricTypeByKey(key)
    formatted[key] = {
      value: formatMetricValue(metricData.value, metricType),
      unit: metricData.unit || '',
      recorded_at: metricData.recorded_at || ''
    }
  }
  return formatted
})

// 根据指标名称获取类型编号
const getMetricTypeByKey = (key: string): number => {
  const map: Record<string, number> = {
    '体温': 1,
    '血压-收缩压': 2,
    '血压-舒张压': 3,
    '心率': 4,
    '血氧': 5,
    '血糖': 6,
    '体重': 7,
    '身高': 8,
    '睡眠时长': 9,
    '今日步数': 10
  }
  return map[key] || 0
}

const resetSearch = () => {
  searchForm.elder_id = null
  searchForm.metric_type = null
  pagination.page = 1
  latestMetrics.value = null
  getMetrics()
}

const submitForm = async () => {
  try {
    const res: any = await api.post('/health/metrics', metricForm)
    if (res.code === 200) {
      ElMessage.success('记录成功')
      showAddDialog.value = false
      getMetrics()
      getLatestMetrics()
    }
  } catch (error) {
    console.error('记录失败', error)
  }
}

watch(() => searchForm.elder_id, () => {
  getLatestMetrics()
})

onMounted(() => {
  getMetrics()
  getElders()
})
</script>

<style scoped lang="scss">
.latest-metrics {
  margin-top: 20px;
}

.metric-card {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  text-align: center;

  .metric-label {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 4px;
  }

  .metric-time {
    font-size: 12px;
    color: #c0c4cc;
  }
}
</style>