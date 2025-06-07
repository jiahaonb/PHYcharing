<template>
  <div class="dashboard">
    <h1>用户仪表板</h1>
    
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#409eff"><Lightning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalCharging }}</div>
              <div class="stat-label">总充电次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#67c23a"><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalDuration.toFixed(1) }}h</div>
              <div class="stat-label">总充电时长</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#e6a23c"><Coin /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">¥{{ stats.totalFee.toFixed(2) }}</div>
              <div class="stat-label">总消费金额</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#f56c6c"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.queueCount }}</div>
              <div class="stat-label">当前排队数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="content-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>当前排队状态</span>
              <el-button type="primary" @click="refreshQueue">刷新</el-button>
            </div>
          </template>
          
          <div v-if="queueList.length === 0" class="empty-state">
            <el-empty description="暂无排队记录" />
          </div>
          
          <div v-else>
            <div v-for="queue in queueList" :key="queue.id" class="queue-item">
              <div class="queue-info">
                <div class="queue-number">{{ queue.queue_number }}</div>
                <div class="queue-details">
                  <div>充电模式: {{ queue.charging_mode === 'fast' ? '快充' : '慢充' }}</div>
                  <div>请求电量: {{ queue.requested_amount }}度</div>
                  <div>状态: {{ getStatusText(queue.status) }}</div>
                </div>
              </div>
              <div class="queue-actions">
                <el-button size="small" @click="viewQueue(queue.id)">查看详情</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近充电记录</span>
              <router-link to="/user/records">
                <el-button type="text">查看全部</el-button>
              </router-link>
            </div>
          </template>
          
          <div v-if="recentRecords.length === 0" class="empty-state">
            <el-empty description="暂无充电记录" />
          </div>
          
          <div v-else>
            <div v-for="record in recentRecords" :key="record.id" class="record-item">
              <div class="record-info">
                <div class="record-number">{{ record.record_number }}</div>
                <div class="record-details">
                  <div>充电量: {{ record.charging_amount }}度</div>
                  <div>费用: ¥{{ record.total_fee.toFixed(2) }}</div>
                  <div>时间: {{ formatDate(record.start_time) }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const stats = reactive({
  totalCharging: 0,
  totalDuration: 0,
  totalFee: 0,
  queueCount: 0
})

const queueList = ref([])
const recentRecords = ref([])

const getStatusText = (status) => {
  const statusMap = {
    waiting: '等候区等待',
    queuing: '充电区排队',
    charging: '正在充电',
    completed: '充电完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const fetchStats = async () => {
  try {
    // 获取充电记录统计
    const records = await api.get('/charging/records')
    stats.totalCharging = records.length
    stats.totalDuration = records.reduce((sum, record) => sum + record.charging_duration, 0)
    stats.totalFee = records.reduce((sum, record) => sum + record.total_fee, 0)
    
    // 获取最近记录
    recentRecords.value = records.slice(0, 5)
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const fetchQueue = async () => {
  try {
    const queue = await api.get('/charging/queue')
    queueList.value = queue
    stats.queueCount = queue.length
  } catch (error) {
    console.error('获取排队状态失败:', error)
  }
}

const refreshQueue = () => {
  fetchQueue()
  ElMessage.success('排队状态已刷新')
}

const viewQueue = (queueId) => {
  // 跳转到排队详情
  console.log('查看排队详情:', queueId)
}

onMounted(() => {
  fetchStats()
  fetchQueue()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.content-row {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.queue-item, .record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.queue-item:last-child, .record-item:last-child {
  border-bottom: none;
}

.queue-number, .record-number {
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.queue-details, .record-details {
  font-size: 14px;
  color: #666;
}

.queue-details div, .record-details div {
  margin-bottom: 2px;
}
</style> 