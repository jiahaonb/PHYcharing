<template>
  <div class="admin-dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-item">
            <div class="stats-icon charging">
              <el-icon><Lightning /></el-icon>
            </div>
            <div class="stats-content">
              <div class="stats-number">{{ stats.totalPiles }}</div>
              <div class="stats-label">总充电桩数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-item">
            <div class="stats-icon active">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="stats-content">
              <div class="stats-number">{{ stats.activePiles }}</div>
              <div class="stats-label">使用中充电桩</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-item">
            <div class="stats-icon queue">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stats-content">
              <div class="stats-number">{{ stats.queueLength }}</div>
              <div class="stats-label">排队车辆</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-item">
            <div class="stats-icon revenue">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stats-content">
              <div class="stats-number">¥{{ formatMoney(stats.todayRevenue) }}</div>
              <div class="stats-label">今日收入</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统总览 -->
    <el-row :gutter="20" class="overview-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统概览</span>
              <el-tag :type="getSystemStatusType()" size="small">
                {{ getSystemStatusText() }}
              </el-tag>
            </div>
          </template>
          <div class="overview-content">
            <div class="overview-item">
              <span class="overview-label">快充桩:</span>
              <span class="overview-value">{{ stats.fastPiles }}个</span>
              <span class="overview-status">(运行中: {{ stats.fastPilesActive }}个)</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">慢充桩:</span>
              <span class="overview-value">{{ stats.trickePiles }}个</span>
              <span class="overview-status">(运行中: {{ stats.trickePilesActive }}个)</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">总充电量:</span>
              <span class="overview-value">{{ formatNumber(stats.totalEnergy) }} 度</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">总订单数:</span>
              <span class="overview-value">{{ formatNumber(stats.totalOrders) }}单</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">总收入:</span>
              <span class="overview-value">¥{{ formatMoney(stats.totalRevenue) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>今日运营数据</span>
          </template>
          <div class="today-stats">
            <div class="today-item">
              <div class="today-number">{{ stats.todayOrders }}</div>
              <div class="today-label">今日订单</div>
            </div>
            <div class="today-item">
              <div class="today-number">{{ formatNumber(stats.todayEnergy) }}</div>
              <div class="today-label">今日充电量(度)</div>
            </div>
            <div class="today-item">
              <div class="today-number">{{ stats.activeUsers }}</div>
              <div class="today-label">活跃用户</div>
            </div>
            <div class="today-item">
              <div class="today-number">{{ stats.avgWaitTime }}</div>
              <div class="today-label">平均等待(分钟)</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 充电桩实时状态 -->
    <el-row :gutter="20" class="status-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>充电桩实时状态</span>
              <div>
                <el-button 
                  type="primary" 
                  size="small"
                  @click="refreshStatus"
                  :loading="loading"
                >
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          
          <el-table 
            :data="pileStatus" 
            style="width: 100%"
            v-loading="loading"
            :row-class-name="getTableRowClassName"
          >
            <el-table-column prop="pile_number" label="桩号" width="100" />
            <el-table-column label="类型" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.charging_mode === 'fast' ? 'success' : 'info'" size="small">
                  {{ scope.row.charging_mode === 'fast' ? '快充' : '慢充' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="120">
              <template #default="scope">
                <el-tag 
                  :type="getStatusType(scope.row.status)"
                  effect="dark"
                  size="small"
                >
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="power" label="功率(kW)" width="100">
              <template #default="scope">
                {{ scope.row.power?.toFixed(1) || '0.0' }}
              </template>
            </el-table-column>
            <el-table-column label="电压(V)" width="100">
              <template #default="scope">
                {{ scope.row.charging_mode === 'fast' ? '380' : '220' }}
              </template>
            </el-table-column>
            <el-table-column label="当前电流(A)" width="120">
              <template #default="scope">
                {{ scope.row.current || '0.0' }}
              </template>
            </el-table-column>
            <el-table-column label="使用用户" width="150">
              <template #default="scope">
                <span v-if="scope.row.currentUser && scope.row.currentUser !== '无数据'">
                  {{ scope.row.currentUser }}
                </span>
                <span v-else style="color: #909399;">无数据</span>
              </template>
            </el-table-column>
            <el-table-column label="开始时间" width="150">
              <template #default="scope">
                <span v-if="scope.row.startTime && scope.row.startTime !== '无数据'">
                  {{ scope.row.startTime }}
                </span>
                <span v-else style="color: #909399;">无数据</span>
              </template>
            </el-table-column>
            <el-table-column label="累计统计" width="200">
              <template #default="scope">
                <div class="stats-summary">
                  <div>充电 {{ scope.row.total_charging_count || 0 }} 次</div>
                  <div>{{ (scope.row.total_charging_amount || 0).toFixed(1) }} 度</div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="warning"
                  v-if="scope.row.status === 'CHARGING'"
                  @click="stopCharging(scope.row)"
                >
                  停止充电
                </el-button>
                <el-button 
                  size="small" 
                  type="success"
                  v-if="scope.row.status === 'FAULT'"
                  @click="repairPile(scope.row)"
                >
                  维修完成
                </el-button>
                <el-button 
                  size="small" 
                  type="primary"
                  v-if="scope.row.status === 'NORMAL' && !scope.row.is_active"
                  @click="startPile(scope.row)"
                >
                  启动
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Lightning, 
  Connection, 
  Clock, 
  Money,
  Refresh
} from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const stats = ref({
  totalPiles: 0,
  activePiles: 0,
  queueLength: 0,
  todayRevenue: 0,
  fastPiles: 0,
  trickePiles: 0,
  fastPilesActive: 0,
  trickePilesActive: 0,
  totalEnergy: 0,
  totalOrders: 0,
  totalRevenue: 0,
  todayOrders: 0,
  todayEnergy: 0,
  activeUsers: 0,
  avgWaitTime: 0
})

const pileStatus = ref([])
const loading = ref(false)
let refreshTimer = null

// 格式化函数
const formatMoney = (value) => {
  if (!value) return '0.00'
  return value.toFixed(2)
}

const formatNumber = (value) => {
  if (!value) return '0'
  return value.toLocaleString()
}

// 状态处理函数
const getStatusType = (status) => {
  const statusMap = {
    'charging': 'success',
    'normal': 'info',
    'fault': 'danger',
    'maintenance': 'warning',
    'offline': 'warning'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'charging': '充电中',
    'normal': '正常',
    'fault': '故障',
    'maintenance': '维护中',
    'offline': '离线'
  }
  return statusMap[status] || '未知'
}

const getSystemStatusType = () => {
  const faultCount = pileStatus.value.filter(p => p.status === 'fault').length
  const offlineCount = pileStatus.value.filter(p => p.status === 'offline').length
  
  if (faultCount > 0 || offlineCount > 0) return 'danger'
  if (stats.value.activePiles < stats.value.totalPiles * 0.8) return 'warning'
  return 'success'
}

const getSystemStatusText = () => {
  const faultCount = pileStatus.value.filter(p => p.status === 'fault').length
  const offlineCount = pileStatus.value.filter(p => p.status === 'offline').length
  
  if (faultCount > 0) return `${faultCount}个桩故障`
  if (offlineCount > 0) return `${offlineCount}个桩离线`
  return '系统正常'
}

const getTableRowClassName = ({ row }) => {
  if (row.status === 'charging') return 'charging-row'
  if (row.status === 'fault') return 'fault-row'
  if (row.status === 'offline') return 'offline-row'
  return ''
}

// API调用函数
const fetchDashboardData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchPileStatus(),
      fetchStats(),
      fetchTodayData()
    ])
  } catch (error) {
    console.error('获取仪表板数据失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const fetchPileStatus = async () => {
  try {
    const piles = await api.get('/admin/piles')
    const queueData = await api.get('/admin/queue/piles')
    
    // 获取活跃队列信息（包含start_charging_time）
    const activeQueues = await api.get('/admin/queue/active')
    
    // 合并充电桩数据和队列数据
    pileStatus.value = piles.map(pile => {
      // 查找对应的队列信息
      const queueInfo = queueData.find(q => 
        q.pile_name.includes(pile.pile_number) || 
        q.pileId === pile.pile_number
      )
      
      let currentUser = '无数据'
      let startTime = '无数据'
      let currentCurrent = 0
      
      if (queueInfo) {
        currentUser = queueInfo.currentUser || queueInfo.current_user || '无数据'
        
        // 从活跃队列中找到该充电桩正在充电的记录
        const chargingQueue = activeQueues.find(q => 
          q.charging_pile && 
          q.charging_pile.id === pile.id && 
          q.status === 'charging'
        )
        
        if (chargingQueue && chargingQueue.start_charging_time) {
          startTime = new Date(chargingQueue.start_charging_time).toLocaleString('zh-CN')
        } else if (queueInfo.queueDetails && queueInfo.queueDetails.length > 0) {
          // 如果没找到活跃队列记录，使用队列详情的request_time作为备选
          const chargingRecord = queueInfo.queueDetails.find(d => d.status === 'charging')
          if (chargingRecord && chargingRecord.request_time) {
            startTime = new Date(chargingRecord.request_time).toLocaleString('zh-CN') + ' (排队时间)'
          }
        }
      }
      
      // 如果充电桩正在充电，生成实时电流
      if (pile.status === 'charging') {
        const baseRange = pile.charging_mode === 'fast' ? [40, 50] : [15, 20]
        currentCurrent = (baseRange[0] + Math.random() * (baseRange[1] - baseRange[0])).toFixed(1)
      }
      
      return {
        ...pile,
        currentUser,
        startTime,
        current: currentCurrent
      }
    })
  } catch (error) {
    console.error('获取充电桩状态失败:', error)
    pileStatus.value = []
  }
}

const fetchStats = async () => {
  try {
    const piles = await api.get('/admin/piles')
    const users = await api.get('/admin/users')
    
    // 基础统计
    stats.value.totalPiles = piles.length
    stats.value.activePiles = piles.filter(p => p.status === 'charging').length
    stats.value.fastPiles = piles.filter(p => p.charging_mode === 'fast').length
    stats.value.trickePiles = piles.filter(p => p.charging_mode === 'trickle').length
    stats.value.fastPilesActive = piles.filter(p => p.charging_mode === 'fast' && p.status === 'charging').length
    stats.value.trickePilesActive = piles.filter(p => p.charging_mode === 'trickle' && p.status === 'charging').length
    stats.value.activeUsers = users.filter(u => u.is_active !== false).length
    
    // 获取总体统计数据
    let totalOrders = 0
    let totalRevenue = 0
    let totalEnergy = 0
    
    for (const user of users) {
      try {
        const userOrders = await api.get(`/admin/users/${user.id}/charging-orders?limit=1000`)
        if (userOrders && userOrders.data) {
          totalOrders += userOrders.data.length
          userOrders.data.forEach(order => {
            if (order.total_fee) totalRevenue += order.total_fee
            if (order.charging_amount) totalEnergy += order.charging_amount
          })
        }
      } catch (error) {
        console.warn(`获取用户 ${user.username} 订单失败:`, error)
      }
    }
    
    stats.value.totalOrders = totalOrders
    stats.value.totalRevenue = totalRevenue
    stats.value.totalEnergy = totalEnergy
    
    // 获取队列长度
    try {
      const queueData = await api.get('/admin/queue/piles')
      stats.value.queueLength = queueData.reduce((sum, queue) => sum + (queue.queue_length || 0), 0)
      
      // 计算平均等待时间
      const waitTimes = queueData.filter(q => q.estimated_wait_time > 0).map(q => q.estimated_wait_time)
      stats.value.avgWaitTime = waitTimes.length > 0 
        ? Math.round(waitTimes.reduce((sum, time) => sum + time, 0) / waitTimes.length)
        : 0
    } catch (error) {
      console.warn('获取队列数据失败:', error)
      stats.value.queueLength = 0
      stats.value.avgWaitTime = 0
    }
    
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const fetchTodayData = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const reportData = await api.get(`/admin/reports/daily?date=${today}`)
    
    // 今日收入
    const todayRevenue = reportData.reduce((sum, item) => sum + (item.total_fee || 0), 0)
    stats.value.todayRevenue = todayRevenue
    
    // 今日订单和充电量
    const todayOrders = reportData.reduce((sum, item) => sum + (item.charging_count || 0), 0)
    const todayEnergy = reportData.reduce((sum, item) => sum + (item.charging_amount || 0), 0)
    
    stats.value.todayOrders = todayOrders
    stats.value.todayEnergy = todayEnergy
    
  } catch (error) {
    console.warn('获取今日数据失败:', error)
    stats.value.todayRevenue = 0
    stats.value.todayOrders = 0
    stats.value.todayEnergy = 0
  }
}

// 操作函数
const refreshStatus = () => {
  fetchDashboardData()
}

const stopCharging = async (pile) => {
  try {
    await ElMessageBox.confirm(
      `确定要停止充电桩 ${pile.pile_number} 的充电吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await api.post(`/admin/piles/${pile.id}/stop`)
    ElMessage.success(`充电桩 ${pile.pile_number} 已停止充电`)
    await fetchPileStatus()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('停止充电失败:', error)
      ElMessage.error('停止充电失败')
    }
  }
}

const repairPile = async (pile) => {
  try {
    await ElMessageBox.confirm(
      `确定标记充电桩 ${pile.pile_number} 为维修完成吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    )
    
    await api.post(`/admin/piles/${pile.id}/start`)
    ElMessage.success(`充电桩 ${pile.pile_number} 维修完成`)
    await fetchPileStatus()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('修复充电桩失败:', error)
      ElMessage.error('修复失败')
    }
  }
}

const startPile = async (pile) => {
  try {
    await api.post(`/admin/piles/${pile.id}/start`)
    ElMessage.success(`充电桩 ${pile.pile_number} 已启动`)
    await fetchPileStatus()
  } catch (error) {
    console.error('启动充电桩失败:', error)
    ElMessage.error('启动失败')
  }
}

onMounted(() => {
  fetchDashboardData()
  
  // 设置定时刷新（每30秒）
  refreshTimer = setInterval(() => {
    fetchPileStatus() // 只刷新充电桩状态，保持实时性
  }, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.admin-dashboard {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stats-item {
  display: flex;
  align-items: center;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.stats-icon.charging {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.stats-icon.active {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.stats-icon.queue {
  background-color: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.stats-icon.revenue {
  background-color: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.stats-icon .el-icon {
  font-size: 24px;
}

.stats-content {
  flex: 1;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.overview-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overview-content {
  padding: 10px 0;
}

.overview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.overview-item:last-child {
  border-bottom: none;
}

.overview-label {
  color: #606266;
  font-weight: 500;
}

.overview-value {
  font-weight: bold;
  color: #303133;
}

.overview-status {
  color: #909399;
  font-size: 12px;
}

.today-stats {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 20px 0;
}

.today-item {
  text-align: center;
}

.today-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.today-label {
  font-size: 12px;
  color: #909399;
}

.status-row {
  margin-bottom: 20px;
}

.stats-summary {
  font-size: 12px;
  color: #606266;
}

.stats-summary div {
  margin-bottom: 2px;
}

/* 表格行样式 */
:deep(.charging-row) {
  background-color: rgba(103, 194, 58, 0.05);
}

:deep(.fault-row) {
  background-color: rgba(245, 108, 108, 0.05);
}

:deep(.offline-row) {
  background-color: rgba(230, 162, 60, 0.05);
}
</style> 