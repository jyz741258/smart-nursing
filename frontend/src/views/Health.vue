<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">健康监测</h2>
      <el-button type="primary" @click="showAddDialog = true">
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
      <el-row :gutter="20" class="latest-metrics" v-if="latestMetrics">
        <el-col :span="6" v-for="(value, key) in latestMetrics" :key="key">
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
        <el-table-column prop="metric_value" label="数值" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'
import type { HealthMetric, Elder } from '@/types'

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