<template>
  <router-view v-slot="{ Component, route }">
    <transition
      :name="transitionName"
      mode="out-in"
      @enter="onEnter"
      @after-enter="onAfterEnter"
      @leave="onLeave"
      @after-leave="onAfterLeave"
    >
      <component
        :is="Component"
        :key="route.path"
        class="page-transition-wrapper"
      />
    </transition>
  </router-view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const transitionName = ref('fade-transform')

// 页面进入动画 - 电影级效果
const onEnter = (el: Element, done: () => void) => {
  const element = el as HTMLElement
  element.style.opacity = '0'
  element.style.transform = 'translateY(40px) scale(0.98)'

  // 强制重绘
  element.offsetHeight

  // 使用 GPU 加速的动画
  element.style.transition = 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)'
  element.style.opacity = '1'
  element.style.transform = 'translateY(0) scale(1)'

  setTimeout(done, 600)
}

const onAfterEnter = (el: Element) => {
  const element = el as HTMLElement
  element.style.transition = ''
  element.style.opacity = ''
  element.style.transform = ''
}

// 页面离开动画
const onLeave = (el: Element, done: () => void) => {
  const element = el as HTMLElement
  element.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)'
  element.style.opacity = '0'
  element.style.transform = 'translateY(-30px) scale(1.02)'

  setTimeout(done, 500)
}

const onAfterLeave = (el: Element) => {
  const element = el as HTMLElement
  element.style.transition = ''
  element.style.opacity = ''
  element.style.transform = ''
}

// 监听路由，动态设置过渡效果类型
router.beforeEach((to, from) => {
  // 根据路由深度决定过渡方向
  const toDepth = to.path.split('/').length
  const fromDepth = from.path.split('/').length

  if (toDepth > fromDepth) {
    transitionName.value = 'slide-up-fade'
  } else if (toDepth < fromDepth) {
    transitionName.value = 'slide-down-fade'
  } else {
    transitionName.value = 'fade-transform'
  }
})
</script>

<style>
/* ========================
   电影级页面转场动画
   ======================== */

.page-transition-wrapper {
  will-change: opacity, transform;
  backface-visibility: hidden;
  perspective: 1000px;
}

/* 1. 默认淡入淡出 + 缩放位移 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateY(40px) scale(0.98);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateY(-30px) scale(1.02);
}

/* 2. 向上滑动（进入更深层级） */
.slide-up-fade-enter-active,
.slide-up-fade-leave-active {
  transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.slide-up-fade-enter-from {
  opacity: 0;
  transform: translateY(80px) scale(0.95);
}

.slide-up-fade-leave-to {
  opacity: 0;
  transform: translateY(-40px) scale(1.05);
}

/* 3. 向下滑动（返回上级） */
.slide-down-fade-enter-active,
.slide-down-fade-leave-active {
  transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.slide-down-fade-enter-from {
  opacity: 0;
  transform: translateY(-40px) scale(1.05);
}

.slide-down-fade-leave-to {
  opacity: 0;
  transform: translateY(80px) scale(0.95);
}

/* 4. 左右滑动（横向导航） */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(60px) scale(0.98);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-60px) scale(1.02);
}

/* 5. 缩放 + 弹性效果（模态页面） */
.scale-bounce-enter-active {
  animation: scaleBounceIn 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

.scale-bounce-leave-active {
  animation: scaleBounceOut 0.5s cubic-bezier(0.4, 0, 0.2, 1) both;
}

@keyframes scaleBounceIn {
  0% {
    opacity: 0;
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes scaleBounceOut {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.95);
  }
}

/* 6. 模糊聚焦效果（类似 iOS 转场） */
.blur-fade-enter-active,
.blur-fade-leave-active {
  transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.blur-fade-enter-from {
  opacity: 0;
  filter: blur(10px);
  transform: scale(1.1);
}

.blur-fade-leave-to {
  opacity: 0;
  filter: blur(10px);
  transform: scale(0.9);
}

/* 7. 粒子爆炸效果（重要操作） */
.particle-explode-enter-active {
  animation: particleEnter 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
}

@keyframes particleEnter {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(100px);
    filter: blur(8px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
    filter: blur(0);
  }
}
</style>