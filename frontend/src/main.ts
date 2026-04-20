import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router'
import App from './App.vue'
import './styles/global.css'

// 浅色主题必须在深色主题之前加载
import './styles/theme-light.scss' // 浅色绿色主题样式（必须最先加载）
import './styles/global-dynamic-bg.scss' // 全局动态背景

// 引入动画和动效样式
import './styles/animations.scss'
import './styles/buttons.scss'
import './styles/tables.scss'
import './styles/advanced-effects.scss'

// 深色主题样式（最后加载，可以覆盖）
// 注意：老人界面不应使用深色主题，所以这行可以注释掉
// import './styles/theme.scss'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// 初始化音频管理器（需要用户交互后才能真正初始化）
import { audioManager } from '@/utils/audioManager'

// 全局挂载音频管理器，便于组件访问
app.config.globalProperties.$audio = audioManager
app.provide('audioManager', audioManager)

// 页面加载完成后读取偏好
window.addEventListener('load', () => {
  audioManager.loadPreferences()
})

app.mount('#app')