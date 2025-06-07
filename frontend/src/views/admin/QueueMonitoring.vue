<template>
  <div class="queue-monitoring">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>队列监控</span>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <!-- 队列概览统计 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ queueSummary.total_queues }}</div>
              <div class="stat-label">总排队人数</div>
            </div>
            <el-icon class="stat-icon"><UserFilled /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ queueSummary.charging_count }}</div>
              <div class="stat-label">正在充电</div>
            </div>
            <el-icon class="stat-icon"><Lightning /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ queueSummary.waiting_count }}</div>
              <div class="stat-label">等待充电</div>
            </div>
            <el-icon class="stat-icon"><Clock /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ queueSummary.avg_wait_time }}min</div>
              <div class="stat-label">平均等待时间</div>
            </div>
            <el-icon class="stat-icon"><Timer /></el-icon>
          </el-card>
        </el-col>
      </el-row>

      <!-- 各充电桩队列状态 -->
      <div class="pile-queues">
        <h3>各充电桩队列状态</h3>
        <el-row :gutter="20">
          <el-col :span="12" v-for="pileQueue in pileQueues" :key="pileQueue.pile_id">
            <el-card class="pile-queue-card">
              <template #header>
                <div class="pile-header">
                  <span class="pile-name">{{ pileQueue.pile_name }}</span>
                  <el-tag :type="getPileStatusType(pileQueue.pile_status)">
                    {{ getPileStatusText(pileQueue.pile_status) }}
                  </el-tag>
                </div>
              </template>
              
              <div class="queue-content">
                <div class="queue-stats">
                  <div class="stat-item">
                    <span class="label">排队人数:</span>
                    <span class="value">{{ pileQueue.queue_length }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="label">当前用户:</span>
                    <span class="value">{{ pileQueue.current_user || '无' }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="label">预计等待:</span>
                    <span class="value">{{ pileQueue.estimated_wait_time }}分钟</span>
                  </div>
                </div>
                
                <!-- 队列详情 -->
                <div v-if="pileQueue.queue_details && pileQueue.queue_details.length > 0" class="queue-details">
                  <h4>排队详情</h4>
                  <el-table :data="pileQueue.queue_details" size="small">
                    <el-table-column prop="position" label="位置" width="60" />
                    <el-table-column prop="username" label="用户" width="100" />
                    <el-table-column prop="vehicle_info" label="车辆" width="120" />
                    <el-table-column prop="request_time" label="请求时间" width="120">
                      <template #default="scope">
                        {{ formatTime(scope.row.request_time) }}
                      </template>
                    </el-table-column>
                    <el-table-column prop="status" label="状态" width="80">
                      <template #default="scope">
                        <el-tag size="small" :type="getStatusType(scope.row.status)">
                          {{ getStatusText(scope.row.status) }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
                
                <div v-else class="no-queue">
                  <el-empty description="当前无人排队" :image-size="60" />
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 实时队列变化日志 -->
      <div class="queue-logs">
        <h3>实时队列变化</h3>
        <el-table :data="queueLogs" style="width: 100%; max-height: 300px" v-loading="loading">
          <el-table-column prop="timestamp" label="时间" width="120">
            <template #default="scope">
              {{ formatTime(scope.row.timestamp) }}
            </template>
          </el-table-column>
          <el-table-column prop="pile_name" label="充电桩" width="120" />
          <el-table-column prop="user" label="用户" width="100" />
          <el-table-column prop="action" label="动作" width="100">
            <template #default="scope">
              <el-tag size="small" :type="getActionType(scope.row.action)">
                {{ scope.row.action }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, UserFilled, Lightning, Clock, Timer } from '@element-plus/icons-vue'
import api from '@/utils/api'

const loading = ref(false)
const queueSummary = ref({
  total_queues: 0,
  charging_count: 0,
  waiting_count: 0,
  avg_wait_time: 0
})
const pileQueues = ref([])
const queueLogs = ref([])
let refreshTimer = null

// 获取队列监控数据
const fetchQueueData = async () => {
  loading.value = true
  try {
    // 获取队列概览
    const summary = await api.get('/admin/queue/summary')
    queueSummary.value = summary

    // 获取各充电桩队列状态
    const queues = await api.get('/admin/queue/piles')
    pileQueues.value = queues

    // 获取队列变化日志
    const logs = await api.get('/admin/queue/logs')
    queueLogs.value = logs.slice(0, 20) // 只显示最近20条
  } catch (error) {
    console.error('获取队列数据失败:', error)
    ElMessage.error('获取队列数据失败')
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  fetchQueueData()
  ElMessage.success('数据已刷新')
}

// 获取充电桩状态类型
const getPileStatusType = (status) => {
  const statusMap = {
    'normal': 'success',
    'charging': 'warning',
    'fault': 'danger',
    'maintenance': 'info'
  }
  return statusMap[status] || 'info'
}

// 获取充电桩状态文本
const getPileStatusText = (status) => {
  const statusMap = {
    'normal': '空闲',
    'charging': '充电中',
    'fault': '故障',
    'maintenance': '维护中'
  }
  return statusMap[status] || '未知'
}

// 获取状态类型
const getStatusType = (status) => {
  const statusMap = {
    'waiting': 'warning',
    'charging': 'success',
    'completed': 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'waiting': '等待',
    'charging': '充电中',
    'completed': '已完成'
  }
  return statusMap[status] || '未知'
}

// 获取动作类型
const getActionType = (action) => {
  const actionMap = {
    '加入队列': 'success',
    '开始充电': 'warning',
    '完成充电': 'info',
    '取消排队': 'danger'
  }
  return actionMap[action] || 'info'
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchQueueData()
  
  // 设置定时刷新（每30秒）
  refreshTimer = setInterval(() => {
    fetchQueueData()
  }, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.queue-monitoring {
  padding: 0;
  min-height: calc(100vh - 140px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-content {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.stat-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 40px;
  color: #e6e6e6;
}

.pile-queues {
  margin-bottom: 30px;
}

.pile-queues h3 {
  margin-bottom: 15px;
  color: #333;
}

.pile-queue-card {
  margin-bottom: 15px;
  min-height: 200px;
}

.pile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pile-name {
  font-weight: bold;
  font-size: 16px;
}

.queue-content {
  padding: 10px 0;
}

.queue-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 5px;
}

.stat-item {
  text-align: center;
}

.stat-item .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.stat-item .value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.queue-details h4 {
  margin-bottom: 10px;
  color: #666;
  font-size: 14px;
}

.no-queue {
  text-align: center;
  padding: 20px;
}

.queue-logs h3 {
  margin-bottom: 15px;
  color: #333;
}
</style> 