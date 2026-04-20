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
        <!-- 语音播报按钮 -->
        <el-tooltip content="语音播报AI回复" placement="bottom">
          <el-button
            :type="voiceEnabled ? 'primary' : 'default'"
            circle
            @click="toggleVoice"
            :disabled="!lastAiResponse"
          >
            <el-icon :size="18">
              <Microphone v-if="!voiceEnabled" />
              <CloseBold v-else />
            </el-icon>
          </el-button>
        </el-tooltip>
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
      <!-- 语音输入动画提示 -->
      <div v-if="isListening" class="voice-indicator">
        <div class="voice-wave">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span class="voice-text">
          {{ interimTranscript || '正在聆听...' }}
        </span>
        <el-button type="danger" size="small" @click="stopListening">停止</el-button>
      </div>

      <el-input
        v-model="userInput"
        type="textarea"
        :rows="3"
        :placeholder="isListening ? '正在聆听，请说话...' : '请输入您的问题，或点击下方麦克风按钮语音输入'"
        :disabled="isSending || isListening"
        @keydown.ctrl.enter="sendMessage"
        resize="none"
      />
      <div class="input-actions">
        <div class="action-left">
          <!-- 语音输入按钮 -->
          <el-tooltip :content="getVoiceButtonTooltip()" placement="top">
            <el-button
              :type="isListening ? 'danger' : 'success'"
              circle
              @click="toggleVoiceInput"
              :disabled="isSending"
              class="voice-btn"
            >
              <div class="voice-btn-content">
                <el-icon :size="22" :class="{ 'pulsing': isListening }">
                  <Microphone v-if="!isListening" />
                  <CloseBold v-else />
                </el-icon>
              </div>
            </el-button>
          </el-tooltip>
        </div>
        <div class="action-right">
          <el-button
            type="primary"
            :loading="isSending"
            @click="sendMessage"
            :disabled="!userInput.trim() && !speechTranscript"
          >
            <el-icon><Promotion /></el-icon>
            发送 (Ctrl+Enter)
          </el-button>
        </div>
      </div>
      <!-- 错误提示 -->
      <div v-if="speechError" class="speech-error">
        <el-icon><Warning /></el-icon>
        <span class="error-text">{{ speechError }}</span>
        <el-button
          v-if="speechError.includes('权限')"
          type="primary"
          size="small"
          @click="handleRetryPermission"
          :loading="isRequestingPermission"
        >
          重新授权
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, User, Promotion, Microphone, CloseBold, Warning } from '@element-plus/icons-vue'
import api from '@/store/auth'
import { useSpeechRecognition } from '@/composables/useSpeechRecognition'
import { audioManager } from '@/utils/audioManager'

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
const lastAiResponse = ref('')
const voiceEnabled = ref(false)

// 语音识别相关
const {
  isListening,
  isSupported,
  isRequestingPermission,
  transcript: speechTranscript,
  interimTranscript,
  error: speechError,
  startListening,
  stopListening: stopVoiceInput,
  retryPermission
} = useSpeechRecognition()

// 获取语音按钮提示文本
const getVoiceButtonTooltip = () => {
  if (isListening.value) {
    return '正在聆听...'
  }
  if (!isSupported.value) {
    return '您的浏览器不支持语音输入'
  }
  if (isRequestingPermission.value) {
    return '正在请求权限...'
  }
  return '点击开始语音输入'
}

// 点击语音输入按钮
const toggleVoiceInput = async () => {
  if (isListening.value) {
    stopVoiceInput()
  } else {
    await startListening()
  }
}

// 重新请求麦克风权限
const handleRetryPermission = async () => {
  retryPermission()
  await startListening()
}

// 停止语音输入
const stopListening = () => {
  stopVoiceInput()
}

// 监听语音识别结果，自动填充到输入框
watch(speechTranscript, (newTranscript) => {
  if (newTranscript) {
    userInput.value = newTranscript
  }
})

// 切换语音播报
const toggleVoice = async () => {
  if (!lastAiResponse.value) return

  voiceEnabled.value = !voiceEnabled.value

  if (voiceEnabled.value) {
    try {
      await audioManager.speak(lastAiResponse.value)
    } catch (e) {
      ElMessage.error('语音播报失败')
      voiceEnabled.value = false
    }
  } else {
    audioManager.stopSpeaking()
  }
}

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

  // 停止语音播报
  if (voiceEnabled.value) {
    audioManager.stopSpeaking()
    voiceEnabled.value = false
  }

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    time: getCurrentTime()
  })
  userInput.value = ''
  speechTranscript.value = ''
  interimTranscript.value = ''
  await scrollToBottom()

  isSending.value = true
  isTyping.value = true

  try {
    const res: any = await api.post('/ai/chat', { message })
    if (res.code === 200) {
      const reply = res.data.reply
      messages.value.push({
        role: 'assistant',
        content: reply,
        time: getCurrentTime()
      })
      lastAiResponse.value = reply

      // 如果启用了语音播报，自动播放
      if (voiceEnabled.value) {
        try {
          await audioManager.speak(reply)
        } catch (e) {
          console.error('语音播报失败:', e)
        }
      }
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

onMounted(async () => {
  await audioManager.init() // 初始化音频
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
    display: flex;
    align-items: center;
    gap: 10px;

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

  // 语音输入指示器
  .voice-indicator {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 16px;
    margin-bottom: 12px;
    background: linear-gradient(135deg, #22c55e, #16a34a);
    border-radius: 12px;
    color: #fff;

    .voice-wave {
      display: flex;
      align-items: center;
      gap: 4px;
      height: 30px;

      span {
        width: 4px;
        background: #fff;
        border-radius: 2px;
        animation: voiceWave 0.8s ease-in-out infinite;

        &:nth-child(1) { height: 10px; animation-delay: 0s; }
        &:nth-child(2) { height: 20px; animation-delay: 0.1s; }
        &:nth-child(3) { height: 30px; animation-delay: 0.2s; }
        &:nth-child(4) { height: 20px; animation-delay: 0.3s; }
        &:nth-child(5) { height: 10px; animation-delay: 0.4s; }
      }
    }

    .voice-text {
      flex: 1;
      font-size: 14px;
      color: #fff;
    }
  }

  @keyframes voiceWave {
    0%, 100% {
      transform: scaleY(0.5);
      opacity: 0.7;
    }
    50% {
      transform: scaleY(1);
      opacity: 1;
    }
  }

  // 错误提示
  .speech-error {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
    padding: 10px 14px;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    color: #dc2626;
    font-size: 13px;
    flex-wrap: wrap;

    .error-text {
      flex: 1;
    }

    .el-button {
      margin-left: auto;
    }
  }

  .input-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;

    .action-left {
      display: flex;
      align-items: center;
      gap: 10px;

      .voice-btn {
        width: 48px;
        height: 48px;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;

        .voice-btn-content {
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .pulsing {
          animation: pulse 1.5s ease-in-out infinite;
        }
      }

      @keyframes pulse {
        0%, 100% {
          transform: scale(1);
          opacity: 1;
        }
        50% {
          transform: scale(1.2);
          opacity: 0.8;
        }
      }
    }

    .action-right {
      .el-button {
        display: flex;
        align-items: center;
        gap: 6px;
      }
    }
  }
}
</style>
