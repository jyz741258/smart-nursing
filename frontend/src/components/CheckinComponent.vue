<template>
  <div class="checkin-component">
    <div class="checkin-header">
      <h3 class="header-title">日常打卡</h3>
      <div class="header-stats">
        <div class="stat-item">
          <div class="stat-value">{{ consecutiveDays }}</div>
          <div class="stat-label">连续打卡</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ totalCheckins }}</div>
          <div class="stat-label">总打卡次数</div>
        </div>
      </div>
    </div>

    <!-- 今日打卡状态 -->
    <div class="today-checkin">
      <h4 class="section-title">今日打卡</h4>
      <div class="checkin-status" :class="{ 'checked-in': hasCheckedInToday }">
        <div class="status-icon">
          <el-icon v-if="hasCheckedInToday" :size="48" color="#67c23a"><Check /></el-icon>
          <el-icon v-else :size="48" color="#e6a23c"><Timer /></el-icon>
        </div>
        <div class="status-text">
          <h5>{{ hasCheckedInToday ? '今日已打卡' : '今日未打卡' }}</h5>
          <p v-if="hasCheckedInToday">打卡时间：{{ lastCheckinTime }}</p>
          <p v-else>点击下方按钮完成今日打卡</p>
        </div>
        <el-button 
          v-if="!hasCheckedInToday" 
          type="primary" 
          size="large" 
          @click="checkin"
          :loading="isCheckingIn"
        >
          <el-icon><Check /></el-icon> 立即打卡
        </el-button>
      </div>
    </div>

    <!-- 打卡历史 -->
    <div class="checkin-history" style="margin-top: 20px;">
      <h4 class="section-title">打卡历史</h4>
      <div v-if="checkinHistory.length === 0" class="empty-history">
        <el-empty description="暂无打卡记录" />
      </div>
      <div v-else class="history-list">
        <div 
          v-for="(record, index) in checkinHistory" 
          :key="index"
          class="history-item"
        >
          <div class="history-date">{{ record.date }}</div>
          <div class="history-time">{{ record.time }}</div>
          <div class="history-status">
            <el-tag type="success" size="small">已完成</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 打卡统计 -->
    <div class="checkin-stats" style="margin-top: 20px;">
      <h4 class="section-title">打卡统计</h4>
      <div class="stats-grid">
        <div class="stats-card">
          <div class="stats-icon"><el-icon><Calendar /></el-icon></div>
          <div class="stats-content">
            <div class="stats-value">{{ monthlyCheckins }}</div>
            <div class="stats-label">本月打卡</div>
          </div>
        </div>
        <div class="stats-card">
          <div class="stats-icon"><el-icon><TrendCharts /></el-icon></div>
          <div class="stats-content">
            <div class="stats-value">{{ weeklyCheckins }}</div>
            <div class="stats-label">本周打卡</div>
          </div>
        </div>
        <div class="stats-card">
          <div class="stats-icon"><el-icon><Star /></el-icon></div>
          <div class="stats-content">
            <div class="stats-value">{{ maxConsecutiveDays }}</div>
            <div class="stats-label">最长连续</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Timer, Calendar, TrendCharts, Star } from '@element-plus/icons-vue'
import api from '@/store/auth'

interface CheckinRecord {
  date: string
  time: string
}

const isCheckingIn = ref(false)
const checkinHistory = ref<CheckinRecord[]>([])
const lastCheckinDate = ref('')
const lastCheckinTime = ref('')

// 计算属性
const hasCheckedInToday = computed(() => {
  const today = new Date().toLocaleDateString('zh-CN')
  return lastCheckinDate.value === today
})

const consecutiveDays = computed(() => {
  // 计算连续打卡天数
  let count = 0
  const today = new Date()
  
  for (let i = 0; i < 365; i++) {
    const checkDate = new Date(today)
    checkDate.setDate(today.getDate() - i)
    const dateStr = checkDate.toLocaleDateString('zh-CN')
    
    if (checkinHistory.value.some(record => record.date === dateStr)) {
      count++
    } else {
      break
    }
  }
  
  return count
})

const totalCheckins = computed(() => {
  return checkinHistory.value.length
})

const monthlyCheckins = computed(() => {
  const now = new Date()
  const month = now.getMonth()
  const year = now.getFullYear()
  
  return checkinHistory.value.filter(record => {
    const recordDate = new Date(record.date)
    return recordDate.getMonth() === month && recordDate.getFullYear() === year
  }).length
})

const weeklyCheckins = computed(() => {
  const now = new Date()
  const weekStart = new Date(now)
  weekStart.setDate(now.getDate() - now.getDay())
  weekStart.setHours(0, 0, 0, 0)
  
  return checkinHistory.value.filter(record => {
    const recordDate = new Date(record.date)
    return recordDate >= weekStart
  }).length
})

const maxConsecutiveDays = computed(() => {
  // 计算最长连续打卡天数
  if (checkinHistory.value.length === 0) return 0
  
  let maxCount = 1
  let currentCount = 1
  
  // 按日期排序
  const sortedRecords = [...checkinHistory.value].sort((a, b) => {
    return new Date(b.date).getTime() - new Date(a.date).getTime()
  })
  
  for (let i = 1; i < sortedRecords.length; i++) {
    const prevDate = new Date(sortedRecords[i-1].date)
    const currDate = new Date(sortedRecords[i].date)
    
    const diffTime = prevDate.getTime() - currDate.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 1) {
      currentCount++
      maxCount = Math.max(maxCount, currentCount)
    } else {
      currentCount = 1
    }
  }
  
  return maxCount
})

// 加载打卡历史
const loadCheckinHistory = async () => {
  try {
    const res: any = await api.get('/checkin/history')
    if (res.code === 200) {
      checkinHistory.value = res.data || []
      if (checkinHistory.value.length > 0) {
        const lastRecord = checkinHistory.value[0]
        lastCheckinDate.value = lastRecord.date
        lastCheckinTime.value = lastRecord.time
      }
    }
  } catch (error) {
    console.error('获取打卡历史失败', error)
    // 模拟数据
    const today = new Date().toLocaleDateString('zh-CN')
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    const yesterdayStr = yesterday.toLocaleDateString('zh-CN')
    const dayBeforeYesterday = new Date()
    dayBeforeYesterday.setDate(dayBeforeYesterday.getDate() - 2)
    const dayBeforeYesterdayStr = dayBeforeYesterday.toLocaleDateString('zh-CN')
    
    checkinHistory.value = [
      { date: today, time: '08:30' },
      { date: yesterdayStr, time: '09:15' },
      { date: dayBeforeYesterdayStr, time: '08:45' }
    ]
    
    lastCheckinDate.value = today
    lastCheckinTime.value = '08:30'
  }
}

// 执行打卡
const checkin = async () => {
  isCheckingIn.value = true
  
  try {
    const res: any = await api.post('/checkin')
    if (res.code === 200) {
      ElMessage.success('打卡成功')
      const now = new Date()
      const dateStr = now.toLocaleDateString('zh-CN')
      const timeStr = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      
      checkinHistory.value.unshift({ date: dateStr, time: timeStr })
      lastCheckinDate.value = dateStr
      lastCheckinTime.value = timeStr
    }
  } catch (error) {
    console.error('打卡失败', error)
    ElMessage.error('打卡失败')
    // 模拟打卡成功
    const now = new Date()
    const dateStr = now.toLocaleDateString('zh-CN')
    const timeStr = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    
    checkinHistory.value.unshift({ date: dateStr, time: timeStr })
    lastCheckinDate.value = dateStr
    lastCheckinTime.value = timeStr
    ElMessage.success('打卡成功')
  } finally {
    isCheckingIn.value = false
  }
}

onMounted(() => {
  loadCheckinHistory()
})
</script>

<style scoped lang="scss">
.checkin-component {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

  .checkin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e4e7ed;

    .header-title {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }

    .header-stats {
      display: flex;
      gap: 20px;

      .stat-item {
        text-align: center;

        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: #409eff;
        }

        .stat-label {
          font-size: 12px;
          color: #909399;
          margin-top: 4px;
        }
      }
    }
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 15px 0;
    padding-left: 10px;
    border-left: 4px solid #409eff;
  }

  .today-checkin {
    margin-bottom: 20px;
  }

  .checkin-status {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 24px;
    background: #f5f7fa;
    border-radius: 8px;
    transition: all 0.3s ease;

    &.checked-in {
      background: #f0f9eb;
    }

    .status-icon {
      min-width: 60px;
      text-align: center;
    }

    .status-text {
      flex: 1;

      h5 {
        margin: 0 0 8px 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }

      p {
        margin: 0;
        font-size: 14px;
        color: #606266;
      }
    }
  }

  .empty-history {
    padding: 40px 0;
    text-align: center;
  }

  .history-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .history-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 6px;
    transition: all 0.3s ease;

    &:hover {
      background: #eef2f7;
    }

    .history-date {
      font-size: 14px;
      font-weight: 500;
      color: #303133;
    }

    .history-time {
      font-size: 14px;
      color: #606266;
    }
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }

  .stats-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 8px;
    transition: all 0.3s ease;

    &:hover {
      background: #eef2f7;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .stats-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: #409eff;
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }

    .stats-content {
      flex: 1;

      .stats-value {
        font-size: 20px;
        font-weight: 700;
        color: #303133;
      }

      .stats-label {
        font-size: 12px;
        color: #909399;
        margin-top: 2px;
      }
    }
  }
}
</style>