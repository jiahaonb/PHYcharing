<template>
  <div class="charging-scene-container">
    <!-- 页面标题 -->
    <div class="scene-header">
      <h1>智能充电场景监控</h1>
      <div class="scene-controls">
        <el-button @click="refreshScene" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新场景
        </el-button>
        <el-button @click="resetAnimation">
          <el-icon><VideoPause /></el-icon>
          重置动画
        </el-button>
        <el-button @click="loadMockData" type="warning">
          <el-icon><Setting /></el-icon>
          加载模拟数据
        </el-button>
      </div>
    </div>

    <!-- 调试信息 -->
    <div class="debug-info" v-if="true">
      <el-alert 
        :title="`调试信息: 车辆总数 ${vehicles.length}, 暂留区 ${stayingVehicles.length}, 等待区 ${waitingVehicles.length}, 充电区 ${chargingVehicles.length}`"
        type="info" 
        :closable="false"
        style="margin-bottom: 10px;"
      />
    </div>

    <!-- 场景统计信息 -->
    <div class="scene-stats">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ sceneStats.stayingVehicles }}</div>
            <div class="stat-label">暂留区车辆</div>
            <div class="stat-color stay"></div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ sceneStats.waitingVehicles }}</div>
            <div class="stat-label">等待区车辆</div>
            <div class="stat-color waiting"></div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ sceneStats.chargingVehicles }}</div>
            <div class="stat-label">充电区车辆</div>
            <div class="stat-color charging"></div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ sceneStats.totalVehicles }}</div>
            <div class="stat-label">总车辆数</div>
            <div class="stat-color total"></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 主要场景区域 -->
    <div class="scene-main">
      <!-- 暂留区 -->
      <div class="scene-area stay-area">
        <div class="area-header">
          <h3>暂留区</h3>
          <span class="area-count">{{ sceneStats.stayingVehicles }} 辆车</span>
        </div>
        <div class="area-content">
          <!-- 空状态 -->
          <div v-if="stayingVehicles.length === 0" class="empty-message">
            <el-empty description="暂留区暂无车辆">
              <template #image>
                <el-icon size="64"><Van /></el-icon>
              </template>
            </el-empty>
          </div>
          
          <div class="vehicle-grid" v-else>
            <div 
              v-for="vehicle in stayingVehicles" 
              :key="`stay-${vehicle.id}`"
              :class="['vehicle-item', 'stay']"
              @click="showVehicleDetail(vehicle)"
              :style="{ animationDelay: `${vehicle.animationDelay || 0}s` }"
            >
              <div class="vehicle-icon">
                <el-icon><Van /></el-icon>
              </div>
              <div class="vehicle-info">
                <div class="vehicle-plate">{{ vehicle.license_plate }}</div>
                <div class="vehicle-status">待命中</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 等待区 -->
      <div class="scene-area waiting-area">
        <div class="area-header">
          <h3>等待区</h3>
          <span class="area-count">{{ sceneStats.waitingVehicles }} 辆车排队</span>
        </div>
        <div class="area-content">
          <div class="queue-line">
            <div 
              v-for="(vehicle, index) in waitingVehicles" 
              :key="`wait-${vehicle.id}`"
              :class="['vehicle-item', 'waiting']"
              @click="showVehicleDetail(vehicle)"
              :style="{ 
                animationDelay: `${vehicle.animationDelay || 0}s`,
                '--queue-position': index
              }"
            >
              <div class="vehicle-icon">
                <el-icon><Van /></el-icon>
              </div>
              <div class="vehicle-info">
                <div class="vehicle-plate">{{ vehicle.license_plate }}</div>
                <div class="vehicle-status">第{{ index + 1 }}位排队</div>
              </div>
              <div class="queue-number">{{ vehicle.queue_number }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 充电区 -->
      <div class="scene-area charging-area">
        <div class="area-header">
          <h3>充电区</h3>
          <span class="area-count">{{ sceneStats.chargingVehicles }} / {{ totalChargingSpots }} 车位使用中</span>
        </div>
        <div class="area-content">
          <div class="charging-piles">
            <div 
              v-for="pile in chargingPiles" 
              :key="`pile-${pile.id}`"
              class="charging-pile"
            >
              <div class="pile-header">
                <h4>{{ pile.pile_id }} ({{ pile.type === 'fast' ? '快充' : '慢充' }})</h4>
                <div class="pile-status" :class="pile.status">
                  {{ getPileStatusText(pile.status) }}
                </div>
              </div>
              <div class="pile-spots">
                <div 
                  v-for="spot in pile.spots" 
                  :key="`spot-${pile.id}-${spot.index}`"
                  :class="['charging-spot', { occupied: spot.vehicle }]"
                >
                  <div class="spot-number">{{ spot.index + 1 }}</div>
                  <div 
                    v-if="spot.vehicle"
                    :class="['vehicle-item', 'charging']"
                    @click="showVehicleDetail(spot.vehicle)"
                    :style="{ animationDelay: `${spot.vehicle.animationDelay || 0}s` }"
                  >
                    <div class="vehicle-icon">
                      <el-icon><Van /></el-icon>
                    </div>
                    <div class="vehicle-info">
                      <div class="vehicle-plate">{{ spot.vehicle.license_plate }}</div>
                      <div class="vehicle-status">充电中</div>
                      <div class="charging-progress">
                        <el-progress 
                          :percentage="spot.vehicle.chargingProgress || 0" 
                          :stroke-width="3"
                          :show-text="false"
                        />
                      </div>
                    </div>
                  </div>
                  <div v-else class="empty-spot">
                    <el-icon><Plus /></el-icon>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 车辆详情弹窗 -->
    <el-dialog 
      v-model="vehicleDetailVisible" 
      title="车辆详细信息" 
      width="500px"
    >
      <div v-if="selectedVehicle" class="vehicle-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="车牌号码">
            {{ selectedVehicle.license_plate }}
          </el-descriptions-item>
          <el-descriptions-item label="车辆型号">
            {{ selectedVehicle.model || '未设置' }}
          </el-descriptions-item>

          <el-descriptions-item label="电池容量">
            {{ selectedVehicle.battery_capacity || '未设置' }} kWh
          </el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :type="getVehicleStatusType(selectedVehicle.status)">
              {{ getVehicleStatusText(selectedVehicle.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="排队号码" v-if="selectedVehicle.queue_number">
            {{ selectedVehicle.queue_number }}
          </el-descriptions-item>
          <el-descriptions-item label="充电进度" v-if="selectedVehicle.status === 'charging'">
            <el-progress :percentage="selectedVehicle.chargingProgress || 0" />
          </el-descriptions-item>
          <el-descriptions-item label="预计完成" v-if="selectedVehicle.estimated_completion">
            {{ formatTime(selectedVehicle.estimated_completion) }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedVehicle.owner" class="owner-info">
          <h4>车主信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户名">
              {{ selectedVehicle.owner.username }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ selectedVehicle.owner.email }}
            </el-descriptions-item>
            <el-descriptions-item label="电话">
              {{ selectedVehicle.owner.phone || '未设置' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Refresh, 
  VideoPause, 
  Van, 
  Plus,
  Setting 
} from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const vehicles = ref([])
const chargingPiles = ref([])
const queueData = ref([])
const vehicleDetailVisible = ref(false)
const selectedVehicle = ref(null)

// 配置参数
const spotsPerPile = ref(3) // 每个充电桩的车位数，可以从配置获取
const systemConfig = ref({})

// 计算属性
const sceneStats = computed(() => {
  const staying = stayingVehicles.value.length
  const waiting = waitingVehicles.value.length
  const charging = chargingVehicles.value.length
  return {
    stayingVehicles: staying,
    waitingVehicles: waiting,
    chargingVehicles: charging,
    totalVehicles: staying + waiting + charging
  }
})

const stayingVehicles = computed(() => {
  try {
    // 获取所有已注册的车辆
    const allVehicles = vehicles.value || []
    
    // 获取正在排队或充电的车辆ID列表
    const queuedVehicleIds = new Set()
    ;(queueData.value || []).forEach(queue => {
      if (queue.vehicle && queue.vehicle.id) {
        queuedVehicleIds.add(queue.vehicle.id)
      }
    })
    
    // 暂留区显示所有未在队列中的已注册车辆
    return allVehicles
      .filter(vehicle => 
        vehicle && 
        vehicle.id && 
        !queuedVehicleIds.has(vehicle.id) &&
        (vehicle.status === 'registered' || vehicle.status === 'idle' || !vehicle.status)
      )
      .map((vehicle, index) => ({
        ...vehicle,
        status: 'registered', // 确保状态为已注册
        animationDelay: index * 0.1
      }))
  } catch (error) {
    console.error('计算暂留车辆时出错:', error)
    return []
  }
})

const waitingVehicles = computed(() => {
  try {
    return (queueData.value || [])
      .filter(queue => queue && queue.status === 'waiting')
      .map((queue, index) => ({
        ...(queue.vehicle || {}),
        queue_number: queue.queue_number,
        status: 'waiting',
        animationDelay: index * 0.2
      }))
      .sort((a, b) => (a.queue_number || '').localeCompare(b.queue_number || ''))
  } catch (error) {
    console.error('计算等待车辆时出错:', error)
    return []
  }
})

const chargingVehicles = computed(() => {
  try {
    const chargingQueues = (queueData.value || []).filter(queue => queue && queue.status === 'charging')
    return chargingQueues.map(queue => ({
      ...(queue.vehicle || {}),
      pile_id: queue.pile_id,
      status: 'charging',
      chargingProgress: Math.floor(Math.random() * 100), // 模拟充电进度
      estimated_completion: queue.estimated_completion
    }))
  } catch (error) {
    console.error('计算充电车辆时出错:', error)
    return []
  }
})

const totalChargingSpots = computed(() => {
  try {
    return (chargingPiles.value || []).reduce((total, pile) => total + spotsPerPile.value, 0)
  } catch (error) {
    console.error('计算充电车位总数时出错:', error)
    return 0
  }
})

// 内部数据获取方法（不管理loading状态）
const fetchAllData = async () => {
  console.log('🔄 开始获取场景数据...')
  
  await Promise.all([
    fetchVehicles(),
    fetchChargingPiles(),
    fetchQueueData()
  ])
  
  console.log('✅ API数据获取成功')
  console.log('📊 实际数据统计:', {
    vehicles: vehicles.value.length,
    piles: chargingPiles.value.length,
    queues: queueData.value.length
  })
  
  await nextTick()
  // 触发动画
  triggerVehicleAnimations()
}

// 公共刷新方法（管理loading状态）
const refreshScene = async () => {
  loading.value = true
  
  try {
    await fetchAllData()
  } catch (error) {
    console.error('⚠️ API调用失败:', error.message)
    ElMessage.error('获取数据失败，请检查网络连接或联系管理员')
    throw error
  } finally {
    loading.value = false
  }
}

const fetchVehicles = async () => {
  try {
    const response = await api.get('/admin/scene/vehicles')
    vehicles.value = Array.isArray(response) ? response : []
    console.log('✅ 获取车辆数据成功，数量:', vehicles.value.length)
  } catch (error) {
    console.error('获取车辆数据失败:', error)
    vehicles.value = []
    throw error
  }
}

const fetchChargingPiles = async () => {
  try {
    const response = await api.get('/admin/scene/charging-piles')
    const piles = Array.isArray(response) ? response : []
    
    // 为每个充电桩创建车位
    chargingPiles.value = piles.map(pile => ({
      ...pile,
      spots: Array.from({ length: spotsPerPile.value }, (_, index) => ({
        index,
        vehicle: null
      }))
    }))
    
    // 将充电中的车辆分配到对应车位
    chargingVehicles.value.forEach(vehicle => {
      const pile = chargingPiles.value.find(p => p.pile_id === vehicle.pile_id)
      if (pile) {
        const emptySpot = pile.spots.find(spot => !spot.vehicle)
        if (emptySpot) {
          emptySpot.vehicle = vehicle
        }
      }
    })
    console.log('✅ 获取充电桩数据成功，数量:', chargingPiles.value.length)
  } catch (error) {
    console.error('获取充电桩数据失败:', error)
    chargingPiles.value = []
    throw error
  }
}

const fetchQueueData = async () => {
  try {
    const response = await api.get('/admin/scene/charging-queue')
    queueData.value = Array.isArray(response) ? response : []
    console.log('✅ 获取排队数据成功，数量:', queueData.value.length)
  } catch (error) {
    console.error('获取排队数据失败:', error)
    queueData.value = []
    throw error
  }
}

const triggerVehicleAnimations = () => {
  // 添加进入动画类
  document.querySelectorAll('.vehicle-item').forEach((el, index) => {
    el.style.animationDelay = `${index * 0.1}s`
    el.classList.add('vehicle-enter')
  })
}

const resetAnimation = () => {
  document.querySelectorAll('.vehicle-item').forEach(el => {
    el.classList.remove('vehicle-enter')
    el.style.animationDelay = '0s'
  })
  
  setTimeout(() => {
    triggerVehicleAnimations()
  }, 100)
}



const showVehicleDetail = (vehicle) => {
  selectedVehicle.value = vehicle
  vehicleDetailVisible.value = true
}

const getPileStatusText = (status) => {
  const statusMap = {
    'idle': '空闲',
    'charging': '使用中',
    'fault': '故障',
    'maintenance': '维护中'
  }
  return statusMap[status] || '未知'
}

const getVehicleStatusType = (status) => {
  const typeMap = {
    'registered': 'info',
    'waiting': 'warning',
    'charging': 'success',
    'completed': 'info'
  }
  return typeMap[status] || 'info'
}

const getVehicleStatusText = (status) => {
  const textMap = {
    'registered': '已注册',
    'waiting': '排队中',
    'charging': '充电中',
    'completed': '已完成'
  }
  return textMap[status] || '未知'
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString()
}



// 定时器引用
let refreshInterval = null

// 生命周期
onMounted(async () => {
  console.log('🚀 充电场景页面已挂载，开始初始化...')
  
  // 设置初始加载状态
  loading.value = true
  
  try {
    // 立即获取API数据（使用内部方法，不重复管理loading）
    await fetchAllData()
    
    // 设置定时刷新（使用公共方法，会管理loading状态）
    refreshInterval = setInterval(() => {
      console.log('⏰ 定时刷新数据...')
      refreshScene()
    }, 30000) // 30秒刷新一次
    
    console.log('✅ 页面初始化完成')
  } catch (error) {
    console.error('❌ 页面初始化失败:', error)
    ElMessage.error('页面初始化失败，请刷新重试')
  } finally {
    loading.value = false
  }
})

// 组件卸载时清除定时器
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    console.log('🧹 清理定时器')
  }
})
</script>

<style scoped>
.charging-scene-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.scene-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.scene-header h1 {
  color: #303133;
  margin: 0;
  font-size: 24px;
}

.scene-controls {
  display: flex;
  gap: 10px;
}

.scene-stats {
  margin-bottom: 20px;
}

.stat-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
  position: relative;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-color {
  width: 4px;
  height: 60px;
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  border-radius: 0 2px 2px 0;
}

.stat-color.stay { background: #909399; }
.stat-color.waiting { background: #409EFF; }
.stat-color.charging { background: #67C23A; }
.stat-color.total { background: #E6A23C; }

.scene-main {
  display: grid;
  grid-template-columns: 1fr 1fr 2fr;
  gap: 20px;
  min-height: 600px;
}

.scene-area {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.area-header {
  padding: 15px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.area-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.area-count {
  color: #606266;
  font-size: 12px;
}

.area-content {
  padding: 20px;
  height: calc(100% - 60px);
}

/* 暂留区样式 */
.stay-area {
  border-left: 4px solid #909399;
}

.vehicle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
  height: 100%;
  overflow-y: auto;
}

/* 等待区样式 */
.waiting-area {
  border-left: 4px solid #409EFF;
}

.queue-line {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  overflow-y: auto;
}

/* 充电区样式 */
.charging-area {
  border-left: 4px solid #67C23A;
}

.charging-piles {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  overflow-y: auto;
}

.charging-pile {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 15px;
}

.pile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.pile-header h4 {
  margin: 0;
  color: #303133;
  font-size: 14px;
}

.pile-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: white;
}

.pile-status.idle { background: #909399; }
.pile-status.charging { background: #67C23A; }
.pile-status.fault { background: #F56C6C; }

.pile-spots {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.charging-spot {
  border: 2px dashed #e4e7ed;
  border-radius: 6px;
  padding: 10px;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s ease;
}

.charging-spot.occupied {
  border-style: solid;
  border-color: #67C23A;
  background: #f0f9ff;
}

.spot-number {
  position: absolute;
  top: 5px;
  left: 5px;
  font-size: 10px;
  color: #909399;
  background: white;
  padding: 2px 4px;
  border-radius: 2px;
}

.empty-spot {
  color: #c0c4cc;
  font-size: 24px;
}

/* 车辆项样式 */
.vehicle-item {
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: vehicleEnter 0.6s ease-out forwards;
  opacity: 0;
  transform: translateY(20px);
}

.vehicle-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.vehicle-item.stay {
  background: linear-gradient(135deg, #f5f5f5, #e8e8e8);
  border: 1px solid #d3d3d3;
}

.vehicle-item.waiting {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border: 1px solid #409EFF;
}

.vehicle-item.charging {
  background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
  border: 1px solid #67C23A;
}

.vehicle-icon {
  text-align: center;
  font-size: 24px;
  margin-bottom: 8px;
}

.vehicle-item.stay .vehicle-icon { color: #909399; }
.vehicle-item.waiting .vehicle-icon { color: #409EFF; }
.vehicle-item.charging .vehicle-icon { color: #67C23A; }

.vehicle-info {
  text-align: center;
}

.vehicle-plate {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
  font-size: 12px;
}

.vehicle-status {
  color: #606266;
  font-size: 11px;
  margin-bottom: 5px;
}

.charging-progress {
  margin-top: 5px;
}

.queue-number {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
}

/* 动画 */
@keyframes vehicleEnter {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.vehicle-enter {
  animation: vehicleMove 0.8s ease-out forwards;
}

@keyframes vehicleMove {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(30px);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.05) translateY(-5px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 车辆详情弹窗 */
.vehicle-detail {
  margin-top: 10px;
}

.owner-info {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e4e7ed;
}

.owner-info h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

/* 空状态样式 */
.empty-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  text-align: center;
}

.debug-info {
  margin-bottom: 15px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .scene-main {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto 1fr;
  }
  
  .vehicle-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
  
  .pile-spots {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .charging-scene-container {
    padding: 10px;
  }
  
  .scene-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .vehicle-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }
  
  .pile-spots {
    grid-template-columns: 1fr;
  }
}
</style>