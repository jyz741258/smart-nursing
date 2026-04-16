<template>
  <div class="theme-switcher">
    <el-tooltip
      :content="isDark ? '切换到浅色模式' : '切换到深色模式'"
      placement="bottom"
      :show-arrow="false"
    >
      <button
        class="theme-toggle-btn"
        :class="{ 'is-dark': isDark }"
        @click="toggleTheme"
        aria-label="切换主题"
      >
        <!-- 太阳图标（浅色） -->
        <svg
          v-if="isDark"
          class="icon-sun"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>

        <!-- 月亮图标（深色） -->
        <svg
          v-else
          class="icon-moon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>

        <!-- 光晕背景 -->
        <div class="glow-bg" :class="{ 'glow-sun': isDark, 'glow-moon': !isDark }"></div>
      </button>
    </el-tooltip>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isDark = ref(true)

// 切换主题
const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme(isDark.value)
  localStorage.setItem('smart-nursing-theme', isDark.value ? 'dark' : 'light')
}

// 应用主题
const applyTheme = (dark) => {
  if (dark) {
    document.documentElement.setAttribute('data-theme', 'dark')
    document.documentElement.classList.remove('light-mode')
  } else {
    document.documentElement.setAttribute('data-theme', 'light')
    document.documentElement.classList.add('light-mode')
  }
}

// 初始化：读取用户偏好
onMounted(() => {
  const savedTheme = localStorage.getItem('smart-nursing-theme')
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

  if (savedTheme) {
    isDark.value = savedTheme === 'dark'
  } else {
    isDark.value = systemPrefersDark // 跟随系统
  }

  applyTheme(isDark.value)

  // 监听系统主题变化
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('smart-nursing-theme')) {
      isDark.value = e.matches
      applyTheme(isDark.value)
    }
  })
})
</script>

<style scoped lang="scss">
.theme-switcher {
  display: inline-flex;
  align-items: center;
}

.theme-toggle-btn {
  position: relative;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full);
  border: 2px solid var(--border-color);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s var(--ease-bounce);
  overflow: visible;

  &:hover {
    transform: scale(1.1) rotate(15deg);
    border-color: var(--color-primary);
    color: var(--color-primary);
    box-shadow: var(--shadow-glow-primary);
  }

  &:active {
    transform: scale(0.95);
  }

  // 图标动画
  .icon-sun,
  .icon-moon {
    width: 20px;
    height: 20px;
    transition: all 0.3s var(--ease-bounce);
    z-index: 1;
  }

  .icon-sun {
    animation: sunSpin 4s linear infinite;
  }

  .icon-moon {
    animation: moonFloat 3s ease-in-out infinite;
  }

  @keyframes sunSpin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  @keyframes moonFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
  }
}

// 光晕背景动画
.glow-bg {
  position: absolute;
  inset: -4px;
  border-radius: var(--radius-full);
  opacity: 0;
  z-index: -1;
  transition: opacity 0.3s ease;

  &.glow-sun {
    background: radial-gradient(circle, rgba(251, 191, 36, 0.4) 0%, transparent 70%);
  }

  &.glow-moon {
    background: radial-gradient(circle, rgba(102, 126, 234, 0.4) 0%, transparent 70%);
  }
}

.theme-toggle-btn:hover .glow-bg {
  opacity: 1;
  animation: glowPulse 2s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.1); opacity: 0.8; }
}
</style>
