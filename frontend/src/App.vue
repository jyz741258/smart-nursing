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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSettingsStore } from '@/store/settings'

const router = useRouter()
const settingsStore = useSettingsStore()
const transitionName = ref('fade-transform')

// 初始化字体设置
onMounted(() => {
  settingsStore.initSettings()
})

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

/* ========================
   字体大小和高对比度样式
   ======================== */

// CSS 变量定义
:root {
  --base-font-size: 18px;
  --font-scale-small: 0.78;    /* 14/18 ≈ 0.78 */
  --font-scale-medium: 1;       /* 18/18 = 1 */
  --font-scale-large: 1.22;     /* 22/18 ≈ 1.22 */
  --font-scale-xlarge: 1.56;    /* 28/18 ≈ 1.56 */
}

// 全局字体大小应用
html {
  font-size: var(--base-font-size);
}

// 使用缩放因子调整所有元素
body {
  font-size: var(--base-font-size);
  line-height: 1.6;
  transition: font-size 0.3s ease;
}

// 高对比度模式
body.high-contrast {
  background-color: #000000 !important;
  color: #ffffff !important;

  * {
    border-color: #ffffff !important;
    box-shadow: none !important;
  }

  .el-card,
  .el-dialog,
  .el-dropdown-menu,
  .el-menu,
  .el-table,
  .el-input__inner,
  .el-textarea__inner,
  .el-select .el-input__inner,
  .el-date-editor .el-input__inner {
    background-color: #000000 !important;
    color: #ffffff !important;
    border-color: #ffffff !important;
  }

  .el-table {
    th,
    tr,
    td {
      background-color: #000000 !important;
      color: #ffffff !important;
      border-color: #ffffff !important;
    }

    &:hover > tr:hover > td {
      background-color: #1a1a1a !important;
    }
  }

  .el-button {
    background-color: #ffffff !important;
    color: #000000 !important;
    border-color: #ffffff !important;

    &.is-plain {
      background-color: transparent !important;
      color: #ffffff !important;
    }

    &:hover {
      opacity: 0.85;
    }
  }

  .el-link {
    color: #4ade80 !important;

    &:hover {
      color: #22c55e !important;
    }
  }

  .el-tag {
    background-color: #ffffff !important;
    color: #000000 !important;
    border-color: #ffffff !important;
  }

  .el-badge__content {
    background-color: #f56c6c !important;
    color: #ffffff !important;
  }

  .el-drawer {
    background-color: #000000 !important;
    color: #ffffff !important;
  }
}

// 响应式字体大小 - 移动端更友好
@media (max-width: 768px) {
  html {
    font-size: calc(var(--base-font-size) * 0.95);
  }
}

// 老年友好按钮增强
.el-button {
  min-height: 44px;
  font-weight: 500;
  transition: all 0.2s;
  
  &:active {
    transform: scale(0.98);
  }
}

// 输入框增强
.el-input__inner,
.el-textarea__inner,
.el-select .el-input__inner {
  min-height: 44px;
  font-size: inherit;
}

// 表格字体增强
.el-table {
  th,
  td {
    font-size: inherit;
    padding: 12px 8px;
  }
}

// 卡片字体增强
.el-card {
  font-size: inherit;
}

// 对话框字体增强
.el-dialog {
  font-size: inherit;
  
  .el-dialog__title {
    font-size: 1.2em;
    font-weight: 600;
  }
  
  .el-dialog__body {
    font-size: inherit;
  }
}

// 下拉菜单字体增强
.el-dropdown-menu__item {
  font-size: inherit;
  min-height: 44px;
  display: flex;
  align-items: center;
}

// 分页组件字体增强
.el-pagination {
  button,
  .el-pager li,
  .el-pagination__editor.el-input .el-input__inner,
  .el-pagination__jump {
    font-size: inherit;
    min-width: 36px;
    min-height: 36px;
  }
}

// 表单标签字体增强
.el-form-item__label {
  font-size: inherit;
  font-weight: 500;
  padding-bottom: 8px;
}

// 消息提示字体增强
.el-message {
  font-size: 1em;
  min-height: 44px;
  padding: 12px 20px;
}

// 通知徽章增强
.el-badge__content {
  min-width: 18px;
  height: 18px;
  line-height: 18px;
  font-size: 0.75em;
  font-weight: bold;
}

// 侧边栏菜单增强
.el-menu-item,
.el-sub-menu__title {
  min-height: 56px;
  font-size: inherit;
}

// 移动端菜单增强
.el-drawer .el-menu-item,
.el-drawer .el-sub-menu__title {
  min-height: 56px;
  font-size: 1.1em;
}

// 标签页增强
.el-tabs__item {
  font-size: inherit;
  font-weight: 500;
  height: 48px;
  line-height: 48px;
}

// 步骤条增强
.el-steps {
  .el-step__title {
    font-size: inherit;
    font-weight: 500;
  }
  
  .el-step__description {
    font-size: 0.9em;
  }
}

// 级联选择器增强
.el-cascader-menu,
.el-cascader-node {
  font-size: inherit;
  min-height: 40px;
}

// 日期选择器增强
.el-date-editor .el-range__icon,
.el-date-editor .el-range__close-icon {
  font-size: 1.1em;
}

.el-date-editor .el-range-separator {
  font-size: inherit;
  font-weight: 500;
}

// 颜色选择器增强
.el-color-dropdown__link {
  font-size: inherit;
}

// 上传组件增强
.el-upload-list__item {
  font-size: inherit;
}

// 树形控件增强
.el-tree-node__content {
  min-height: 44px;
  font-size: inherit;
}

// 评分组件增强
.el-rate {
  font-size: 1.2em;
  
  .el-rate__icon {
    font-size: 1.2em;
  }
}

// 开关组件增强
.el-switch {
  .el-switch__label {
    font-size: inherit;
  }
}

// 单选框和复选框增强
.el-radio,
.el-checkbox {
  .el-radio__label,
  .el-checkbox__label {
    font-size: inherit;
    font-weight: 500;
  }
}

// 数值输入框增强
.el-input-number {
  .el-input-number__decrease,
  .el-input-number__increase {
    min-height: 44px;
    font-size: 1.2em;
  }
  
  .el-input__inner {
    text-align: center;
    font-size: 1.1em;
    font-weight: 600;
  }
}

// 级联选择器增强
.el-cascader .el-input__inner {
  min-height: 44px;
  font-size: inherit;
}

// 下拉选择器增强
.el-select .el-input.is-focus .el-input__inner,
.el-select:hover .el-input__inner,
.el-select .el-input__inner:focus {
  border-color: #22c55e;
  font-size: inherit;
}

.el-select-dropdown__item {
  font-size: inherit;
  padding: 12px 20px;
  min-height: 44px;
}

// 表格内输入控件
.el-table .cell .el-input__inner,
.el-table .cell .el-textarea__inner {
  font-size: inherit;
  min-height: 36px;
}

// 进度条增强
.el-progress__text {
  font-size: inherit;
  font-weight: 600;
}

// 头像增强
.el-avatar {
  font-size: 1.1em;
  font-weight: 600;
}

// 徽章增强
.el-badge {
  font-size: inherit;
}

// 时间轴增强
.el-timeline-item__content {
  font-size: inherit;
}

.el-timeline-item__timestamp {
  font-size: 0.9em;
  color: #909399;
}

// 空状态增强
.el-empty__description {
  font-size: 1em;
  color: #909399;
}

// 工具提示增强
.el-tooltip__trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

// 弹出框增强
.el-popover {
  font-size: inherit;
}

// 加载中增强
.el-loading-mask {
  .el-loading-spinner {
    .el-loading-text {
      font-size: 1em;
      margin-top: 10px;
    }
    
    .circular {
      width: 40px;
      height: 40px;
      
      .path {
        stroke-width: 3;
      }
    }
  }
}

// 消息框增强
.el-message-box {
  font-size: inherit;
  
  .el-message-box__title {
    font-size: 1.1em;
    font-weight: 600;
  }
  
  .el-message-box__content {
    font-size: inherit;
  }
}

// 滚动条美化 - 支持高对比度
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 5px;
}

::-webkit-scrollbar-thumb {
  background: #c1c9d2;
  border-radius: 5px;
  
  &:hover {
    background: #a8b2c1;
  }
}

// 高对比度模式下的滚动条
body.high-contrast {
  ::-webkit-scrollbar-track {
    background: #1a1a1a;
  }
  
  ::-webkit-scrollbar-thumb {
    background: #ffffff;
    
    &:hover {
      background: #cccccc;
    }
  }
}

// 焦点样式增强 - 键盘导航友好
*:focus-visible {
  outline: 2px solid #22c55e !important;
  outline-offset: 2px;
}

// 减少动画 - 为老年人提供减少动画选项
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

// 打印样式优化
@media print {
  body {
    font-size: 12pt;
    line-height: 1.5;
    color: #000;
    background: #fff;
  }
  
  .no-print {
    display: none !important;
  }
}
</style>