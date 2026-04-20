<template>
  <div class="staff-location-map">
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
        :show-circle="mapMode === 'fence' && selectedElderId"
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
            活动轨迹
          </el-radio-button>
          <el-radio-button value="fence">
            <el-icon><LocationInformation /></el-icon>
            电子围栏
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
        <el-button circle @click="centerToSelected" title="定位选中老人" :disabled="!selectedElderId">
          <el-icon><Search /></el-icon>
        </el-button>
      </div>

      <!-- 轨迹回放控制 -->
      <div v-if="mapMode === 'track' && selectedElderId && trackHistory.length > 0" class="track-player">
        <el-button circle size="small" @click="playTrack" :disabled="isPlaying">
          <el-icon><VideoPlay /></el-icon>
        </el-button>
        <el-button circle size="small" @click="pauseTrack" :disabled="!isPlaying">
          <el-icon><VideoPause /></el-icon>
        </el-button>
        <el-slider
          v-model="playbackProgress"
          :step="1"
          :min="0"
          :max="trackHistory.length - 1"
          size="small"
          class="playback-slider"
          @change="seekTrack"
        />
        <span class="playback-time">{{ currentPlaybackTime }}</span>
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
            <div class="info-row">
              <span class="label">床位数：</span>
              <span class="value">200张</span>
            </div>
            <div class="info-row">
              <span class="label">当前入住：</span>
              <span class="value">{{ visibleElders.length }}人</span>
            </div>
          </div>
        </el-card>

        <!-- 在线状态统计 -->
        <el-card shadow="hover" class="status-card">
          <template #header>
            <div class="card-header">
              <el-icon><DataLine /></el-icon>
              <span>老人状态统计</span>
            </div>
          </template>
          <div class="status-stats">
            <div class="stat-item success">
              <span class="stat-icon">✓</span>
              <span class="stat-value">{{ normalCount }}</span>
              <span class="stat-label">正常</span>
            </div>
            <div class="stat-item warning">
              <span class="stat-icon">⚠</span>
              <span class="stat-value">{{ warningCount }}</span>
              <span class="stat-label">异常</span>
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

      <!-- 老人选择 (轨迹和围栏模式) -->
      <div v-if="mapMode === 'track' || mapMode === 'fence'" class="panel-section">
        <div class="section-header">
          <el-icon><User /></el-icon>
          <h3>{{ userTypeLabel }} - 选择老人</h3>
        </div>
        <el-select
          v-model="selectedElderId"
          placeholder="请选择老人"
          filterable
          class="elder-select"
          @change="handleElderChange"
        >
          <el-option
            v-for="elder in visibleElders"
            :key="elder.id"
            :label="elder.name"
            :value="elder.id"
          >
            <div class="elder-option">
              <el-avatar :size="24" :style="{ background: elder.status === 'normal' ? '#22c55e' : '#f97316' }">
                {{ elder.name.charAt(0) }}
              </el-avatar>
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
            <div class="info-row">
              <span class="label">活动范围：</span>
              <span class="value">{{ activityRange }} 米</span>
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
            <el-radio-group v-model="timeRange" size="small" @change="handleTimeRangeChange">
              <el-radio-button value="today">今日</el-radio-button>
              <el-radio-button value="week">本周</el-radio-button>
              <el-radio-button value="month">本月</el-radio-button>
            </el-radio-group>
          </div>
        </el-card>

        <!-- 轨迹统计 -->
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

      <!-- 电子围栏设置 -->
      <div v-if="mapMode === 'fence' && selectedElderId" class="panel-section">
        <div class="section-header danger">
          <el-icon><LocationInformation /></el-icon>
          <h3>电子围栏设置</h3>
        </div>
        <el-card shadow="hover">
          <el-form label-width="80px" size="small">
            <el-form-item label="围栏名称">
              <el-input v-model="fenceName" placeholder="请输入围栏名称" />
            </el-form-item>
            <el-form-item label="半径范围">
              <el-slider
                v-model="fenceRadius"
                :min="50"
                :max="1000"
                :step="50"
                :marks="fenceMarks"
                show-input
              />
              <span class="radius-display">{{ fenceRadius }} 米</span>
            </el-form-item>
            <el-form-item label="告警类型">
              <el-checkbox-group v-model="alertTypes">
                <el-checkbox label="越界告警">越界告警</el-checkbox>
                <el-checkbox label="滞留告警">滞留告警</el-checkbox>
                <el-checkbox label="静止告警">静止告警</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveFence">
                <el-icon><Check /></el-icon>
                保存围栏
              </el-button>
              <el-button @click="clearFence">
                <el-icon><Delete /></el-icon>
                清除围栏
              </el-button>
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
          <el-button type="danger" size="large" @click="handleEmergency">
            <el-icon><Bell /></el-icon>
            紧急求助
          </el-button>
          <el-button type="warning" size="large" @click="handleLocate">
            <el-icon><Search /></el-icon>
            定位老人
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
  OfficeBuilding, Guide, LocationInformation, User,
  Warning, Bell, Search, Plus, Minus, House, Grid,
  Check, Delete, VideoPlay, VideoPause, DataLine, Timer
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/auth'
import AMapView from '@/components/AMapView.vue'

const authStore = useAuthStore()
const mapViewRef = ref()

// 地图相关状态 - 郫都区坐标
const PIDU_CENTER_LNG = 103.8986
const PIDU_CENTER_LAT = 30.7980

const mapMode = ref<'nursingHome' | 'track' | 'fence'>('nursingHome')
const mapCenter = ref<[number, number]>([PIDU_CENTER_LNG, PIDU_CENTER_LAT])
const mapZoom = ref(16)

// 用户类型判断
const userType = computed(() => authStore.userInfo?.user_type || 3)
const userTypeLabel = computed(() => {
  const labels: Record<number, string> = { 1: '老人', 2: '护理员', 3: '管理员', 4: '家属' }
  return labels[userType.value] || '用户'
})

// 获取用户绑定的老人ID列表（家属用）
const boundElderIds = computed(() => {
  // 模拟：家属绑定老人ID为1和2
  if (userType.value === 4) {
    return [1, 2]
  }
  return []
})

// 所有老人数据
const allElders = ref([
  {
    id: 1,
    name: '王建国',
    avatar: '',
    status: 'normal',
    location: '休息室',
    lastUpdate: '10:30',
    position: [PIDU_CENTER_LNG + 0.0008, PIDU_CENTER_LAT - 0.0003] as [number, number],
  },
  {
    id: 2,
    name: '李秀英',
    avatar: '',
    status: 'normal',
    location: '花园',
    lastUpdate: '10:25',
    position: [PIDU_CENTER_LNG + 0.0012, PIDU_CENTER_LAT + 0.0005] as [number, number],
  },
  {
    id: 3,
    name: '张德明',
    avatar: '',
    status: 'warning',
    location: '外出',
    lastUpdate: '09:15',
    position: [PIDU_CENTER_LNG + 0.003, PIDU_CENTER_LAT - 0.001] as [number, number],
  },
  {
    id: 4,
    name: '陈桂兰',
    avatar: '',
    status: 'normal',
    location: '餐厅',
    lastUpdate: '10:45',
    position: [PIDU_CENTER_LNG - 0.0005, PIDU_CENTER_LAT - 0.0008] as [number, number],
  },
  {
    id: 5,
    name: '刘永华',
    avatar: '',
    status: 'normal',
    location: '活动室',
    lastUpdate: '10:20',
    position: [PIDU_CENTER_LNG + 0.0015, PIDU_CENTER_LAT + 0.0002] as [number, number],
  },
])

// 根据用户类型过滤老人列表
const visibleElders = computed(() => {
  // 护理员和管理员可以查看所有老人
  if (userType.value === 2 || userType.value === 3) {
    return allElders.value
  }
  // 家属只能查看绑定的老人
  if (userType.value === 4) {
    return allElders.value.filter(elder => boundElderIds.value.includes(elder.id))
  }
  // 默认返回所有老人
  return allElders.value
})

// 统计正常和异常老人数量
const normalCount = computed(() => visibleElders.value.filter(e => e.status === 'normal').length)
const warningCount = computed(() => visibleElders.value.filter(e => e.status === 'warning').length)

const selectedElderId = ref<number | null>(null)

// 轨迹相关
const trackPath = ref<[number, number][]>([])
const trackHistory = ref<Array<{
  time: string
  location: string
  position: [number, number]
  type: 'move' | 'stay' | 'arrive' | 'leave'
  duration?: number
}>>([])
const currentLocation = ref('')
const lastUpdate = ref('')
const todayDistance = ref(0)
const totalStayTime = ref(0)
const activityRange = ref(0)
const activityStatus = ref('活跃')
const timeRange = ref('today')
const isPlaying = ref(false)
const playbackProgress = ref(0)
const currentPlaybackTime = ref('00:00')

// 轨迹统计
const trackStats = ref({
  steps: 0,
  calories: 0,
  heartRate: 0,
  sleepHours: 0
})

// 围栏相关
const fenceName = ref('')
const fenceRadius = ref(200)
const fenceCenter = ref<[number, number]>([PIDU_CENTER_LNG, PIDU_CENTER_LAT])
const alertTypes = ref(['越界告警'])

const fenceMarks = {
  50: '50m',
  200: '200m',
  500: '500m',
  1000: '1km'
}

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

  // 可见的老人位置
  if (mapMode.value === 'track' || mapMode.value === 'fence') {
    visibleElders.value.forEach(elder => {
      result.push({
        position: elder.position,
        title: elder.name,
        icon: elder.status === 'normal' ? '👴' : '⚠️',
        color: elder.status === 'normal' ? 'green' : 'orange' as const
      })
    })
  }

  return result
})

let playbackTimer: number | null = null

const handleModeChange = () => {
  selectedElderId.value = null
  trackPath.value = []
  trackHistory.value = []
  pauseTrack()

  if (mapMode.value === 'nursingHome') {
    mapCenter.value = [PIDU_CENTER_LNG, PIDU_CENTER_LAT]
    mapZoom.value = 16
  }
}

const handleTimeRangeChange = () => {
  if (selectedElderId.value) {
    generateTrackHistory()
  }
}

const handleElderChange = (id: number) => {
  const elder = visibleElders.value.find(e => e.id === id)
  if (elder) {
    currentLocation.value = elder.location
    lastUpdate.value = elder.lastUpdate
    todayDistance.value = Math.floor(Math.random() * 2000) + 500
    totalStayTime.value = Math.floor(Math.random() * 120) + 30
    activityRange.value = Math.floor(Math.random() * 200) + 50
    activityStatus.value = Math.random() > 0.2 ? '活跃' : '静止'

    fenceCenter.value = elder.position

    if (mapMode.value === 'track') {
      generateTrackHistory()
      generateTrackPath()
    } else if (mapMode.value === 'fence') {
      mapCenter.value = elder.position
      mapZoom.value = 17
    }

    trackStats.value = {
      steps: Math.floor(Math.random() * 5000) + 3000,
      calories: Math.floor(Math.random() * 300) + 150,
      heartRate: Math.floor(Math.random() * 30) + 65,
      sleepHours: Math.floor(Math.random() * 3) + 6
    }
  }
}

const generateTrackHistory = () => {
  const elder = visibleElders.value.find(e => e.id === selectedElderId.value)
  if (!elder) return

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

  locations.forEach((loc, index) => {
    const hours = index * (timeRange.value === 'today' ? 1 : timeRange.value === 'week' ? 2 : 4)
    const time = new Date(currentTime.getTime() + hours * 60 * 60 * 1000)

    history.push({
      time: formatTime(time),
      location: loc.name,
      position: [
        baseLng + (Math.random() - 0.5) * 0.002,
        baseLat + (Math.random() - 0.5) * 0.002
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

const playTrack = () => {
  if (isPlaying.value || trackHistory.value.length === 0) return
  isPlaying.value = true

  playbackTimer = window.setInterval(() => {
    if (playbackProgress.value < trackHistory.value.length - 1) {
      playbackProgress.value++
      updatePlaybackTime()
    } else {
      pauseTrack()
    }
  }, 1500)
}

const pauseTrack = () => {
  isPlaying.value = false
  if (playbackTimer) {
    clearInterval(playbackTimer)
    playbackTimer = null
  }
}

const seekTrack = (index: number) => {
  playbackProgress.value = index
  updatePlaybackTime()
}

const updatePlaybackTime = () => {
  if (trackHistory.value[playbackProgress.value]) {
    currentPlaybackTime.value = trackHistory.value[playbackProgress.value].time
  }
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
  } else if (mapMode.value !== 'nursingHome' && index > 0) {
    // 老人标记 - 根据可见老人数量调整
    const elderIndex = index - 1
    if (elderIndex < visibleElders.value.length) {
      const elder = visibleElders.value[elderIndex]
      if (elder) {
        selectedElderId.value = elder.id
        handleElderChange(elder.id)
      }
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

const centerToSelected = () => {
  if (selectedElderId.value) {
    const elder = visibleElders.value.find(e => e.id === selectedElderId.value)
    if (elder) {
      mapCenter.value = elder.position
      mapZoom.value = 17
    }
  }
}

const saveFence = () => {
  if (!fenceName.value) {
    ElMessage.warning('请输入围栏名称')
    return
  }
  ElMessage.success('围栏保存成功')
}

const clearFence = () => {
  fenceName.value = ''
  fenceRadius.value = 200
  alertTypes.value = ['越界告警']
  ElMessage.info('围栏已清除')
}

const handleEmergency = () => {
  ElMessageBox.confirm('确定要发送紧急求助信号吗？', '紧急求助', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('紧急求助信号已发送')
  }).catch(() => {})
}

const handleLocate = () => {
  if (selectedElderId.value) {
    const elder = visibleElders.value.find(e => e.id === selectedElderId.value)
    if (elder) {
      mapCenter.value = elder.position
      mapZoom.value = 17
      ElMessage.success(`已定位到 ${elder.name}`)
    }
  } else {
    ElMessage.warning('请先选择一位老人')
  }
}

onMounted(() => {
  authStore.getProfile()
})

onUnmounted(() => {
  pauseTrack()
})
</script>

<style scoped lang="scss">
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

.staff-location-map {
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

      &:disabled {
        opacity: 0.5;
      }
    }
  }

  .track-player {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    gap: 12px;
    background: $white;
    padding: 12px 20px;
    border-radius: 24px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    z-index: 10;

    .el-button {
      background: $primary-green;
      border: none;
      color: $white;

      &:hover {
        background: $primary-green-dark;
      }

      &:disabled {
        background: $gray-300;
      }
    }

    .playback-slider {
      width: 200px;

      :deep(.el-slider__runway) {
        background: $gray-200;
      }

      :deep(.el-slider__bar) {
        background: $primary-green;
      }

      :deep(.el-slider__button) {
        border-color: $primary-green;
      }
    }

    .playback-time {
      font-size: 14px;
      color: $gray-600;
      font-weight: 500;
      min-width: 40px;
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
    }

    .elder-select {
      width: 100%;

      :deep(.el-input__wrapper) {
        border-radius: 12px;
      }
    }

    .elder-option {
      display: flex;
      align-items: center;
      gap: 10px;
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

    .status-stats {
      display: flex;
      gap: 16px;

      .stat-item {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 16px;
        border-radius: 12px;

        .stat-icon {
          font-size: 24px;
          margin-bottom: 8px;
        }

        .stat-value {
          font-size: 28px;
          font-weight: 700;
        }

        .stat-label {
          font-size: 14px;
          margin-top: 4px;
        }

        &.success {
          background: rgba(34, 197, 94, 0.1);
          color: $primary-green;
        }

        &.warning {
          background: rgba(249, 115, 22, 0.1);
          color: #f97316;
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

  .status-card {
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

        &[type="warning"] {
          background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
          border: none;
          box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);

          &:hover {
            box-shadow: 0 6px 16px rgba(249, 115, 22, 0.4);
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
  .staff-location-map {
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
