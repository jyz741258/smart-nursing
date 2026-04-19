import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  // 从 localStorage 读取字体设置
  const fontSizeMode = ref<'normal' | 'large'>(
    (localStorage.getItem('fontSizeMode') as 'normal' | 'large') || 'normal'
  )

  // 切换字体大小模式
  const toggleFontSize = () => {
    fontSizeMode.value = fontSizeMode.value === 'normal' ? 'large' : 'normal'
    localStorage.setItem('fontSizeMode', fontSizeMode.value)
  }

  // 设置字体大小模式
  const setFontSize = (mode: 'normal' | 'large') => {
    fontSizeMode.value = mode
    localStorage.setItem('fontSizeMode', mode)
  }

  // 监听变化并更新 HTML class
  watch(fontSizeMode, (newMode) => {
    if (newMode === 'large') {
      document.documentElement.classList.add('large-font-mode')
    } else {
      document.documentElement.classList.remove('large-font-mode')
    }
  }, { immediate: true })

  return { fontSizeMode, toggleFontSize, setFontSize }
})
