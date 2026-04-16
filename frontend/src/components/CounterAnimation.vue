<template>
  <div class="counter-animation" :class="sizeClass" :style="colorStyle">
    <span ref="numberRef" class="counter-value">
      {{ displayValue }}
    </span>

    <!-- 后缀图标或文字 -->
    <span v-if="suffix" class="counter-suffix">{{ suffix }}</span>

    <!-- 前缀图标或文字 -->
    <span v-if="prefix" class="counter-prefix">{{ prefix }}</span>

    <!-- 增长箭头指示器 -->
    <span v-if="showTrend && trend > 0" class="trend-indicator up">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="18 15 12 9 6 15" />
      </svg>
      <span class="trend-value">+{{ trend }}%</span>
    </span>

    <span v-else-if="showTrend && trend < 0" class="trend-indicator down">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 12 15 18 9" />
      </svg>
      <span class="trend-value">{{ trend }}%</span>
    </span>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'

interface Props {
  value: number // 目标值
  startValue?: number // 起始值
  duration?: number // 动画时长（毫秒）
  delay?: number // 延迟（毫秒）
  decimals?: number // 小数位数
  prefix?: string // 前缀
  suffix?: string // 后缀
  showTrend?: boolean // 是否显示趋势
  trend?: number // 趋势百分比
  size?: 'small' | 'medium' | 'large' | 'xlarge' // 尺寸
  color?: string // 自定义颜色
  separator?: string // 千位分隔符
  animateOnMount?: boolean // 挂载时是否自动播放
}

const props = withDefaults(defineProps<Props>(), {
  startValue: 0,
  duration: 1500,
  delay: 0,
  decimals: 0,
  showTrend: false,
  trend: 0,
  size: 'medium',
  separator: ',',
  animateOnMount: true
})

const displayValue = ref(props.startValue.toString())
const numberRef = ref<HTMLElement>()
let animationFrameId: number | null = null
let startTime: number | null = null

// 缓动函数：easeOutQuart（平滑减速）
const easeOutQuart = (t: number): number => {
  return 1 - Math.pow(1 - t, 4)
}

// 格式化数字
const formatNumber = (num: number): string => {
  const fixed = num.toFixed(props.decimals)
  const parts = fixed.split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, props.separator)
  return parts.join('.')
}

// 动画循环
const animate = (timestamp: number) => {
  if (!startTime) startTime = timestamp
  const elapsed = timestamp - startTime
  const progress = Math.min(elapsed / props.duration, 1)
  const easedProgress = easeOutQuart(progress)

  // 计算当前值
  const current = props.startValue + (props.value - props.startValue) * easedProgress
  displayValue.value = formatNumber(current)

  if (progress < 1) {
    animationFrameId = requestAnimationFrame(animate)
  }
}

// 启动动画
const startAnimation = () => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  startTime = null
  displayValue.value = formatNumber(props.startValue)

  // 延迟启动
  setTimeout(() => {
    animationFrameId = requestAnimationFrame(animate)
  }, props.delay)
}

// 重置并重新播放
const replay = () => {
  startAnimation()
}

// 尺寸类名
const sizeClass = computed(() => ({
  [`counter-${props.size}`]: true
}))

// 颜色样式
const colorStyle = computed(() => {
  if (!props.color) return {}

  let color = props.color

  // 根据趋势设置颜色
  if (props.showTrend) {
    if (props.trend > 0) {
      color = 'var(--color-success)'
    } else if (props.trend < 0) {
      color = 'var(--color-error)'
    }
  }

  return {
    color
  }
})

// 监听 value 变化
watch(() => props.value, () => {
  if (props.animateOnMount) {
    startAnimation()
  }
})

onMounted(() => {
  if (props.animateOnMount) {
    startAnimation()
  }
})

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
})

// 暴露方法
defineExpose({
  replay,
  startAnimation
})
</script>

<style scoped lang="scss">
.counter-animation {
  display: inline-flex;
  align-items: baseline;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  letter-spacing: -0.02em;

  // 尺寸变体
  &.counter-small {
    font-size: 14px;
    line-height: 1.4;
  }

  &.counter-medium {
    font-size: 20px;
    line-height: 1.3;
  }

  &.counter-large {
    font-size: 32px;
    line-height: 1.2;
  }

  &.counter-xlarge {
    font-size: 48px;
    line-height: 1.1;
    font-weight: 800;
  }

  .counter-value {
    display: inline;
    background: linear-gradient(
      135deg,
      var(--text-primary) 0%,
      var(--color-primary-light) 100%
    );
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.3));
    animation: valueGlow 2s ease-in-out infinite alternate;
  }

  @keyframes valueGlow {
    0% {
      filter: drop-shadow(0 0 4px rgba(102, 126, 234, 0.2));
    }
    100% {
      filter: drop-shadow(0 0 12px rgba(102, 126, 234, 0.5));
    }
  }

  .counter-suffix,
  .counter-prefix {
    color: var(--text-secondary);
    font-weight: 500;
    margin: 0 4px;
  }

  // 趋势指示器
  .trend-indicator {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-left: 8px;
    padding: 2px 6px;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-weight: 600;
    animation: trendPop 0.4s var(--ease-bounce);

    svg {
      width: 14px;
      height: 14px;
    }

    &.up {
      background: var(--color-success-bg);
      color: var(--color-success);
    }

    &.down {
      background: var(--color-error-bg);
      color: var(--color-error);
    }

    .trend-value {
      font-variant-numeric: tabular-nums;
    }
  }

  @keyframes trendPop {
    0% {
      opacity: 0;
      transform: scale(0);
    }
    50% {
      transform: scale(1.1);
    }
    100% {
      opacity: 1;
      transform: scale(1);
    }
  }

  // 计数完成时的闪光效果
  &.completed .counter-value {
    animation: countComplete 0.5s var(--ease-bounce);
  }
}

@keyframes countComplete {
  0% {
    transform: scale(1);
  }
  30% {
    transform: scale(1.1);
  }
  60% {
    transform: scale(0.95);
  }
  100% {
    transform: scale(1);
  }
}
</style>
