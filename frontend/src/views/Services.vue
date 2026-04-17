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
            <span v-if="!isNurse" class="service-price">¥{{ service.price }}/{{ service.unit }}</span>
            <span v-else class="service-requirements-tag">服务要求</span>
          </div>
        </template>
        <div class="service-body">
          <p class="service-description">{{ service.description }}</p>
          <div class="service-info">
            <span class="service-category">{{ service.category }}</span>
            <span class="service-duration" v-if="service.duration">预计{{ service.duration }}分钟</span>
          </div>
          <!-- 护理人员看到服务要求 -->
          <div v-if="isNurse && service.requirements" class="service-requirements">
            <strong>服务要求：</strong>{{ service.requirements }}
          </div>
        </div>
        <div class="service-footer">
          <el-button type="primary" size="small" @click.stop="orderService(service)" v-if="authStore.userInfo && authStore.userInfo.user_type !== 2">立即预约</el-button>
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
        <div v-if="!isNurse" class="detail-price">¥{{ currentService.price }}/{{ currentService.unit }}</div>
        <div v-else class="detail-requirements">
          <el-tag type="warning">服务要求</el-tag>
          <p>{{ currentService.requirements || '暂无具体要求' }}</p>
        </div>
        <div class="detail-info">
          <p><strong>服务类别：</strong>{{ currentService.category }}</p>
          <p><strong>预计时长：</strong>{{ currentService.duration }}分钟</p>
          <p><strong>服务描述：</strong>{{ currentService.description }}</p>
          <p><strong>详细说明：</strong>{{ currentService.details }}</p>
          <p><strong>注意事项：</strong>{{ currentService.precautions }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="orderService(currentService)" v-if="authStore.userInfo && authStore.userInfo.user_type !== 2">立即预约</el-button>
      </template>
    </el-dialog>

    <!-- 预约服务对话框 -->
    <el-dialog v-model="showOrderDialog" title="预约服务" width="500px">
      <el-form ref="orderFormRef" :model="orderForm" label-width="100px">
        <el-form-item label="服务名称">
          <el-input v-model="orderForm.service_name" disabled />
        </el-form-item>
        <el-form-item v-if="!isNurse" label="服务价格">
          <el-input :value="'¥' + orderForm.price" disabled />
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

    <!-- 支付对话框 -->
    <el-dialog v-model="showPayDialog" title="选择支付方式" width="400px" :close-on-click-modal="false">
      <div class="pay-info">
        <div class="pay-amount">
          <span class="label">支付金额</span>
          <span class="amount">¥{{ currentOrder?.actualAmount || 0 }}</span>
        </div>
        <div class="pay-order">订单号：{{ currentOrder?.orderNo }}</div>
      </div>
      
      <div class="pay-methods">
        <div class="pay-method-title">请选择支付方式</div>
        <el-radio-group v-model="payPlatform" class="method-group">
          <el-radio label="alipay" class="pay-method-item" :class="{ disabled: !paymentConfig.alipay_enabled }">
            <div class="method-content">
              <div class="method-icon alipay-icon">支</div>
              <span class="method-name">支付宝</span>
              <el-tag v-if="!paymentConfig.alipay_enabled" type="info" size="small">暂不可用</el-tag>
            </div>
          </el-radio>
          <el-radio label="wechat" class="pay-method-item" :class="{ disabled: !paymentConfig.wechat_enabled }">
            <div class="method-content">
              <div class="method-icon wechat-icon">微</div>
              <span class="method-name">微信支付</span>
              <el-tag v-if="!paymentConfig.wechat_enabled" type="info" size="small">暂不可用</el-tag>
            </div>
          </el-radio>
        </el-radio-group>
      </div>
      
      <template #footer>
        <el-button @click="cancelPayment">取消支付</el-button>
        <el-button type="primary" @click="confirmPayment" :loading="paying">确认支付</el-button>
      </template>
    </el-dialog>

    <!-- 支付中对话框 -->
    <el-dialog v-model="showPayingDialog" title="正在支付" width="300px" :close-on-click-modal="false">
      <div class="paying-content">
        <div class="loading-spinner"></div>
        <p>请在{{ payPlatform === 'alipay' ? '支付宝' : '微信' }}中完成支付</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'
import { useAuthStore } from '@/store/auth'

const loading = ref(false)
const services = ref<any[]>([])
const categories = ref<string[]>([])
const selectedCategory = ref('')
const showDetailDialog = ref(false)
const showOrderDialog = ref(false)
const currentService = ref<any>({})
const orderFormRef = ref()
const authStore = useAuthStore()

// 支付相关
const showPayDialog = ref(false)
const showPayingDialog = ref(false)
const currentOrder = ref<any>(null)
const payPlatform = ref('alipay')
const paying = ref(false)
const paymentConfig = reactive({
  alipay_enabled: true,
  wechat_enabled: false
})

// 判断是否为护理人员
const isNurse = computed(() => {
  return authStore.userInfo?.user_type === 2
})

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
    const res: any = await api.get('/services/', { params })
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
  // 护理人员不能预约服务
  if (isNurse.value) {
    ElMessage.warning('护理人员不能预约服务')
    return
  }
  currentService.value = service
  orderForm.service_id = service.id
  orderForm.service_name = service.name
  orderForm.price = service.price
  showOrderDialog.value = true
}

const submitOrder = async () => {
  try {
    // 验证必填项
    if (!orderForm.service_time) {
      ElMessage.warning('请选择服务时间')
      return
    }

    // 格式化服务时间
    let serviceTime = orderForm.service_time
    if (serviceTime instanceof Date) {
      const year = serviceTime.getFullYear()
      const month = String(serviceTime.getMonth() + 1).padStart(2, '0')
      const day = String(serviceTime.getDate()).padStart(2, '0')
      const hours = String(serviceTime.getHours()).padStart(2, '0')
      const minutes = String(serviceTime.getMinutes()).padStart(2, '0')
      serviceTime = `${year}-${month}-${day} ${hours}:${minutes}:00`
    }

    const res: any = await api.post('/orders/', {
      service_id: orderForm.service_id,
      service_time: serviceTime,
      notes: orderForm.notes
    })
    if (res.code === 200) {
      ElMessage.success('预约成功，请在30分钟内完成支付')
      showOrderDialog.value = false
      // 显示支付对话框
      currentOrder.value = res.data
      showPayDialog.value = true
      // 获取支付配置
      getPaymentConfig()
    } else {
      ElMessage.error(res.message || '预约失败')
    }
  } catch (error: any) {
    console.error('预约失败', error)
    const errorMsg = error?.response?.data?.message || error?.message || '预约失败'
    ElMessage.error(errorMsg)
  }
}

// 获取支付配置
const getPaymentConfig = async () => {
  try {
    const res: any = await api.get('/payment/config')
    if (res.code === 200) {
      paymentConfig.alipay_enabled = res.data.alipay_enabled
      paymentConfig.wechat_enabled = res.data.wechat_enabled
      // 默认选择启用的支付方式
      if (!paymentConfig.alipay_enabled && paymentConfig.wechat_enabled) {
        payPlatform.value = 'wechat'
      }
    }
  } catch (error) {
    console.error('获取支付配置失败', error)
  }
}

// 确���支付
const confirmPayment = async () => {
  if (!currentOrder.value) return

  paying.value = true
  showPayingDialog.value = true

  try {
    // 创建支付
    const res: any = await api.post('/payment/create', {
      order_id: currentOrder.value.id,
      platform: payPlatform.value
    })

    if (res.code === 200) {
      const paymentData = res.data.payment_data

      // 检查是否是模拟模式
      if (paymentData.mock) {
        // 模拟支付 - 直接跳转模拟支付页面
        window.location.href = paymentData.payment_url
        return
      }

      // 根据平台调用支付
      if (payPlatform.value === 'alipay') {
        // 支付宝支付
        window.location.href = paymentData.payment_url
      } else {
        // 微信支付 - 唤起微信支付
        if (paymentData.appid) {
          // APP支付
          callWechatPay(paymentData)
        } else {
          ElMessage.error('微信支付配置不完整')
          showPayingDialog.value = false
        }
      }

      // 启动轮询检查支付状态
      startPaymentPolling()
    } else {
      ElMessage.error(res.message || '创建支付失败')
      showPayingDialog.value = false
    }
  } catch (error) {
    console.error('支付失败', error)
    ElMessage.error('支付失败')
    showPayingDialog.value = false
  } finally {
    paying.value = false
  }
}

// 微信支付
const callWechatPay = (data: any) => {
  // 在实际环境中，这里需要调用微信SDK唤起支付
  // 由于没有真实AppId，暂时使用模拟方式
  ElMessage.info('微信支付功能需要配置真实AppId')
  showPayingDialog.value = false
}

// 轮询检查支付状态
let pollingTimer: any = null
const startPaymentPolling = () => {
  let count = 0
  const maxCount = 60 // 最多查询60次，约30秒
  
  pollingTimer = setInterval(async () => {
    count++
    try {
      const res: any = await api.get(`/payment/query/${currentOrder.value.orderNo}?platform=${payPlatform.value}`)
      if (res.code === 200) {
        const orderStatus = res.data.order_status
        if (orderStatus === 2) { // 已支付
          ElMessage.success('支付成功！')
          showPayingDialog.value = false
          showPayDialog.value = false
          stopPaymentPolling()
          // 刷新订单列表或跳转
        } else if (orderStatus === 0) { // 已取消
          ElMessage.warning('订单已超时取消')
          showPayingDialog.value = false
          showPayDialog.value = false
          stopPaymentPolling()
        }
      }
    } catch (error) {
      console.error('查询支付状态失败', error)
    }
    
    if (count >= maxCount) {
      ElMessage.warning('支付超时，请稍后查看支付结果')
      showPayingDialog.value = false
      stopPaymentPolling()
    }
  }, 1000)
}

const stopPaymentPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

// 取消支付
const cancelPayment = () => {
  if (currentOrder.value) {
    api.post(`/payment/cancel/${currentOrder.value.id}`)
      .then((res: any) => {
        if (res.code === 200) {
          ElMessage.success('订单已取消')
        }
      })
      .catch(console.error)
  }
  showPayDialog.value = false
  showPayingDialog.value = false
  stopPaymentPolling()
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
  getPaymentConfig()
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

.service-requirements-tag {
  color: #67c23a;
  font-weight: 600;
  font-size: 12px;
  background: #f0f9eb;
  padding: 2px 8px;
  border-radius: 4px;
}

.service-requirements {
  margin-top: 10px;
  padding: 8px 12px;
  background: #f4f4f5;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  
  strong {
    color: #303133;
    margin-right: 5px;
  }
}

.detail-requirements {
  color: #67c23a;
  font-weight: 600;
  font-size: 16px;
  margin: 10px 0;
  padding: 10px;
  background: #f0f9eb;
  border-radius: 4px;
  
  p {
    margin: 10px 0 0 0;
    font-weight: normal;
    color: #606266;
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

// 支付相关样式
.pay-info {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
  
  .pay-amount {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    
    .label {
      font-size: 14px;
      color: #606266;
    }
    
    .amount {
      font-size: 28px;
      font-weight: 700;
      color: #f56c6c;
    }
  }
  
  .pay-order {
    font-size: 12px;
    color: #909399;
  }
}

.pay-methods {
  .pay-method-title {
    font-size: 14px;
    color: #606266;
    margin-bottom: 15px;
  }
  
  .method-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .pay-method-item {
    padding: 15px;
    border: 1px solid #dcdfe6;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover:not(.disabled) {
      border-color: #409eff;
      background: #ecf5ff;
    }
    
    &.is-checked {
      border-color: #409eff;
      background: #ecf5ff;
    }
    
    &.disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .method-content {
      display: flex;
      align-items: center;
      gap: 15px;
      
      .method-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: bold;
        color: #fff;
        
        &.alipay-icon {
          background: linear-gradient(135deg, #1677ff 0%, #0958d9 100%);
        }
        
        &.wechat-icon {
          background: linear-gradient(135deg, #07c160 0%, #06ad56 100%);
        }
      }
      
      .method-name {
        flex: 1;
        font-size: 16px;
        font-weight: 500;
      }
    }
  }
}

.paying-content {
  text-align: center;
  padding: 30px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 20px auto;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
