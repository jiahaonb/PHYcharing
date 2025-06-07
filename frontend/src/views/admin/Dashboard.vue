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
              <div class="stats-number">¥{{ stats.todayRevenue }}</div>
              <div class="stats-label">今日收入</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>充电桩使用率趋势</span>
          </template>
          <div ref="usageChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>收入趋势</span>
          </template>
          <div ref="revenueChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时状态 -->
    <el-row :gutter="20" class="status-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>充电桩实时状态</span>
            <el-button 
              type="primary" 
              size="small" 
              style="float: right;"
              @click="refreshStatus"
            >
              刷新
            </el-button>
          </template>
          
          <el-table :data="pileStatus" style="width: 100%">
            <el-table-column prop="id" label="桩号" width="80" />
            <el-table-column prop="type" label="类型" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.type === 'fast' ? 'success' : 'info'">
                  {{ scope.row.type === 'fast' ? '快充' : '慢充' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="scope">
                <el-tag 
                  :type="getStatusType(scope.row.status)"
                  effect="dark"
                >
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="power" label="功率 (kW)" width="120" />
            <el-table-column prop="voltage" label="电压 (V)" width="120" />
            <el-table-column prop="current" label="电流 (A)" width="120" />
            <el-table-column prop="user" label="使用用户" />
            <el-table-column prop="startTime" label="开始时间" width="150" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="warning"
                  v-if="scope.row.status === 'charging'"
                  @click="stopCharging(scope.row.id)"
                >
                  停止充电
                </el-button>
                <el-button 
                  size="small" 
                  type="success"
                  v-if="scope.row.status === 'fault'"
                  @click="repairPile(scope.row.id)"
                >
                  维修完成
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
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Lightning, 
  Connection, 
  Clock, 
  Money 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/utils/api'

// 响应式数据
const stats = ref({
  totalPiles: 0,
  activePiles: 0,
  queueLength: 0,
  todayRevenue: 0
})

const pileStatus = ref([])

const usageChart = ref()
const revenueChart = ref()
const loading = ref(false)

// 状态处理函数
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
    'charging': '充电中',
    'idle': '空闲',
    'fault': '故障',
    'maintenance': '维护中'
  }
  return statusMap[status] || '未知'
}

// API调用函数
const fetchDashboardData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchPileStatus(),
      fetchStats(),
      fetchTodayRevenue()
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
    
    // 转换数据格式并添加实时数据
    pileStatus.value = piles.map(pile => ({
      id: pile.pile_number,
      type: pile.charging_mode,
      status: pile.status,
      power: pile.power,
      voltage: pile.charging_mode === 'fast' ? 380 : 220,
      current: generateRealtimeCurrent(pile),
      user: '待实现', // 需要从队列获取当前用户
      startTime: '待实现',
      ...pile
    }))
  } catch (error) {
    console.error('获取充电桩状态失败:', error)
  }
}

const fetchStats = async () => {
  try {
    const piles = await api.get('/admin/piles')
    const queueData = await api.get('/admin/queue/summary')
    
    stats.value.totalPiles = piles.length
    stats.value.activePiles = piles.filter(p => p.is_active && p.status !== 'fault').length
    stats.value.queueLength = queueData.total_in_system
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const fetchTodayRevenue = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const reportData = await api.get(`/admin/reports/daily?date=${today}`)
    
    const totalRevenue = reportData.reduce((sum, item) => sum + item.total_fee, 0)
    stats.value.todayRevenue = totalRevenue
  } catch (error) {
    console.error('获取今日收入失败:', error)
    stats.value.todayRevenue = 0
  }
}

// 生成实时电流数据（模拟）
const generateRealtimeCurrent = (pile) => {
  if (pile.status !== 'charging') return 0
  
  const baseRange = pile.charging_mode === 'fast' ? [40, 50] : [15, 20]
  const variation = (Math.random() - 0.5) * 2 // -1 到 1 的变化
  const current = baseRange[0] + Math.random() * (baseRange[1] - baseRange[0]) + variation
  
  return Math.max(0, Number(current.toFixed(1)))
}

// 操作函数
const refreshStatus = () => {
  fetchDashboardData()
  ElMessage.success('状态已刷新')
}

const stopCharging = async (pileId) => {
  try {
    const pile = pileStatus.value.find(p => p.id === pileId)
    if (pile) {
      await api.post(`/admin/piles/${pile.pile_id}/stop`)
      ElMessage.success(`充电桩 ${pileId} 已停止充电`)
      await fetchPileStatus()
    }
  } catch (error) {
    console.error('停止充电失败:', error)
    ElMessage.error('停止充电失败')
  }
}

const repairPile = async (pileId) => {
  try {
    const pile = pileStatus.value.find(p => p.id === pileId)
    if (pile) {
      await api.post(`/admin/piles/${pile.pile_id}/start`)
      ElMessage.success(`充电桩 ${pileId} 维修完成`)
      await fetchPileStatus()
    }
  } catch (error) {
    console.error('修复充电桩失败:', error)
    ElMessage.error('修复失败')
  }
}

// 初始化图表
const initCharts = () => {
  // 使用率趋势图
  if (usageChart.value) {
    const usageChartInstance = echarts.init(usageChart.value)
    const usageOption = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
      },
      yAxis: { type: 'value', max: 100 },
      series: [{
        data: [20, 15, 45, 80, 90, 85, 60],
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.3 }
      }]
    }
    usageChartInstance.setOption(usageOption)
  }

  // 收入趋势图
  if (revenueChart.value) {
    const revenueChartInstance = echarts.init(revenueChart.value)
    const revenueOption = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [850, 920, 1100, 1200, 1350, 1600, 1250],
        type: 'bar',
        itemStyle: { color: '#409eff' }
      }]
    }
    revenueChartInstance.setOption(revenueOption)
  }
}

onMounted(() => {
  nextTick(() => {
    initCharts()
    fetchDashboardData()
    
    // 设置定时刷新（每30秒）
    setInterval(() => {
      fetchPileStatus() // 只刷新充电桩状态，保持实时性
    }, 30000)
  })
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

.charts-row {
  margin-bottom: 20px;
}

.status-row {
  margin-bottom: 20px;
}
</style> 