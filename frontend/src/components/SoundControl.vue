<template>
  <div class="sound-control">
    <el-tooltip
      :content="isEnabled ? '音效已开启' : '音效已关闭'"
      placement="bottom"
      :show-arrow="false"
    >
      <button
        class="sound-toggle-btn"
        :class="{ muted: !isEnabled }"
        @click="toggleSound"
      >
        <!-- 扬声器图标 -->
        <svg v-if="isEnabled" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
          <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
        </svg>

        <!-- 静音图标 -->
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
          <line x1="23" y1="9" x2="17" y2="15" />
          <line x1="17" y1="9" x2="23" y2="15" />
        </svg>

        <!-- 音波动画 -->
        <div v-if="isEnabled" class="sound-waves">
          <span class="wave"></span>
          <span class="wave"></span>
          <span class="wave"></span>
        </div>
      </button>
    </el-tooltip>

    <!-- 音量滑块 -->
    <el-slider
      v-if="showVolume"
      v-model="volume"
      :min="0"
      :max="100"
      :step="1"
      class="volume-slider"
      :show-tooltip="false"
      @change="onVolumeChange"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { audioManager } from '@/utils/audioManager'

const emit = defineEmits(['toggle', 'volume-change'])

const showVolume = ref(false)
const volume = ref(audioManager.getVolume() * 100)

const isEnabled = computed(() => audioManager.isEnabled())

const toggleSound = async () => {
  const newState = !isEnabled.value
  audioManager.setEnabled(newState)
  emit('toggle', newState)

  // 播放测试音效
  if (newState) {
    await audioManager.init()
    audioManager.play('click')
  }
}

const onVolumeChange = (val: number) => {
  const normalizedVolume = val / 100
  audioManager.setVolume(normalizedVolume)
  emit('volume-change', normalizedVolume)
}
</script>

<style scoped lang="scss">
.sound-control {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.sound-toggle-btn {
  position: relative;
  width: 40px;
  height: 40px;
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

  svg {
    width: 18px;
    height: 18px;
    transition: all 0.3s ease;
  }

  &:hover {
    transform: scale(1.1);
    border-color: var(--color-primary);
    color: var(--color-primary);
    box-shadow: var(--shadow-glow-primary);
  }

  &.muted {
    color: var(--text-tertiary);

    &:hover {
      color: var(--color-error);
      border-color: var(--color-error);
      box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
    }
  }
}

// 音波动画
.sound-waves {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 2px;
  align-items: flex-end;
  height: 12px;

  .wave {
    width: 3px;
    background: var(--color-primary);
    border-radius: 2px;
    animation: soundWave 0.8s ease-in-out infinite;
  }

  .wave:nth-child(1) {
    height: 6px;
    animation-delay: 0s;
  }

  .wave:nth-child(2) {
    height: 10px;
    animation-delay: 0.1s;
  }

  .wave:nth-child(3) {
    height: 4px;
    animation-delay: 0.2s;
  }

  @keyframes soundWave {
    0%, 100% {
      transform: scaleY(0.5);
      opacity: 0.6;
    }
    50% {
      transform: scaleY(1);
      opacity: 1;
    }
  }
}

// 音量滑块
.volume-slider {
  width: 80px;
  height: 4px;
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s ease;

  :deep(.el-slider__runway) {
    background: var(--border-color);
    border-radius: 2px;
  }

  :deep(.el-slider__bar) {
    background: var(--color-primary);
    border-radius: 2px;
  }

  :deep(.el-slider__button) {
    width: 12px;
    height: 12px;
    border: 2px solid var(--color-primary);
  }
}

.sound-control:hover .volume-slider {
  opacity: 1;
  pointer-events: auto;
}
</style>
