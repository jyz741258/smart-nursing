<template>
  <div class="ai-chat-page">
    <AIChat style="height: calc(100vh - 120px)" />
  </div>
</template>

<script setup lang="ts">
import AIChat from '@/components/AIChat.vue'
</script>

<style scoped lang="scss">
.ai-chat-page {
  padding: 20px;
  height: 100%;
}
</style>