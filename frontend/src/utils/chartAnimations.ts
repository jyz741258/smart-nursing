// ============================================
// 智慧养老系统 - 图表动效增强库
// 提供 ECharts 动画配置 + 自定义动效
// ============================================

// --- 1. 通用图表入场动画 ---
export const chartEnterAnimation = {
  animation: true,
  animationDuration: 1000,
  animationEasing: 'cubicOut',
  animationDelay: (idx: number) => idx * 100
}

// --- 2. 折线图/面积图动效配置 ---
export const lineChartAnimation = {
  ...chartEnterAnimation,
  progressive: 200,
  progressiveThreshold: 300
}

// --- 3. 柱状图动效配置 ---
export const barChartAnimation = {
  ...chartEnterAnimation,
  animationDelayUpdate: (idx: number) => idx * 50
}

// --- 4. 饼图/环形图动效配置 ---
export const pieChartAnimation = {
  animationType: 'expansion',
  animationEasing: 'elasticOut',
  animationDelay: (idx: number) => idx * 100
}

// --- 5. 散点图动效配置 ---
export const scatterChartAnimation = {
  ...chartEnterAnimation,
  animationDelay: (idx: number) => Math.random() * 200
}

// --- 6. 仪表盘动效配置 ---
export const gaugeChartAnimation = {
  animationDuration: 2000,
  animationEasing: 'bounceOut'
}

// --- 7. 动态数据更新动画（用于实时刷新）---
export const dataUpdateAnimation = {
  animation: true,
  animationDuration: 500,
  animationEasing: 'linear'
}

// --- 8. 主题色彩配置（深色/浅色）---
export const darkThemeColors = [
  '#667eea', '#764ba2', '#f093fb', '#4facfe',
  '#00f2fe', '#43e97b', '#38f9d7', '#fa709a',
  '#fee140', '#30cfd0', '#a8edea', '#fed6e3'
]

export const lightThemeColors = [
  '#5b8ff9', '#5ad8a6', '#5d7092', '#f6bd16',
  '#e86452', '#6dc8ec', '#945fb9', '#ff9845'
]

// --- 9. 图表初始加载动画（模拟数据加载）---
export const loadingAnimationConfig = {
  text: '加载中...',
  color: '#667eea',
  textColor: '#8b949e',
  maskColor: 'rgba(0, 0, 0, 0.3)',
  zlevel: 0,
  fontSize: 14,
  spinnerRadius: 10,
  lineWidth: 3
}

// --- 10. 数据变化高亮动画 ---
export const highlightAnimation = {
  emphasis: {
    focus: 'series',
    blurScope: 'coordinateSystem',
    lineStyle: {
      width: 4,
      shadowBlur: 10,
      shadowColor: 'rgba(102, 126, 234, 0.5)'
    },
    itemStyle: {
      shadowBlur: 10,
      shadowColor: 'rgba(102, 126, 234, 0.5)'
    }
  }
}

// --- 11. 区域缩放动画 ---
export const roamZoomAnimation = {
  roam: true,
  zoom: {
    animation: true,
    animationDuration: 300,
    animationEasing: 'quadraticInOut'
  },
  dataZoom: {
    show: true,
    start: 0,
    end: 100,
    animation: true,
    animationDuration: 300
  }
}

// --- 12. 时序数据滚动动画（用于实时监控）---
export const timelineAnimation = {
  axisPointer: {
    type: 'line',
    lineStyle: {
      color: '#667eea',
      width: 2,
      type: 'dashed'
    },
    label: {
      backgroundColor: '#667eea'
    }
  },
  tooltip: {
    trigger: 'axis',
    transitionDuration: 0
  }
}

// --- 13. 3D 柱状图动效（如果使用 echarts-gl）---
export const bar3DEffect = {
  shading: 'lambert',
  light: {
    main: {
      color: '#fff',
      intensity: 1.2
    },
    ambient: {
      color: '#667eea',
      intensity: 0.3
    }
  },
  viewControl: {
    autoRotate: true,
    autoRotateSpeed: 5,
    beta: 40,
    distance: 200
  }
}

// --- 14. 图表切换动画（多图表联动）---
export const chartTransition = {
  universalTransition: {
    enabled: true,
    seriesType: 'line',
    divideShape: 'clone',
    delay: 0,
    duration: 800,
    easing: 'cubicInOut'
  }
}

// --- 15. 动态颜色渐变生成器 ---
export function generateGradientColors(baseColor: string, count: number) {
  const colors: string[] = []
  for (let i = 0; i < count; i++) {
    const ratio = i / (count - 1 || 1)
    colors.push(baseColor)
  }
  return colors
}

// --- 16. 图表加载完成回调动画 ---
export const onChartReady = (chart: any) => {
  chart.on('finished', () => {
    console.log('图表动画完成')
  })

  chart.on('rendered', () => {
    // 可以在这里添加额外的渲染后效果
  })
}
