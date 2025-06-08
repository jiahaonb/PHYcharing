<template>
  <div class="monitoring">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>充电桩监控</span>
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <!-- 实时状态卡片 -->
      <el-row :gutter="20" class="status-cards">
        <el-col :span="6" v-for="pile in pileStatus" :key="pile.id">
          <el-card class="pile-card" :class="getPileCardClass(pile.status)">
            <div class="pile-info">
              <div class="pile-header">
                <h3>{{ pile.name }}</h3>
                <el-tag :type="getStatusType(pile.status)">
                  {{ getStatusText(pile.status) }}
                </el-tag>
              </div>
              
              <div class="pile-details">
                <div class="detail-item">
                  <span class="label">功率:</span>
                  <span class="value">{{ pile.power }} kW</span>
                </div>
                <div class="detail-item">
                  <span class="label">电压:</span>
                  <span class="value">{{ pile.voltage }} V</span>
                </div>
                <div class="detail-item">
                  <span class="label">电流:</span>
                  <span class="value">{{ pile.current }} A</span>
                </div>
                <div class="detail-item" v-if="pile.user">
                  <span class="label">用户:</span>
                  <span class="value">{{ pile.user }}</span>
                </div>
                <div class="detail-item" v-if="pile.startTime">
                  <span class="label">开始时间:</span>
                  <span class="value">{{ pile.startTime }}</span>
                </div>
              </div>
              
              <div class="pile-actions" v-if="pile.status === 'charging'">
                <el-button size="small" type="warning" @click="stopCharging(pile.id)">
                  停止充电
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 实时图表 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>实时功率监控</span>
            </template>
            <div ref="powerChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>排队状况</span>
            </template>
            <div class="queue-status">
              <div class="queue-item" v-for="queue in queueData" :key="queue.pileId">
                <div class="queue-header">
                  <el-tooltip effect="dark" placement="top-start" :disabled="queue.queueDetails.length === 0">
                    <template #content>
                      <div v-if="queue.queueDetails.length > 0">
                        <div style="font-weight: bold; margin-bottom: 5px;">排队详情:</div>
                        <div v-for="detail in queue.queueDetails.slice(0, 5)" :key="detail.queue_id" style="margin-bottom: 3px;">
                          第{{ detail.position }}位: {{ detail.username }} ({{ detail.vehicle_info }})
                        </div>
                        <div v-if="queue.queueDetails.length > 5" style="color: #909399;">
                          还有{{ queue.queueDetails.length - 5 }}人...
                        </div>
                      </div>
                    </template>
                    <span style="cursor: pointer;">{{ queue.pileName }}</span>
                  </el-tooltip>
                  <div class="queue-tags">
                    <el-tag size="small" :type="getQueueStatusType(queue.queueLength)">
                      {{ queue.queueLength }}人排队
                    </el-tag>
                    <el-tag size="small" :type="getStatusType(queue.pileStatus)" style="margin-left: 5px;">
                      {{ getStatusText(queue.pileStatus) }}
                    </el-tag>
                  </div>
                </div>
                <el-progress 
                  :percentage="Math.min((queue.queueLength / 5) * 100, 100)" 
                  :status="queue.queueLength > 3 ? 'exception' : queue.queueLength > 1 ? 'warning' : 'success'"
                />
                <div class="queue-info">
                  <small style="color: #909399;">
                    当前车辆: {{ queue.currentVehicle || '无数据' }}
                    <span v-if="queue.currentUser" style="margin-left: 10px;">
                      当前用户: {{ queue.currentUser }}
                    </span>
                    <span v-else style="margin-left: 10px;">
                      当前用户: 无数据
                    </span>
                    <span v-if="queue.queueLength > 0" style="margin-left: 10px;">
                      预计等待: {{ Math.round(queue.estimatedWaitTime) }}分钟
                    </span>
                    <span v-else style="margin-left: 10px;">
                      预计等待: 0分钟
                    </span>
                  </small>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 警报信息 -->
      <el-row style="margin-top: 20px;">
        <el-col :span="24">
          <el-card>
            <template #header>
              <span>系统警报</span>
            </template>
            <el-table :data="alerts" style="width: 100%">
              <el-table-column prop="time" label="时间" width="150" />
              <el-table-column prop="type" label="类型" width="100">
                <template #default="scope">
                  <el-tag :type="getAlertType(scope.row.level)">
                    {{ scope.row.type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="pile" label="充电桩" width="120" />
              <el-table-column prop="message" label="警报信息" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 'resolved' ? 'success' : 'danger'">
                    {{ scope.row.status === 'resolved' ? '已解决' : '待处理' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/utils/api'

const powerChart = ref()
const loading = ref(false)
let refreshTimer = null
let chartInstance = null

const pileStatus = ref([])
const queueData = ref([])
const alerts = ref([])

// 历史功率数据（用于图表）
const powerHistory = ref([])

const getStatusType = (status) => {
  const statusMap = {
    'charging': 'success',
    'idle': 'info',
    'fault': 'danger',
    'maintenance': 'warning'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'normal': '空闲',
    'idle': '空闲',
    'charging': '充电中',
    'fault': '故障',
    'maintenance': '维护中'
  }
  return statusMap[status] || `未知(${status})`
}

const getPileCardClass = (status) => {
  return {
    'pile-charging': status === 'charging',
    'pile-idle': status === 'idle',
    'pile-fault': status === 'fault',
    'pile-maintenance': status === 'maintenance'
  }
}

const getAlertType = (level) => {
  const typeMap = {
    'error': 'danger',
    'warning': 'warning',
    'info': 'info'
  }
  return typeMap[level] || 'info'
}

const getQueueStatusType = (queueLength) => {
  if (queueLength === 0) return 'info'
  if (queueLength <= 1) return 'success'
  if (queueLength <= 3) return 'warning'
  return 'danger'
}

// API调用函数
const fetchMonitoringData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchPileStatus(),
      fetchQueueData(),
      fetchAlerts()
    ])
  } catch (error) {
    console.error('获取监控数据失败:', error)
    ElMessage.error('获取监控数据失败')
  } finally {
    loading.value = false
  }
}

const fetchPileStatus = async () => {
  try {
    const piles = await api.get('/admin/piles')
    
    // 转换数据格式并添加实时数据
    pileStatus.value = await Promise.all(piles.map(async (pile) => {
      const currentPower = generateRealtimePower(pile)
      const currentCurrent = generateRealtimeCurrent(pile)
      
      // 尝试获取当前用户信息（如果有的话）
      let currentUser = null
      let startTime = null
      
      try {
        const queueInfo = await api.get(`/admin/piles/${pile.id}/queue`)
        const chargingQueue = queueInfo.find(q => q.status === 'charging')
        if (chargingQueue) {
          // 这里可以获取用户信息，但需要额外的API
          currentUser = `用户${chargingQueue.user_id}`
          startTime = new Date(chargingQueue.start_charging_time).toLocaleTimeString('zh-CN', { hour12: false })
        }
      } catch (error) {
        // 忽略错误，继续处理
      }
      
      return {
        id: pile.pile_number,
        name: `${pile.charging_mode === 'fast' ? '快充桩' : '慢充桩'}-${pile.pile_number}`,
        status: pile.status,
        power: currentPower,
        voltage: pile.charging_mode === 'fast' ? 380 : 220,
        current: currentCurrent,
        user: currentUser,
        startTime: startTime,
        originalId: pile.id,
        ...pile
      }
    }))
    
    // 更新功率历史数据
    updatePowerHistory()
  } catch (error) {
    console.error('获取充电桩状态失败:', error)
  }
}

const fetchQueueData = async () => {
  try {
    // 使用正确的API端点获取各充电桩的队列状态
    const pileQueues = await api.get('/admin/queue/piles')
    
    queueData.value = pileQueues.map((pileQueue) => {
      // 获取当前充电中的车辆信息
      let currentVehicle = '无数据'
      let currentUser = '无数据'
      
      if (pileQueue.queue_details && pileQueue.queue_details.length > 0) {
        // 找到正在充电的车辆（状态为charging的排在第一位）
        const chargingVehicle = pileQueue.queue_details.find(detail => detail.status === 'charging')
        if (chargingVehicle) {
          currentVehicle = chargingVehicle.vehicle_info || '无数据'
          currentUser = chargingVehicle.username || '无数据'
        } else if (pileQueue.current_user) {
          // 如果没有找到charging状态的，但有current_user，使用current_user
          currentUser = pileQueue.current_user
          // 尝试从队列中找到对应的车辆信息
          const firstInQueue = pileQueue.queue_details[0]
          if (firstInQueue) {
            currentVehicle = firstInQueue.vehicle_info || '无数据'
          }
        }
      } else if (pileQueue.current_user) {
        currentUser = pileQueue.current_user
      }
      
      return {
        pileId: pileQueue.pile_name.split('-')[1] || pileQueue.pile_id, // 提取桩编号
        pileName: pileQueue.pile_name,
        queueLength: pileQueue.queue_length,
        chargingMode: pileQueue.pile_name.includes('快充') ? 'fast' : 'trickle',
        pileStatus: pileQueue.pile_status,
        currentUser: currentUser,
        currentVehicle: currentVehicle,
        estimatedWaitTime: pileQueue.estimated_wait_time,
        queueDetails: pileQueue.queue_details || []
      }
    })
    
    console.log('排队数据已更新:', queueData.value)
  } catch (error) {
    console.error('获取队列数据失败:', error)
    // 如果获取失败，尝试备用方案
    try {
      const piles = await api.get('/admin/piles')
      queueData.value = piles.map((pile) => ({
        pileId: pile.pile_number,
        pileName: `${pile.charging_mode === 'fast' ? '快充桩' : '慢充桩'}-${pile.pile_number}`,
        queueLength: 0,
        chargingMode: pile.charging_mode,
        pileStatus: pile.status,
        currentUser: '无数据',
        currentVehicle: '无数据',
        estimatedWaitTime: 0,
        queueDetails: []
      }))
      console.log('使用备用数据:', queueData.value)
    } catch (fallbackError) {
      console.error('备用数据获取也失败:', fallbackError)
      queueData.value = []
    }
  }
}

const fetchAlerts = async () => {
  const currentTime = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  const faultPiles = pileStatus.value.filter(p => p.status === 'fault')
  const busyQueues = queueData.value.filter(q => q.queueLength > 3)
  const offlinePiles = pileStatus.value.filter(p => p.status === 'offline')
  
  alerts.value = [
    // 故障警报
    ...faultPiles.map(pile => ({
      time: currentTime,
      type: '故障警报',
      level: 'error',
      pile: pile.id,
      message: `充电桩 ${pile.id} 发生故障，需要维修`,
      status: 'pending'
    })),
    // 离线警报
    ...offlinePiles.map(pile => ({
      time: currentTime,
      type: '离线警报',
      level: 'error',
      pile: pile.id,
      message: `充电桩 ${pile.id} 已离线，请检查网络连接`,
      status: 'pending'
    })),
    // 排队警报（基于真实排队数据）
    ...busyQueues.map(queue => ({
      time: currentTime,
      type: '排队警报',
      level: 'warning',
      pile: queue.pileId,
      message: `${queue.pileName} 排队人数较多 (${queue.queueLength}人)，建议引导用户到其他充电桩`,
      status: 'pending'
    }))
  ]
  
  // 如果没有警报，显示系统正常
  if (alerts.value.length === 0) {
    alerts.value = [{
      time: currentTime,
      type: '系统状态',
      level: 'info',
      pile: '-',
      message: '所有充电桩运行正常，无排队警报',
      status: 'resolved'
    }]
  }
}

// 生成实时功率数据
const generateRealtimePower = (pile) => {
  // 如果不是正在充电状态，功率为0
  if (pile.status !== 'charging') return 0
  
  // 使用充电桩的实际功率配置而不是硬编码
  const ratedPower = pile.power || (pile.charging_mode === 'fast' ? 30 : 10) // 使用实际power字段
  const variation = (Math.random() - 0.5) * 0.2 // ±10%变化
  return Math.max(0, Number((ratedPower * (1 + variation)).toFixed(1)))
}

// 生成实时电流数据
const generateRealtimeCurrent = (pile) => {
  if (pile.status !== 'charging') return 0
  
  const baseRange = pile.charging_mode === 'fast' ? [40, 50] : [15, 20]
  const variation = (Math.random() - 0.5) * 2
  const current = baseRange[0] + Math.random() * (baseRange[1] - baseRange[0]) + variation
  
  return Math.max(0, Number(current.toFixed(1)))
}

// 更新功率历史数据
const updatePowerHistory = () => {
  const now = new Date()
  const timeLabel = now.toLocaleTimeString('zh-CN', { hour12: false })
  
  // 保持最近12个数据点
  if (powerHistory.value.length >= 12) {
    powerHistory.value.shift()
  }
  
  powerHistory.value.push({
    time: timeLabel,
    data: pileStatus.value.reduce((acc, pile) => {
      acc[pile.id] = pile.power
      return acc
    }, {})
  })
  
  // 更新图表
  updateChart()
}

const refreshData = () => {
  fetchMonitoringData()
  ElMessage.success('数据已刷新')
}

const stopCharging = async (pileId) => {
  try {
    const pile = pileStatus.value.find(p => p.id === pileId)
    if (pile) {
      await api.post(`/admin/piles/${pile.originalId}/stop`)
      ElMessage.success(`充电桩 ${pileId} 已停止充电`)
      await fetchPileStatus()
    }
  } catch (error) {
    console.error('停止充电失败:', error)
    ElMessage.error('停止充电失败')
  }
}

const initCharts = () => {
  if (powerChart.value) {
    chartInstance = echarts.init(powerChart.value)
    updateChart()
  }
}

const updateChart = () => {
  if (!chartInstance || powerHistory.value.length === 0) return
  
  const timeLabels = powerHistory.value.map(item => item.time)
  const allPileIds = [...new Set(pileStatus.value.map(pile => pile.id))]
  
  const series = allPileIds.map(pileId => {
    const pileData = powerHistory.value.map(item => item.data[pileId] || 0)
    const pile = pileStatus.value.find(p => p.id === pileId)
    
    return {
      name: pileId,
      type: 'line',
      data: pileData,
      smooth: true,
      lineStyle: {
        width: 2
      },
      itemStyle: {
        color: pile?.status === 'charging' ? '#67c23a' : '#909399'
      }
    }
  })
  
  chartInstance.setOption({
    title: { 
      text: '实时功率监控',
      left: 'center'
    },
    tooltip: { 
      trigger: 'axis',
      formatter: function(params) {
        let result = `时间: ${params[0].axisValue}<br/>`
        params.forEach(param => {
          result += `${param.seriesName}: ${param.value} kW<br/>`
        })
        return result
      }
    },
    legend: {
      top: 30,
      data: allPileIds
    },
    grid: {
      top: 60,
      left: 50,
      right: 30,
      bottom: 50
    },
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: { 
      type: 'value', 
      name: '功率 (kW)',
      min: 0
    },
    series: series
  })
}

onMounted(() => {
  nextTick(async () => {
    initCharts()
    await fetchMonitoringData()
    
    // 设置定时刷新（每10秒）
    refreshTimer = setInterval(() => {
      fetchPileStatus() // 刷新充电桩状态
      fetchQueueData()  // 刷新排队数据
      fetchAlerts()     // 刷新警报信息
    }, 10000)
  })
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.monitoring {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-cards {
  margin-bottom: 20px;
}

.pile-card {
  border-left: 4px solid #dcdfe6;
  transition: all 0.3s;
}

.pile-card.pile-charging {
  border-left-color: #67c23a;
}

.pile-card.pile-idle {
  border-left-color: #909399;
}

.pile-card.pile-fault {
  border-left-color: #f56c6c;
}

.pile-card.pile-maintenance {
  border-left-color: #e6a23c;
}

.pile-info {
  padding: 0;
}

.pile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.pile-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.pile-details {
  margin-bottom: 15px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item .label {
  color: #909399;
}

.detail-item .value {
  color: #303133;
  font-weight: 500;
}

.queue-status {
  padding: 10px 0;
}

.queue-item {
  margin-bottom: 15px;
}

.queue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.queue-tags {
  display: flex;
  align-items: center;
}

.queue-info {
  margin-top: 5px;
  text-align: center;
}
</style> 