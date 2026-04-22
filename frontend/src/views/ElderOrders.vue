<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">我的订单</h2>
      <el-button type="primary" @click="loadOrders">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-table :data="orders" v-loading="loading" style="width: 100%">
      <el-table-column prop="order_no" label="订单号" width="180" />
      <el-table-column prop="service_name" label="服务项目" min-width="120" />
      <el-table-column prop="total_amount" label="金额" width="80">
        <template #default="{ row }">
          <span class="price">¥{{ row.total_amount }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status_name" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ row.status_name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="appointment_date" label="预约日期" width="120" />
      <el-table-column prop="appointment_time" label="预约时间" width="100" />
      <el-table-column prop="nurse_name" label="护理员" width="100">
        <template #default="{ row }">
          <span v-if="row.nurse_name">{{ row.nurse_name }}</span>
          <span v-else class="text-gray">未分配</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="下单时间" width="160">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewOrder(row)">查看</el-button>
          <el-button v-if="row.status === 2 && !row.nurse_id" type="success" size="small" @click="selectNurse(row)">选择护理员</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />

    <!-- 订单详情对话框 -->
    <el-dialog v-model="orderDialog" title="订单详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ currentOrder.order_no }}</el-descriptions-item>
        <el-descriptions-item label="服务项目">{{ currentOrder.service_name }}</el-descriptions-item>
        <el-descriptions-item label="服务对象">{{ currentOrder.elder_name }}</el-descriptions-item>
        <el-descriptions-item label="金额">¥{{ currentOrder.total_amount }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentOrder.status)">{{ currentOrder.status_name }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="护理员">{{ currentOrder.nurse_name || '未分配' }}</el-descriptions-item>
        <el-descriptions-item label="预约日期">{{ currentOrder.appointment_date || '待定' }}</el-descriptions-item>
        <el-descriptions-item label="预约时间">{{ currentOrder.appointment_time || '待定' }}</el-descriptions-item>
        <el-descriptions-item label="下单时间" :span="2">{{ formatDate(currentOrder.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentOrder.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="orderDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 选择护理员对话框 -->
    <el-dialog v-model="nurseDialog" title="选择护理员" width="500px">
      <el-form :model="nurseForm" label-width="100px">
        <el-form-item label="订单信息">
          <div class="order-info">
            <p>{{ selectOrder.service_name }}</p>
            <p class="text-gray">预约时间：{{ selectOrder.appointment_date }} {{ selectOrder.appointment_time }}</p>
          </div>
        </el-form-item>
        <el-form-item label="选择护理员" prop="nurse_id">
          <el-select v-model="nurseForm.nurse_id" placeholder="请选择护理员" style="width: 100%">
            <el-option
              v-for="nurse in nurseList"
              :key="nurse.id"
              :label="nurse.name"
              :value="nurse.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="nurseDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmNurse" :loading="confirmLoading">确认选择</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import api from '@/store/auth'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const loading = ref(false)
const orders = ref<any[]>([])
const orderDialog = ref(false)
const nurseDialog = ref(false)
const currentOrder = ref({})
const selectOrder = ref({})
const nurseList = ref<any[]>([])
const confirmLoading = ref(false)

const nurseForm = ref({
  nurse_id: null as number | null
})

const loadOrders = async () => {
  loading.value = true
  try {
    console.log('开始获取订单列表...')
    const res: any = await api.get('/orders/')
    console.log('获取订单列表结果:', res)
    if (res.code === 200) {
      orders.value = res.data.items || []
      console.log('订单列表数据:', orders.value)
    } else {
      console.error('获取订单列表失败，返回码:', res.code, '消息:', res.message)
      ElMessage.error(res.message || '获取订单列表失败')
    }
  } catch (error) {
    console.error('获取订单列表异常:', error)
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

const loadNurses = async () => {
  try {
    const res: any = await api.get('/users/workers')
    if (res.code === 200) {
      nurseList.value = res.data || []
    }
  } catch (error) {
    console.error('获取护理员列表失败', error)
  }
}

const viewOrder = (order: any) => {
  currentOrder.value = order
  orderDialog.value = true
}

const selectNurse = (order: any) => {
  selectOrder.value = order
  nurseForm.value.nurse_id = null
  loadNurses()
  nurseDialog.value = true
}

const confirmNurse = async () => {
  if (!nurseForm.value.nurse_id) {
    ElMessage.warning('请选择护理员')
    return
  }

  confirmLoading.value = true
  try {
    const res: any = await api.put(`/orders/${selectOrder.value.id}`, {
      nurse_id: nurseForm.value.nurse_id
    })
    if (res.code === 200) {
      ElMessage.success('护理员选择成功')
      nurseDialog.value = false
      loadOrders()
    } else {
      ElMessage.error(res.message || '护理员选择失败')
    }
  } catch (error) {
    console.error('选择护理员失败', error)
    ElMessage.error('选择护理员失败')
  } finally {
    confirmLoading.value = false
  }
}

const getStatusType = (status: number) => {
  const types: Record<number, string> = {
    0: 'danger',
    1: 'warning',
    2: 'info',
    3: 'primary',
    4: 'success',
    5: 'danger'
  }
  return types[status] || 'info'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'  
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  loadOrders()
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

.text-gray {
  color: #909399;
}

.order-info {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  
  p {
    margin: 0 0 5px 0;
    &.text-gray {
      font-size: 14px;
      margin-top: 5px;
    }
  }
}
</style>