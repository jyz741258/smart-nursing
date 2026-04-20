<template>
  <div class="elderly-map">
    <!-- 地图容器 -->
    <div class="map-wrapper">
      <div ref="mapContainer" class="map-container"></div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-overlay">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <span>地图加载中...</span>
      </div>
      
      <!-- 地图工具栏 -->
      <div class="map-toolbar">
        <el-radio-group v-model="mapMode" size="default" @change="handleModeChange">
          <el-radio-button value="nursingHome">
            <el-icon><OfficeBuilding /></el-icon>
            养老院位置
          </el-radio-button>
          <el-radio-button value="track">
            <el-icon><Guide /></el-icon>
            活动轨迹
          </el-radio-button>
          <el-radio-button value="fence">
            <el-icon><LocationInformation /></el-icon>
            电子围栏
          </el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 侧边信息面板 -->
    <div class="info-panel">
      <!-- 养老院信息 -->
      <div v-if="mapMode === 'nursingHome'" class="panel-section">
        <div class="section-header">
          <el-icon><OfficeBuilding /></el-icon>
          <h3>养老院信息</h3>
        </div>
        <el-card shadow="hover" class="nursing-home-card">
          <div class="nursing-info">
            <div class="info-row">
              <span class="label">名称：</span>
              <span class="value">阳光养老护理中心</span>
            </div>
            <div class="info-row">
              <span class="label">地址：</span>
              <span class="value">北京市朝阳区建国路88号</span>
            </div>
            <div class="info-row">
              <span class="label">电话：</span>
              <span class="value">010-88888888</span>
            </div>
            <div class="info-row">
              <span class="label">床位数：</span>
              <span class="value">200张</span>
            </div>
            <div class="info-row">
              <span class="label">当前入住：</span>
              <span class="value">156人</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 老人选择 (轨迹和围栏模式) -->
      <div v-if="mapMode === 'track' || mapMode === 'fence'" class="panel-section">
        <div class="section-header">
          <el-icon><User /></el-icon>
          <h3>选择老人</h3>
        </div>
        <el-select
          v-model="selectedElderId"
          placeholder="请选择老人"
          filterable
          class="elder-select"
          @change="handleElderChange"
        >
          <el-option
            v-for="elder in elders"
            :key="elder.id"
            :label="elder.name"
            :value="elder.id"
          >
            <div class="elder-option">
              <el-avatar :size="24" :src="elder.avatar">{{ elder.name.charAt(0) }}</el-avatar>
              <span>{{ elder.name }}</span>
              <el-tag size="small" :type="elder.status === 'normal' ? 'success' : 'warning'">
                {{ elder.status === 'normal' ? '正常' : '异常' }}
              </el-tag>
            </div>
          </el-option>
        </el-select>
      </div>

      <!-- 轨迹信息 -->
      <div v-if="mapMode === 'track' && selectedElderId" class="panel-section">
        <div class="section-header">
          <el-icon><Guide /></el-icon>
          <h3>活动轨迹</h3>
        </div>
        <el-card shadow="hover">
          <div class="track-info">
            <div class="info-row">
              <span class="label">当前位置：</span>
              <span class="value">{{ currentLocation || '未知' }}</span>
            </div>
            <div class="info-row">
              <span class="label">最后更新：</span>
              <span class="value">{{ lastUpdate || '未知' }}</span>
            </div>
            <div class="info-row">
              <span class="label">今日行走：</span>
              <span class="value">{{ todayDistance || '0' }} 米</span>
            </div>
            <div class="info-row">
              <span class="label">活动状态：</span>
              <el-tag :type="activityStatus === '活跃' ? 'success' : 'info'">
                {{ activityStatus }}
              </el-tag>
            </div>
          </div>
          <el-divider />
          <div class="time-filter">
            <span class="filter-label">时间范围：</span>
            <el-radio-group v-model="timeRange" size="small">
              <el-radio-button value="today">今日</el-radio-button>
              <el-radio-button value="week">本周</el-radio-button>
              <el-radio-button value="month">本月</el-radio-button>
            </el-radio-group>
          </div>
        </el-card>
      </div>

      <!-- 电子围栏设置 -->
      <div v-if="mapMode === 'fence' && selectedElderId" class="panel-section">
        <div class="section-header">
          <el-icon><LocationInformation /></el-icon>
          <h3>电子围栏设置</h3>
        </div>
        <el-card shadow="hover">
          <el-form label-width="80px" size="small">
            <el-form-item label="围栏名称">
              <el-input v-model="fenceName" placeholder="请输入围栏名称" />
            </el-form-item>
            <el-form-item label="半径范围">
              <el-slider v-model="fenceRadius" :min="50" :max="500" :step="10" show-input />
              <span class="radius-label">{{ fenceRadius }} 米</span>
            </el-form-item>
            <el-form-item label="告警类型">
              <el-checkbox-group v-model="alertTypes">
                <el-checkbox label="越界告警">越界告警</el-checkbox>
                <el-checkbox label="滞留告警">滞留告警</el-checkbox>
                <el-checkbox label="静止告警">静止告警</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveFence">保存围栏</el-button>
              <el-button @click="clearFence">清除围栏</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 紧急操作 -->
      <div v-if="selectedElderId" class="panel-section emergency-section">
        <div class="section-header danger">
          <el-icon><Warning /></el-icon>
          <h3>紧急操作</h3>
        </div>
        <div class="emergency-actions">
          <el-button type="danger" @click="handleEmergency">
            <el-icon><Bell /></el-icon>
            紧急求助
          </el-button>
          <el-button type="warning" @click="handleLocate">
            <el-icon><Search /></el-icon>
            定位老人
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, OfficeBuilding, Guide, LocationInformation, User, Warning, Bell, Search } from '@element-plus/icons-vue'

// 地图相关 refs
const mapContainer = ref<HTMLElement | null>(null)
const loading = ref(true)
const mapMode = ref<'nursingHome' | 'track' | 'fence'>('nursingHome')
const selectedElderId = ref<number | null>(null)

// 老人数据
const elders = ref([
  { id: 1, name: '王建国', avatar: '', status: 'normal', location: '休息室', lastUpdate: '10:30' },
  { id: 2, name: '李秀英', avatar: '', status: 'normal', location: '花园', lastUpdate: '10:25' },
  { id: 3, name: '张德明', avatar: '', status: 'warning', location: '未知', lastUpdate: '09:15' },
  { id: 4, name: '陈桂兰', avatar: '', status: 'normal', location: '餐厅', lastUpdate: '10:45' },
  { id: 5, name: '刘永华', avatar: '', status: 'normal', location: '活动室', lastUpdate: '10:20' },
])

// 地图实例
let mapInstance: any = null
let markers: any[] = []
let polyline: any = null
let circle: any = null

// 模拟当前位置
const currentLocation = ref('')
const lastUpdate = ref('')
const todayDistance = ref(0)
const activityStatus = ref('活跃')

// 围栏设置
const fenceName = ref('')
const fenceRadius = ref(100)
const alertTypes = ref(['越界告警'])

// 养老院位置 (北京)
const nursingHomeCenter = { lng: 116.427428, lat: 39.92923 }

// 初始化地图 (使用简单的SVG模拟)
const initMap = () => {
  loading.value = true
  // 模拟地图加载
  setTimeout(() => {
    loading.value = false
    renderMap()
  }, 500)
}

// 渲染模拟地图
const renderMap = () => {
  if (!mapContainer.value) return
  
  // 清空容器
  mapContainer.value.innerHTML = ''
  
  // 创建模拟地图背景
  const mapBg = document.createElement('div')
  mapBg.className = 'simulated-map'
  mapBg.style.cssText = `
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 50%, #a5d6a7 100%);
    position: relative;
    overflow: hidden;
  `
  
  // 添加网格线
  const grid = document.createElement('div')
  grid.className = 'map-grid'
  grid.style.cssText = `
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
      linear-gradient(rgba(0,0,0,0.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,0,0,0.05) 1px, transparent 1px);
    background-size: 40px 40px;
  `
  mapBg.appendChild(grid)
  
  // 添加建筑物标记
  const buildings = [
    { name: '主楼', x: 30, y: 25, w: 15, h: 20, color: '#7986cb' },
    { name: '花园', x: 55, y: 20, w: 20, h: 25, color: '#81c784' },
    { name: '餐厅', x: 15, y: 55, w: 12, h: 15, color: '#ffb74d' },
    { name: '活动室', x: 35, y: 60, w: 15, h: 12, color: '#4fc3f7' },
    { name: '休息室', x: 60, y: 55, w: 18, h: 18, color: '#ba68c8' },
  ]
  
  buildings.forEach(b => {
    const building = document.createElement('div')
    building.className = 'map-building'
    building.style.cssText = `
      position: absolute;
      left: ${b.x}%;
      top: ${b.y}%;
      width: ${b.w}%;
      height: ${b.h}%;
      background: ${b.color};
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 11px;
      font-weight: bold;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      cursor: pointer;
      transition: transform 0.2s;
    `
    building.textContent = b.name
    building.onmouseenter = () => building.style.transform = 'scale(1.05)'
    building.onmouseleave = () => building.style.transform = 'scale(1)'
    mapBg.appendChild(building)
  })
  
  // 添加道路
  const roads = [
    { x1: 25, y1: 0, x2: 25, y2: 100 },
    { x1: 50, y1: 0, x2: 50, y2: 100 },
    { x1: 75, y1: 0, x2: 75, y2: 100 },
    { x1: 0, y1: 50, x2: 100, y2: 50 },
  ]
  
  roads.forEach(r => {
    const road = document.createElement('div')
    road.style.cssText = `
      position: absolute;
      left: ${r.x1}%;
      top: ${r.y1}%;
      width: 3px;
      height: ${r.y2 - r.y1}%;
      background: rgba(255,255,255,0.8);
      transform: translateX(-50%);
    `
    mapBg.appendChild(road)
  })
  
  // 添加养老院中心标记
  const centerMarker = createMarker(nursingHomeCenter.lng, nursingHomeCenter.lat, '阳光养老护理中心', 'nursing-home')
  mapBg.appendChild(centerMarker)
  
  // 如果是轨迹模式，显示老人位置
  if (mapMode.value === 'track' && selectedElderId.value) {
    renderElderMarkers(mapBg)
    renderTrack(mapBg)
  }
  
  // 如果是围栏模式，显示围栏
  if (mapMode.value === 'fence' && selectedElderId.value) {
    renderFence(mapBg)
  }
  
  mapContainer.value.appendChild(mapBg)
}

// 创建标记
const createMarker = (lng: number, lat: number, title: string, type: string) => {
  const marker = document.createElement('div')
  marker.className = `map-marker marker-${type}`
  
  const colors: Record<string, string> = {
    'nursing-home': '#1976d2',
    'elder-normal': '#4caf50',
    'elder-warning': '#ff9800',
    'elder-emergency': '#f44336'
  }
  
  const icons: Record<string, string> = {
    'nursing-home': '🏢',
    'elder-normal': '👴',
    'elder-warning': '⚠️',
    'elder-emergency': '🚨'
  }
  
  marker.style.cssText = `
    position: absolute;
    left: ${((lng - 116.4) / 0.1) * 100}%;
    top: ${((39.94 - lat) / 0.1) * 100}%;
    transform: translate(-50%, -100%);
    background: ${colors[type]};
    color: white;
    padding: 6px 10px;
    border-radius: 20px;
    font-size: 12px;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    cursor: pointer;
    z-index: 10;
  `
  marker.innerHTML = `<span style="margin-right:4px">${icons[type]}</span>${title}`
  
  return marker
}

// 渲染老人标记
const renderElderMarkers = (container: HTMLElement) => {
  elders.value.forEach(elder => {
    const lng = 116.42 + Math.random() * 0.05
    const lat = 39.91 + Math.random() * 0.05
    const type = elder.status === 'normal' ? 'elder-normal' : 'elder-warning'
    const marker = createMarker(lng, lat, elder.name, type)
    container.appendChild(marker)
  })
}

// 渲染轨迹线
const renderTrack = (container: HTMLElement) => {
  const trackPoints = []
  for (let i = 0; i < 8; i++) {
    trackPoints.push({
      lng: 116.42 + i * 0.005,
      lat: 39.92 + Math.sin(i * 0.5) * 0.01
    })
  }
  
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;'
  
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
  const d = trackPoints.map((p, i) => {
    const x = ((p.lng - 116.4) / 0.1) * 100
    const y = ((39.94 - p.lat) / 0.1) * 100
    return `${i === 0 ? 'M' : 'L'} ${x}% ${y}%`
  }).join(' ')
  
  path.setAttribute('d', d)
  path.setAttribute('stroke', '#2196f3')
  path.setAttribute('stroke-width', '3')
  path.setAttribute('fill', 'none')
  path.setAttribute('stroke-dasharray', '8,4')
  path.setAttribute('stroke-linecap', 'round')
  
  svg.appendChild(path)
  container.appendChild(svg)
}

// 渲染电子围栏
const renderFence = (container: HTMLElement) => {
  const center = { lng: 116.43, lat: 39.925 }
  const radius = fenceRadius.value * 0.0001
  
  const fence = document.createElement('div')
  fence.style.cssText = `
    position: absolute;
    left: ${((center.lng - 116.4) / 0.1) * 100}%;
    top: ${((39.94 - center.lat) / 0.1) * 100}%;
    width: ${radius * 2 * 100}%;
    height: ${radius * 2 * 100}%;
    border: 3px dashed #ff5722;
    border-radius: 50%;
    background: rgba(255, 87, 34, 0.1);
    transform: translate(-50%, -50%);
    pointer-events: none;
  `
  container.appendChild(fence)
}

// 处理模式切换
const handleModeChange = () => {
  selectedElderId.value = null
  renderMap()
}

// 处理老人选择
const handleElderChange = (id: number) => {
  const elder = elders.value.find(e => e.id === id)
  if (elder) {
    currentLocation.value = elder.location
    lastUpdate.value = elder.lastUpdate
    todayDistance.value = Math.floor(Math.random() * 2000) + 500
    activityStatus.value = Math.random() > 0.3 ? '活跃' : '静止'
  }
  renderMap()
}

// 保存围栏
const saveFence = () => {
  if (!fenceName.value) {
    ElMessage.warning('请输入围栏名称')
    return
  }
  ElMessage.success('围栏保存成功')
  renderMap()
}

// 清除围栏
const clearFence = () => {
  fenceName.value = ''
  fenceRadius.value = 100
  alertTypes.value = ['越界告警']
  ElMessage.info('围栏已清除')
  renderMap()
}

// 紧急求助
const handleEmergency = () => {
  ElMessageBox.confirm('确定要发送紧急求助信号吗？', '紧急求助', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('紧急求助信号已发送')
  }).catch(() => {})
}

// 定位老人
const handleLocate = () => {
  ElMessage.success('正在定位老人...')
  renderMap()
}

onMounted(() => {
  initMap()
})

// 监听窗口大小变化
const handleResize = () => {
  renderMap()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
.elderly-map {
  display: flex;
  gap: 20px;
  height: calc(100vh - 140px);
  padding: 20px;
  background: #f5f7fa;
}

.map-wrapper {
  flex: 1;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

  .map-container {
    width: 100%;
    height: 100%;
    min-height: 500px;
  }

  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    color: #666;
  }

  .map-toolbar {
    position: absolute;
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    background: #fff;
    padding: 8px 16px;
    border-radius: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);

    :deep(.el-radio-group) {
      display: flex;
      gap: 8px;

      .el-radio-button__inner {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        border-radius: 20px;
      }
    }
  }
}

.info-panel {
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;

  .panel-section {
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    .section-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid #eee;

      h3 {
        margin: 0;
        font-size: 16px;
        color: #333;
      }

      &.danger h3 {
        color: #f56c6c;
      }
    }

    .elder-select {
      width: 100%;
      margin-bottom: 16px;

      .elder-option {
        display: flex;
        align-items: center;
        gap: 10px;
      }
    }

    .nursing-info,
    .track-info {
      .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
          border-bottom: none;
        }

        .label {
          color: #666;
          font-size: 14px;
        }

        .value {
          color: #333;
          font-weight: 500;
        }
      }
    }

    .time-filter {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 12px;

      .filter-label {
        color: #666;
        font-size: 14px;
      }
    }
  }

  .emergency-section {
    border: 1px solid #fef0f0;
    background: #fff5f5;

    .emergency-actions {
      display: flex;
      gap: 12px;

      .el-button {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
      }
    }
  }
}

:deep(.el-card) {
  border: none;
  border-radius: 8px;

  .el-card__body {
    padding: 16px;
  }
}

.radius-label {
  margin-left: 12px;
  color: #409eff;
  font-weight: 500;
}

// 响应式
@media (max-width: 1024px) {
  .elderly-map {
    flex-direction: column;
    height: auto;

    .map-wrapper {
      height: 400px;
    }

    .info-panel {
      width: 100%;
    }
  }
}
</style>
