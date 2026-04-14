<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">服务管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增服务
      </el-button>
    </div>

    <div class="search-form">
      <el-input v-model="searchForm.name" placeholder="服务名称" style="width: 200px; margin-right: 10px" />
      <el-select v-model="searchForm.category" placeholder="服务类别" clearable style="width: 150px; margin-right: 10px">
        <el-option v-for="category in categories" :key="category" :label="category" :value="category" />
      </el-select>
      <el-select v-model="searchForm.status" placeholder="状态" clearable style="width: 100px; margin-right: 10px">
        <el-option label="上架" :value="1" />
        <el-option label="下架" :value="0" />
      </el-select>
      <el-button type="primary" @click="getServices">搜索</el-button>
      <el-button @click="resetSearch">重置</el-button>
    </div>

    <el-table :data="services" v-loading="loading" style="margin-top: 20px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="服务名称" />
      <el-table-column prop="category" label="服务类别" width="120" />
      <el-table-column prop="price" label="价格" width="100">
        <template #default="{ row }">¥{{ row.price }}</template>
      </el-table-column>
      <el-table-column prop="unit" label="单位" width="80" />
      <el-table-column prop="duration" label="时长(分钟)" width="120" />
      <el-table-column prop="salesCount" label="销量" width="80" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.status === 1" type="success">上架</el-tag>
          <el-tag v-else type="info">下架</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="创建时间" width="180" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
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

    <!-- 服务编辑对话框 -->
    <el-dialog v-model="showEditDialog" :title="isEditing ? '编辑服务' : '新增服务'" width="600px">
      <el-form ref="serviceFormRef" :model="serviceForm" label-width="100px">
        <el-form-item label="服务名称" required>
          <el-input v-model="serviceForm.name" placeholder="请输入服务名称" />
        </el-form-item>
        <el-form-item label="服务类别" required>
          <el-input v-model="serviceForm.category" placeholder="请输入服务类别" />
        </el-form-item>
        <el-form-item label="服务价格" required>
          <el-input v-model.number="serviceForm.price" type="number" placeholder="请输入服务价格" />
        </el-form-item>
        <el-form-item label="计费单位" required>
          <el-input v-model="serviceForm.unit" placeholder="请输入计费单位" />
        </el-form-item>
        <el-form-item label="预计时长" required>
          <el-input v-model.number="serviceForm.duration" type="number" placeholder="请输入预计时长(分钟)" />
        </el-form-item>
        <el-form-item label="服务描述">
          <el-input v-model="serviceForm.description" type="textarea" rows="3" placeholder="请输入服务描述" />
        </el-form-item>
        <el-form-item label="详细说明">
          <el-input v-model="serviceForm.details" type="textarea" rows="3" placeholder="请输入详细说明" />
        </el-form-item>
        <el-form-item label="注意事项">
          <el-input v-model="serviceForm.precautions" type="textarea" rows="3" placeholder="请输入注意事项" />
        </el-form-item>
        <el-form-item label="服务要求">
          <el-input v-model="serviceForm.requirements" type="textarea" rows="3" placeholder="请输入服务要求" />
        </el-form-item>
        <el-form-item label="库存">
          <el-input v-model.number="serviceForm.stock" type="number" placeholder="请输入库存" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="serviceForm.status" style="width: 100%">
            <el-option label="上架" :value="1" />
            <el-option label="下架" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否推荐">
          <el-select v-model="serviceForm.isRecommended" style="width: 100%">
            <el-option label="是" :value="1" />
            <el-option label="否" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input v-model.number="serviceForm.sortOrder" type="number" placeholder="请输入排序" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/store/auth'

const loading = ref(false)
const services = ref<any[]>([])
const categories = ref<string[]>([])
const showEditDialog = ref(false)
const isEditing = ref(false)
const serviceFormRef = ref()

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const searchForm = reactive({
  name: '',
  category: '',
  status: ''
})

const serviceForm = reactive({
  id: '',
  name: '',
  category: '',
  description: '',
  price: '',
  unit: '',
  duration: '',
  details: '',
  precautions: '',
  requirements: '',
  stock: 999,
  status: 1,
  isRecommended: 0,
  sortOrder: 0
})

const getServices = async () => {
  loading.value = true
  try {
    const params: any = { page: pagination.page, page_size: pagination.page_size }
    if (searchForm.name) params.name = searchForm.name
    if (searchForm.category) params.category = searchForm.category
    if (searchForm.status) params.status = searchForm.status
    console.log('请求参数:', params)
    const res: any = await api.get('/services/', { params })
    console.log('API响应:', res)
    if (res.code === 200) {
      services.value = res.data.items
      pagination.total = res.data.total
      console.log('服务数据:', services.value)
      console.log('总条数:', pagination.total)
    }
  } catch (error) {
    console.error('获取服务列表失败', error)
  } finally {
    loading.value = false
  }
}

const getCategories = async () => {
  try {
    const res: any = await api.get('/services/categories')
    if (res.code === 200) {
      categories.value = res.data
    }
  } catch (error) {
    console.error('获取服务类别失败', error)
  }
}

const handleAdd = () => {
  isEditing.value = false
  serviceForm.id = ''
  serviceForm.name = ''
  serviceForm.category = ''
  serviceForm.description = ''
  serviceForm.price = ''
  serviceForm.unit = ''
  serviceForm.duration = ''
  serviceForm.details = ''
  serviceForm.precautions = ''
  serviceForm.requirements = ''
  serviceForm.stock = 999
  serviceForm.status = 1
  serviceForm.isRecommended = 0
  serviceForm.sortOrder = 0
  showEditDialog.value = true
}

const handleEdit = (row: any) => {
  isEditing.value = true
  serviceForm.id = row.id
  serviceForm.name = row.name
  serviceForm.category = row.category
  serviceForm.description = row.description
  serviceForm.price = row.price
  serviceForm.unit = row.unit
  serviceForm.duration = row.duration
  serviceForm.details = row.details
  serviceForm.precautions = row.precautions
  serviceForm.requirements = row.requirements
  serviceForm.stock = row.stock
  serviceForm.status = row.status
  serviceForm.isRecommended = row.isRecommended
  serviceForm.sortOrder = row.sortOrder
  showEditDialog.value = true
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个服务吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const res: any = await api.delete(`/services/${id}/`)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      getServices()
    }
  } catch (error) {
    console.error('删除失败', error)
  }
}

const submitForm = async () => {
  try {
    if (isEditing.value) {
      const res: any = await api.put(`/services/${serviceForm.id}`, serviceForm)
      if (res.code === 200) {
        ElMessage.success('更新成功')
        showEditDialog.value = false
        getServices()
      }
    } else {
      const res: any = await api.post('/services', serviceForm)
      if (res.code === 200) {
        ElMessage.success('创建成功')
        showEditDialog.value = false
        getServices()
      }
    }
  } catch (error) {
    console.error('保存失败', error)
    ElMessage.error('保存失败')
  }
}

const resetSearch = () => {
  searchForm.name = ''
  searchForm.category = ''
  searchForm.status = ''
  getServices()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  getServices()
}

const handleCurrentChange = (current: number) => {
  pagination.page = current
  getServices()
}

onMounted(() => {
  getServices()
  getCategories()
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
}

.search-form {
  display: flex;
  align-items: center;
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}
</style>
