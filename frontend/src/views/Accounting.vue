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
        <el-option label="待支付" :value="1" />
        <el-option label="待服务" :value="2" />
        <el-option label="服务中" :value="3" />
        <el-option label="已完成" :value="4" />
        <el-option label="已取消" :value="0" />
        <el-option label="已退款" :value="5" />
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
      <el-table-column prop="service_name" label="服务名称" />
      <el-table-column prop="elder_name" label="老人姓名" width="120" />
      <el-table-column prop="actual_amount" label="价格" width="100">
        <template #default="{ row }">¥{{ row.actual_amount }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="订单时间" width="180" />
      <el-table-column label="预约服务时间" width="180">
        <template #default="{ row }">
          {{ row.appointment_date }} {{ row.appointment_time }}
        </template>
      </el-table-column>
      <el-table-column prop="status_name" label="状态" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.status === 1" type="warning">{{ row.status_name }}</el-tag>
          <el-tag v-else-if="row.status === 2" type="primary">{{ row.status_name }}</el-tag>
          <el-tag v-else-if="row.status === 4" type="success">{{ row.status_name }}</el-tag>
          <el-tag v-else type="info">{{ row.status_name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" show-overflow-tooltip />
      <el-table-column prop="nurse_name" label="护理员" width="120" />
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
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

// 从API获取的汇总数据
const summaryData = ref({
  total_orders: 0,
  total_sales: 0,
  completed_orders: 0,
  pending_orders: 0
})

const totalOrders = computed(() => summaryData.value.total_orders)
const totalSales = computed(() => summaryData.value.total_sales.toFixed(2))
const completedOrders = computed(() => summaryData.value.completed_orders)
const pendingOrders = computed(() => summaryData.value.pending_orders)

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
      console.log('[Accounting] 订单列表响应:', res.data)
      console.log('[Accounting] 表格显示总数 pagination.total =', pagination.total)
    }
  } catch (error) {
    console.error('获取订单列表失败', error)
  } finally {
    loading.value = false
  }
}

const getSummary = async () => {
  try {
    const params: any = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (orderStatus.value) {
      params.status = orderStatus.value
    }
    console.log('[Accounting] 调用 orders/summary, params:', params)
    const res: any = await api.get('/orders/summary', { params })
    console.log('[Accounting] orders/summary 响应:', res)
    if (res.code === 200) {
      summaryData.value = res.data
      console.log('[Accounting] 汇总数据已更新:', summaryData.value)
    }
  } catch (error) {
    console.error('获取订单汇总失败', error)
  }
}

// 同时获取订单列表和汇总数据
const refreshData = async () => {
  await Promise.all([
    getOrders(),
    getSummary()
  ])
}

const exportCSV = async () => {
  loading.value = true
  try {
    // 获取所有订单数据（不分页）
    const params: any = { page: 1, page_size: 10000 } // 设置一个很大的page_size来获取所有数据
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (orderStatus.value) {
      params.status = orderStatus.value
    }
    
    const res: any = await api.get('/orders/', { params })
    if (res.code === 200 && res.data.items.length > 0) {
      const allOrders = res.data.items
      
      // 生成CSV内容
      const headers = ['订单ID', '服务名称', '老人姓名', '价格', '订单时间', '预约服务时间', '状态', '备注', '护理员']
      const rows = allOrders.map((order: any) => [
        order.id,
        order.service_name,
        order.elder_name,
        order.actual_amount || order.total_amount,
        order.created_at,
        (order.appointment_date || '') + ' ' + (order.appointment_time || ''),
        order.status_name,
        order.remark || '',
        order.nurse_name || ''
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
      
      ElMessage.success('导出成功')
    } else {
      ElMessage.warning('没有数据可导出')
    }
  } catch (error) {
    console.error('导出CSV失败', error)
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  dateRange.value = []
  orderStatus.value = ''
  refreshData()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  refreshData()
}

const handleCurrentChange = (current: number) => {
  pagination.page = current
  refreshData()
}

onMounted(() => {
  refreshData()
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
