<template>
  <div ref="mapRef" class="amap-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

interface Marker {
  position: [number, number]
  title?: string
  icon?: string
  color?: 'green' | 'blue' | 'red' | 'orange'
  offset?: [number, number]
}

interface Props {
  center?: [number, number]  // [lng, lat]
  zoom?: number
  markers?: Marker[]
  polylinePath?: [number, number][]
  circleCenter?: [number, number]
  circleRadius?: number
  showCircle?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  center: () => [116.427428, 39.92923],
  zoom: 15,
  markers: () => [],
  polylinePath: () => [],
  circleCenter: () => [116.427428, 39.92923],
  circleRadius: 200,
  showCircle: false
})

const emit = defineEmits<{
  (e: 'click', lng: number, lat: number): void
  (e: 'marker-click', index: number): void
}>()

const mapRef = ref<HTMLElement | null>(null)
let mapInstance: any = null
let AMap: any = null
let markerList: any[] = []
let polylineInstance: any = null
let circleInstance: any = null

// 加载高德地图 SDK
const loadAMap = (): Promise<any> => {
  return new Promise((resolve, reject) => {
    if ((window as any).AMap) {
      resolve((window as any).AMap)
      return
    }

    // 高德地图 API Key
    const key = 'e000fdb2e8100fb640bf9b3b36c5913e'
    
    // 动态创建 script 标签
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${key}&plugin=AMap.ToolBar,AMap.Scale,AMap.MapType`
    script.async = true
    script.onload = () => {
      // 等待 DOM 加载完成
      setTimeout(() => {
        if ((window as any).AMap) {
          resolve((window as any).AMap)
        } else {
          reject(new Error('AMap 加载失败'))
        }
      }, 100)
    }
    script.onerror = () => reject(new Error('高德地图 SDK 加载失败'))
    document.head.appendChild(script)
  })
}

// 创建标记点
const createMarkers = () => {
  // 清除旧标记
  markerList.forEach(m => m.setMap(null))
  markerList = []

  const colors: Record<string, string> = {
    green: '#22c55e',
    blue: '#3b82f6',
    red: '#ef4444',
    orange: '#f97316'
  }

  props.markers.forEach((marker, index) => {
    const color = marker.color || 'blue'
    const size = 36
    const offsetX = marker.offset?.[0] || 0
    const offsetY = marker.offset?.[1] || 0

    // 创建自定义标记
    const markerContent = document.createElement('div')
    markerContent.className = 'custom-marker'
    markerContent.style.cssText = `
      position: relative;
      width: ${size}px;
      height: ${size}px;
    `

    // 标记图标
    const iconDiv = document.createElement('div')
    iconDiv.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      background: ${colors[color]};
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 3px 10px rgba(0,0,0,0.3);
      border: 2px solid white;
    `
    
    // 标记内的符号
    const iconText = document.createElement('span')
    iconText.textContent = marker.icon || '📍'
    iconText.style.cssText = `
      transform: rotate(45deg);
      font-size: 16px;
    `
    iconDiv.appendChild(iconText)
    markerContent.appendChild(iconDiv)

    // 标题
    if (marker.title) {
      const label = document.createElement('div')
      label.style.cssText = `
        position: absolute;
        top: -24px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        white-space: nowrap;
      `
      label.textContent = marker.title
      markerContent.appendChild(label)
    }

    const aMarker = new AMap.Marker({
      position: marker.position,
      content: markerContent,
      offset: new AMap.Pixel(offsetX || -size/2, offsetY || -size),
      title: marker.title
    })

    aMarker.on('click', () => {
      emit('marker-click', index)
    })

    aMarker.setMap(mapInstance)
    markerList.push(aMarker)
  })
}

// 绘制轨迹线
const createPolyline = () => {
  if (polylineInstance) {
    polylineInstance.setMap(null)
    polylineInstance = null
  }

  if (props.polylinePath.length < 2) return

  polylineInstance = new AMap.Polyline({
    path: props.polylinePath,
    strokeColor: '#3b82f6',
    strokeWeight: 4,
    strokeStyle: 'solid',
    lineJoin: 'round',
    lineCap: 'round',
    showDir: true,
    map: mapInstance
  })
}

// 绘制电子围栏
const createCircle = () => {
  if (circleInstance) {
    circleInstance.setMap(null)
    circleInstance = null
  }

  if (!props.showCircle) return

  circleInstance = new AMap.Circle({
    center: props.circleCenter,
    radius: props.circleRadius,
    strokeColor: '#ef4444',
    strokeWeight: 2,
    strokeOpacity: 0.8,
    fillColor: '#ef4444',
    fillOpacity: 0.15,
    map: mapInstance
  })
}

// 初始化地图
const initMap = async () => {
  try {
    AMap = await loadAMap()
    
    if (!mapRef.value) return

    mapInstance = new AMap.Map(mapRef.value, {
      zoom: props.zoom,
      center: props.center,
      viewMode: '2D',
      mapStyle: 'amap://styles/whitesmoke'
    })

    // 添加控件
    mapInstance.addControl(new AMap.Scale())
    mapInstance.addControl(new AMap.ToolBar({ position: 'RB' }))

    // 绑定点击事件
    mapInstance.on('click', (e: any) => {
      emit('click', e.lnglat.getLng(), e.lnglat.getLat())
    })

    // 创建标记、轨迹、围栏
    createMarkers()
    createPolyline()
    createCircle()

  } catch (error) {
    console.error('地图初始化失败:', error)
  }
}

// 定位到指定位置
const panTo = (position: [number, number]) => {
  if (mapInstance) {
    mapInstance.panTo(position)
  }
}

// 缩放到指定级别
const setZoom = (zoom: number) => {
  if (mapInstance) {
    mapInstance.setZoom(zoom)
  }
}

// 设置缩放范围
const setView = (center: [number, number], zoom: number) => {
  if (mapInstance) {
    mapInstance.setCenter(center)
    mapInstance.setZoom(zoom)
  }
}

// 监听属性变化
watch(() => props.markers, () => {
  if (mapInstance && AMap) {
    createMarkers()
  }
}, { deep: true })

watch(() => props.polylinePath, () => {
  if (mapInstance && AMap) {
    createPolyline()
  }
}, { deep: true })

watch(() => props.showCircle, () => {
  if (mapInstance && AMap) {
    createCircle()
  }
})

// 监听 center 变化
watch(() => props.center, (newCenter) => {
  if (mapInstance && newCenter) {
    mapInstance.setCenter(newCenter)
  }
})

// 监听 zoom 变化
watch(() => props.zoom, (newZoom) => {
  if (mapInstance && newZoom) {
    mapInstance.setZoom(newZoom)
  }
})

onMounted(() => {
  initMap()
})

onUnmounted(() => {
  if (mapInstance) {
    mapInstance.destroy()
    mapInstance = null
  }
})

// 暴露方法给父组件
defineExpose({
  panTo,
  setZoom,
  setView
})
</script>

<style scoped>
.amap-container {
  width: 100%;
  height: 100%;
}

:deep(.custom-marker) {
  cursor: pointer;
  transition: transform 0.2s;
}

:deep(.custom-marker:hover) {
  transform: scale(1.1);
}
</style>
