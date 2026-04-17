<template>
  <div class="mock-payment-container">
    <el-card class="mock-card">
      <template #header>
        <div class="mock-header">
          <el-icon size="32" color="#409eff"><Wallet /></el-icon>
          <h2>模拟支付</h2>
        </div>
      </template>

      <div class="mock-content">
        <div class="order-info">
          <p><strong>订单号：</strong>{{ orderNo }}</p>
          <p><strong>商品：</strong>{{ subject }}</p>
          <p class="amount"><strong>支付金额：</strong>¥{{ amount }}</p>
        </div>

        <el-divider />

        <div class="payment-methods">
          <h3>选择支付方式（模拟）</h3>
          <el-radio-group v-model="selectedMethod" class="method-group">
            <el-radio label="balance">
              <div class="method-item">
                <span>账户余额支付</span>
                <span class="balance">余额: ¥99999.00</span>
              </div>
            </el-radio>
            <el-radio label="coupon">
              <div class="method-item">
                <span>优惠券抵扣</span>
                <span class="balance">暂无可用优惠券</span>
              </div>
            </el-radio>
          </el-radio-group>
        </div>

        <el-divider />

        <div class="actions">
          <el-button type="primary" size="large" :loading="processing" @click="handleMockPay">
            确认支付 ¥{{ amount }}
          </el-button>
          <el-button size="large" @click="handleCancel">取消</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Wallet } from '@element-plus/icons-vue'
import api from '@/store/auth'

const router = useRouter()
const route = useRoute()

const orderNo = ref('')
const subject = ref('护理服务')
const amount = ref('0.00')
const selectedMethod = ref('balance')
const processing = ref(false)

const handleMockPay = async () => {
  if (!orderNo.value) {
    ElMessage.error('订单号无效')
    return
  }

  processing.value = true

  try {
    const res: any = await api.post('/payment/mock', null, {
      params: { order_no: orderNo.value }
    })

    if (res.success) {
      ElMessage.success('支付成功！')
      // 跳转到结果页面
      setTimeout(() => {
        router.replace(`/payment/result?out_trade_no=${orderNo.value}`)
      }, 500)
    } else {
      ElMessage.error(res.message || '支付失败')
    }
  } catch (error: any) {
    console.error('模拟支付失败:', error)
    ElMessage.error(error?.response?.data?.message || '支付失败，请重试')
  } finally {
    processing.value = false
  }
}

const handleCancel = () => {
  router.push('/services')
}

onMounted(() => {
  orderNo.value = route.query.order_no as string || ''
  subject.value = route.query.subject as string || '护理服务'
  amount.value = route.query.amount as string || '0.00'

  if (!orderNo.value) {
    ElMessage.error('订单号无效')
    router.push('/services')
  }
})
</script>

<style scoped lang="scss">
.mock-payment-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.mock-card {
  max-width: 450px;
  width: 100%;

  :deep(.el-card__header) {
    text-align: center;
  }
}

.mock-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;

  h2 {
    margin: 0;
    color: #303133;
  }
}

.mock-content {
  padding: 10px 0;
}

.order-info {
  text-align: left;

  p {
    margin: 10px 0;
    color: #606266;

    &.amount {
      font-size: 24px;
      color: #f56c6c;
      font-weight: bold;
    }
  }
}

.payment-methods {
  h3 {
    margin: 0 0 15px 0;
    font-size: 14px;
    color: #606266;
  }

  .method-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;

    :deep(.el-radio) {
      width: 100%;
      padding: 12px;
      border: 1px solid #dcdfe6;
      border-radius: 8px;
      margin-right: 0;

      &:hover {
        border-color: #409eff;
        background: #f5f7fa;
      }

      &.is-checked {
        border-color: #409eff;
        background: #ecf5ff;
      }
    }

    .method-item {
      display: flex;
      justify-content: space-between;
      width: 100%;

      .balance {
        color: #909399;
        font-size: 12px;
      }
    }
  }
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 10px;

  .el-button {
    width: 100%;
  }
}
</style>
