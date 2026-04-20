<template>
  <div class="bigdata-analytics">
    <div class="page-header">
      <div>
        <h2 class="page-title">大数据分析中心</h2>
        <p class="page-desc">智能健康数据分析与预测</p>
      </div>
      <div class="header-actions">
        <el-select v-model="selectedElderId" placeholder="选择老人" size="large" @change="loadAllData">
          <el-option label="全部老人" :value="null" />
          <el-option v-for="elder in elderList" :key="elder.id" :label="elder.name" :value="elder.id" />
        </el-select>
        <el-select v-model="timeRange" size="large" style="width: 150px">
          <el-option label="近7天" :value="7" />
          <el-option label="近30天" :value="30" />
          <el-option label="近90天" :value="90" />
        </el-select>
        <el-button type="primary" size="large" @click="loadAllData">
          <el-icon><Refresh /></el-icon> 刷新数据
        </el-button>
      </div>
    </div>

    <!-- 健康评分卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card score">
          <div class="card-icon"><el-icon><TrendCharts /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ healthScore }}</div>
            <div class="card-label">健康评分</div>
          </div>
          <div class="card-trend" :class="scoreTrend">
            <el-icon><Top v-if="scoreTrend === 'up'" /><Bottom v-else /></el-icon>
            {{ scoreTrendPercent }}%
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card records">
          <div class="card-icon"><el-icon><Document /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ totalRecords }}</div>
            <div class="card-label">数据记录</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card alerts">
          <div class="card-icon"><el-icon><Warning /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ abnormalCount }}</div>
            <div class="card-label">异常告警</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stats-card completeness">
          <div class="card-icon"><el-icon><CircleCheck /></el-icon></div>
          <div class="card-content">
            <div class="card-value">{{ dataCompleteness }}%</div>
            <div class="card-label">数据完整度</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 健康洞察 -->
    <el-row :gutter="20" class="insights-row">
      <el-col :span="24">
        <div class="card-container">
          <div class="card-header">
            <span class="card-title">智能洞察</span>
          </div>
          <div class="insights-grid">
            <div v-for="insight in insights" :key="insight.type" class="insight-card" :class="insight.status">
              <div class="insight-icon">
                <el-icon v-if="insight.type === 'data_quality'"><DataAnalysis /></el-icon>
                <el-icon v-else-if="insight.type === 'measurement_frequency'"><Stopwatch /></el-icon>
                <el-icon v-else-if="insight.type === 'trend'"><DataLine /></el-icon>
                <el-icon v-else><Warning /></el-icon>
              </div>
              <div class="insight-content">
                <div class="insight-title">{{ insight.title }}</div>
                <div class="insight-desc">{{ insight.description }}</div>
              </div>
              <el-tag :type="getInsightTagType(insight.status)" size="small">
                {{ getInsightStatus(insight.status) }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 健康指标分析 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="16">
        <div class="card-container">
          <div class="card-header">
            <span class="card-title">健康指标统计</span>
            <el-radio-group v-model="selectedMetric" size="small">
              <el-radio-button label="heart">心率</el-radio-button>
              <el-radio-button label="blood_pressure_systolic">血压(收缩)</el-radio-button>
              <el-radio-button label="blood_pressure_diastolic">血压(舒张)</el-radio-button>
              <el-radio-button label="blood_sugar">血糖</el-radio-button>
              <el-radio-button label="temperature">体温</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="metricChartRef" style="height: 350px"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="8">
        <div class="card-container">
          <div class="card-header">
            <span class="card-title">指标统计详情</span>
          </div>
          <div class="metric-details">
            <div v-if="currentMetricStats" class="stat-item">
              <div class="stat-label">平均值</div>
              <div class="stat-value">{{ currentMetricStats.avg }} {{ currentMetricStats.unit }}</div>
            </div>
            <div v-if="currentMetricStats" class="stat-item">
              <div class="stat-label">最小值</div>
              <div class="stat-value">{{ currentMetricStats.min }} {{ currentMetricStats.unit }}</div>
            </div>
            <div v-if="currentMetricStats" class="stat-item">
              <div class="stat-label">最大值</div>
              <div class="stat-value">{{ currentMetricStats.max }} {{ currentMetricStats.unit }}</div>
            </div>
            <div v-if="currentMetricStats" class="stat-item">
              <div class="stat-label">中位数</div>
              <div class="stat-value">{{ currentMetricStats.median }} {{ currentMetricStats.unit }}</div>
            </div>
            <div v-if="currentMetricStats" class="stat-item">
              <div class="stat-label">标准差</div>
              <div class="stat-value">{{ currentMetricStats.std }}</div>
            </div>
            <div v-if="currentMetricStats" class="stat-item">
              <div class="stat-label">异常率</div>
              <div class="stat-value" :class="{ danger: currentMetricStats.abnormal_rate > 20 }">
                {{ currentMetricStats.abnormal_rate }}%
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 趋势预测 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <div class="card-container">
          <div class="card-header">
            <span class="card-title">趋势预测</span>
            <el-select v-model="predictMetricType" size="small" style="width: 120px">
              <el-option label="心率" :value="4" />
              <el-option label="血压(收)" :value="2" />
              <el-option label="血压(舒)" :value="3" />
              <el-option label="血糖" :value="6" />
            </el-select>
          </div>
          <div ref="predictionChartRef" style="height: 300px"></div>
          <div class="prediction-info">
            <div class="prediction-item">
              <span class="label">趋势方向：</span>
              <el-tag :type="predictionTrend === 'rising' ? 'danger' : predictionTrend === 'falling' ? 'warning' : 'success'" size="small">
                {{ getTrendText(predictionTrend) }}
              </el-tag>
            </div>
            <div class="prediction-item">
              <span class="label">变化率：</span>
              <span>{{ predictionSlope > 0 ? '+' : '' }}{{ predictionSlope }}</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="card-container">
          <div class="card-header">
            <span class="card-title">风险评估</span>
          </div>
          <div class="risk-assessment">
            <div v-for="elder in riskAssessments" :key="elder.elder_id" class="risk-item" :class="elder.risk_level">
              <div class="risk-header">
                <span class="elder-name">{{ elder.elder_name }}</span>
                <el-tag :type="getRiskTagType(elder.risk_level)" size="small">
                  {{ getRiskLevelText(elder.risk_level) }}
                </el-tag>
              </div>
              <el-progress 
                :percentage="elder.risk_score" 
                :color="getRiskColor(elder.risk_score)"
                :stroke-width="10"
              />
              <div v-if="elder.risk_factors && elder.risk_factors.length > 0" class="risk-factors">
                <div v-for="(factor, idx) in elder.risk_factors.slice(0, 2)" :key="idx" class="factor-item">
                  {{ factor.factor }}: {{ factor.abnormal_rate }}%异常
                </div>
              </div>
            </div>
            <el-empty v-if="riskAssessments.length === 0" description="暂无风险评估数据" />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 活动模式分析 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="24">
        <div class="card-container">
          <div class="card-header">
            <span class="card-title">活动模式分析</span>
          </div>
          <el-row :gutter="20">
            <el-col :xs="24" :lg="12">
              <div ref="sleepChartRef" style="height: 250px"></div>
            </el-col>
            <el-col :xs="24" :lg="12">
              <div ref="stepsChartRef" style="height: 250px"></div>
            </el-col>
          </el-row>
        </div>
      </el-col>
    </el-row>

    <!-- 异常告警 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="24">
        <div class="card-container">
          <div class="card-header">
            <span class="card-title">异常告警</span>
            <el-badge :value="anomalyAlerts.length" :hidden="anomalyAlerts.length === 0">
              <el-button size="small">查看全部</el-button>
            </el-badge>
          </div>
          <div class="alerts-list">
            <div v-for="alert in anomalyAlerts.slice(0, 10)" :key="alert.id" class="alert-item" :class="alert.severity">
              <div class="alert-icon">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-title">
                  {{ alert.elder_name }} - {{ alert.metric_name }}异常
                </div>
                <div class="alert-desc">
                  检测值: {{ alert.value }} {{ alert.unit }} | 时间: {{ alert.recorded_at }}
                </div>
                <div class="alert-recommendation">{{ alert.recommendation }}</div>
              </div>
              <el-tag :type="alert.severity === 'critical' ? 'danger' : 'warning'" size="small">
                {{ alert.severity === 'critical' ? '紧急' : '警告' }}
              </el-tag>
            </div>
            <el-empty v-if="anomalyAlerts.length === 0" description="暂无异常告警，数据健康" />
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '@/store/auth'

// 数据
const selectedElderId = ref<number | null>(null)
const timeRange = ref(30)
const elderList = ref<any[]>([])
const insights = ref<any[]>([])
const anomalyAlerts = ref<any[]>([])
const riskAssessments = ref<any[]>([])
const healthAnalysis = ref<any>({})

// 统计数据
const healthScore = ref(85)
const totalRecords = ref(0)
const abnormalCount = ref(0)
const dataCompleteness = ref(0)
const scoreTrend = ref('stable')
const scoreTrendPercent = ref(0)

// 图表相关
const metricChartRef = ref<HTMLElement | null>(null)
const predictionChartRef = ref<HTMLElement | null>(null)
const sleepChartRef = ref<HTMLElement | null>(null)
const stepsChartRef = ref<HTMLElement | null>(null)
const selectedMetric = ref('heart')
const predictMetricType = ref(4)

// 图表实例
let metricChart: echarts.ECharts | null = null
let predictionChart: echarts.ECharts | null = null
let sleepChart: echarts.ECharts | null = null
let stepsChart: echarts.ECharts | null = null

// 预测数据
const predictionTrend = ref('stable')
const predictionSlope = ref(0)
const predictionData = ref<any[]>([])

// 当前选中指标的统计
const currentMetricStats = computed(() => {
  const metricMap: Record<string, { unit: string; type: number }> = {
    'heart': { unit: 'BPM', type: 4 },
    'blood_pressure_systolic': { unit: 'mmHg', type: 2 },
    'blood_pressure_diastolic': { unit: 'mmHg', type: 3 },
    'blood_sugar': { unit: 'mmol/L', type: 6 },
    'temperature': { unit: '°C', type: 1 }
  }
  
  const config = metricMap[selectedMetric.value]
  if (!config || !healthAnalysis.value) return null
  
  const key = ['心率', '血压-收缩压', '血压-舒张压', '心率', '血糖', '体温'][config.type]
  const data = healthAnalysis.value[key]
  
  if (!data) return null
  
  return {
    min: data.min,
    max: data.max,
    avg: data.avg,
    median: data.median,
    std: data.std,
    unit: config.unit,
    abnormal_rate: data.abnormal_rate || 0
  }
})

// 方法
const getInsightTagType = (status: string) => {
  const map: Record<string, string> = {
    'excellent': 'success',
    'good': 'primary',
    'warning': 'warning',
    'poor': 'danger'
  }
  return map[status] || 'info'
}

const getInsightStatus = (status: string) => {
  const map: Record<string, string> = {
    'excellent': '优秀',
    'good': '良好',
    'warning': '需注意',
    'poor': '需改进'
  }
  return map[status] || status
}

const getTrendText = (trend: string) => {
  const map: Record<string, string> = {
    'rising': '上升',
    'falling': '下降',
    'stable': '稳定'
  }
  return map[trend] || trend
}

const getRiskTagType = (level: string) => {
  const map: Record<string, string> = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'success'
  }
  return map[level] || 'info'
}

const getRiskLevelText = (level: string) => {
  const map: Record<string, string> = {
    'high': '高风险',
    'medium': '中风险',
    'low': '低风险'
  }
  return map[level] || level
}

const getRiskColor = (score: number) => {
  if (score >= 60) return '#f56c6c'
  if (score >= 30) return '#e6a23c'
  return '#67c23a'
}

// 加载老人列表
const loadElderList = async () => {
  try {
    const res: any = await api.get('/users/elder/list')
    if (res.code === 200) {
      elderList.value = res.data || []
      console.log('老人列表加载成功:', elderList.value)
    } else {
      console.warn('老人列表接口返回:', res)
    }
  } catch (error) {
    console.error('获取老人列表失败', error)
  }
}

// 加载所有数据
const loadAllData = async () => {
  try {
    const params = {
      elder_id: selectedElderId.value,
      days: timeRange.value
    }
    
    // 顺序加载数据（避免并发问题）
    try {
      const analysisRes = await api.get('/bigdata/health-analysis', { params })
      if (analysisRes.code === 200) {
        healthAnalysis.value = analysisRes.data || {}
        updateStatistics(analysisRes.data || {})
      } else {
        console.warn('健康分析接口返回:', analysisRes)
      }
    } catch (e) {
      console.error('健康分析加载失败:', e)
    }

    try {
      const insightRes = await api.get('/bigdata/health-insights', { params })
      if (insightRes.code === 200) {
        insights.value = insightRes.data || []
        // 更新数据完整度
        const completenessInsight = insights.value.find((i: any) => i.type === 'data_quality')
        if (completenessInsight) {
          dataCompleteness.value = completenessInsight.value
        } else {
          dataCompleteness.value = 100
        }
      } else {
        console.warn('智能洞察接口返回:', insightRes)
      }
    } catch (e) {
      console.error('智能洞察加载失败:', e)
    }

    try {
      const alertRes = await api.get('/bigdata/anomaly-alerts', { params })
      if (alertRes.code === 200) {
        anomalyAlerts.value = alertRes.data || []
        // 使用实际异常告警数量
        abnormalCount.value = anomalyAlerts.value.length
      } else {
        console.warn('异常告警接口返回:', alertRes)
      }
    } catch (e) {
      console.error('异常告警加载失败:', e)
    }
    
    try {
      const riskRes = await api.get('/bigdata/risk-assessment', { params })
      if (riskRes.code === 200) {
        riskAssessments.value = riskRes.data || []
      } else {
        console.warn('风险评估接口返回:', riskRes)
      }
    } catch (e) {
      console.error('风险评估加载失败:', e)
    }
    
    try {
      const activityRes = await api.get('/bigdata/activity-patterns', { params })
      if (activityRes.code === 200) {
        updateActivityCharts(activityRes.data || { daily_patterns: [] })
      } else {
        console.warn('活动模式接口返回:', activityRes)
      }
    } catch (e) {
      console.error('活动模式加载失败:', e)
    }
    
    try {
      const predictionParams = { 
        elder_id: selectedElderId.value,
        metric_type: predictMetricType.value,
        days: 14,
        predict_days: 7
      }
      const predictionRes = await api.get('/bigdata/health-prediction', { params: predictionParams })
      if (predictionRes.code === 200) {
        predictionTrend.value = predictionRes.data.trend || 'stable'
        predictionSlope.value = predictionRes.data.slope || 0
        predictionData.value = predictionRes.data
        updatePredictionChart(predictionRes.data || {})
      } else {
        console.warn('趋势预测接口返回:', predictionRes)
        // 即使预测失败也更新图表（显示暂无数据）
        updatePredictionChart({})
      }
    } catch (e) {
      console.error('趋势预测加载失败:', e)
      updatePredictionChart({})
    }
    
    updateMetricChart()
    ElMessage.success('数据加载完成')
    
  } catch (error) {
    console.error('加载数据失败', error)
    ElMessage.error('加载数据失败，请检查网络连接')
  }
}

// 更新统计数据
const updateStatistics = (data: any) => {
  totalRecords.value = Object.values(data).reduce((sum: number, metric: any) => sum + (metric.count || 0), 0)

  // 计算健康评分（基于异常率）
  let totalAbnormal = 0
  let totalCount = 0

  Object.values(data).forEach((metric: any) => {
    if (metric.abnormal_rate && metric.count) {
      totalAbnormal += metric.count * metric.abnormal_rate / 100
      totalCount += metric.count
    }
  })

  if (totalCount > 0) {
    healthScore.value = Math.max(0, Math.round(100 - totalAbnormal / totalCount * 100))
  } else {
    healthScore.value = 100 // 无数据时默认满分
  }
}

// 更新指标图表
const updateMetricChart = () => {
  if (!metricChartRef.value) return
  
  if (!metricChart) {
    metricChart = echarts.init(metricChartRef.value)
  }
  
  const metricMap: Record<string, string> = {
    'heart': '心率',
    'blood_pressure_systolic': '血压-收缩压',
    'blood_pressure_diastolic': '血压-舒张压',
    'blood_sugar': '血糖',
    'temperature': '体温'
  }
  
  const key = metricMap[selectedMetric.value]
  const metricData = healthAnalysis.value?.[key]
  
  // 检查是否有数据
  if (!metricData || !metricData.historical || metricData.historical.length === 0) {
    metricChart.setOption({
      title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#9aafc0' } },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: []
    })
    return
  }
  
  const dates = metricData.historical.map((h: any) => h.date)
  const values = metricData.historical.map((h: any) => h.value)
  
  metricChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: [key, '正常范围'], top: 10 },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45 }
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: key,
        type: 'line',
        smooth: true,
        data: values,
        areaStyle: { opacity: 0.3 },
        lineStyle: { width: 3 }
      },
      {
        name: '正常范围',
        type: 'line',
        data: Array(dates.length).fill(metricData.max || 37.3),
        lineStyle: { width: 1, type: 'dashed', color: '#67c23a' }
      },
      {
        name: '正常范围下限',
        type: 'line',
        data: Array(dates.length).fill(metricData.min || 36.0),
        lineStyle: { width: 1, type: 'dashed', color: '#67c23a' }
      }
    ]
  })
}

// 更新预测图表
const updatePredictionChart = (data: any) => {
  if (!predictionChartRef.value) {
    console.warn('预测图表容器不存在')
    return
  }
  
  try {
    if (!predictionChart) {
      predictionChart = echarts.init(predictionChartRef.value)
    }
    
    const historical = data?.historical || []
    const predictions = data?.predictions || []
    
    console.log('预测数据:', { historical, predictions })
    
    if (historical.length === 0 && predictions.length === 0) {
      predictionChart.setOption({
        title: { text: '暂无预测数据（请先选择老人）', left: 'center', top: 'center', textStyle: { color: '#9aafc0', fontSize: 14 } },
        xAxis: { type: 'category', data: [] },
        yAxis: { type: 'value' },
        series: []
      })
      return
    }
    
    const dates = [...historical.map((h: any) => h.date), ...predictions.map((p: any) => p.date)]
    const values = [...historical.map((h: any) => h.value), ...predictions.map((p: any) => p.predicted_value)]
    
    predictionChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['历史数据', '预测数据'], top: 10 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: { rotate: 45 }
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '历史数据',
          type: 'line',
          data: historical.map((h: any) => h.value),
          smooth: true,
          lineStyle: { width: 3, color: '#409eff' },
          areaStyle: { opacity: 0.2, color: '#409eff' }
        },
        {
          name: '预测数据',
          type: 'line',
          data: [...Array(historical.length).fill('-'), ...predictions.map((p: any) => p.predicted_value)],
          smooth: true,
          lineStyle: { width: 3, color: '#e6a23c', type: 'dashed' },
          itemStyle: { color: '#e6a23c' }
        }
      ]
    })
  } catch (error) {
    console.error('更新预测图表失败:', error)
  }
}

// 更新活动图表
const updateActivityCharts = (data: any) => {
  const dailyPatterns = data?.daily_patterns || []
  
  console.log('活动模式数据:', dailyPatterns)
  
  // 睡眠图表
  if (sleepChartRef.value) {
    if (!sleepChart) {
      sleepChart = echarts.init(sleepChartRef.value)
    }
    
    if (dailyPatterns.length === 0) {
      sleepChart.setOption({
        title: { text: '睡眠时长趋势（暂无数据）', left: 'center', top: 10, textStyle: { color: '#9aafc0', fontSize: 12 } },
        xAxis: { type: 'category', data: [] },
        yAxis: { type: 'value', name: '小时' },
        series: []
      })
    } else {
      sleepChart.setOption({
        title: { text: '睡眠时长趋势', left: 'center', top: 10 },
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: {
          type: 'category',
          data: dailyPatterns.map((p: any) => p.date?.slice(5) || '')
        },
        yAxis: { type: 'value', name: '小时' },
        series: [{
          type: 'bar',
          data: dailyPatterns.map((p: any) => ({
            value: p.avg_sleep || 0,
            itemStyle: {
              color: p.activity_level === 'high' ? '#67c23a' : 
                     p.activity_level === 'medium' ? '#e6a23c' : '#909399'
            }
          }))
        }]
      })
    }
  }
  
  // 步数图表
  if (stepsChartRef.value) {
    if (!stepsChart) {
      stepsChart = echarts.init(stepsChartRef.value)
    }
    
    if (dailyPatterns.length === 0) {
      stepsChart.setOption({
        title: { text: '每日步数趋势（暂无数据）', left: 'center', top: 10, textStyle: { color: '#9aafc0', fontSize: 12 } },
        xAxis: { type: 'category', data: [] },
        yAxis: { type: 'value', name: '步数' },
        series: []
      })
    } else {
      stepsChart.setOption({
        title: { text: '每日步数趋势', left: 'center', top: 10 },
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: {
          type: 'category',
          data: dailyPatterns.map((p: any) => p.date?.slice(5) || '')
        },
        yAxis: { type: 'value', name: '步数' },
        series: [{
          type: 'line',
          data: dailyPatterns.map((p: any) => p.avg_steps || 0),
          smooth: true,
          areaStyle: { opacity: 0.3 },
          lineStyle: { width: 3 }
        }]
      })
    }
  }
}

// 监听窗口变化
const handleResize = () => {
  metricChart?.resize()
  predictionChart?.resize()
  sleepChart?.resize()
  stepsChart?.resize()
}

// 监听选择变化
watch(selectedMetric, () => {
  updateMetricChart()
})

watch(predictMetricType, () => {
  loadAllData()
})

onMounted(async () => {
  await loadElderList()
  await loadAllData()
  
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
.bigdata-analytics {
  position: relative;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #0a0e14 0%, #12151c 50%, #0d1117 100%);

  &::before {
    content: '';
    position: fixed;
    top: -100%;
    left: -100%;
    width: 300%;
    height: 300%;
    background: 
      radial-gradient(ellipse at 30% 30%, rgba(103, 126, 234, 0.12) 0%, transparent 40%),
      radial-gradient(ellipse at 70% 70%, rgba(102, 126, 234, 0.08) 0%, transparent 40%),
      radial-gradient(ellipse at 50% 50%, rgba(103, 126, 234, 0.1) 0%, transparent 50%);
    animation: adminBgFloat 25s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
  }

  &::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: 
      linear-gradient(rgba(103, 126, 234, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(103, 126, 234, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: gridMove 20s linear infinite;
    pointer-events: none;
    z-index: 0;
  }

  @keyframes adminBgFloat {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    25% { transform: translate(2%, -2%) rotate(1deg); }
    50% { transform: translate(-2%, 2%) rotate(-1deg); }
    75% { transform: translate(1%, -1%) rotate(0.5deg); }
  }

  @keyframes gridMove {
    0% { background-position: 0 0; }
    100% { background-position: 50px 50px; }
  }
}

.page-header {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(103, 126, 234, 0.2);

  .page-title {
    font-size: 26px;
    font-weight: 700;
    color: #ffffff;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }

  .page-desc {
    font-size: 14px;
    color: #a8b4c4;
    margin-top: 4px;
  }

  .header-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.stats-row, .insights-row, .charts-row {
  position: relative;
  z-index: 1;
  margin-bottom: 20px;
}

.stats-card {
  position: relative;
  background: rgba(35, 45, 55, 0.95);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid rgba(103, 126, 234, 0.2);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.5, 1);
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transform: scaleX(0);
    transition: transform 0.3s ease;
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(103, 126, 234, 0.2);
    border-color: rgba(103, 126, 234, 0.4);

    &::before {
      transform: scaleX(1);
    }
  }

  .card-icon {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: #fff;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  }

  .card-content {
    flex: 1;

    .card-value {
      font-size: 32px;
      font-weight: 800;
      color: #ffffff;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    .card-label {
      font-size: 14px;
      color: #9aafc0;
      margin-top: 4px;
    }
  }

  .card-trend {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    font-weight: 600;

    &.up {
      color: #f56c6c;
    }

    &.down {
      color: #67c23a;
    }

    &.stable {
      color: #909399;
    }
  }

  &.score .card-icon {
    background: linear-gradient(135deg, #409eff, #66b1ff);
  }

  &.records .card-icon {
    background: linear-gradient(135deg, #67c23a, #85ce61);
  }

  &.alerts .card-icon {
    background: linear-gradient(135deg, #f56c6c, #fab6b6);
  }

  &.completeness .card-icon {
    background: linear-gradient(135deg, #e6a23c, #f3d19e);
  }
}

.card-container {
  position: relative;
  z-index: 1;
  background: rgba(35, 45, 55, 0.95);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(103, 126, 234, 0.2);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 12px 32px rgba(103, 126, 234, 0.15);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;

    .card-title {
      font-size: 17px;
      font-weight: 600;
      color: #ffffff;
      padding-left: 12px;
      border-left: 3px solid #409eff;
    }
  }
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;

  .insight-card {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 16px;
    background: rgba(30, 40, 50, 0.9);
    border-radius: 12px;
    border: 1px solid rgba(103, 126, 234, 0.15);
    transition: all 0.3s ease;

    &:hover {
      transform: translateX(8px);
      border-color: rgba(103, 126, 234, 0.4);
    }

    &.excellent {
      border-left: 3px solid #67c23a;
    }

    &.good {
      border-left: 3px solid #409eff;
    }

    &.warning {
      border-left: 3px solid #e6a23c;
    }

    &.poor {
      border-left: 3px solid #f56c6c;
    }

    .insight-icon {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(64, 158, 255, 0.2);
      color: #409eff;
      font-size: 20px;
      flex-shrink: 0;
    }

    .insight-content {
      flex: 1;

      .insight-title {
        font-size: 15px;
        font-weight: 600;
        color: #e8eef5;
        margin-bottom: 6px;
      }

      .insight-desc {
        font-size: 13px;
        color: #9aafc0;
        line-height: 1.5;
      }
    }
  }
}

.metric-details {
  .stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: rgba(30, 40, 50, 0.9);
    border-radius: 10px;
    margin-bottom: 10px;
    transition: all 0.3s ease;

    &:hover {
      background: rgba(40, 50, 60, 0.9);
      transform: translateX(4px);
    }

    .stat-label {
      font-size: 14px;
      color: #9aafc0;
    }

    .stat-value {
      font-size: 16px;
      font-weight: 600;
      color: #ffffff;

      &.danger {
        color: #f56c6c;
      }
    }
  }
}

.prediction-info {
  display: flex;
  gap: 20px;
  padding: 16px;
  background: rgba(30, 40, 50, 0.9);
  border-radius: 10px;
  margin-top: 16px;

  .prediction-item {
    display: flex;
    align-items: center;
    gap: 8px;

    .label {
      font-size: 14px;
      color: #9aafc0;
    }

    span:last-child {
      font-size: 15px;
      font-weight: 600;
      color: #ffffff;
    }
  }
}

.risk-assessment {
  .risk-item {
    padding: 16px;
    background: rgba(30, 40, 50, 0.9);
    border-radius: 12px;
    margin-bottom: 14px;
    border: 1px solid rgba(103, 126, 234, 0.15);
    transition: all 0.3s ease;

    &:hover {
      transform: translateX(4px);
      border-color: rgba(103, 126, 234, 0.4);
    }

    &.high {
      border-left: 3px solid #f56c6c;
    }

    &.medium {
      border-left: 3px solid #e6a23c;
    }

    &.low {
      border-left: 3px solid #67c23a;
    }

    .risk-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      .elder-name {
        font-size: 15px;
        font-weight: 600;
        color: #e8eef5;
      }
    }

    .risk-factors {
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid rgba(103, 126, 234, 0.1);

      .factor-item {
        font-size: 13px;
        color: #9aafc0;
        margin-bottom: 4px;

        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }
}

.alerts-list {
  .alert-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 16px;
    background: rgba(30, 40, 50, 0.9);
    border-radius: 12px;
    margin-bottom: 12px;
    border: 1px solid rgba(245, 108, 108, 0.2);
    transition: all 0.3s ease;

    &:hover {
      transform: translateX(8px);
      border-color: rgba(245, 108, 108, 0.4);
    }

    &.critical {
      background: rgba(245, 108, 108, 0.1);
      border-left: 3px solid #f56c6c;
    }

    &.warning {
      background: rgba(230, 162, 60, 0.1);
      border-left: 3px solid #e6a23c;
    }

    .alert-icon {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      flex-shrink: 0;
      color: #f56c6c;
      background: rgba(245, 108, 108, 0.2);
    }

    .alert-content {
      flex: 1;

      .alert-title {
        font-size: 15px;
        font-weight: 600;
        color: #e8eef5;
        margin-bottom: 6px;
      }

      .alert-desc {
        font-size: 13px;
        color: #9aafc0;
        margin-bottom: 6px;
      }

      .alert-recommendation {
        font-size: 13px;
        color: #e6a23c;
      }
    }
  }
}
</style>
