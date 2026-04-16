<template>
  <div
    class="chat-message"
    :class="{
      'is-user': isUser,
      'is-typing': isTyping,
      'has-avatar': showAvatar
    }"
    :style="messageStyle"
  >
    <!-- 头像 -->
    <div v-if="showAvatar" class="message-avatar">
      <div v-if="isUser" class="avatar user-avatar">
        <el-icon><User /></el-icon>
      </div>
      <div v-else class="avatar ai-avatar">
        <img src="/ai-avatar.png" alt="AI" @error="handleAvatarError" />
        <div class="avatar-glow"></div>
      </div>
    </div>

    <!-- 消息内容容器 -->
    <div class="message-wrapper">
      <!-- 消息气泡 -->
      <div class="message-bubble" :class="bubbleClass">
        <!-- 打字机效果文本 -->
        <div class="message-content" ref="contentRef">
          <span v-if="isTyping" class="typing-cursor"></span>
          <span v-html="displayContent"></span>
        </div>

        <!-- 快速回复按钮（仅 AI 消息） -->
        <div v-if="!isUser && quickReplies?.length" class="quick-replies">
          <el-button
            v-for="(reply, idx) in quickReplies"
            :key="idx"
            size="small"
            @click="handleQuickReply(reply)"
            class="quick-reply-btn"
          >
            {{ reply }}
          </el-button>
        </div>

        <!-- 操作按钮（复制/删除等） -->
        <div v-if="!isUser && actions" class="message-actions">
          <button class="action-btn" @click="$emit('copy', content)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 时间戳 -->
      <div class="message-time" v-if="showTime">
        <span>{{ formattedTime }}</span>
        <span v-if="isUser && status" class="message-status">
          <svg v-if="status === 'sent'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12" />
          </svg>
          <svg v-else-if="status === 'sending'" class="sending-animation" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="12" x2="12" y2="12" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from 'vue'

interface Props {
  content: string // 完整消息内容
  isUser?: boolean // 是否为用户消息
  typingSpeed?: number // 打字速度（毫秒/字符）
  showAvatar?: boolean // 是否显示头像
  showTime?: boolean // 是否显示时间
  timestamp?: Date // 消息时间
  status?: 'sent' | 'sending' | 'error' // 消息状态
  quickReplies?: string[] // 快捷回复选项
  actions?: boolean // 是否显示操作按钮
  delay?: number // 动画延迟
}

const props = withDefaults(defineProps<Props>(), {
  isUser: false,
  typingSpeed: 30,
  showAvatar: true,
  showTime: true,
  status: 'sent',
  quickReplies: () => [],
  actions: false,
  delay: 0
})

const emit = defineEmits(['quick-reply', 'copy', 'typing-complete'])

const contentRef = ref<HTMLElement>()
const displayContent = ref('')
const isTyping = ref(false)
const isComplete = ref(false)
let typingTimer: NodeJS.Timeout | null = null
let currentIndex = 0

// 格式化时间
const formattedTime = computed(() => {
  if (!props.timestamp) return ''
  const date = props.timestamp instanceof Date ? props.timestamp : new Date(props.timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})

// 气泡类名
const bubbleClass = computed(() => ({
  'bubble-user': props.isUser,
  'bubble-ai': !props.isUser
}))

// 消息容器样式
const messageStyle = computed(() => {
  const style: any = {}
  if (props.delay) {
    style.animationDelay = `${props.delay}ms`
  }
  return style
})

// 处理头像加载失败
const handleAvatarError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

// 执行打字机动画
const typeWriter = () => {
  if (currentIndex < props.content.length) {
    displayContent.value = props.content.slice(0, currentIndex + 1)
    currentIndex++

    // 随机打字速度（模拟真人）
    const randomSpeed = props.typingSpeed + (Math.random() - 0.5) * 10
    typingTimer = setTimeout(typeWriter, randomSpeed)
  } else {
    // 完成
    isTyping.value = false
    isComplete.value = true
    emit('typing-complete')
  }
}

// 开始动画
const startTyping = () => {
  if (isComplete.value) return

  isTyping.value = true
  displayContent.value = ''

  // 延迟开始
  setTimeout(() => {
    currentIndex = 0
    typeWriter()
  }, props.delay)
}

// 跳过动画，直接显示全部
const skipTyping = () => {
  if (typingTimer) {
    clearTimeout(typingTimer)
  }
  displayContent.value = props.content
  isTyping.value = false
  isComplete.value = true
  emit('typing-complete')
}

// 处理快捷回复点击
const handleQuickReply = (reply: string) => {
  emit('quick-reply', reply)
}

// 监听内容变化
watch(() => props.content, () => {
  currentIndex = 0
  isComplete.value = false

  if (props.isUser) {
    // 用户消息立即显示
    displayContent.value = props.content
    isTyping.value = false
    isComplete.value = true
  } else {
    // AI 消息打字机效果
    startTyping()
  }
}, { immediate: true })

onMounted(() => {
  // 挂载后自动开始（如果配置了）
})

onUnmounted(() => {
  if (typingTimer) {
    clearTimeout(typingTimer)
  }
})

// 暴露方法
defineExpose({
  startTyping,
  skipTyping
})
</script>

<style scoped lang="scss">
.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  opacity: 0;
  animation: messageSlideIn 0.5s var(--ease-bounce) both;

  &.is-user {
    flex-direction: row-reverse;

    .message-wrapper {
      align-items: flex-end;
    }
  }

  @keyframes messageSlideIn {
    0% {
      opacity: 0;
      transform: translateY(20px) scale(0.95);
    }
    100% {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }
}

.message-avatar {
  flex-shrink: 0;

  .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    position: relative;
    overflow: visible;

    &.user-avatar {
      background: var(--gradient-primary);
      color: white;
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    &.ai-avatar {
      background: var(--bg-tertiary);
      border: 2px solid var(--border-color);
      overflow: hidden;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .avatar-glow {
        position: absolute;
        inset: -2px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
        opacity: 0.5;
        filter: blur(4px);
        z-index: -1;
        animation: avatarGlow 2s ease-in-out infinite;
      }
    }
  }

  @keyframes avatarGlow {
    0%, 100% { opacity: 0.3; transform: scale(0.95); }
    50% { opacity: 0.6; transform: scale(1.05); }
  }
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 80%;
}

.message-bubble {
  position: relative;
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
  animation: bubblePop 0.4s var(--ease-bounce) both;

  &.bubble-user {
    background: var(--gradient-primary);
    color: white;
    border: none;
    border-bottom-right-radius: 4px;
  }

  &.bubble-ai {
    background: var(--bg-elevated);
    color: var(--text-primary);
    border-bottom-left-radius: 4px;
  }

  @keyframes bubblePop {
    0% {
      opacity: 0;
      transform: scale(0.8) translateY(10px);
    }
    100% {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }
}

.message-content {
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;

  // 打字时光标闪烁
  .typing-cursor {
    display: inline-block;
    width: 2px;
    height: 1em;
    background: var(--color-primary);
    margin-left: 2px;
    vertical-align: middle;
    animation: blink 1s step-end infinite;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
  }

  // AI 消息添加波纹强调效果
  .is-typing & {
    &::after {
      content: '';
      display: inline-block;
      width: 4px;
      height: 4px;
      background: var(--color-primary);
      border-radius: 50%;
      margin-left: 4px;
      animation: dotPulse 1.4s ease-in-out infinite both;
    }
  }
}

// 快捷回复
.quick-replies {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-light);

  .quick-reply-btn {
    font-size: 12px;
    padding: 4px 12px;
    border-radius: var(--radius-full);
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    transition: all 0.2s ease;

    &:hover {
      background: var(--color-primary);
      color: white;
      border-color: var(--color-primary);
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
  }
}

// 消息操作按钮
.message-actions {
  position: absolute;
  top: 4px;
  right: -30px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;

  .message-bubble:hover & {
    opacity: 1;
  }

  .action-btn {
    width: 24px;
    height: 24px;
    padding: 0;
    border: none;
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;

    svg {
      width: 14px;
      height: 14px;
    }

    &:hover {
      background: var(--color-primary);
      color: white;
    }
  }
}

.message-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-tertiary);
  padding: 0 4px;

  .message-status {
    display: flex;
    align-items: center;

    svg {
      width: 14px;
      height: 14px;
    }

    .sending-animation {
      animation: spin 1s linear infinite;
    }
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes dotPulse {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}
</style>
