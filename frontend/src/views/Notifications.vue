<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">消息通知</h2>
      <el-button @click="markAllRead" :disabled="unreadCount === 0" v-if="!isElder">
        全部已读
      </el-button>
    </div>

    <div class="card-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="全部" name="all">
          <div v-if="notifications.length === 0 && !loading" class="empty-state">
            <el-empty description="暂无通知" />
          </div>
          <el-table v-else :data="notifications" v-loading="loading" @row-click="handleRowClick">
            <el-table-column width="50">
              <template #default="{ row }">
                <el-badge is-dot :hidden="row.is_read" />
              </template>
            </el-table-column>
            <el-table-column prop="title" label="标题" min-width="150" />
            <el-table-column prop="created_by_name" label="发送者" width="100">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.created_by_name }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="user_name" label="接收者" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.user_name }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notification_type_name" label="类型" width="100" />
            <el-table-column prop="priority_name" label="优先级" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.priority === 2" type="danger" size="small">{{ row.priority_name }}</el-tag>
                <el-tag v-else-if="row.priority === 1" type="warning" size="small">{{ row.priority_name }}</el-tag>
                <span v-else>{{ row.priority_name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="160" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="未读" name="unread">
          <div v-if="unreadNotifications.length === 0 && !loading" class="empty-state">
            <el-empty description="暂无未读通知" />
          </div>
          <el-table v-else :data="unreadNotifications" v-loading="loading" @row-click="handleRowClick">
            <el-table-column width="50">
              <template #default="{ row }">
                <el-badge is-dot :hidden="row.is_read" />
              </template>
            </el-table-column>
            <el-table-column prop="title" label="标题" min-width="150" />
            <el-table-column prop="created_by_name" label="发送者" width="100">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.created_by_name }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="user_name" label="接收者" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.user_name }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notification_type_name" label="类型" width="100" />
            <el-table-column prop="created_at" label="时间" width="160" />
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <el-pagination
        v-if="notifications.length > 0"
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="getNotifications"
        @current-change="getNotifications"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </div>

    <!-- 通知详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="通知详情" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="标题">{{ currentNotification.title }}</el-descriptions-item>
        <el-descriptions-item label="发送者">{{ currentNotification.created_by_name }}</el-descriptions-item>
        <el-descriptions-item label="接收者">{{ currentNotification.user_name }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ currentNotification.notification_type_name }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag v-if="currentNotification.priority === 2" type="danger" size="small">紧急</el-tag>
          <el-tag v-else-if="currentNotification.priority === 1" type="warning" size="small">重要</el-tag>
          <span v-else>普通</span>
        </el-descriptions-item>
        <el-descriptions-item label="时间">{{ currentNotification.created_at }}</el-descriptions-item>
        <el-descriptions-item label="内容">{{ currentNotification.content }}</el-descriptions-item>
      </el-descriptions>

      <!-- 关联订单信息 -->
      <div v-if="currentNotification.orderId && relatedOrder" style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
        <h4 style="margin-bottom: 10px;">关联订单详情</h4>
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="订单号">{{ relatedOrder.order_no }}</el-descriptions-item>
          <el-descriptions-item label="服务项目">{{ relatedOrder.service_name }}</el-descriptions-item>
          <el-descriptions-item label="服务对象">{{ relatedOrder.elder_name }}</el-descriptions-item>
          <el-descriptions-item label="护理员">{{ relatedOrder.nurse_name || '未分配' }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getOrderStatusType(relatedOrder.status)">{{ relatedOrder.status_name }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="金额">¥{{ relatedOrder.total_amount }}</el-descriptions-item>
          <el-descriptions-item label="预约时间">{{ relatedOrder.appointment_date }} {{ relatedOrder.appointment_time }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button 
          v-if="(userInfo.value?.user_type === 2 || userInfo.value?.user_type === 3) && currentNotification.orderId && relatedOrder?.status === 3" 
          type="primary" 
          @click="completeOrder"
        >
          完成订单
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/store/auth'
import type { Notification } from '@/types'

const loading = ref(false)
const showDetailDialog = ref(false)
const activeTab = ref('all')
const unreadCount = ref(0)

const notifications = ref<Notification[]>([])
const currentNotification = ref<any>({})
const relatedOrder = ref<any>(null)

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const unreadNotifications = computed(() =>
  notifications.value.filter(n => !n.is_read)
)

// 获取用户信息判断是否为老人
const userInfo = computed(() => {
  const info = localStorage.getItem('userInfo')
  return info ? JSON.parse(info) : null
})

const isElder = computed(() => userInfo.value?.user_type === 1)

const getNotifications = async () => {
  loading.value = true
  try {
    const params: any = { page: pagination.page, page_size: pagination.page_size }
    if (activeTab.value === 'unread') {
      params.is_read = 'false'
    }
    const res: any = await api.get('/notifications/', { params })
    if (res.code === 200) {
      notifications.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('获取通知失败', error)
  } finally {
    loading.value = false
  }
}

const getUnreadCount = async () => {
  try {
    const res: any = await api.get('/notifications/unread-count')
    if (res.code === 200) {
      unreadCount.value = res.data.count
    }
  } catch (error) {
    console.error('获取未读数失败', error)
  }
}

const handleRowClick = async (row: Notification) => {
  currentNotification.value = row
  relatedOrder.value = null
  showDetailDialog.value = true

  // 加载关联的订单信息
  if (row.orderId) {
    try {
      const res: any = await api.get(`/orders/${row.orderId}`)
      if (res.code === 200) {
        relatedOrder.value = res.data
      }
    } catch (error) {
      console.error('加载订单信息失败', error)
    }
  }

  if (!row.is_read) {
    try {
      await api.post(`/notifications/${row.id}/read`)
      row.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (error) {
      console.error('标记已读失败', error)
    }
  }
}

const markAllRead = async () => {
  try {
    const res: any = await api.post('/notifications/read-all')
    if (res.code === 200) {
      ElMessage.success('已全部标记为已读')
      unreadCount.value = 0
      getNotifications()
    }
  } catch (error) {
    console.error('标记全部已读失败', error)
  }
}

const completeOrder = async () => {
  try {
    // 检查通知是否关联了订单
    if (!currentNotification.value.orderId) {
      ElMessage.warning('此通知未关联订单，无法完成')
      return
    }

    // 获取关联的订单
    const orderId = currentNotification.value.orderId
    const res: any = await api.get(`/orders/${orderId}`)
    
    if (res.code !== 200) {
      ElMessage.error('订单不存在')
      return
    }

    const order = res.data
    
    // 验证订单状态
    if (order.status !== 3) {
      ElMessage.warning(`订单状态为「${order.status_name}」，只有「服务中」的订单才能完成`)
      return
    }

    // 确认完成
    const confirmRes = await ElMessageBox.confirm(
      `确定要完成订单「${order.service_name}」吗？`,
      '确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).catch(() => false)

    if (!confirmRes) return

    // 调用API完成订单
    const updateRes: any = await api.put(`/orders/${orderId}`, {
      status: 4  // 已完成
    })

    if (updateRes.code === 200) {
      ElMessage.success('订单已完成')
      showDetailDialog.value = false
      // 重新加载通知列表
      getNotifications()
    } else {
      ElMessage.error(updateRes.message || '完成订单失败')
    }
  } catch (error: any) {
    console.error('完成订单失败', error)
    if (error.message !== 'cancel') {
      ElMessage.error('完成订单失败，请稍后重试')
    }
  }
}

const getOrderStatusType = (status: number): string => {
  const statusTypeMap: Record<number, string> = {
    0: 'info',    // 已取消
    1: 'warning', // 待支付
    2: 'info',    // 待服务
    3: 'warning', // 服务中
    4: 'success', // 已完成
    5: 'danger'   // 已退款
  }
  return statusTypeMap[status] || 'info'
}

watch(activeTab, () => {
  pagination.page = 1
  getNotifications()
})

onMounted(() => {
  getNotifications()
  getUnreadCount()
})
</script>