<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">账目管理</h2>
      <div class="header-buttons">
        <el-button type="success" @click="exportCSV">
          <el-icon><Download /></el-icon>
          导出CSV
        </el-button>
      </div>
    </div>

    <div class="search-form">
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 300px; margin-right: 10px" />
      <el-select v-model="orderStatus" placeholder="订单状态" clearable style="width: 120px; margin-right: 10px">
        <el-option label="待处理" :value="1" />
        <el-option label="已完成" :value="2" />
        <el-option label="已取消" :value="3" />
      </el-select>
      <el-button type="primary" @click="getOrders">搜索</el-button>
      <el-button @click="resetSearch">重置</el-button>
    </div>

    <div class="stats-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总订单数</div>
            <div class="stat-value">{{ totalOrders }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总销售额</div>
            <div class="stat-value">¥{{ totalSales }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">已完成订单</div>
            <div class="stat-value">{{ completedOrders }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">待处理订单</div>
            <div class="stat-value">{{ pendingOrders }}</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-table :data="orders" v-loading="loading" style="margin-top: 20px">
      <el-table-column prop="id" label="订单ID" width="100" />
      <el-table-column prop="serviceName" label="服务名称" />
      <el-table-column prop="elderName" label="老人姓名" width="120" />
      <el-table-column prop="actualAmount" label="价格" width="100">
        <template #default="{ row }">¥{{ row.actualAmount }}</template>
      </el-table-column>
      <el-table-column prop="orderTime" label="订单时间" width="180" />
      <el-table-column label="预约服务时间" width="180">
        <template #default="{ row }">
          {{ row.appointmentDate }} {{ row.appointmentTime }}
        </template>
      </el-table-column>
      <el-table-column prop="statusName" label="状态" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.status === 1" type="warning">{{ row.statusName }}</el-tag>
          <el-tag v-else-if="row.status === 2" type="primary">{{ row.statusName }}</el-tag>
          <el-tag v-else-if="row.status === 4" type="success">{{ row.statusName }}</el-tag>
          <el-tag v-else type="info">{{ row.statusName }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="notes" label="备注" show-overflow-tooltip />
    </el-table>

    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.page_size"
      :total="pagination.total"
      :page-sizes="[10, 20, 30, 50]"
      layout="total, sizes, prev, pager, next"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 20px; justify-content: flex-end"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import api from '@/store/auth'

const loading = ref(false)
const orders = ref<any[]>([])
const dateRange = ref([])
const orderStatus = ref('')

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const totalOrders = computed(() => pagination.total)
const totalSales = computed(() => {
  // 计算当前页订单的总金额
  const total = orders.value.reduce((sum, order) => sum + (order.actualAmount || order.totalAmount || 0), 0)
  return total.toFixed(2)
})
const completedOrders = computed(() => {
  return orders.value.filter(order => order.status === 2).length
})
const pendingOrders = computed(() => {
  return orders.value.filter(order => order.status === 1).length
})

const getOrders = async () => {
  loading.value = true
  try {
    const params: any = { page: pagination.page, page_size: pagination.page_size }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (orderStatus.value) {
      params.status = orderStatus.value
    }
    const res: any = await api.get('/orders/', { params })
    if (res.code === 200) {
      orders.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('获取订单列表失败', error)
  } finally {
    loading.value = false
  }
}

const exportCSV = () => {
  if (orders.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }

  // 生成CSV内容
  const headers = ['订单ID', '服务名称', '老人姓名', '价格', '订单时间', '预约服务时间', '状态', '备注']
  const rows = orders.value.map(order => [
    order.id,
    order.serviceName,
    order.elderName,
    order.actualAmount || order.totalAmount,
    order.orderTime,
    (order.appointmentDate || '') + ' ' + (order.appointmentTime || ''),
    order.statusName,
    order.notes || ''
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
  link.setAttribute('download', `账目_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const resetSearch = () => {
  dateRange.value = []
  orderStatus.value = ''
  getOrders()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  getOrders()
}

const handleCurrentChange = (current: number) => {
  pagination.page = current
  getOrders()
}

onMounted(() => {
  getOrders()
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

.search-form {
  display: flex;
  align-items: center;
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.stats-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

  .stat-item {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    border-radius: 8px;

    .stat-label {
      font-size: 14px;
      opacity: 0.9;
      margin-bottom: 8px;
    }

    .stat-value {
      font-size: 24px;
      font-weight: 700;
    }
  }
}
</style>
