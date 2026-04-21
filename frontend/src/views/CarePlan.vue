<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">护理计划</h2>
      <el-button type="primary" @click="showPlanDialog = true">
        <el-icon><Plus /></el-icon>
        创建计划
      </el-button>
    </div>

    <div class="card-container">
      <el-table :data="plans" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="计划标题" />
        <el-table-column prop="elder_name" label="老人" />
        <el-table-column prop="status_name" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="end_date" label="结束日期" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewPlan(row)">查看</el-button>
            <el-button type="success" size="small" @click="addTask(row)">添加任务</el-button>
            <el-button type="warning" size="small" @click="editPlan(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        layout="total, prev, pager, next"
        @current-change="getPlans"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </div>

    <!-- 计划详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="护理计划详情" width="800px">
      <el-descriptions :column="2" border style="margin-bottom: 20px">
        <el-descriptions-item label="标题">{{ currentPlan.title }}</el-descriptions-item>
        <el-descriptions-item label="老人">{{ currentPlan.elder_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentPlan.status)">{{ currentPlan.status_name }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="开始日期">{{ currentPlan.start_date }}</el-descriptions-item>
        <el-descriptions-item label="结束日期">{{ currentPlan.end_date }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentPlan.description }}</el-descriptions-item>
      </el-descriptions>

      <div class="tasks-section">
        <h4>护理任务</h4>
        <el-table :data="currentPlan.tasks" size="small">
          <el-table-column prop="task_name" label="任务名称" />
          <el-table-column prop="task_type" label="任务类型" width="100" />
          <el-table-column prop="frequency" label="频率" width="100" />
          <el-table-column prop="status_name" label="状态" width="80">
            <template #default="{ row }">
              <el-tag size="small" :type="row.status === 2 ? 'success' : 'warning'">
                {{ row.status_name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button v-if="row.status === 1" type="primary" size="small" @click="completeTask(row)">
                完成
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 创建/编辑计划对话框 -->
    <el-dialog v-model="showPlanDialog" :title="isEditPlan ? '编辑计划' : '创建护理计划'" width="500px">
      <el-form ref="planFormRef" :model="planForm" label-width="100px">
        <el-form-item label="老人" prop="elder_id">
          <el-select v-model="planForm.elder_id" placeholder="请选择老人">
            <el-option v-for="elder in elders" :key="elder.id" :label="elder.name" :value="elder.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input v-model="planForm.title" placeholder="请输入计划标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="planForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="planForm.start_date" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="planForm.end_date" type="date" placeholder="选择日期" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPlanDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPlan">确定</el-button>
      </template>
    </el-dialog>

    <!-- 添加任务对话框 -->
    <el-dialog v-model="showTaskDialog" title="添加护理任务" width="500px">
      <el-form ref="taskFormRef" :model="taskForm" label-width="100px">
        <el-form-item label="任务名称" prop="task_name">
          <el-input v-model="taskForm.task_name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型" prop="task_type">
          <el-select v-model="taskForm.task_type" placeholder="请选择">
            <el-option label="日常照护" :value="1" />
            <el-option label="医疗护理" :value="2" />
            <el-option label="康复训练" :value="3" />
            <el-option label="心理疏导" :value="4" />
            <el-option label="饮食护理" :value="5" />
          </el-select>
        </el-form-item>
        <el-form-item label="频率">
          <el-input v-model="taskForm.frequency" placeholder="如：每天2次" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="taskForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTaskDialog = false">取消</el-button>
        <el-button type="primary" @click="submitTask">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'
import type { CarePlan, Elder } from '@/types'

const loading = ref(false)
const showDetailDialog = ref(false)
const showPlanDialog = ref(false)
const showTaskDialog = ref(false)
const isEditPlan = ref(false)
const planFormRef = ref()
const taskFormRef = ref()

const plans = ref<CarePlan[]>([])
const elders = ref<Elder[]>([])
const currentPlan = ref<any>({})
const currentPlanId = ref<number | null>(null)

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const planForm = reactive({
  id: null as number | null,
  elder_id: null as number | null,
  title: '',
  description: '',
  start_date: '',
  end_date: ''
})

const taskForm = reactive({
  task_name: '',
  task_type: null as number | null,
  frequency: '',
  description: ''
})

const getPlans = async () => {
  loading.value = true
  try {
    const res: any = await api.get('/care/plans', {
      params: { page: pagination.page, page_size: pagination.page_size }
    })
    if (res.code === 200) {
      plans.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('获取护理计划失败', error)
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

const getStatusType = (status: number) => {
  return status === 1 ? 'warning' : status === 2 ? 'success' : 'info'
}

const viewPlan = async (row: CarePlan) => {
  try {
    const res: any = await api.get(`/care/plans/${row.id}`)
    if (res.code === 200) {
      currentPlan.value = res.data
      showDetailDialog.value = true
    }
  } catch (error) {
    console.error('获取计划详情失败', error)
  }
}

const editPlan = (row: CarePlan) => {
  isEditPlan.value = true
  Object.assign(planForm, row)
  showPlanDialog.value = true
}

const addTask = (row: CarePlan) => {
  currentPlanId.value = row.id
  showTaskDialog.value = true
}

const completeTask = async (task: any) => {
  try {
    const res: any = await api.post(`/care/tasks/${task.id}/complete`)
    if (res.code === 200) {
      ElMessage.success('任务已完成')
      viewPlan(currentPlan.value)
    }
  } catch (error) {
    console.error('完成任务失败', error)
  }
}

const submitPlan = async () => {
  try {
    if (isEditPlan.value) {
      const res: any = await api.put(`/care/plans/${planForm.id}`, planForm)
      if (res.code === 200) {
        ElMessage.success('更新成功')
      }
    } else {
      const res: any = await api.post('/care/plans', planForm)
      if (res.code === 200) {
        ElMessage.success('创建成功')
      }
    }
    showPlanDialog.value = false
    getPlans()
  } catch (error) {
    console.error('保存计划失败', error)
  }
}

const submitTask = async () => {
  try {
    const res: any = await api.post('/care/tasks', {
      care_plan_id: currentPlanId.value,
      ...taskForm
    })
    if (res.code === 200) {
      ElMessage.success('任务添加成功')
      showTaskDialog.value = false
    }
  } catch (error) {
    console.error('添加任务失败', error)
  }
}

onMounted(() => {
  getPlans()
  getElders()
})
</script>

<style scoped lang="scss">
.page-container {
  padding: 24px;
  min-height: 100vh;
  background: var(--bg-primary);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);

  .page-title {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
  }
}

.card-container {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
  transition: all 0.3s var(--ease-smooth);
  position: relative;

  &:hover {
    border-color: var(--color-primary);
    box-shadow: var(--shadow-lg);
    transform: translateY(-4px);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--gradient-primary);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.4s var(--ease-smooth);
  }

  &:hover::before {
    transform: scaleX(1);
  }
}

.tasks-section {
  margin-top: 24px;

  h4 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
    padding-left: 10px;
    border-left: 4px solid var(--color-primary);
  }
}

/* 表格样式优化 */
:deep(.el-table) {
  background: transparent;

  th.el-table__cell {
    background: var(--bg-secondary);
    color: var(--text-primary);
    font-weight: 600;
  }

  td.el-table__cell {
    color: var(--text-primary);
  }

  .el-table__row {
    transition: background-color 0.3s ease;

    &:hover {
      background-color: var(--bg-hover);
    }
  }
}

/* 对话框样式优化 */
:deep(.el-dialog) {
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);

  .el-dialog__title {
    color: var(--text-primary);
    font-weight: 600;
  }

  .el-dialog__body {
    color: var(--text-primary);
  }
}

/* 描述列表样式优化 */
:deep(.el-descriptions) {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);

  .el-descriptions__label {
    color: var(--text-secondary);
    font-weight: 500;
  }

  .el-descriptions__content {
    color: var(--text-primary);
  }
}

/* 表单样式优化 */
:deep(.el-form-item__label) {
  color: var(--text-secondary);
  font-weight: 500;
}

:deep(.el-input__inner),
:deep(.el-textarea__inner) {
  color: var(--text-primary);
  background-color: var(--bg-secondary);
  border-color: var(--border-color);

  &:focus {
    border-color: var(--color-primary);
  }
}

:deep(.el-select) {
  .el-select__input {
    color: var(--text-primary);
  }

  .el-select__placeholder {
    color: var(--text-tertiary);
  }
}

/* 按钮样式优化 */
:deep(.el-button) {
  font-weight: 500;

  &.el-button--primary {
    background-color: var(--color-primary);
    border-color: var(--color-primary);

    &:hover {
      background-color: var(--color-primary-light);
      border-color: var(--color-primary-light);
    }
  }

  &.el-button--success {
    background-color: var(--color-success);
    border-color: var(--color-success);

    &:hover {
      background-color: var(--color-success-light);
      border-color: var(--color-success-light);
    }
  }

  &.el-button--warning {
    background-color: var(--color-warning);
    border-color: var(--color-warning);

    &:hover {
      background-color: var(--color-warning-light);
      border-color: var(--color-warning-light);
    }
  }
}

/* 标签样式优化 */
:deep(.el-tag) {
  font-weight: 500;
}
</style>