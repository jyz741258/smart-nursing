<template>
  <el-button
    ref="btnRef"
    :class="buttonClass"
    :type="type"
    :size="size"
    :disabled="disabled || loading"
    v-bind="$attrs"
    @click="handleClick"
    @mouseenter="onMouseEnter"
    @mousemove="onMouseMove"
    @mouseleave="onMouseLeave"
  >
    <!-- 加载状态 -->
    <template v-if="loading" #loading>
      <svg class="loading-spinner" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-dasharray="31.4 31.4" />
      </svg>
    </template>

    <!-- 图标 -->
    <span v-if="$slots.icon || icon" class="btn-icon">
      <slot name="icon">
        <el-icon v-if="icon">
          <component :is="icon" />
        </el-icon>
      </slot>
    </span>

    <!-- 文字 -->
    <span class="btn-text" :class="{ 'has-icon': $slots.icon || icon }">
      <slot></slot>
    </span>

    <!-- 磁性吸附效果层 -->
    <div
      v-if="magnetic"
      class="magnetic-layer"
      :style="magneticStyle"
    ></div>

    <!-- 涟漪效果容器 -->
    <div v-if="ripple && !loading" class="ripple-container" ref="rippleContainer"></div>

    <!-- 光泽扫过效果 -->
    <div v-if="shine" class="shine-layer" :class="{ 'shine-active': shineActive }"></div>

    <!-- 成功/错误状态指示器 -->
    <div v-if="statusIndicator" class="status-indicator" :class="statusClass">
      <svg v-if="status === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
        <polyline points="20 6 9 17 4 12" />
      </svg>
      <svg v-else-if="status === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
    </div>
  </el-button>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import type { ButtonProps } from 'element-plus'

interface Props {
  type?: ButtonProps['type']
  size?: ButtonProps['size']
  disabled?: boolean
  loading?: boolean
  icon?: string // Element Plus 图标名称

  // 动效配置
  magnetic?: boolean // 磁性吸附效果
  ripple?: boolean // 涟漪点击效果
  shine?: boolean // 光泽扫过效果
  statusIndicator?: boolean // 成功/错误状态指示

  // 音效
  sound?: 'click' | 'success' | 'error' | 'none' // 点击音效类型

  // 状态
  status?: 'success' | 'error' | null
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'default',
  disabled: false,
  loading: false,
  magnetic: false,
  ripple: true,
  shine: true,
  statusIndicator: false,
  sound: 'click',
  status: null
})

const emit = defineEmits(['click', 'magnetic-move'])

const btnRef = ref<HTMLElement>()
const rippleContainer = ref<HTMLElement>()
const mouseX = ref(0)
const mouseY = ref(0)
const buttonX = ref(0)
const buttonY = ref(0)
const shineActive = ref(false)

// 磁性吸附样式
const magneticStyle = computed(() => {
  if (!props.magnetic) return {}

  const deltaX = mouseX.value - buttonX.value
  const deltaY = mouseY.value - buttonY.value
  const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
  const maxMove = 8 // 最大移动距离

  // 计算吸附强度（越近吸附越强）
  const strength = Math.max(0, 1 - distance / (btnRef.value?.offsetWidth || 100))
  const moveX = (deltaX / distance) * strength * maxMove || 0
  const moveY = (deltaY / distance) * strength * maxMove || 0

  return {
    transform: `translate(${moveX}px, ${moveY}px)`,
    transition: strength > 0.8 ? 'transform 0.1s ease-out' : 'none'
  }
})

// 按钮类名
const buttonClass = computed(() => ({
  'btn-enhanced': true,
  'btn-magnetic': props.magnetic,
  'btn-ripple': props.ripple,
  'btn-shine': props.shine,
  'btn-status-indicator': props.statusIndicator,
  [`btn-${props.type}`]: props.type,
  [`btn-${props.size}`]: props.size,
  'is-loading': props.loading,
  'has-status': props.status
}))

// 状态类名
const statusClass = computed(() => ({
  [`status-${props.status}`]: props.status
}))

// 创建涟漪效果
const createRipple = (event: MouseEvent) => {
  if (!props.ripple || !rippleContainer.value) return

  const button = btnRef.value
  if (!button) return

  const rect = button.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top

  const ripple = document.createElement('span')
  ripple.className = 'ripple-effect'
  ripple.style.cssText = `
    left: ${x}px;
    top: ${y}px;
    width: 100px;
    height: 100px;
    margin-left: -50px;
    margin-top: -50px;
  `

  rippleContainer.value.appendChild(ripple)

  // 动画结束后移除
  ripple.addEventListener('animationend', () => {
    ripple.remove()
  })
}

// 播放音效
const playSound = () => {
  if (props.sound === 'none') return

  // 这里需要访问 audioManager，通过 inject 或全局
  // 延迟一点以确保音频上下文已激活
  setTimeout(() => {
    const audioManager = (window as any).$audio
    if (audioManager?.isEnabled()) {
      audioManager.play(props.sound === 'click' ? 'click' : props.sound || 'click')
    }
  }, 0)
}

// 处理点击
const handleClick = (event: MouseEvent) => {
  if (props.disabled || props.loading) return

  createRipple(event)
  playSound()

  // 触发光效
  shineActive.value = true
  setTimeout(() => {
    shineActive.value = false
  }, 600)

  emit('click', event)
}

// 鼠标移动（用于磁性效果）
const onMouseMove = (event: MouseEvent) => {
  const button = btnRef.value
  if (!button) return

  const rect = button.getBoundingClientRect()
  mouseX.value = event.clientX - rect.left
  mouseY.value = event.clientY - rect.top
  buttonX.value = rect.width / 2
  buttonY.value = rect.height / 2

  emit('magnetic-move', { x: mouseX.value, y: mouseY.value })
}

const onMouseEnter = () => {
  // 可以在这里添加悬停音效
}

const onMouseLeave = () => {
  mouseX.value = 0
  mouseY.value = 0
}

onMounted(() => {
  // 初始化时可以做一些准备工作
})
</script>

<style scoped lang="scss">
.btn-enhanced {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
  transform: translateZ(0); // GPU 加速

  // 禁用状态
  &:disabled,
  &.is-disabled {
    cursor: not-allowed;
    opacity: 0.6;
    transform: none !important;
  }

  // 加载状态
  &.is-loading {
    cursor: wait;
  }

  // 光泽扫过效果
  &.btn-shine::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.25),
      transparent
    );
    transform: skewX(-15deg);
    transition: none;
    pointer-events: none;
  }

  &.btn-shine:hover::after,
  .shine-active::after {
    animation: shineSweep 0.6s ease;
  }

  @keyframes shineSweep {
    0% {
      left: -100%;
    }
    100% {
      left: 100%;
    }
  }

  // 涟漪效果
  .ripple-container {
    position: absolute;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
    z-index: 1;
  }

  .ripple-effect {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.4);
    transform: scale(0);
    animation: rippleExpand 0.6s ease-out;
    pointer-events: none;
  }

  @keyframes rippleExpand {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }

  // 磁性吸附层
  .magnetic-layer {
    position: absolute;
    inset: -20px;
    z-index: 0;
    pointer-events: none;
  }

  // 状态指示器
  .status-indicator {
    position: absolute;
    right: -8px;
    top: -8px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
    animation: statusPop 0.3s var(--ease-bounce);

    svg {
      width: 12px;
      height: 12px;
    }

    &.status-success {
      background: var(--color-success);
      color: white;
      box-shadow: 0 0 10px var(--color-success);
    }

    &.status-error {
      background: var(--color-error);
      color: white;
      box-shadow: 0 0 10px var(--color-error);
    }
  }

  @keyframes statusPop {
    0% {
      transform: scale(0);
      opacity: 0;
    }
    50% {
      transform: scale(1.2);
    }
    100% {
      transform: scale(1);
      opacity: 1;
    }
  }

  // 加载动画
  .loading-spinner {
    width: 16px;
    height: 16px;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
}

// 按钮尺寸适配
.btn-sm {
  .btn-icon {
    font-size: 14px;
  }
}

.btn-lg {
  .btn-icon {
    font-size: 18px;
  }
}

// 按钮类型微调
.btn-primary {
  background: var(--gradient-primary);
  border: none;
  color: white;

  &:hover {
    box-shadow: var(--shadow-glow-primary);
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
  }
}

// 主题色变化动画
.btn-primary.btn-enhanced {
  position: relative;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.2) 0%,
      transparent 50%,
      rgba(255, 255, 255, 0.1) 100%
    );
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover::before {
    opacity: 1;
  }
}
</style>
