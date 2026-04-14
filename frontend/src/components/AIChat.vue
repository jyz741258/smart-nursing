<template>
  <div class="ai-chat-container">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-left">
        <el-icon :size="24" color="#409eff"><ChatDotRound /></el-icon>
        <div>
          <h2 class="title">AI健康助手</h2>
          <p class="subtitle" v-if="aiStatus === 'online'">● 在线</p>
          <p class="subtitle" v-else-if="aiStatus === 'offline'">● 服务未配置</p>
          <p class="subtitle" v-else>● 检查中...</p>
        </div>
      </div>
      <div class="header-right">
        <el-tag v-if="modelInfo" type="info" size="small">{{ modelInfo }}</el-tag>
      </div>
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message">
        <el-icon :size="48" color="#409eff"><ChatDotRound /></el-icon>
        <h3>你好！我是智能养老护理助手</h3>
        <p>我可以帮你解答以下问题：</p>
        <ul>
          <li>老年人健康咨询与护理建议</li>
          <li>常见老年病日常注意事项</li>
          <li>老年人心理关怀与沟通技巧</li>
          <li>紧急情况应对指导</li>
          <li>老年人日常生活护理知识</li>
        </ul>
        <el-alert
          title="重要提示"
          type="warning"
          :closable="false"
          show-icon
          style="max-width: 400px; margin-top: 20px;"
        >
          我提供的信息仅供参考，不能替代专业医疗建议。如有紧急情况，请立即联系医护人员或拨打急救电话。
        </el-alert>
      </div>

      <!-- 消息列表 -->
      <div v-else>
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <div class="message-avatar">
            <el-avatar :size="40" :icon="msg.role === 'user' ? 'User' : 'ChatDotRound'" />
          </div>
          <div class="message-content">
            <div class="message-bubble">
              {{ msg.content }}
            </div>
            <div class="message-time">{{ msg.time }}</div>
          </div>
        </div>

        <!-- AI正在输入 -->
        <div v-if="isTyping" class="message ai-message">
          <div class="message-avatar">
            <el-avatar :size="40" icon="ChatDotRound" />
          </div>
          <div class="message-content">
            <div class="message-bubble typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-area">
      <el-input
        v-model="userInput"
        type="textarea"
        :rows="3"
        placeholder="请输入您的问题..."
        :disabled="isSending"
        @keydown.ctrl.enter="sendMessage"
        resize="none"
      />
      <div class="input-actions">
        <el-button
          type="primary"
          :loading="isSending"
          @click="sendMessage"
          :disabled="!userInput.trim()"
        >
          <el-icon><Promotion /></el-icon>
          发送 (Ctrl+Enter)
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, User, Promotion } from '@element-plus/icons-vue'
import api from '@/store/auth'

interface Message {
  role: 'user' | 'assistant'
  content: string
  time: string
}

const messages = ref<Message[]>([])
const userInput = ref('')
const isSending = ref(false)
const isTyping = ref(false)
const aiStatus = ref<'checking' | 'online' | 'offline'>('checking')
const modelInfo = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 获取当前时间
const getCurrentTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

// 发送消息
const sendMessage = async () => {
  const message = userInput.value.trim()
  if (!message || isSending.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    time: getCurrentTime()
  })
  userInput.value = ''
  await scrollToBottom()

  isSending.value = true
  isTyping.value = true

  try {
    const res: any = await api.post('/ai/chat', { message })
    if (res.code === 200) {
      messages.value.push({
        role: 'assistant',
        content: res.data.reply,
        time: getCurrentTime()
      })
    } else {
      ElMessage.error(res.message || '发送失败')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '网络错误')
  } finally {
    isSending.value = false
    isTyping.value = false
    scrollToBottom()
  }
}

// 检查AI服务状态
const checkAIStatus = async () => {
  try {
    const res: any = await api.get('/ai/health-check')
    if (res.code === 200) {
      aiStatus.value = res.data.status === 'ok' ? 'online' : 'offline'
      modelInfo.value = res.data.model || '未知'
    } else {
      aiStatus.value = 'offline'
    }
  } catch (error) {
    aiStatus.value = 'offline'
  }
}

// 获取模型信息
const getModelInfo = async () => {
  try {
    const res: any = await api.get('/ai/models')
    if (res.code === 200 && res.data.length > 0) {
      modelInfo.value = res.data[0].name
    }
  } catch (error) {
    // 忽略错误
  }
}

onMounted(() => {
  checkAIStatus()
  getModelInfo()
})
</script>

<style scoped lang="scss">
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;

    .title {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }

    .subtitle {
      margin: 4px 0 0;
      font-size: 12px;
      opacity: 0.9;
    }
  }

  .header-right {
    .el-tag {
      background: rgba(255, 255, 255, 0.2);
      border: none;
      color: #fff;
    }
  }
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;

  .welcome-message {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    color: #606266;

    h3 {
      margin: 20px 0 10px;
      font-size: 20px;
      color: #303133;
    }

    p {
      margin: 5px 0;
      font-size: 14px;
    }

    ul {
      text-align: left;
      margin: 15px 0;
      padding-left: 20px;

      li {
        margin: 8px 0;
        font-size: 14px;
        color: #606266;
      }
    }
  }

  .message {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;

    &.user-message {
      flex-direction: row-reverse;

      .message-content {
        align-items: flex-end;
      }

      .message-bubble {
        background: #409eff;
        color: #fff;
        border-radius: 16px 16px 4px 16px;
      }
    }

    &.ai-message {
      .message-bubble {
        background: #fff;
        color: #303133;
        border-radius: 16px 16px 16px 4px;
      }
    }

    .message-avatar {
      flex-shrink: 0;
    }

    .message-content {
      display: flex;
      flex-direction: column;
      max-width: 70%;
    }

    .message-bubble {
      padding: 12px 16px;
      font-size: 14px;
      line-height: 1.6;
      word-wrap: break-word;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);

      &.typing {
        display: flex;
        gap: 4px;
        padding: 16px 20px;

        span {
          width: 8px;
          height: 8px;
          background: #909399;
          border-radius: 50%;
          animation: typing 1.4s infinite ease-in-out;

          &:nth-child(1) { animation-delay: -0.32s; }
          &:nth-child(2) { animation-delay: -0.16s; }
        }
      }
    }

    .message-time {
      font-size: 11px;
      color: #909399;
      margin-top: 4px;
      padding: 0 4px;
    }
  }
}

@keyframes typing {
  0%, 80%, 100% {
    transform: translateY(0);
    opacity: 0.6;
  }
  40% {
    transform: translateY(-6px);
    opacity: 1;
  }
}

.chat-input-area {
  padding: 16px 20px;
  background: #fff;
  border-top: 1px solid #e4e7ed;

  .input-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;

    .el-button {
      display: flex;
      align-items: center;
      gap: 6px;
    }
  }
}
</style>
