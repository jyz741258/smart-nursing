<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">护理记录</h2>
      <el-button v-if="canAddRecord" type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        添加记录
      </el-button>
    </div>

    <div class="card-container">
      <div class="search-form">
        <el-select v-model="searchForm.nursing_type" placeholder="护理类型" clearable style="width: 150px">
          <el-option label="日常照护" :value="1" />
          <el-option label="医疗护理" :value="2" />
          <el-option label="康复训练" :value="3" />
          <el-option label="心理疏导" :value="4" />
          <el-option label="饮食护理" :value="5" />
          <el-option label="清洁护理" :value="6" />
          <el-option label="安全护理" :value="7" />
        </el-select>
        <el-button type="primary" @click="getNursingRecords">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>

      <el-table :data="records" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="elder_name" label="老人姓名" />
        <el-table-column prop="nursing_type_name" label="护理类型" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="staff_name" label="护理人员" />
        <el-table-column prop="status_name" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">查看</el-button>
            <el-button v-if="row.status === 1 && (userInfo.value?.user_type === 2 || userInfo.value?.user_type === 3)" type="success" size="small" @click="completeRecord(row)">
              完成
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="getNursingRecords"
        @current-change="getNursingRecords"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </div>

    <!-- 添加记录对话框 -->
    <el-dialog v-model="showAddDialog" title="添加护理记录" width="600px">
      <el-form ref="formRef" :model="recordForm" label-width="100px">
        <el-form-item label="老人" prop="elder_id">
          <el-select v-model="recordForm.elder_id" placeholder="请选择老人">
            <el-option v-for="elder in elders" :key="elder.id" :label="elder.name" :value="elder.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="护理类型" prop="nursing_type">
          <el-select v-model="recordForm.nursing_type" placeholder="请选择护理类型">
            <el-option label="日常照护" :value="1" />
            <el-option label="医疗护理" :value="2" />
            <el-option label="康复训练" :value="3" />
            <el-option label="心理疏导" :value="4" />
            <el-option label="饮食护理" :value="5" />
            <el-option label="清洁护理" :value="6" />
            <el-option label="安全护理" :value="7" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="recordForm.description" type="textarea" :rows="3" placeholder="请输入护理描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="护理记录详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="老人">{{ currentRecord.elder_name }}</el-descriptions-item>
        <el-descriptions-item label="护理类型">{{ currentRecord.nursing_type_name }}</el-descriptions-item>
        <el-descriptions-item label="护理人员">{{ currentRecord.staff_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRecord.status)">{{ currentRecord.status_name }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentRecord.description }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ currentRecord.start_time }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ currentRecord.end_time }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentRecord.notes || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'
import type { NursingRecord, Elder } from '@/types'

const loading = ref(false)
const showAddDialog = ref(false)
const showDetailDialog = ref(false)

const records = ref<NursingRecord[]>([])
const elders = ref<Elder[]>([])
const currentRecord = ref<any>({})

// 用户类型判断
const userInfo = computed(() => {
  const info = localStorage.getItem('userInfo')
  return info ? JSON.parse(info) : null
})

// 只有护理人员(2)和管理员(3)可以添加记录
const canAddRecord = computed(() => {
  const type = userInfo.value?.user_type
  return type === 2 || type === 3
})

// 老人只能查看自己的记录
const elderId = computed(() => userInfo.value?.user_type === 1 ? userInfo.value?.id : null)

const searchForm = reactive({
  nursing_type: null as number | null
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const recordForm = reactive({
  elder_id: null as number | null,
  nursing_type: null as number | null,
  description: ''
})

const getNursingRecords = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.page_size
    }

    // 如果有筛选条件
    if (searchForm.nursing_type) {
      params.nursing_type = searchForm.nursing_type
    }

    // 如果是老人，只能查看自己的记录
    if (userInfo.value?.user_type === 1 && userInfo.value?.id) {
      params.elder_id = userInfo.value.id
    }

    const res: any = await api.get('/nursing/records', { params })
    if (res.code === 200) {
      records.value = res.data.items || []
      pagination.total = res.data.total || 0
    } else {
      console.error('API返回错误:', res.message)
    }
  } catch (error) {
    console.error('获取护理记录失败', error)
  } finally {
    loading.value = false
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
  searchForm.nursing_type = null
  pagination.page = 1
  getNursingRecords()
}

const getStatusType = (status: number) => {
  const types: Record<number, string> = {
    1: 'warning',
    2: 'success',
    3: 'info'
  }
  return types[status] || ''
}

const viewDetail = async (row: NursingRecord) => {
  try {
    const res: any = await api.get(`/nursing/records/${row.id}`)
    if (res.code === 200) {
      currentRecord.value = res.data
      showDetailDialog.value = true
    }
  } catch (error) {
    console.error('获取记录详情失败', error)
  }
}

const completeRecord = async (row: NursingRecord) => {
  try {
    const res: any = await api.post(`/nursing/records/${row.id}/complete`, {
      notes: ''
    })
    if (res.code === 200) {
      ElMessage.success('记录已完成')
      getNursingRecords()
    }
  } catch (error) {
    console.error('完成记录失败', error)
  }
}

const submitForm = async () => {
  try {
    const res: any = await api.post('/nursing/records', recordForm)
    if (res.code === 200) {
      ElMessage.success('添加成功')
      showAddDialog.value = false
      getNursingRecords()
    }
  } catch (error) {
    console.error('添加失败', error)
  }
}

onMounted(() => {
  getNursingRecords()
  // 只有护理人员和管理员需要获取老人列表用于添加记录
  if (canAddRecord.value) {
    getElders()
  }
})
</script>