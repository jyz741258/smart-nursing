<template>
  <div class="home-container">
    <div class="home-content">
      <div class="hero-section">
        <h1 class="hero-title">智慧养老服务平台</h1>
        <p class="hero-subtitle">Smart Nursing Platform</p>
        <p class="hero-desc">为老年人提供专业、便捷的护理服务</p>
      </div>

      <div class="demo-section">
        <h2 class="section-title">体验演示账号</h2>
        <p class="section-desc">点击下方账号快速体验不同角色的功能</p>

        <div class="user-cards">
          <div
            v-for="user in demoUsers"
            :key="user.id"
            class="user-card"
            :class="user.role"
            @click="quickLogin(user)"
          >
            <div class="user-avatar">
              <el-icon :size="40"><UserFilled /></el-icon>
            </div>
            <div class="user-info">
              <h3 class="user-name">{{ user.name }}</h3>
              <p class="user-role">{{ user.roleName }}</p>
              <p class="user-phone">{{ user.phone }}</p>
              <p class="user-password">密码: {{ user.password }}</p>
            </div>
            <div class="user-features">
              <span v-for="feature in user.features" :key="feature" class="feature-tag">
                {{ feature }}
              </span>
            </div>
            <div class="login-hint">
              <el-icon><Pointer /></el-icon>
              <span>点击登录</span>
            </div>
          </div>
        </div>
      </div>

      <div class="info-section">
        <div class="info-card">
          <el-icon :size="32"><Clock /></el-icon>
          <h4>24小时服务</h4>
          <p>全天候在线预约与咨询</p>
        </div>
        <div class="info-card">
          <el-icon :size="32"><FirstAidKit /></el-icon>
          <h4>专业护理</h4>
          <p>持证护理人员上门服务</p>
        </div>
        <div class="info-card">
          <el-icon :size="32"><DataAnalysis /></el-icon>
          <h4>健康监测</h4>
          <p>实时记录健康数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { UserFilled, Pointer, Clock, FirstAidKit, DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/store/auth'

const demoUsers = [
  {
    id: 1,
    name: '张三',
    role: 'elder',
    roleName: '老人用户',
    phone: '13900001001',
    password: '123456',
    features: ['健康记录', '护理计划', '预约服务']
  },
  {
    id: 2,
    name: '李护理',
    role: 'nurse',
    roleName: '护理人员',
    phone: '13900001002',
    password: '123456',
    features: ['护理记录', '健康监测', '任务管理']
  },
  {
    id: 3,
    name: '系统管理员',
    role: 'admin',
    roleName: '管理员',
    phone: '13800138000',
    password: 'admin123',
    features: ['老人管理', '数据统计', '系统设置']
  }
]

const quickLogin = async (user: any) => {
  try {
    const res: any = await api.post('/users/login', {
      phone: user.phone,
      password: user.password
    })
    if (res.code === 200) {
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('userInfo', JSON.stringify(res.data))
      ElMessage.success(`以${user.roleName}身份登录成功`)
      window.location.href = '/dashboard'
    }
  } catch (error) {
    ElMessage.error('登录失败，请稍后重试')
  }
}
</script>

<style scoped lang="scss">
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.home-content {
  max-width: 1200px;
  width: 100%;
}

.hero-section {
  text-align: center;
  color: #fff;
  margin-bottom: 50px;

  .hero-title {
    font-size: 48px;
    font-weight: 700;
    margin-bottom: 10px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  }

  .hero-subtitle {
    font-size: 24px;
    opacity: 0.9;
    margin-bottom: 20px;
  }

  .hero-desc {
    font-size: 18px;
    opacity: 0.8;
  }
}

.demo-section {
  text-align: center;
  margin-bottom: 50px;

  .section-title {
    color: #fff;
    font-size: 28px;
    margin-bottom: 10px;
  }

  .section-desc {
    color: rgba(255, 255, 255, 0.8);
    font-size: 16px;
    margin-bottom: 30px;
  }
}

.user-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.user-card {
  background: #fff;
  border-radius: 20px;
  padding: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  &:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);

    .login-hint {
      opacity: 1;
      transform: translateY(0);
    }
  }

  &.elder {
    border: 3px solid #67c23a;
    .user-avatar { background: linear-gradient(135deg, #67c23a, #85ce61); }
  }

  &.nurse {
    border: 3px solid #409eff;
    .user-avatar { background: linear-gradient(135deg, #409eff, #66b1ff); }
  }

  &.admin {
    border: 3px solid #e6a23c;
    .user-avatar { background: linear-gradient(135deg, #e6a23c, #ebb563); }
  }

  .user-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin: 0 auto 20px;
  }

  .user-info {
    text-align: center;
    margin-bottom: 15px;

    .user-name {
      font-size: 22px;
      color: #303133;
      margin-bottom: 5px;
    }

    .user-role {
      font-size: 14px;
      color: #909399;
      margin-bottom: 10px;
    }

    .user-phone, .user-password {
      font-size: 12px;
      color: #c0c4cc;
    }
  }

  .user-features {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;

    .feature-tag {
      background: #f4f4f5;
      color: #606266;
      padding: 4px 12px;
      border-radius: 15px;
      font-size: 12px;
    }
  }

  .login-hint {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(102, 126, 234, 0.95), transparent);
    color: #fff;
    padding: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 14px;
    opacity: 0;
    transform: translateY(100%);
    transition: all 0.3s ease;
  }
}

.info-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;

  .info-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 30px;
    text-align: center;
    color: #fff;

    h4 {
      font-size: 18px;
      margin: 15px 0 10px;
    }

    p {
      font-size: 14px;
      opacity: 0.8;
    }
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px !important;
  }

  .info-section {
    grid-template-columns: 1fr;
  }
}
</style>