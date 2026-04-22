<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">待接订单</h2>
      <el-button type="primary" @click="loadOrders">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-alert
      v-if="pendingOrders.length > 0"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 20px"
    >
      <template #title>
        您有 {{ pendingOrders.length }} 个待接订单
      </template>
    </el-alert>

    <el-table :data="pendingOrders" v-loading="loading" style="width: 100%">
      <el-table-column prop="order_no" label="订单号" width="180" />
      <el-table-column prop="service_name" label="服务项目" min-width="120" />
      <el-table-column prop="elder_name" label="服务对象" width="100" />
      <el-table-column prop="total_amount" label="金额" width="80">
        <template #default="{ row }">
          <span class="price">¥{{ row.total_amount }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'warning' : 'primary'" size="small">
            {{ row.status === 1 ? '待支付' : '待接单' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="appointment_date" label="预约日期" width="120" />
      <el-table-column prop="appointment_time" label="预约时间" width="100" />
      <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
      <el-table-column prop="created_at" label="下单时间" width="160">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status === 2" type="primary" size="small" @click="handleAccept(row)">接单</el-button>
          <el-tag v-else type="info" size="small">待支付</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && pendingOrders.length === 0" description="暂无待接订单" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import api from '@/store/auth'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const loading = ref(false)
const pendingOrders = ref<any[]>([])
let pollTimer: any = null

const loadOrders = async () => {
  loading.value = true
  try {
    // 获取待服务和待支付的订单
    const res: any = await api.get('/orders/', { params: { page: 1, page_size: 50 } })
    if (res.code === 200) {
      // 过滤出待服务和待支付的订单
      pendingOrders.value = (res.data.items || []).filter((order: any) =>
        order.status === 1 || order.status === 2
      )
    }
  } catch (error) {
    console.error('获取订单列表失败', error)
  } finally {
    loading.value = false
  }
}

const handleAccept = async (order: any) => {
  try {
    const res: any = await api.put(`/orders/${order.id}`, {
      nurse_id: authStore.userInfo?.id,
      status: 3
    })
    if (res.code === 200) {
      ElMessage.success('接单成功')
      loadOrders()
    } else {
      ElMessage.error(res.message || '接单失败')
    }
  } catch (error) {
    console.error('接单失败', error)
    ElMessage.error('接单失败')
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  loadOrders()
  // 每30秒轮询
  pollTimer = setInterval(loadOrders, 30000)
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }
})
</script>

<style scoped lang="scss">
.page-container {
  padding: 20px;
}

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
}

.price {
  color: #f56c6c;
  font-weight: 600;
}
</style>
