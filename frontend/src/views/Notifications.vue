<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">消息通知</h2>
      <el-button @click="markAllRead" :disabled="unreadCount === 0">
        全部已读
      </el-button>
    </div>

    <div class="card-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="全部" name="all">
          <el-table :data="notifications" v-loading="loading" @row-click="handleRowClick">
            <el-table-column width="50">
              <template #default="{ row }">
                <el-badge is-dot :hidden="row.is_read" />
              </template>
            </el-table-column>
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="notification_type_name" label="类型" width="120" />
            <el-table-column prop="priority_name" label="优先级" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.priority === 2" type="danger" size="small">{{ row.priority_name }}</el-tag>
                <el-tag v-else-if="row.priority === 1" type="warning" size="small">{{ row.priority_name }}</el-tag>
                <span v-else>{{ row.priority_name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="未读" name="unread">
          <el-table :data="unreadNotifications" v-loading="loading" @row-click="handleRowClick">
            <el-table-column width="50">
              <template #default="{ row }">
                <el-badge is-dot :hidden="row.is_read" />
              </template>
            </el-table-column>
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="notification_type_name" label="类型" width="120" />
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <el-pagination
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
    <el-dialog v-model="showDetailDialog" title="通知详情" width="500px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="标题">{{ currentNotification.title }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ currentNotification.notification_type_name }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag v-if="currentNotification.priority === 2" type="danger" size="small">紧急</el-tag>
          <el-tag v-else-if="currentNotification.priority === 1" type="warning" size="small">重要</el-tag>
          <span v-else>普通</span>
        </el-descriptions-item>
        <el-descriptions-item label="时间">{{ currentNotification.created_at }}</el-descriptions-item>
        <el-descriptions-item label="内容">{{ currentNotification.content }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'
import type { Notification } from '@/types'

const loading = ref(false)
const showDetailDialog = ref(false)
const activeTab = ref('all')
const unreadCount = ref(0)

const notifications = ref<Notification[]>([])
const currentNotification = ref<any>({})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const unreadNotifications = computed(() =>
  notifications.value.filter(n => !n.is_read)
)

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
  showDetailDialog.value = true

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

watch(activeTab, () => {
  pagination.page = 1
  getNotifications()
})

onMounted(() => {
  getNotifications()
  getUnreadCount()
})
</script>