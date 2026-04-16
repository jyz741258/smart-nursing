<template>
  <div
    class="card-3d-wrapper"
    :class="{
      'is-tilted': isTilted,
      'is-glitching': glitchEffect,
      'with-glow': glowEffect
    }"
    :style="cardStyle"
    @mousemove="onMouseMove"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <!-- 主内容区 -->
    <div class="card-3d-content" :class="contentClass">
      <slot></slot>
    </div>

    <!-- 渐变光晕层（跟随鼠标） -->
    <div
      class="glare-layer"
      :style="glareStyle"
    ></div>

    <!-- 顶部高光线 -->
    <div class="top-shine"></div>

    <!-- 底部阴影 -->
    <div class="card-shadow"></div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'

interface Props {
  maxTilt?: number // 最大倾斜角度
  scale?: number // 悬停缩放倍数
  glowEffect?: boolean // 是否启用发光效果
  glitchEffect?: boolean // 是否启用故障风
  speed?: number // 倾斜响应速度
  contentClass?: string | object // 内容区类名
}

const props = withDefaults(defineProps<Props>(), {
  maxTilt: 15,
  scale: 1.02,
  glowEffect: true,
  glitchEffect: false,
  speed: 400,
  contentClass: ''
})

const isTilted = ref(false)
const mouseX = ref(0)
const mouseY = ref(0)
const currentX = ref(0)
const currentY = ref(0)
const rafId = ref<number | null>(null)

// 计算卡片旋转角度
const rotateX = computed(() => {
  return (currentY.value / window.innerHeight - 0.5) * -props.maxTilt
})

const rotateY = computed(() => {
  return (currentX.value / window.innerWidth - 0.5) * props.maxTilt
})

// 卡片内联样式
const cardStyle = computed(() => ({
  transform: `
    perspective(1000px)
    rotateX(${rotateX.value}deg)
    rotateY(${rotateY.value}deg)
    scale3d(${isTilted.value ? props.scale : 1}, ${isTilted.value ? props.scale : 1}, 1)
  `,
  transition: isTilted.value ? `transform ${props.speed}ms cubic-bezier(0.25, 0.46, 0.45, 0.94)` : 'transform 0.8s ease-out'
}))

// 光晕样式（跟随鼠标的反方向移动）
const glareStyle = computed(() => {
  const glareX = (mouseX.value / window.innerWidth) * 100
  const glareY = (mouseY.value / window.innerHeight) * 100

  return {
    background: `radial-gradient(circle at ${glareX}% ${glareY}%, 
      rgba(255, 255, 255, 0.15) 0%, 
      rgba(255, 255, 255, 0.05) 30%, 
      transparent 70%)`
  }
})

// 动画循环（平滑插值）
const animate = () => {
  const lerpFactor = 0.1

  currentX.value += (mouseX.value - currentX.value) * lerpFactor
  currentY.value += (mouseY.value - currentY.value) * lerpFactor

  rafId.value = requestAnimationFrame(animate)
}

// 鼠标移动处理
const onMouseMove = (e: MouseEvent) => {
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  mouseX.value = e.clientX - rect.left
  mouseY.value = e.clientY - rect.top
}

// 鼠标进入
const onMouseEnter = () => {
  isTilted.value = true

  // 启动动画循环
  if (!rafId.value) {
    rafId.value = requestAnimationFrame(animate)
  }

  // 播放轻微音效
  // audioManager?.play('click')
}

// 鼠标离开
const onMouseLeave = () => {
  isTilted.value = false
  mouseX.value = 0
  mouseY.value = 0

  // 停止动画循环
  if (rafId.value) {
    cancelAnimationFrame(rafId.value)
    rafId.value = null
  }
}

// 清理
onUnmounted(() => {
  if (rafId.value) {
    cancelAnimationFrame(rafId.value)
  }
})
</script>

<style scoped lang="scss">
.card-3d-wrapper {
  position: relative;
  transform-style: preserve-3d;
  will-change: transform;
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.card-3d-content {
  position: relative;
  z-index: 1;
  transform: translateZ(20px); // 内容悬浮
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  transition: all 0.4s var(--ease-smooth);
  overflow: hidden;

  // 卡片入场动画
  animation: cardEntry 0.6s var(--ease-bounce) both;
}

@keyframes cardEntry {
  0% {
    opacity: 0;
    transform: translateY(40px) scale(0.9);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

// 光晕层
.glare-layer {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
  mix-blend-mode: overlay;
}

.card-3d-wrapper:hover .glare-layer {
  opacity: 1;
}

// 顶部高光
.top-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.6),
    transparent
  );
  z-index: 2;
  transition: left 0.6s ease;
}

.card-3d-wrapper:hover .top-shine {
  left: 100%;
  transition: left 0.8s ease-in-out;
}

// 底部投影（动态）
.card-shadow {
  position: absolute;
  bottom: -20px;
  left: 10%;
  right: 10%;
  height: 20px;
  background: radial-gradient(
    ellipse at center,
    rgba(0, 0, 0, 0.4) 0%,
    transparent 70%
  );
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.4s var(--ease-smooth);
  z-index: 0;
  filter: blur(10px);
}

.card-3d-wrapper:hover .card-shadow {
  opacity: 0.6;
  transform: scale(1.1);
}

// 悬停时边框高亮
.card-3d-wrapper:hover .card-3d-content {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-glow-primary);
}

// 故障效果
.is-glitching .card-3d-content {
  animation: glitch 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) infinite;

  @keyframes glitch {
    0% { transform: translate(0); }
    20% { transform: translate(-2px, 2px); }
    40% { transform: translate(-2px, -2px); }
    60% { transform: translate(2px, 2px); }
    80% { transform: translate(2px, -2px); }
    100% { transform: translate(0); }
  }
}

// 发光边框
.is-tilted.with-glow .card-3d-content::before {
  content: '';
  position: absolute;
  inset: -1px;
  z-index: -1;
  background: linear-gradient(
    45deg,
    var(--color-primary),
    var(--color-secondary),
    var(--color-accent),
    var(--color-primary)
  );
  background-size: 400% 400%;
  border-radius: calc(var(--radius-lg) + 1px);
  animation: gradientShift 3s ease infinite;
  opacity: 0.7;
}

@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

// 确保内容不会随卡片倾斜而变形
.card-3d-content > * {
  transform: translateZ(0); // 触发 GPU 加速
}
</style>
