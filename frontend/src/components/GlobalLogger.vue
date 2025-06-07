<template>
  <div class="global-logger" :class="{ 'collapsed': collapsed }">
    <div class="logger-header" @click="toggleCollapse">
      <span class="logger-title">
        <el-icon><Monitor /></el-icon>
        系统日志
      </span>
      <span class="logger-controls">
        <el-button size="small" text @click.stop="clearLogs">
          <el-icon><Delete /></el-icon>
        </el-button>
        <el-button size="small" text @click.stop="toggleCollapse">
          <el-icon v-if="collapsed"><ArrowUp /></el-icon>
          <el-icon v-else><ArrowDown /></el-icon>
        </el-button>
      </span>
    </div>
    
    <div v-show="!collapsed" class="logger-content">
      <div 
        ref="logContainer" 
        class="log-container"
      >
        <div 
          v-for="(log, index) in logs" 
          :key="index"
          class="log-item"
          :class="getLogClass(log.level)"
        >
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span class="log-level">{{ log.level.toUpperCase() }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { Monitor, Delete, ArrowUp, ArrowDown } from '@element-plus/icons-vue'

const collapsed = ref(false)
const logs = reactive([])
const logContainer = ref()
const maxLogs = 100

// 存储原始的console方法
const originalConsole = {
  log: console.log,
  warn: console.warn,
  error: console.error,
  info: console.info,
  debug: console.debug
}

const addLog = (level, message) => {
  const timestamp = new Date()
  
  // 处理对象和数组
  let formattedMessage
  if (typeof message === 'object') {
    try {
      formattedMessage = JSON.stringify(message, null, 2)
    } catch (e) {
      formattedMessage = String(message)
    }
  } else {
    formattedMessage = String(message)
  }
  
  logs.push({
    level,
    message: formattedMessage,
    timestamp
  })
  
  // 限制日志数量
  if (logs.length > maxLogs) {
    logs.shift()
  }
  
  // 自动滚动到底部
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

const interceptConsole = () => {
  console.log = (...args) => {
    originalConsole.log.apply(console, args)
    addLog('info', args.join(' '))
  }
  
  console.warn = (...args) => {
    originalConsole.warn.apply(console, args)
    // 不记录warn日志到界面，只输出到原始console
  }
  
  console.error = (...args) => {
    originalConsole.error.apply(console, args)
    addLog('error', args.join(' '))
  }
  
  console.info = (...args) => {
    originalConsole.info.apply(console, args)
    addLog('info', args.join(' '))
  }
  
  console.debug = (...args) => {
    originalConsole.debug.apply(console, args)
    // 不记录debug日志到界面，只输出到原始console
  }
}

const restoreConsole = () => {
  console.log = originalConsole.log
  console.warn = originalConsole.warn
  console.error = originalConsole.error
  console.info = originalConsole.info
  console.debug = originalConsole.debug
}

const toggleCollapse = () => {
  collapsed.value = !collapsed.value
}

const clearLogs = () => {
  logs.splice(0, logs.length)
}

const formatTime = (timestamp) => {
  return timestamp.toLocaleTimeString('zh-CN', { 
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getLogClass = (level) => {
  return `log-${level}`
}

onMounted(() => {
  interceptConsole()
  // 添加一条初始日志
  addLog('info', '系统日志监控已启动')
})

onUnmounted(() => {
  restoreConsole()
})
</script>

<style scoped>
.global-logger {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.9);
  border-top: 1px solid #333;
  z-index: 9999;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  transition: all 0.3s ease;
}

.global-logger.collapsed {
  height: 32px;
  overflow: hidden;
}

.logger-header {
  height: 32px;
  padding: 8px 12px;
  background: #2c3e50;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.logger-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: bold;
}

.logger-controls {
  display: flex;
  gap: 4px;
}

.logger-content {
  height: 150px;
  overflow: hidden;
}

.log-container {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
  background: #1e1e1e;
}

.log-item {
  display: flex;
  gap: 8px;
  margin-bottom: 2px;
  word-break: break-all;
  white-space: pre-wrap;
}

.log-time {
  color: #666;
  min-width: 60px;
}

.log-level {
  min-width: 50px;
  font-weight: bold;
}

.log-message {
  flex: 1;
  color: #ccc;
}

.log-info .log-level {
  color: #5dade2;
}

.log-error .log-level {
  color: #e74c3c;
}

/* 滚动条样式 */
.log-container::-webkit-scrollbar {
  width: 6px;
}

.log-container::-webkit-scrollbar-track {
  background: #2c3e50;
}

.log-container::-webkit-scrollbar-thumb {
  background: #34495e;
  border-radius: 3px;
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: #4a6fa5;
}
</style> 