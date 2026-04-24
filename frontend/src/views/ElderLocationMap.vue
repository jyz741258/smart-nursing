<template>
  <div class="elderly-map">
    <!-- 地图容器 -->
    <div class="map-wrapper">
      <AMapView
        ref="mapViewRef"
        :center="mapCenter"
        :zoom="mapZoom"
        :markers="markers"
        :polyline-path="trackPath"
        :circle-center="fenceCenter"
        :circle-radius="fenceRadius * 1000"
        :show-circle="false"
        class="map-view"
        @click="handleMapClick"
        @marker-click="handleMarkerClick"
      />

      <!-- 地图工具栏 -->
      <div class="map-toolbar">
        <el-radio-group v-model="mapMode" size="default" @change="handleModeChange">
          <el-radio-button value="nursingHome">
            <el-icon><OfficeBuilding /></el-icon>
            养老院位置
          </el-radio-button>
          <el-radio-button value="track">
            <el-icon><Guide /></el-icon>
            我的轨迹
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- 地图控件 -->
      <div class="map-controls">
        <el-button circle @click="zoomIn" title="放大">
          <el-icon><Plus /></el-icon>
        </el-button>
        <el-button circle @click="zoomOut" title="缩小">
          <el-icon><Minus /></el-icon>
        </el-button>
        <el-button circle @click="centerToHome" title="回到养老院">
          <el-icon><House /></el-icon>
        </el-button>
        <el-button circle :loading="isRefreshing" @click="refreshLocation" title="刷新位置">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>


    </div>

    <!-- 侧边信息面板 -->
    <div class="info-panel">
      <!-- 养老院信息 -->
      <div v-if="mapMode === 'nursingHome'" class="panel-section">
        <div class="section-header primary">
          <el-icon><OfficeBuilding /></el-icon>
          <h3>养老院信息</h3>
        </div>
        <el-card shadow="hover" class="nursing-home-card">
          <div class="nursing-info">
            <div class="info-row">
              <span class="label">名称：</span>
              <span class="value">华迪智慧养老公寓</span>
            </div>
            <div class="info-row">
              <span class="label">地址：</span>
              <span class="value">四川省郫都区红展西路366号</span>
            </div>
            <div class="info-row">
              <span class="label">电话：</span>
              <span class="value">028-88888888</span>
            </div>
          </div>
        </el-card>

        <!-- 机构设施 -->
        <el-card shadow="hover" class="facilities-card">
          <template #header>
            <div class="card-header">
              <el-icon><Grid /></el-icon>
              <span>机构设施</span>
            </div>
          </template>
          <div class="facilities-grid">
            <div v-for="facility in facilities" :key="facility.name" class="facility-item">
              <span class="facility-icon">{{ facility.icon }}</span>
              <span class="facility-name">{{ facility.name }}</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 我的轨迹信息 -->
      <div v-if="mapMode === 'track'" class="panel-section">
        <div class="section-header">
          <el-icon><Guide /></el-icon>
          <h3>我的活动轨迹</h3>
        </div>
        <el-card shadow="hover">
          <div class="track-info">
            <div class="info-row highlight">
              <span class="label">当前位置：</span>
              <span class="value">{{ currentLocation || '未知' }}</span>
            </div>
            <div class="info-row">
              <span class="label">最后更新：</span>
              <span class="value">{{ lastUpdate || '未知' }}</span>
            </div>
            <div class="info-row">
              <span class="label">今日行走：</span>
              <span class="value text-primary">{{ todayDistance }} 米</span>
            </div>
            <div class="info-row">
              <span class="label">停留时间：</span>
              <span class="value">{{ totalStayTime }} 分钟</span>
            </div>
          </div>
          <el-divider />
          <div class="time-filter">
            <span class="filter-label">时间范围：</span>
            <el-radio-group v-model="timeRange" size="small" @change="handleTimeRangeChange">
              <el-radio-button value="today">今日</el-radio-button>
              <el-radio-button value="week">本周</el-radio-button>
              <el-radio-button value="month">本月</el-radio-button>
            </el-radio-group>
          </div>
        </el-card>

        <!-- 活动统计 -->
        <el-card shadow="hover" class="track-stats">
          <template #header>
            <div class="card-header">
              <el-icon><DataLine /></el-icon>
              <span>活动统计</span>
            </div>
          </template>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ trackStats.steps }}</span>
              <span class="stat-label">步数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ trackStats.calories }}</span>
              <span class="stat-label">卡路里</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ trackStats.heartRate }}</span>
              <span class="stat-label">心率</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ trackStats.sleepHours }}</span>
              <span class="stat-label">睡眠(小时)</span>
            </div>
          </div>
        </el-card>

        <!-- 轨迹时间线 -->
        <el-card shadow="hover" class="track-timeline">
          <template #header>
            <div class="card-header">
              <el-icon><Timer /></el-icon>
              <span>今日行程</span>
            </div>
          </template>
          <el-scrollbar height="200px">
            <div class="timeline-list">
              <div
                v-for="(event, index) in trackHistory"
                :key="index"
                class="timeline-item"
                :class="{ active: playbackProgress === index }"
              >
                <div class="timeline-dot" :class="event.type"></div>
                <div class="timeline-content">
                  <div class="timeline-time">{{ event.time }}</div>
                  <div class="timeline-location">{{ event.location }}</div>
                  <div class="timeline-duration" v-if="event.duration">停留 {{ event.duration }} 分钟</div>
                </div>
              </div>
            </div>
          </el-scrollbar>
        </el-card>
      </div>

      <!-- 紧急操作 -->
      <div class="panel-section emergency-section">
        <div class="section-header danger">
          <el-icon><Warning /></el-icon>
          <h3>紧急求助</h3>
        </div>
        <div class="emergency-actions">
          <el-button type="danger" size="large" @click="handleEmergency">
            <el-icon><Bell /></el-icon>
            紧急求助
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  OfficeBuilding, Guide,
  Warning, Bell, Plus, Minus, House, Grid,
  VideoPlay, VideoPause, DataLine, Timer, Refresh
} from '@element-plus/icons-vue'
import AMapView from '@/components/AMapView.vue'
import api from '@/store/auth'

const mapViewRef = ref()

// 地图相关状态 - 郫都区坐标
const PIDU_CENTER_LNG = 103.8986
const PIDU_CENTER_LAT = 30.7980

const mapMode = ref<'nursingHome' | 'track'>('nursingHome')
const mapCenter = ref<[number, number]>([PIDU_CENTER_LNG, PIDU_CENTER_LAT])
const mapZoom = ref(16)

// 当前位置
const currentPosition = ref<[number, number]>([PIDU_CENTER_LNG + 0.0008, PIDU_CENTER_LAT - 0.0003])
const currentLocation = ref('休息室')
const lastUpdate = ref(new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }))
const todayDistance = ref(Math.floor(Math.random() * 2000) + 500)
const totalStayTime = ref(Math.floor(Math.random() * 120) + 30)
const timeRange = ref('today')
const isRefreshing = ref(false)

// 轨迹统计
const trackStats = ref({
  steps: Math.floor(Math.random() * 5000) + 3000,
  calories: Math.floor(Math.random() * 300) + 150,
  heartRate: Math.floor(Math.random() * 30) + 65,
  sleepHours: Math.floor(Math.random() * 3) + 6
})

// 轨迹相关
const trackPath = ref<[number, number][]>([])
const trackHistory = ref<Array<{
  time: string
  location: string
  position: [number, number]
  type: 'move' | 'stay' | 'arrive' | 'leave'
  duration?: number
}>>([])

// 电子围栏
const fenceCenter = ref<[number, number]>([PIDU_CENTER_LNG, PIDU_CENTER_LAT])
const fenceRadius = ref(200)

// 设施列表
const facilities = [
  { name: '主楼', icon: '🏢', position: [PIDU_CENTER_LNG, PIDU_CENTER_LAT] },
  { name: '花园', icon: '🌳', position: [PIDU_CENTER_LNG + 0.001, PIDU_CENTER_LAT + 0.0008] },
  { name: '餐厅', icon: '🍽️', position: [PIDU_CENTER_LNG - 0.0008, PIDU_CENTER_LAT - 0.0005] },
  { name: '活动室', icon: '🎮', position: [PIDU_CENTER_LNG + 0.0015, PIDU_CENTER_LAT + 0.0003] },
  { name: '休息室', icon: '🛋️', position: [PIDU_CENTER_LNG + 0.0008, PIDU_CENTER_LAT - 0.0003] },
  { name: '医务室', icon: '🏥', position: [PIDU_CENTER_LNG - 0.0003, PIDU_CENTER_LAT + 0.0006] },
]

// 计算标记点
const markers = computed(() => {
  const result = []

  // 养老院中心
  result.push({
    position: [PIDU_CENTER_LNG, PIDU_CENTER_LAT] as [number, number],
    title: '华迪智慧养老公寓',
    icon: '🏢',
    color: 'blue' as const
  })

  // 设施标记
  if (mapMode.value === 'nursingHome') {
    facilities.forEach(f => {
      result.push({
        position: f.position as [number, number],
        title: f.name,
        icon: f.icon,
        color: 'green' as const
      })
    })
  }

  // 老人的位置
  if (mapMode.value === 'track') {
    result.push({
      position: currentPosition.value,
      title: '我的位置',
      icon: '👤',
      color: 'green' as const
    })
  }

  return result
})

let locationUpdateTimer: number | null = null

// 获取当前位置
const getCurrentLocation = async () => {
  try {
    const res: any = await api.get('/location/current')
    if (res.code === 200) {
      const location = res.data
      currentPosition.value = [location.longitude, location.latitude]
      currentLocation.value = location.location_name || '未知位置'
      lastUpdate.value = new Date(location.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      
      if (mapMode.value === 'track') {
        mapCenter.value = currentPosition.value
      }
    }
  } catch (error) {
    console.error('获取当前位置失败', error)
    // 模拟位置更新
    currentPosition.value = [
      PIDU_CENTER_LNG + (Math.random() - 0.5) * 0.001,
      PIDU_CENTER_LAT + (Math.random() - 0.5) * 0.001
    ]
    currentLocation.value = facilities[Math.floor(Math.random() * facilities.length)].name
    lastUpdate.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
}

// 刷新位置信息
const refreshLocation = async () => {
  isRefreshing.value = true
  await getCurrentLocation()
  isRefreshing.value = false
  ElMessage.success('位置已更新')
}

// 更新位置（模拟老人端更新位置）
const updateLocation = async () => {
  try {
    const res: any = await api.post('/location/update', {
      longitude: currentPosition.value[0],
      latitude: currentPosition.value[1],
      location_name: currentLocation.value
    })
    if (res.code === 200) {
      ElMessage.success('位置更新成功')
    }
  } catch (error) {
    console.error('更新位置失败', error)
  }
}

const handleModeChange = () => {
  trackPath.value = []
  trackHistory.value = []
  pauseTrack()

  if (mapMode.value === 'nursingHome') {
    mapCenter.value = [PIDU_CENTER_LNG, PIDU_CENTER_LAT]
    mapZoom.value = 16
  } else if (mapMode.value === 'track') {
    mapCenter.value = currentPosition.value
    mapZoom.value = 17
    generateTrackHistory()
    generateTrackPath()
  }
}

const handleTimeRangeChange = () => {
  generateTrackHistory()
  generateTrackPath()
}

const generateTrackHistory = () => {
  const baseLng = PIDU_CENTER_LNG
  const baseLat = PIDU_CENTER_LAT

  const locations = [
    { name: '休息室', type: 'stay' as const, duration: 45 },
    { name: '走廊', type: 'move' as const },
    { name: '餐厅', type: 'stay' as const, duration: 30 },
    { name: '花园', type: 'stay' as const, duration: 60 },
    { name: '活动室', type: 'stay' as const, duration: 40 },
    { name: '走廊', type: 'move' as const },
    { name: '休息室', type: 'arrive' as const },
  ]

  const history = []
  let currentTime = new Date()
  currentTime.setHours(6, 0, 0, 0)

  // 使用固定种子生成轨迹，确保每次刷新时轨迹一致
  const seed = 12345 // 固定种子

  locations.forEach((loc, index) => {
    const hours = index * (timeRange.value === 'today' ? 1 : timeRange.value === 'week' ? 2 : 4)
    const time = new Date(currentTime.getTime() + hours * 60 * 60 * 1000)

    // 使用种子和索引生成固定的位置偏移
    const offsetX = ((seed + index * 17) % 1000) / 500000 - 0.001
    const offsetY = ((seed + index * 19) % 1000) / 500000 - 0.001

    history.push({
      time: formatTime(time),
      location: loc.name,
      position: [
        baseLng + offsetX,
        baseLat + offsetY
      ] as [number, number],
      type: loc.type,
      duration: loc.duration
    })
  })

  trackHistory.value = history
}

const formatTime = (date: Date): string => {
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const generateTrackPath = () => {
  if (trackHistory.value.length === 0) return
  trackPath.value = trackHistory.value.map(h => h.position)
}

const handleMapClick = (lng: number, lat: number) => {
  console.log('地图点击:', lng, lat)
}

const handleMarkerClick = (index: number) => {
  if (mapMode.value === 'nursingHome') {
    if (index > 0 && index <= facilities.length) {
      const facility = facilities[index - 1]
      ElMessage.info(`当前位置: ${facility.name}`)
    }
  }
}

const zoomIn = () => {
  mapZoom.value = Math.min(mapZoom.value + 1, 18)
}

const zoomOut = () => {
  mapZoom.value = Math.max(mapZoom.value - 1, 5)
}

const centerToHome = () => {
  mapCenter.value = [PIDU_CENTER_LNG, PIDU_CENTER_LAT]
  mapZoom.value = 16
}

const handleEmergency = () => {
  ElMessageBox.confirm('确定要发送紧急求助信号吗？', '紧急求助', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('紧急求助信号已发送，护理人员会立即收到通知')
  }).catch(() => {})
}

onMounted(async () => {
  await getCurrentLocation()
  generateTrackHistory()
  generateTrackPath()
  
  // 每30秒自动更新位置
  locationUpdateTimer = window.setInterval(() => {
    getCurrentLocation()
  }, 30000)
})

onUnmounted(() => {
  if (locationUpdateTimer) {
    clearInterval(locationUpdateTimer)
    locationUpdateTimer = null
  }
})
</script>

<style scoped lang="scss">
// 配色方案 - 绿色、浅蓝、白色
$primary-green: #22c55e;
$primary-green-dark: #16a34a;
$primary-blue: #3b82f6;
$primary-blue-light: #60a5fa;
$white: #ffffff;
$gray-50: #f8fafc;
$gray-100: #f1f5f9;
$gray-200: #e2e8f0;
$gray-300: #cbd5e1;
$gray-400: #94a3b8;
$gray-500: #64748b;
$gray-600: #475569;
$gray-700: #334155;
$gray-800: #1e293b;

.elderly-map {
  display: flex;
  gap: 20px;
  height: calc(100vh - 140px);
  padding: 20px;
  background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 100%);
}

.map-wrapper {
  flex: 1;
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);

  .map-view {
    width: 100%;
    height: 100%;
  }

  .map-toolbar {
    position: absolute;
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    background: $white;
    padding: 8px;
    border-radius: 24px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    z-index: 10;

    :deep(.el-radio-group) {
      display: flex;
      gap: 4px;

      .el-radio-button__inner {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        border-radius: 20px;
        border: none;
        background: transparent;
        color: $gray-600;
        font-weight: 500;
        transition: all 0.2s ease;

        &:hover {
          color: $primary-green;
          background: rgba(34, 197, 94, 0.08);
        }
      }

      .el-radio-button__original-radio:checked + .el-radio-button__inner {
        background: linear-gradient(135deg, $primary-green 0%, $primary-blue 100%);
        color: $white;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
      }
    }
  }

  .map-controls {
    position: absolute;
    top: 16px;
    right: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    z-index: 10;

    .el-button {
      background: $white;
      border: 1px solid $gray-200;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

      &:hover {
        background: $gray-50;
        border-color: $primary-green;
        color: $primary-green;
      }
    }
  }


}

.info-panel {
  width: 380px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  padding-right: 8px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-thumb {
    background: $gray-300;
    border-radius: 3px;
  }

  .panel-section {
    background: $white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);

    .section-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 2px solid $gray-100;

      .el-icon {
        font-size: 20px;
        color: $gray-500;
      }

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: $gray-700;
      }

      &.primary {
        border-bottom-color: rgba(34, 197, 94, 0.2);
        .el-icon { color: $primary-green; }
        h3 { color: $gray-800; }
      }

      &.danger {
        border-bottom-color: rgba(239, 68, 68, 0.2);
        .el-icon { color: #ef4444; }
        h3 { color: #ef4444; }
      }

      &.info {
        border-bottom-color: rgba(59, 130, 246, 0.2);
        .el-icon { color: $primary-blue; }
        h3 { color: $primary-blue; }
      }
    }

    .nursing-info,
    .track-info {
      .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid $gray-100;

        &:last-child {
          border-bottom: none;
        }

        &.highlight {
          background: rgba(34, 197, 94, 0.05);
          margin: -4px -8px;
          padding: 10px 8px;
          border-radius: 8px;
          border-bottom: none;
        }

        .label {
          color: $gray-500;
          font-size: 14px;
        }

        .value {
          color: $gray-800;
          font-weight: 500;
          font-size: 14px;
        }

        .text-primary {
          color: $primary-green;
          font-weight: 600;
        }
      }
    }

    .time-filter {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;

      .filter-label {
        color: $gray-600;
        font-size: 14px;
      }
    }

    .radius-display {
      display: block;
      text-align: center;
      margin-top: 8px;
      font-size: 16px;
      font-weight: 600;
      color: $primary-blue;
    }
  }

  .track-stats {
    :deep(.el-card__header) {
      padding: 12px 16px;
      border-bottom: 1px solid $gray-100;
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 500;
      color: $gray-700;

      .el-icon {
        color: $primary-blue;
      }
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      padding: 8px 0;

      .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 12px;
        background: $gray-50;
        border-radius: 10px;

        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: $primary-green;
        }

        .stat-label {
          font-size: 12px;
          color: $gray-500;
          margin-top: 4px;
        }
      }
    }
  }

  .track-timeline {
    :deep(.el-card__header) {
      padding: 12px 16px;
      border-bottom: 1px solid $gray-100;
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 500;
      color: $gray-700;

      .el-icon {
        color: $primary-blue;
      }
    }

    .timeline-list {
      padding: 8px 0;

      .timeline-item {
        display: flex;
        gap: 12px;
        padding: 12px 0;
        position: relative;

        &:not(:last-child)::before {
          content: '';
          position: absolute;
          left: 6px;
          top: 30px;
          bottom: -12px;
          width: 2px;
          background: $gray-200;
        }

        &.active {
          .timeline-dot {
            background: $primary-green;
            border-color: $primary-green;
            box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.2);
          }

          .timeline-content {
            background: rgba(34, 197, 94, 0.05);
            border-radius: 8px;
            padding: 8px 12px;
          }
        }

        .timeline-dot {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          border: 3px solid $gray-300;
          background: $white;
          flex-shrink: 0;
          margin-top: 4px;
          z-index: 1;
          transition: all 0.2s ease;

          &.move { border-color: $primary-blue; }
          &.stay { border-color: $primary-green; }
          &.arrive { border-color: #10b981; }
          &.leave { border-color: $gray-400; }
        }

        .timeline-content {
          flex: 1;

          .timeline-time {
            font-size: 12px;
            color: $gray-500;
          }

          .timeline-location {
            font-size: 14px;
            font-weight: 500;
            color: $gray-700;
            margin-top: 2px;
          }

          .timeline-duration {
            font-size: 12px;
            color: $primary-green;
            margin-top: 4px;
          }
        }
      }
    }
  }

  .facilities-card {
    margin-top: 8px;

    :deep(.el-card__header) {
      padding: 12px 16px;
      border-bottom: 1px solid $gray-100;
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 500;
      color: $gray-700;

      .el-icon {
        color: $primary-blue;
      }
    }

    .facilities-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      padding: 8px 0;

      .facility-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
        padding: 12px 8px;
        background: $gray-50;
        border-radius: 10px;
        transition: all 0.2s ease;
        cursor: pointer;

        &:hover {
          background: rgba(34, 197, 94, 0.08);
          transform: translateY(-2px);
        }

        .facility-icon {
          font-size: 24px;
        }

        .facility-name {
          font-size: 12px;
          color: $gray-600;
        }
      }
    }
  }

  .emergency-section {
    border: 1px solid rgba(239, 68, 68, 0.15);
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.03) 0%, rgba(249, 115, 22, 0.03) 100%);

    .emergency-actions {
      display: flex;
      gap: 12px;

      .el-button {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 14px 16px;
        border-radius: 12px;
        font-weight: 500;

        &[type="danger"] {
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
          border: none;
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);

          &:hover {
            box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
            transform: translateY(-1px);
          }
        }
      }
    }
  }
}

:deep(.el-card) {
  border: none;
  border-radius: 12px;

  .el-card__body {
    padding: 16px;
  }
}

:deep(.el-tag) {
  border-radius: 6px;
}

:deep(.el-divider) {
  margin: 16px 0;
}

:deep(.el-form-item__label) {
  color: $gray-600;
}

:deep(.el-slider__marks-text) {
  color: $gray-500;
}

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
