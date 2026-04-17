<template>
  <div class="payment-result-container">
    <el-card class="result-card">
      <div v-if="loading" class="loading-content">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>正在处理支付结果...</p>
      </div>

      <div v-else-if="success" class="success-content">
        <el-icon class="success-icon"><CircleCheck /></el-icon>
        <h2>支付成功</h2>
        <p class="order-info">订单号：{{ orderNo }}</p>
        <p class="amount">支付金额：¥{{ amount }}</p>
        <el-button type="primary" @click="goToServices">返回服务列表</el-button>
        <el-button @click="goToDashboard">返回工作台</el-button>
      </div>

      <div v-else class="failed-content">
        <el-icon class="failed-icon"><CircleClose /></el-icon>
        <h2>{{ failedMessage }}</h2>
        <p class="order-info">订单号：{{ orderNo }}</p>
        <el-button type="primary" @click="goToServices">重新支付</el-button>
        <el-button @click="goToDashboard">返回工作台</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { CircleCheck, CircleClose, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const success = ref(false)
const failedMessage = ref('支付失败')
const orderNo = ref('')
const amount = ref('')

const checkPaymentResult = async () => {
  const order_no = route.query.out_trade_no || route.query.order_no

  if (!order_no) {
    failedMessage.value = '未找到订单信息'
    loading.value = false
    return
  }

  orderNo.value = order_no as string
  amount.value = (route.query.total_amount as string) || ''

  try {
    // 查询支付状态
    const res: any = await api.get(`/payment/query/${order_no}?platform=alipay`)

    if (res.code === 200) {
      if (res.data.order_status === 2) {
        success.value = true
        ElMessage.success('支付成功！')
      } else if (res.data.order_status === 0) {
        failedMessage.value = '订单已取消'
        loading.value = false
      } else {
        failedMessage.value = `订单状态：${res.data.status_text}`
        loading.value = false
      }
    } else {
      failedMessage.value = res.message || '查询支付结果失败'
      loading.value = false
    }
  } catch (error) {
    console.error('查询支付结果失败:', error)
    failedMessage.value = '网络错误，请稍后重试'
  }

  loading.value = false
}

const goToServices = () => {
  router.push('/services')
}

const goToDashboard = () => {
  router.push('/dashboard')
}

onMounted(() => {
  checkPaymentResult()
})
</script>

<style scoped lang="scss">
.payment-result-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.result-card {
  max-width: 400px;
  width: 100%;
  text-align: center;

  :deep(.el-card__body) {
    padding: 40px;
  }
}

.loading-content,
.success-content,
.failed-content {
  p {
    color: #606266;
    margin: 10px 0;
  }
}

.loading-content {
  .el-icon {
    font-size: 48px;
    color: #409eff;
    margin-bottom: 20px;
  }
}

.success-content,
.failed-content {
  .el-icon {
    font-size: 64px;
    margin-bottom: 20px;
  }

  h2 {
    margin: 0 0 20px 0;
    color: #303133;
  }

  .order-info {
    font-size: 14px;
    color: #909399;
  }

  .amount {
    font-size: 24px;
    color: #f56c6c;
    font-weight: bold;
    margin-bottom: 30px;
  }

  .el-button {
    margin: 5px;
  }
}

.success-icon {
  color: #67c23a;
}

.failed-icon {
  color: #f56c6c;
}
</style>
