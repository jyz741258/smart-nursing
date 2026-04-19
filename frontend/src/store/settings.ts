import { defineStore } from 'pinia'
import { ref, watch, computed } from 'vue'

// 字体大小选项
export const FONT_SIZES = {
  SMALL: 'small',   // 正常字体
  MEDIUM: 'medium', // 中等字体
  LARGE: 'large',   // 大字体
  XLARGE: 'xlarge'  // 特大字体
} as const

// 字体大小对应的缩放比例（基于 18px = 1 的比例）
export const FONT_SCALE = {
  small: 14 / 18,     // ≈ 0.78
  medium: 1,          // 1
  large: 22 / 18,     // ≈ 1.22
  xlarge: 28 / 18     // ≈ 1.56
} as const

export const useSettingsStore = defineStore('settings', () => {
  // 字体大小设置，默认 medium（中等，适合老人）
  const fontSize = ref<string>(localStorage.getItem('fontSize') || FONT_SIZES.MEDIUM)
  const highContrast = ref<boolean>(localStorage.getItem('highContrast') === 'true')

  // 计算缩放比例
  const scale = computed(() => FONT_SCALE[fontSize.value as keyof typeof FONT_SCALE] || 1)

  // 切换字体大小
  const setFontSize = (size: string) => {
    fontSize.value = size
    localStorage.setItem('fontSize', size)
  }

  // 应用字体大小到文档根元素（通过缩放整个页面）
  const applyScale = () => {
    // 使用 transform: scale() 整体缩放页面
    document.body.style.transform = `scale(${scale.value})`
    document.body.style.transformOrigin = 'top left'
    // 调整 body 宽度以适应缩放
    const width = 100 / scale.value
    document.body.style.width = `${width}%`
  }

  // 切换高对比度模式
  const toggleHighContrast = () => {
    highContrast.value = !highContrast.value
    localStorage.setItem('highContrast', String(highContrast.value))
    applyHighContrast()
  }

  // 应用高对比度样式
  const applyHighContrast = () => {
    if (highContrast.value) {
      document.body.classList.add('high-contrast')
    } else {
      document.body.classList.remove('high-contrast')
    }
  }

  // 初始化设置
  const initSettings = () => {
    applyScale()
    applyHighContrast()
  }

  // 监听设置变化，自动应用
  watch(fontSize, () => {
    applyScale()
  })

  watch(highContrast, () => {
    applyHighContrast()
  })

  return {
    fontSize,
    highContrast,
    scale,
    setFontSize,
    toggleHighContrast,
    initSettings,
    FONT_SIZES,
    FONT_SCALE
  }
})
