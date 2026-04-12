<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">服务列表</h2>
      <el-select v-model="selectedCategory" placeholder="服务类别" clearable style="width: 150px" @change="handleCategoryChange">
        <el-option v-for="category in categories" :key="category" :label="category" :value="category" />
      </el-select>
    </div>

    <div class="services-grid">
      <el-card v-for="service in services" :key="service.id" class="service-card" @click="viewService(service)">
        <template #header>
          <div class="service-header">
            <span class="service-name">{{ service.name }}</span>
            <span class="service-price">¥{{ service.price }}/{{ service.unit }}</span>
          </div>
        </template>
        <div class="service-body">
          <p class="service-description">{{ service.description }}</p>
          <div class="service-info">
            <span class="service-category">{{ service.category }}</span>
            <span class="service-duration" v-if="service.duration">预计{{ service.duration }}分钟</span>
          </div>
        </div>
        <div class="service-footer">
          <el-button type="primary" size="small" @click.stop="orderService(service)">立即预约</el-button>
        </div>
      </el-card>
    </div>

    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.page_size"
      :total="pagination.total"
      :page-sizes="[10, 20, 30, 50]"
      layout="total, sizes, prev, pager, next"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 30px; justify-content: flex-end"
    />

    <!-- 服务详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="服务详情" width="600px">
      <div class="service-detail">
        <h3>{{ currentService.name }}</h3>
        <div class="detail-price">¥{{ currentService.price }}/{{ currentService.unit }}</div>
        <div class="detail-info">
          <p><strong>服务类别：</strong>{{ currentService.category }}</p>
          <p><strong>预计时长：</strong>{{ currentService.duration }}分钟</p>
          <p><strong>服务描述：</strong>{{ currentService.description }}</p>
          <p><strong>详细说明：</strong>{{ currentService.details }}</p>
          <p><strong>注意事项：</strong>{{ currentService.precautions }}</p>
          <p><strong>服务要求：</strong>{{ currentService.requirements }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="orderService(currentService)">立即预约</el-button>
      </template>
    </el-dialog>

    <!-- 预约服务对话框 -->
    <el-dialog v-model="showOrderDialog" title="预约服务" width="500px">
      <el-form ref="orderFormRef" :model="orderForm" label-width="100px">
        <el-form-item label="服务名称">
          <el-input v-model="orderForm.service_name" disabled />
        </el-form-item>
        <el-form-item label="服务价格">
          <el-input v-model="orderForm.price" disabled />
        </el-form-item>
        <el-form-item label="服务时间">
          <el-date-picker v-model="orderForm.service_time" type="datetime" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="orderForm.notes" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showOrderDialog = false">取消</el-button>
        <el-button type="primary" @click="submitOrder">提交预约</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'

const loading = ref(false)
const services = ref<any[]>([])
const categories = ref<string[]>([])
const selectedCategory = ref('')
const showDetailDialog = ref(false)
const showOrderDialog = ref(false)
const currentService = ref<any>({})
const orderFormRef = ref()

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const orderForm = reactive({
  service_id: '',
  service_name: '',
  price: '',
  service_time: '',
  notes: ''
})

const getServices = async () => {
  loading.value = true
  try {
    const params: any = { page: pagination.page, page_size: pagination.page_size }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    const res: any = await api.get('/services', { params })
    if (res.code === 200) {
      services.value = res.data.items
      pagination.total = res.data.total
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

const viewService = (service: any) => {
  currentService.value = service
  showDetailDialog.value = true
}

const orderService = (service: any) => {
  currentService.value = service
  orderForm.service_id = service.id
  orderForm.service_name = service.name
  orderForm.price = service.price
  showOrderDialog.value = true
}

const submitOrder = async () => {
  try {
    const res: any = await api.post('/orders/', {
      service_id: orderForm.service_id,
      service_time: orderForm.service_time,
      notes: orderForm.notes
    })
    if (res.code === 200) {
      ElMessage.success('预约成功')
      showOrderDialog.value = false
    }
  } catch (error) {
    console.error('预约失败', error)
    ElMessage.error('预约失败')
  }
}

const handleCategoryChange = () => {
  pagination.page = 1
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
  margin-bottom: 30px;

  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
  }
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.service-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  }

  .service-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .service-name {
      font-weight: 600;
      font-size: 16px;
    }

    .service-price {
      color: #f56c6c;
      font-weight: 600;
      font-size: 18px;
    }
  }

  .service-body {
    margin: 15px 0;

    .service-description {
      color: #606266;
      line-height: 1.5;
      margin-bottom: 10px;
    }

    .service-info {
      display: flex;
      justify-content: space-between;
      color: #909399;
      font-size: 14px;
    }
  }

  .service-footer {
    margin-top: 20px;
    text-align: right;
  }
}

.service-detail {
  .detail-price {
    color: #f56c6c;
    font-weight: 600;
    font-size: 20px;
    margin: 10px 0;
  }

  .detail-info {
    margin-top: 20px;

    p {
      margin-bottom: 10px;
      line-height: 1.5;
    }
  }
}
</style>
