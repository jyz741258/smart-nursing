<template>
  <router-view v-slot="{ Component }">
    <transition
      name="fade"
      mode="out-in"
      @enter="onEnter"
      @leave="onLeave"
    >
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 页面进入动画
const onEnter = (el: Element, done: () => void) => {
  const element = el as HTMLElement
  element.style.opacity = '0'
  element.style.transform = 'translateY(20px)'

  setTimeout(() => {
    element.style.transition = 'all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)'
    element.style.opacity = '1'
    element.style.transform = 'translateY(0)'
    setTimeout(done, 400)
  }, 50)
}

// 页面离开动画
const onLeave = (el: Element, done: () => void) => {
  const element = el as HTMLElement
  element.style.transition = 'all 0.3s ease-in'
  element.style.opacity = '0'
  element.style.transform = 'translateY(-20px)'
  setTimeout(done, 300)
}

onMounted(() => {
  console.log('App mounted - 动画系统已就绪')
})
</script>

<style>
/* 全局引入动画样式 */
@import './styles/animations.scss';

// 页面过渡基础样式
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>