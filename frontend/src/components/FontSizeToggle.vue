<template>
  <div class="font-size-toggle" :class="[currentSize, { 'show-menu': showMenu }]">
    <div class="toggle-header" @click="showMenu = !showMenu">
      <el-icon :size="24"><ZoomIn /></el-icon>
      <span class="label">字体大小</span>
      <span class="current-size">{{ sizeLabel }}</span>
      <el-icon class="arrow" :class="{ rotated: showMenu }">
        <ArrowDown />
      </el-icon>
    </div>
    
    <div class="toggle-menu" v-if="showMenu">
      <div class="menu-option" :class="{ active: currentSize === 'small' }" @click="changeSize('small')">
        <span class="option-label">正常</span>
        <span class="option-preview small-preview">示例文字</span>
      </div>
      <div class="menu-option" :class="{ active: currentSize === 'medium' }" @click="changeSize('medium')">
        <span class="option-label">中等</span>
        <span class="option-preview medium-preview">示例文字</span>
      </div>
      <div class="menu-option" :class="{ active: currentSize === 'large' }" @click="changeSize('large')">
        <span class="option-label">大字</span>
        <span class="option-preview large-preview">示例文字</span>
      </div>
      <div class="menu-option" :class="{ active: currentSize === 'xlarge' }" @click="changeSize('xlarge')">
        <span class="option-label">特大</span>
        <span class="option-preview xlarge-preview">示例文字</span>
      </div>
      <div class="menu-divider"></div>
      <div class="menu-option reset" @click="resetSize">
        <el-icon><RefreshLeft /></el-icon>
        <span>恢复默认</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSettingsStore } from '@/store/settings'
import { ZoomIn, ArrowDown, RefreshLeft } from '@element-plus/icons-vue'

const settingsStore = useSettingsStore()
const showMenu = ref(false)

const currentSize = computed(() => settingsStore.fontSize)

const sizeLabel = computed(() => {
  const labels: Record<string, string> = {
    small: '正常',
    medium: '中等',
    large: '大字',
    xlarge: '特大'
  }
  return labels[settingsStore.fontSize] || '中等'
})

const changeSize = (size: string) => {
  settingsStore.setFontSize(size)
  showMenu.value = false
}

const resetSize = () => {
  settingsStore.setFontSize('medium')
  showMenu.value = false
}
</script>

<style scoped lang="scss">
.font-size-toggle {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  box-shadow: 0 4px 20px rgba(34, 197, 94, 0.4);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 25px rgba(34, 197, 94, 0.5);
  }
  
  &.show-menu {
    width: auto;
    height: auto;
    border-radius: 16px;
    background: #ffffff;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    overflow: visible;
    
    &:hover {
      transform: none;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
    }
    
    .toggle-header {
      border-bottom: 1px solid #e2e8f0;
      border-radius: 16px 16px 0 0;
      padding-bottom: 12px;
      margin-bottom: 0;
    }
    
    .toggle-menu {
      display: block;
      border-radius: 0 0 16px 16px;
      overflow: hidden;
    }
  }
  
  .toggle-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    padding: 8px;
    gap: 4px;
    
    .label {
      font-size: 12px;
      font-weight: 600;
      opacity: 0.9;
    }
    
    .current-size {
      font-size: 11px;
      opacity: 0.8;
    }
    
    .arrow {
      font-size: 14px;
      transition: transform 0.3s;
      margin-top: 2px;
      
      &.rotated {
        transform: rotate(180deg);
      }
    }
  }
  
  .toggle-menu {
    display: none;
    padding: 8px 0;
    background: #ffffff;
    
    .menu-option {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 12px 20px;
      cursor: pointer;
      transition: all 0.2s;
      gap: 6px;
      
      &:hover {
        background: #f0fdf4;
      }
      
      &.active {
        background: #dcfce7;
        
        .option-label {
          color: #22c55e;
          font-weight: 700;
        }
      }
      
      &.reset {
        flex-direction: row;
        gap: 8px;
        color: #64748b;
        font-size: 0.9em;
        
        &:hover {
          color: #22c55e;
          background: #f0fdf4;
        }
      }
      
      .option-label {
        font-size: 0.85em;
        font-weight: 600;
        color: #1e293b;
      }
      
      .option-preview {
        font-weight: 600;
        color: #475569;
        
        &.small-preview {
          font-size: 14px;
        }
        
        &.medium-preview {
          font-size: 16px;
        }
        
        &.large-preview {
          font-size: 20px;
        }
        
        &.xlarge-preview {
          font-size: 26px;
        }
      }
    }
    
    .menu-divider {
      height: 1px;
      background: #e2e8f0;
      margin: 8px 0;
    }
  }
}

// 大字体模式下的特殊调整
body.high-contrast & {
  background: #000;
  color: #fff;
  
  &.show-menu {
    background: #000;
    
    .toggle-header {
      color: #fff;
      border-bottom-color: #fff;
    }
    
    .menu-option {
      color: #fff;
      
      &:hover {
        background: #1a1a1a;
      }
      
      &.active {
        background: #1a3d1a;
        
        .option-label {
          color: #4ade80;
        }
      }
      
      .option-label {
        color: #fff;
      }
      
      .option-preview {
        color: #ccc;
      }
      
      &.reset {
        color: #fff;
        
        &:hover {
          background: #1a1a1a;
          color: #4ade80;
        }
      }
    }
    
    .menu-divider {
      background: #fff;
    }
  }
}
</style>
