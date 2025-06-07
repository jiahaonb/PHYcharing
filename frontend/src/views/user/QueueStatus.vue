<template>
  <div class="queue-status">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>排队状态</span>
          <el-button @click="refreshStatus">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <div v-loading="loading">
        <div v-if="currentQueue">
          <el-alert
            :title="getStatusTitle()"
            :type="getStatusType()"
            :description="getStatusDescription()"
            show-icon
            :closable="false"
          />
          
          <div class="queue-info">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="充电桩">
                {{ currentQueue.pile_name }}
              </el-descriptions-item>
              <el-descriptions-item label="排队位置">
                第 {{ currentQueue.position }} 位
              </el-descriptions-item>
              <el-descriptions-item label="总排队人数">
                {{ currentQueue.total_in_queue }} 人
              </el-descriptions-item>
              <el-descriptions-item label="预计等待时间">
                {{ currentQueue.estimated_time }} 分钟
              </el-descriptions-item>
              <el-descriptions-item label="充电请求时间">
                {{ formatTime(currentQueue.request_time) }}
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getTagType(currentQueue.status)">
                  {{ getStatusText(currentQueue.status) }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
            
            <div class="action-buttons">
              <el-button 
                v-if="currentQueue.status === 'waiting'" 
                type="danger" 
                @click="cancelQueue"
              >
                取消排队
              </el-button>
              <el-button 
                v-if="currentQueue.status === 'charging'" 
                type="warning" 
                @click="stopCharging"
              >
                结束充电
              </el-button>
            </div>
          </div>
        </div>
        
        <div v-else>
          <el-alert
            title="当前没有排队"
            type="success"
            description="您当前没有在任何充电桩排队，请前往充电请求页面申请充电"
            show-icon
            :closable="false"
          />
          
          <div class="no-queue-actions">
            <el-button type="primary" @click="goToCharging">
              <el-icon><Lightning /></el-icon>
              申请充电
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Lightning } from '@element-plus/icons-vue'
import api from '@/utils/api'

const router = useRouter()
const currentQueue = ref(null)
const loading = ref(false)

// 获取当前用户的排队状态
const fetchQueueStatus = async () => {
  loading.value = true
  try {
    const response = await api.get('/users/queue/status')
    currentQueue.value = response.length > 0 ? response[0] : null
  } catch (error) {
    console.error('获取排队状态失败:', error)
    ElMessage.error('获取排队状态失败')
  } finally {
    loading.value = false
  }
}

// 刷新状态
const refreshStatus = () => {
  fetchQueueStatus()
  ElMessage.success('状态已刷新')
}

// 取消排队
const cancelQueue = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消排队吗？',
      '取消确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await api.delete(`/users/charging/cancel/${currentQueue.value.id}`)
    ElMessage.success('已取消排队')
    await fetchQueueStatus()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消排队失败:', error)
      ElMessage.error('取消排队失败')
    }
  }
}

// 结束充电
const stopCharging = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要结束充电吗？',
      '结束确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await api.post(`/users/charging/stop/${currentQueue.value.id}`)
    ElMessage.success('充电已结束')
    await fetchQueueStatus()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('结束充电失败:', error)
      ElMessage.error('结束充电失败')
    }
  }
}

// 跳转到充电申请页面
const goToCharging = () => {
  router.push('/user/charging')
}

// 获取状态标题
const getStatusTitle = () => {
  if (!currentQueue.value) return ''
  
  switch (currentQueue.value.status) {
    case 'waiting':
      return '您正在排队中'
    case 'charging':
      return '正在充电中'
    case 'completed':
      return '充电已完成'
    default:
      return '状态未知'
  }
}

// 获取状态类型
const getStatusType = () => {
  if (!currentQueue.value) return 'info'
  
  switch (currentQueue.value.status) {
    case 'waiting':
      return 'warning'
    case 'charging':
      return 'success'
    case 'completed':
      return 'info'
    default:
      return 'info'
  }
}

// 获取状态描述
const getStatusDescription = () => {
  if (!currentQueue.value) return ''
  
  switch (currentQueue.value.status) {
    case 'waiting':
      return `当前排在第${currentQueue.value.position}位，预计等待时间：${currentQueue.value.estimated_time}分钟`
    case 'charging':
      return `正在${currentQueue.value.pile_name}充电，开始时间：${formatTime(currentQueue.value.start_charging_time)}`
    case 'completed':
      return `充电已完成，总用时：${currentQueue.value.duration || '计算中'}分钟`
    default:
      return '状态信息获取中...'
  }
}

// 获取标签类型
const getTagType = (status) => {
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
    'waiting': '等待充电',
    'charging': '正在充电',
    'completed': '已完成'
  }
  return statusMap[status] || '未知'
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 页面挂载时获取数据
onMounted(() => {
  fetchQueueStatus()
})
</script>

<style scoped>
.queue-status {
  padding: 0;
  min-height: calc(100vh - 140px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.queue-info {
  margin-top: 20px;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
}

.no-queue-actions {
  margin-top: 20px;
  text-align: center;
}

/* 确保卡片有足够的高度 */
.el-card {
  min-height: 400px;
}
</style> 