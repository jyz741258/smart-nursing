<template>
  <div class="health-management">
    <div class="page-header">
      <h2 class="page-title">健康管理</h2>
      <p class="page-desc">管理您的用药提醒和日常打卡</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <MedicationReminder />
      </el-col>
      <el-col :span="12">
        <CheckinComponent />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import MedicationReminder from '@/components/MedicationReminder.vue'
import CheckinComponent from '@/components/CheckinComponent.vue'
</script>

<style scoped lang="scss">
.health-management {
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);

  .page-header {
    margin-bottom: 30px;
    text-align: center;

    .page-title {
      font-size: 24px;
      font-weight: 700;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .page-desc {
      font-size: 14px;
      color: #606266;
      margin: 0;
    }
  }
}

@media (max-width: 768px) {
  .health-management {
    padding: 10px;
  }

  .el-row {
    flex-direction: column;
  }

  .el-col {
    width: 100% !important;
    margin-bottom: 20px;
  }
}
</style>