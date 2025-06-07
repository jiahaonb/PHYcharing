<template>
  <div class="system-clock">
    <div class="clock-container">
      <el-icon><Clock /></el-icon>
      <span class="time-text">{{ currentTime }}</span>
      <span class="date-text">{{ currentDate }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Clock } from '@element-plus/icons-vue'

const currentTime = ref('')
const currentDate = ref('')
let timer = null

const updateTime = () => {
  const now = new Date()
  
  // 格式化时间（24小时制）
  currentTime.value = now.toLocaleTimeString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
  
  // 格式化日期
  currentDate.value = now.toLocaleDateString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    weekday: 'short'
  })
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
.system-clock {
  display: flex;
  align-items: center;
}

.clock-container {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.time-text {
  font-size: 16px;
  font-family: 'Courier New', monospace;
  letter-spacing: 1px;
}

.date-text {
  font-size: 14px;
  opacity: 0.9;
}

.clock-container .el-icon {
  font-size: 18px;
}
</style> 