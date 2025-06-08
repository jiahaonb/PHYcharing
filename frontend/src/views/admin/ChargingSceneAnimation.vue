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
        <el-switch 
          v-model="autoRefresh"
          active-text="自动刷新"
          @change="toggleAutoRefresh"
        />
      </div>
    </div>

    <!-- 场景统计信息 -->
    <div class="scene-stats">
      <el-row :gutter="20">
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-number">{{ sceneStats.stayingVehicles }}</div>
            <div class="stat-label">暂留区车辆</div>
            <div class="stat-color stay"></div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-number">{{ sceneStats.fastWaitingVehicles }}</div>
            <div class="stat-label">快充等候</div>
            <div class="stat-color fast-waiting"></div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-number">{{ sceneStats.trickleWaitingVehicles }}</div>
            <div class="stat-label">慢充等候</div>
            <div class="stat-color trickle-waiting"></div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-number">{{ sceneStats.fastChargingVehicles }}</div>
            <div class="stat-label">快充中</div>
            <div class="stat-color fast-charging"></div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-number">{{ sceneStats.trickleChargingVehicles }}</div>
            <div class="stat-label">慢充中</div>
            <div class="stat-color trickle-charging"></div>
          </div>
        </el-col>
        <el-col :span="4">
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
          <div v-if="stayingVehicles.length === 0" class="empty-area">
            <el-icon size="48" color="#ccc"><Van /></el-icon>
            <span>暂留区暂无车辆</span>
          </div>
          <div class="vehicle-grid" v-else>
            <div 
              v-for="vehicle in stayingVehicles" 
              :key="`stay-${vehicle.id}`"
              class="vehicle-item stay"
              @click="showStayingVehicleDetail(vehicle)"
            >
              <div class="vehicle-icon">
                <el-icon><Van /></el-icon>
              </div>
              <div class="vehicle-info">
                <div class="vehicle-plate">{{ vehicle.license_plate }}</div>
                <div class="vehicle-status">暂留</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 等候区 -->
      <div class="scene-area waiting-area">
        <div class="area-header">
          <h3>等候区</h3>
          <span class="area-count">{{ fastWaitingVehicles.length + trickleWaitingVehicles.length }} 辆车排队</span>
        </div>
        <div class="area-content">
          <div class="waiting-columns">
            <!-- 快充等候栏 -->
            <div class="waiting-column fast">
              <div class="column-header">
                <h4>快充等候</h4>
                <span class="column-count">{{ fastWaitingVehicles.length }} 辆</span>
              </div>
              <div class="column-content">
                <div v-if="fastWaitingVehicles.length === 0" class="empty-column">
                  <el-icon size="32" color="#ccc"><Lightning /></el-icon>
                  <span>暂无车辆</span>
                </div>
                <div class="queue-line" v-else>
                  <div 
                    v-for="(vehicle, index) in fastWaitingVehicles" 
                    :key="`fast-wait-${vehicle.record_number}`"
                    class="vehicle-item waiting fast"
                    @click="showOrderDetail(vehicle)"
                  >
                    <div class="queue-position">{{ vehicle.queue_position }}</div>
                    <div class="vehicle-icon">
                      <el-icon><Van /></el-icon>
                    </div>
                    <div class="vehicle-info">
                      <div class="vehicle-plate">{{ vehicle.license_plate }}</div>
                      <div class="vehicle-status">快充等候</div>
                      <div class="queue-number">{{ vehicle.record_number }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 慢充等候栏 -->
            <div class="waiting-column trickle">
              <div class="column-header">
                <h4>慢充等候</h4>
                <span class="column-count">{{ trickleWaitingVehicles.length }} 辆</span>
              </div>
              <div class="column-content">
                <div v-if="trickleWaitingVehicles.length === 0" class="empty-column">
                  <el-icon size="32" color="#ccc"><More /></el-icon>
                  <span>暂无车辆</span>
                </div>
                <div class="queue-line" v-else>
                  <div 
                    v-for="(vehicle, index) in trickleWaitingVehicles" 
                    :key="`trickle-wait-${vehicle.record_number}`"
                    class="vehicle-item waiting trickle"
                    @click="showOrderDetail(vehicle)"
                  >
                    <div class="queue-position">{{ vehicle.queue_position }}</div>
                    <div class="vehicle-icon">
                      <el-icon><Van /></el-icon>
                    </div>
                    <div class="vehicle-info">
                      <div class="vehicle-plate">{{ vehicle.license_plate }}</div>
                      <div class="vehicle-status">慢充等候</div>
                      <div class="queue-number">{{ vehicle.record_number }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 充电区 -->
      <div class="scene-area charging-area">
        <div class="area-header">
          <h3>充电区</h3>
          <span class="area-count">{{ sceneStats.fastChargingVehicles + sceneStats.trickleChargingVehicles }} / {{ totalChargingSpots }} 车位使用中</span>
        </div>
        <div class="area-content">
          <!-- 快充区 -->
          <div class="charging-section fast">
            <h4>快充区</h4>
            <div class="charging-piles">
              <div 
                v-for="pile in fastChargingPiles" 
                :key="`fast-pile-${pile.id}`"
                class="charging-pile fast"
              >
                <div class="pile-header">
                  <h5>{{ pile.pile_id }}</h5>
                  <div class="pile-status" :class="getPileStatusClass(pile.status)">
                    {{ getPileStatusText(pile.status) }}
                  </div>
                  <div class="pile-info-row">
                    <!-- 剩余时间显示 -->
                    <div class="remaining-time" v-if="pile.current_charging_order && pile.current_charging_order.remaining_time !== null && pile.current_charging_order.remaining_time !== undefined">
                      <el-tag 
                        :type="getRemainingTimeTagType(pile.current_charging_order.remaining_time)" 
                        size="small"
                        effect="dark"
                      >
                        <el-icon><Clock /></el-icon>
                        {{ formatRemainingTime(pile.current_charging_order.remaining_time) }}
                      </el-tag>
                    </div>
                    <div class="pile-power">{{ pile.power }}kW</div>
                  </div>
                </div>
                
                <!-- 可滑动的排队区域 -->
                <div class="pile-queue-container">
                  <div class="queue-scroll" ref="fastQueueScroll" @wheel="handleQueueScroll">
                    <div class="queue-spots">
                      <!-- 充电位 -->
                      <div class="charging-spot active">
                        <div class="spot-label">充电位</div>
                        <div 
                          v-if="pile.chargingVehicle"
                          class="vehicle-item charging"
                          @click="showOrderDetail(pile.chargingVehicle)"
                        >
                          <div class="vehicle-icon">
                            <el-icon><Van /></el-icon>
                          </div>
                          <div class="vehicle-plate">{{ pile.chargingVehicle.license_plate }}</div>
                          <div class="charging-time">{{ getChargingTime(pile.chargingVehicle) }}</div>
                          <div class="charging-indicator">
                            <el-icon class="charging-icon"><Lightning /></el-icon>
                          </div>
                        </div>
                        <div v-else class="empty-spot">
                          <el-icon><Plus /></el-icon>
                          <span>空闲</span>
                        </div>
                      </div>
                      
                      <!-- 排队位 -->
                      <div 
                        v-for="(spot, index) in pile.queueSpots" 
                        :key="`fast-queue-${pile.id}-${index}`"
                        class="charging-spot queue"
                      >
                        <div class="spot-label">排队 {{ index + 1 }}</div>
                        <div 
                          v-if="spot.vehicle"
                          class="vehicle-item queuing"
                          @click="showOrderDetail(spot.vehicle)"
                        >
                          <div class="vehicle-icon">
                            <el-icon><Van /></el-icon>
                          </div>
                          <div class="vehicle-plate">{{ spot.vehicle.license_plate }}</div>
                          <div class="queue-position-indicator">{{ index + 1 }}</div>
                        </div>
                        <div v-else class="empty-spot">
                          <el-icon><More /></el-icon>
                          <span>空位</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="scroll-hint">← 滑动查看排队 →</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 慢充区 -->
          <div class="charging-section trickle">
            <h4>慢充区</h4>
            <div class="charging-piles">
              <div 
                v-for="pile in trickleChargingPiles" 
                :key="`trickle-pile-${pile.id}`"
                class="charging-pile trickle"
              >
                <div class="pile-header">
                  <h5>{{ pile.pile_id }}</h5>
                  <div class="pile-status" :class="getPileStatusClass(pile.status)">
                    {{ getPileStatusText(pile.status) }}
                  </div>
                  <div class="pile-info-row">
                    <!-- 剩余时间显示 -->
                    <div class="remaining-time" v-if="pile.current_charging_order && pile.current_charging_order.remaining_time !== null && pile.current_charging_order.remaining_time !== undefined">
                      <el-tag 
                        :type="getRemainingTimeTagType(pile.current_charging_order.remaining_time)" 
                        size="small"
                        effect="dark"
                      >
                        <el-icon><Clock /></el-icon>
                        {{ formatRemainingTime(pile.current_charging_order.remaining_time) }}
                      </el-tag>
                    </div>
                    <div class="pile-power">{{ pile.power }}kW</div>
                  </div>
                </div>
                
                <!-- 可滑动的排队区域 -->
                <div class="pile-queue-container">
                  <div class="queue-scroll" ref="trickleQueueScroll" @wheel="handleQueueScroll">
                    <div class="queue-spots">
                      <!-- 充电位 -->
                      <div class="charging-spot active">
                        <div class="spot-label">充电位</div>
                        <div 
                          v-if="pile.chargingVehicle"
                          class="vehicle-item charging"
                          @click="showOrderDetail(pile.chargingVehicle)"
                        >
                          <div class="vehicle-icon">
                            <el-icon><Van /></el-icon>
                          </div>
                          <div class="vehicle-plate">{{ pile.chargingVehicle.license_plate }}</div>
                          <div class="charging-time">{{ getChargingTime(pile.chargingVehicle) }}</div>
                          <div class="charging-indicator">
                            <el-icon class="charging-icon"><More /></el-icon>
                          </div>
                        </div>
                        <div v-else class="empty-spot">
                          <el-icon><Plus /></el-icon>
                          <span>空闲</span>
                        </div>
                      </div>
                      
                      <!-- 排队位 -->
                      <div 
                        v-for="(spot, index) in pile.queueSpots" 
                        :key="`trickle-queue-${pile.id}-${index}`"
                        class="charging-spot queue"
                      >
                        <div class="spot-label">排队 {{ index + 1 }}</div>
                        <div 
                          v-if="spot.vehicle"
                          class="vehicle-item queuing"
                          @click="showOrderDetail(spot.vehicle)"
                        >
                          <div class="vehicle-icon">
                            <el-icon><Van /></el-icon>
                          </div>
                          <div class="vehicle-plate">{{ spot.vehicle.license_plate }}</div>
                          <div class="queue-position-indicator">{{ index + 1 }}</div>
                        </div>
                        <div v-else class="empty-spot">
                          <el-icon><More /></el-icon>
                          <span>空位</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="scroll-hint">← 滑动查看排队 →</div>
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
            {{ selectedVehicle.battery_capacity || '未设置' }} 度
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

        <!-- 充电详单信息 -->
        <div v-if="selectedVehicleOrder" class="charging-order-info">
          <h4>充电详单信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="订单编号" label-class-name="order-label">
              <span class="order-number">{{ selectedVehicleOrder.record_number && selectedVehicleOrder.record_number !== 'N/A' ? selectedVehicleOrder.record_number : '暂无订单' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="排队号" label-class-name="queue-label">
              <span class="queue-number">{{ selectedVehicleOrder.queue_number }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="车牌号码">
              <strong>{{ selectedVehicleOrder.license_plate || selectedVehicle.license_plate }}</strong>
            </el-descriptions-item>
            <el-descriptions-item label="充电模式">
              <el-tag :type="selectedVehicleOrder.charging_mode === 'fast' ? 'success' : 'warning'" size="small">
                {{ selectedVehicleOrder.charging_mode === 'fast' ? '快充' : '慢充' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="申请充电量">
              <strong>{{ selectedVehicleOrder.charging_amount }} 度</strong>
            </el-descriptions-item>
            <el-descriptions-item label="订单状态">
              <el-tag :type="getOrderStatusType(selectedVehicleOrder.queue_status || selectedVehicleOrder.status)" size="small">
                {{ getOrderStatusText(selectedVehicleOrder.queue_status || selectedVehicleOrder.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="订单创建时间">
              {{ formatTime(selectedVehicleOrder.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="分配充电桩" v-if="selectedVehicleOrder.charging_pile">
              <el-tag type="info" size="small">{{ selectedVehicleOrder.charging_pile.pile_number }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="开始充电时间" v-if="selectedVehicleOrder.start_time">
              {{ formatTime(selectedVehicleOrder.start_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="结束充电时间" v-if="selectedVehicleOrder.end_time">
              {{ formatTime(selectedVehicleOrder.end_time) }}
            </el-descriptions-item>
            
            <!-- 预计充电时长/已充电时长 -->
            <el-descriptions-item label="充电时长">
              <div class="charging-duration-info">
                <!-- 如果正在充电，显示实时时长 -->
                <div v-if="selectedVehicleOrder.charging_duration !== null && selectedVehicleOrder.charging_duration !== undefined">
                  <el-tag type="success" size="small">已充电 {{ formatDuration(selectedVehicleOrder.charging_duration) }}</el-tag>
                </div>
                <!-- 如果有预计完成时间，显示预计总时长 -->
                <div v-if="getEstimatedDuration(selectedVehicleOrder)" class="estimated-duration">
                  <el-tag type="warning" size="small">预计总时长 {{ getEstimatedDuration(selectedVehicleOrder) }}</el-tag>
                </div>
                <!-- 如果没有时长信息，显示基于充电量的预估 -->
                <div v-if="!selectedVehicleOrder.charging_duration && !getEstimatedDuration(selectedVehicleOrder)" class="estimated-duration">
                  <el-tag type="info" size="small">预计 {{ getEstimatedDurationByAmount(selectedVehicleOrder) }}</el-tag>
                </div>
              </div>
            </el-descriptions-item>
            
            <!-- 剩余充电时间 -->
            <el-descriptions-item label="剩余时间" v-if="selectedVehicleOrder.remaining_time !== null && selectedVehicleOrder.remaining_time !== undefined">
              <div class="remaining-time-info">
                <el-tag 
                  :type="getRemainingTimeTagType(selectedVehicleOrder.remaining_time)" 
                  size="small"
                  effect="dark"
                >
                  <el-icon><Clock /></el-icon>
                  {{ formatRemainingTime(selectedVehicleOrder.remaining_time) }}
                </el-tag>
              </div>
            </el-descriptions-item>
            
            <el-descriptions-item label="预计完成时间" v-if="selectedVehicleOrder.estimated_completion_time">
              <el-tag type="warning" size="small">{{ formatTime(selectedVehicleOrder.estimated_completion_time) }}</el-tag>
            </el-descriptions-item>
            
            <!-- 费用信息 -->
            <el-descriptions-item label="充电费用" v-if="selectedVehicleOrder.electricity_fee !== undefined">
              <strong style="color: #67C23A;">¥{{ selectedVehicleOrder.electricity_fee }}</strong>
            </el-descriptions-item>
            <el-descriptions-item label="服务费用" v-if="selectedVehicleOrder.service_fee !== undefined">
              <strong style="color: #E6A23C;">¥{{ selectedVehicleOrder.service_fee }}</strong>
            </el-descriptions-item>
            <el-descriptions-item label="总费用" v-if="selectedVehicleOrder.total_fee !== undefined">
              <strong style="color: #F56C6C; font-size: 16px;">¥{{ selectedVehicleOrder.total_fee }}</strong>
            </el-descriptions-item>
            <el-descriptions-item label="时段电价" v-if="selectedVehicleOrder.time_period && selectedVehicleOrder.unit_price">
              {{ selectedVehicleOrder.time_period }} (¥{{ selectedVehicleOrder.unit_price }}/度)
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 管理操作区域 -->
        <div v-if="canManageVehicle(selectedVehicle)" class="management-actions">
          <el-divider content-position="left">管理操作</el-divider>
          <div class="action-buttons">
            <el-button 
              v-if="selectedVehicle.status === '等候' || selectedVehicle.status === 'waiting'"
              type="warning"
              @click="cancelQueue(selectedVehicle)"
              :loading="selectedVehicle.cancelling"
            >
              <el-icon><Close /></el-icon>
              取消排队
            </el-button>
            <el-button 
              v-if="selectedVehicle.status === '充电中' || selectedVehicle.status === 'charging'"
              type="danger"
              @click="stopCharging(selectedVehicle)"
              :loading="selectedVehicle.stopping"
            >
              <el-icon><VideoPause /></el-icon>
              停止充电
            </el-button>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="vehicleDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  Lightning,
  More,
  Van, 
  Plus,
  Close,
  Clock
} from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useAuthStore } from '@/store/auth'

// 响应式数据
const loading = ref(false)
const autoRefresh = ref(true)
const vehicles = ref([])
const chargingPiles = ref([])
// const queueData = ref([]) // 已删除，不再使用队列数据
const vehicleDetailVisible = ref(false)
const selectedVehicle = ref(null)
const selectedVehicleOrder = ref(null)
const refreshInterval = ref(null)

// 配置参数
const spotsPerPile = ref(3) // 每个充电桩的排队位数量
const systemConfig = ref({})

// 计算属性 - 按新逻辑分区
const sceneStats = computed(() => {
  const staying = stayingVehicles.value.length
  const fastWaiting = fastWaitingVehicles.value.length
  const trickleWaiting = trickleWaitingVehicles.value.length
  const fastCharging = fastChargingPiles.value.reduce((count, pile) => 
    count + (pile.chargingVehicle ? 1 : 0), 0)
  const trickleCharging = trickleChargingPiles.value.reduce((count, pile) => 
    count + (pile.chargingVehicle ? 1 : 0), 0)
  
  return {
    stayingVehicles: staying,
    fastWaitingVehicles: fastWaiting,
    trickleWaitingVehicles: trickleWaiting,
    fastChargingVehicles: fastCharging,
    trickleChargingVehicles: trickleCharging,
    totalVehicles: staying + fastWaiting + trickleWaiting + fastCharging + trickleCharging
  }
})

const stayingVehicles = computed(() => {
  try {
    const allVehicles = vehicles.value || []
    if (allVehicles.length === 0) return []
    
    // 获取正在排队或充电的车辆车牌号列表
    const activeLicensePlates = new Set()
    
    // 从充电桩数据中收集活跃车辆的车牌号
    ;(chargingPiles.value || []).forEach(pile => {
      // 充电中的车辆
      if (pile.current_charging_order) {
        activeLicensePlates.add(pile.current_charging_order.vehicle_license_plate)
      }
      
      // 排队中的车辆
      if (pile.queue_orders && pile.queue_orders.length > 0) {
        pile.queue_orders.forEach(order => {
          activeLicensePlates.add(order.vehicle_license_plate)
        })
      }
    })
    
    // 暂留区显示不在活跃列表中的车辆
    return allVehicles.filter(vehicle => 
      vehicle && vehicle.license_plate && !activeLicensePlates.has(vehicle.license_plate)
    )
  } catch (error) {
    console.error('计算暂留车辆时出错:', error)
    return []
  }
})

// 快充等候车辆 - 从充电桩数据中提取
const fastWaitingVehicles = computed(() => {
  try {
    const waitingVehicles = []
    
    // 遍历所有快充桩，收集等候的车辆
    const fastPiles = (chargingPiles.value || []).filter(pile => pile.type === 'fast')
    
    fastPiles.forEach(pile => {
      if (pile.queue_orders && pile.queue_orders.length > 0) {
        pile.queue_orders.forEach((order, index) => {
          waitingVehicles.push({
            record_number: order.record_number,
            license_plate: order.vehicle_license_plate,
            remaining_time: order.remaining_time,
            start_time: order.start_time,
            charging_amount: order.charging_amount,
            queue_position: index + 1,
            pile_id: pile.pile_id,
            status: '快充等候'
          })
        })
      }
    })
    
    return waitingVehicles.sort((a, b) => a.queue_position - b.queue_position)
  } catch (error) {
    console.error('计算快充等候车辆时出错:', error)
    return []
  }
})

// 慢充等候车辆 - 从充电桩数据中提取
const trickleWaitingVehicles = computed(() => {
  try {
    const waitingVehicles = []
    
    // 遍历所有慢充桩，收集等候的车辆
    const tricklePiles = (chargingPiles.value || []).filter(pile => pile.type === 'trickle')
    
    tricklePiles.forEach(pile => {
      if (pile.queue_orders && pile.queue_orders.length > 0) {
        pile.queue_orders.forEach((order, index) => {
          waitingVehicles.push({
            record_number: order.record_number,
            license_plate: order.vehicle_license_plate,
            remaining_time: order.remaining_time,
            start_time: order.start_time,
            charging_amount: order.charging_amount,
            queue_position: index + 1,
            pile_id: pile.pile_id,
            status: '慢充等候'
          })
        })
      }
    })
    
    return waitingVehicles.sort((a, b) => a.queue_position - b.queue_position)
  } catch (error) {
    console.error('计算慢充等候车辆时出错:', error)
    return []
  }
})

// 快充充电桩 - 直接使用后端返回的数据
const fastChargingPiles = computed(() => {
  try {
    const piles = (chargingPiles.value || [])
      .filter(pile => pile.type === 'fast')
      .map(pile => {
        // 构建充电车辆数据（基于当前充电订单）
        const chargingVehicle = pile.current_charging_order ? {
          license_plate: pile.current_charging_order.vehicle_license_plate,
          remaining_time: pile.current_charging_order.remaining_time,
          record_number: pile.current_charging_order.record_number,
          start_time: pile.current_charging_order.start_time
        } : null

        // 构建排队位数据（基于排队订单，最多3个位置）
        const queueSpots = Array.from({ length: spotsPerPile.value }, (_, index) => ({
          index,
          vehicle: pile.queue_orders && pile.queue_orders[index] ? {
            license_plate: pile.queue_orders[index].vehicle_license_plate,
            record_number: pile.queue_orders[index].record_number,
            queue_position: index + 1
          } : null
        }))
        
        return {
          ...pile,
          chargingVehicle,
          queueSpots
        }
      })
    
    return piles
  } catch (error) {
    console.error('处理快充充电桩数据时出错:', error)
    return []
  }
})

// 慢充充电桩 - 直接使用后端返回的数据
const trickleChargingPiles = computed(() => {
  try {
    const piles = (chargingPiles.value || [])
      .filter(pile => pile.type === 'trickle')
      .map(pile => {
        // 构建充电车辆数据（基于当前充电订单）
        const chargingVehicle = pile.current_charging_order ? {
          license_plate: pile.current_charging_order.vehicle_license_plate,
          remaining_time: pile.current_charging_order.remaining_time,
          record_number: pile.current_charging_order.record_number,
          start_time: pile.current_charging_order.start_time
        } : null

        // 构建排队位数据（基于排队订单，最多3个位置）
        const queueSpots = Array.from({ length: spotsPerPile.value }, (_, index) => ({
          index,
          vehicle: pile.queue_orders && pile.queue_orders[index] ? {
            license_plate: pile.queue_orders[index].vehicle_license_plate,
            record_number: pile.queue_orders[index].record_number,
            queue_position: index + 1
          } : null
        }))
        
        return {
          ...pile,
          chargingVehicle,
          queueSpots
        }
      })
    
    return piles
  } catch (error) {
    console.error('处理慢充充电桩数据时出错:', error)
    return []
  }
})

const totalChargingSpots = computed(() => {
  try {
    return (chargingPiles.value || []).length // 充电桩数量，每个桩一个充电位
  } catch (error) {
    console.error('计算充电车位总数时出错:', error)
    return 0
  }
})

// 滚动处理
const handleQueueScroll = (event) => {
  event.preventDefault()
  const scrollContainer = event.target.closest('.queue-scroll')
  if (scrollContainer) {
    scrollContainer.scrollLeft += event.deltaY
  }
}

// 自动刷新控制
const toggleAutoRefresh = (value) => {
  if (value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh() // 确保没有重复的定时器
  refreshInterval.value = setInterval(() => {
    fetchAllData()
  }, 30000) // 30秒刷新一次
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// 获取充电桩状态样式类
const getPileStatusClass = (status) => {
  const statusMap = {
    'normal': 'normal',
    'idle': 'normal', 
    'fault': 'fault',
    'maintenance': 'maintenance'
  }
  return statusMap[status] || 'unknown'
}

// 防抖标记，避免重复调用
let isFetching = false

// 内部数据获取方法（不管理loading状态）
const fetchAllData = async () => {
  if (isFetching) {
    console.log('⏸️ 数据获取中，跳过重复调用')
    return
  }
  
  isFetching = true
  
  try {
    console.log('🔄 开始获取场景数据...')
    
    // 并行获取数据，提高效率
    const [vehiclesResult, pilesResult, configResult] = await Promise.allSettled([
      fetchVehicles(),
      fetchChargingPiles(),
      fetchSystemConfig()
    ])
    
    // 检查是否有失败的请求
    const failedRequests = [vehiclesResult, pilesResult, configResult]
      .filter(result => result.status === 'rejected')
    
    if (failedRequests.length > 0) {
      console.warn('⚠️ 部分数据获取失败:', failedRequests.length)
    }
    
    console.log('✅ 场景数据获取完成')
    
    // 确保DOM更新后再触发动画（减少延迟）
    await nextTick()
    triggerVehicleAnimations()
    
  } catch (error) {
    console.error('❌ 获取场景数据失败:', error)
    throw error
  } finally {
    isFetching = false
  }
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
    
    // 注释掉旧的车辆分配逻辑，新的逻辑在计算属性中处理
    // 旧的充电车辆分配逻辑已移至计算属性中处理
    console.log('✅ 获取充电桩数据成功，数量:', chargingPiles.value.length)
  } catch (error) {
    console.error('获取充电桩数据失败:', error)
    chargingPiles.value = []
    throw error
  }
}

// fetchQueueData 函数已被删除，因为不再使用队列数据
// 现在从 fetchChargingPiles API 获取所有相关信息

const fetchSystemConfig = async () => {
  try {
    const response = await api.get('/users/charging/config')
    systemConfig.value = response || {}
    console.log('✅ 获取系统配置成功:', {
      快充功率: response.fast_charging_power,
      慢充功率: response.trickle_charging_power
    })
  } catch (error) {
    console.error('获取系统配置失败:', error)
    // 使用默认值
    systemConfig.value = {
      fast_charging_power: 30,
      trickle_charging_power: 7
    }
    throw error
  }
}

const triggerVehicleAnimations = () => {
  // 避免过于频繁的动画触发
  if (loading.value) return
  
  try {
    const vehicleElements = document.querySelectorAll('.vehicle-item')
    
    if (vehicleElements.length === 0) {
      return // 静默处理，避免过多日志
    }
    
    // 批量处理DOM操作，减少重排
    requestAnimationFrame(() => {
      vehicleElements.forEach((el, index) => {
        // 移除可能存在的旧动画类
        el.classList.remove('vehicle-enter')
        
        // 设置动画延迟
        el.style.animationDelay = `${index * 0.1}s`
      })
      
      // 在下一帧添加动画类
      requestAnimationFrame(() => {
        vehicleElements.forEach(el => {
          el.classList.add('vehicle-enter')
        })
      })
    })
  } catch (error) {
    console.error('动画触发失败:', error)
  }
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





// 显示暂留区车辆详情（只显示车辆信息，不显示订单）
const showStayingVehicleDetail = async (vehicle) => {
  try {
    if (!vehicle || !vehicle.id) {
      console.warn('车辆数据无效:', vehicle)
      ElMessage.warning('车辆数据无效')
      return
    }
    
    console.log('🚗 显示暂留区车辆详情:', vehicle.license_plate)
    selectedVehicle.value = { ...vehicle }
    selectedVehicleOrder.value = null // 暂留区车辆不显示订单信息
    
    vehicleDetailVisible.value = true
  } catch (error) {
    console.error('显示车辆详情失败:', error.message || error)
    ElMessage.error('显示车辆详情失败')
  }
}

// 显示订单详情（充电区和等待区的车辆实际上是订单）
const showOrderDetail = async (orderData) => {
  try {
    if (!orderData || !orderData.record_number) {
      console.warn('订单数据无效:', orderData)
      ElMessage.warning('订单数据无效')
      return
    }
    
    console.log('📋 显示订单详情:', orderData.record_number)
    
    // 根据订单数据获取完整的订单和车辆信息
    try {
      const response = await api.get(`/admin/charging-record/${orderData.record_number}`)
      
      // 构建车辆信息（用于显示）
      selectedVehicle.value = {
        id: response.vehicle_id,
        license_plate: response.license_plate,
        model: response.vehicle?.model || '未知型号',
        battery_capacity: response.vehicle?.battery_capacity || 0,
        status: response.status === 'charging' ? '充电中' : '排队中',
        owner: response.vehicle?.owner || null
      }
      
      // 设置订单信息
      selectedVehicleOrder.value = {
        record_number: response.record_number,
        queue_number: response.queue_number,
        license_plate: response.license_plate,
        charging_amount: response.charging_amount,
        charging_duration: response.charging_duration,
        remaining_time: response.remaining_time,
        start_time: response.start_time,
        end_time: response.end_time,
        electricity_fee: response.electricity_fee,
        service_fee: response.service_fee,
        total_fee: response.total_fee,
        charging_mode: response.charging_mode,
        status: response.status,
        created_at: response.created_at
      }
      
      vehicleDetailVisible.value = true
      
      console.log('✅ 获取到完整订单信息:', {
        订单编号: response.record_number,
        车牌号: response.license_plate,
        剩余时间: response.remaining_time,
        状态: response.status
      })
      
    } catch (error) {
      console.error('获取订单详情失败:', error.message || error)
      ElMessage.error('获取订单详情失败')
    }
    
  } catch (error) {
    console.error('显示订单详情失败:', error.message || error)
    ElMessage.error('显示订单详情失败')
  }
}

// 兼容旧版本的通用点击处理函数
const showVehicleDetail = async (vehicle) => {
  // 判断是否为订单数据还是车辆数据
  if (vehicle.record_number) {
    // 如果有record_number，说明这是订单数据
    await showOrderDetail(vehicle)
  } else if (vehicle.id) {
    // 如果有id但没有record_number，说明这是暂留区的车辆数据
    await showStayingVehicleDetail(vehicle)
  } else {
    console.warn('无法识别的数据类型:', vehicle)
    ElMessage.warning('数据类型错误')
  }
}

const getPileStatusText = (status) => {
  const statusMap = {
    'normal': '空闲',
    'idle': '空闲',
    'charging': '使用中',
    'fault': '故障',
    'maintenance': '维护中'
  }
  return statusMap[status] || `未知(${status})`
}

const getVehicleStatusType = (status) => {
  const typeMap = {
    '暂留': 'info',
    '等候': 'warning',
    '充电中': 'success',
    'registered': 'info',
    'waiting': 'warning',
    'charging': 'success',
    'completed': 'info'
  }
  return typeMap[status] || 'info'
}

const getVehicleStatusText = (status) => {
  const textMap = {
    '暂留': '暂留',
    '等候': '等候',
    '充电中': '充电中',
    'registered': '已注册',
    'waiting': '排队中',
    'charging': '充电中',
    'completed': '已完成'
  }
  return textMap[status] || status || '未知'
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString()
}

const formatDuration = (duration) => {
  if (!duration) return ''
  const hours = Math.floor(duration)
  const minutes = Math.round((duration - hours) * 60)
  if (hours > 0) {
    return minutes > 0 ? `${hours}小时${minutes}分钟` : `${hours}小时`
  } else {
    return `${minutes}分钟`
  }
}

// 获取充电时间显示（xx分钟）
const getChargingTime = (vehicle) => {
  if (!vehicle || !vehicle.start_time) return ''
  
  const startTime = new Date(vehicle.start_time)
  const now = new Date()
  const diffMs = now - startTime
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  
  return `${diffMinutes}分钟`
}

// 判断车辆是否在队列中或充电中（非暂留区） - 已不再使用
// const isVehicleInQueueOrCharging = (vehicle) => {
//   // 这个函数已被 stayingVehicles computed 替代
// }

// 计算预计充电时长（基于预计完成时间）
const getEstimatedDuration = (orderData) => {
  if (!orderData.estimated_completion_time || !orderData.start_time) return null
  
  const start = new Date(orderData.start_time)
  const end = new Date(orderData.estimated_completion_time)
  const durationHours = (end - start) / (1000 * 60 * 60)
  
  if (durationHours > 0) {
    return formatDuration(durationHours)
  }
  return null
}

// 基于充电量计算预计充电时长
const getEstimatedDurationByAmount = (orderData) => {
  if (!orderData.charging_amount || !orderData.charging_mode) return '未知'
  
  // 根据充电模式计算预计时长 - 使用配置服务的功率
  const power = orderData.charging_mode === 'fast' 
    ? (systemConfig.value.fast_charging_power) 
    : (systemConfig.value.trickle_charging_power)
  const estimatedHours = orderData.charging_amount / power
  
  return formatDuration(estimatedHours)
}

// 格式化剩余时间
const formatRemainingTime = (minutes) => {
  if (minutes === null || minutes === undefined) return '未知'
  if (minutes <= 0) return '即将完成'
  
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  
  if (hours > 0) {
    return `${hours}小时${remainingMinutes}分钟`
  } else {
    return `${remainingMinutes}分钟`
  }
}

// 获取剩余时间标签类型
const getRemainingTimeTagType = (minutes) => {
  if (minutes === null || minutes === undefined) return 'info'
  if (minutes <= 0) return 'success'
  if (minutes <= 15) return 'danger'   // 15分钟内 - 红色
  if (minutes <= 60) return 'warning'  // 1小时内 - 橙色  
  return 'primary'                     // 超过1小时 - 蓝色
}

// 剩余时间相关函数（简化版，主要数据已经从充电桩API获取）
const getVehicleRemainingTime = async (vehicle_id) => {
  try {
    const response = await api.get(`/admin/vehicle/${vehicle_id}/order`)
    if (response && response.remaining_time !== null && response.remaining_time !== undefined) {
      return response.remaining_time
    }
    return null
  } catch (error) {
    console.warn(`获取车辆 ${vehicle_id} 剩余时间失败:`, error)
    return null
  }
}

// 旧的 fetchVehicleOrder 函数已被删除，因为依赖队列数据
// 现在直接在 showOrderDetail 中通过订单编号获取详细信息

// 不再生成假的订单编号，避免误导用户

// 计算预估费用
const calculateEstimatedFee = (amount) => {
  // 使用简单的费用计算逻辑
  const electricityPrice = 1.0 // 1元/度
  const servicePrice = 0.5 // 0.5元/度
  
  const electricity_fee = amount * electricityPrice
  const service_fee = amount * servicePrice
  const total_fee = electricity_fee + service_fee
  
  return {
    electricity_fee: parseFloat(electricity_fee.toFixed(2)),
    service_fee: parseFloat(service_fee.toFixed(2)),
    total_fee: parseFloat(total_fee.toFixed(2))
  }
}

// 获取订单状态类型
const getOrderStatusType = (status) => {
  const typeMap = {
    'created': 'info',
    'assigned': 'warning', 
    'charging': 'success',
    'completed': 'success',
    'cancelled': 'danger',
    'waiting': 'warning',
    'queuing': 'warning'
  }
  return typeMap[status] || 'info'
}

// 获取订单状态文本
const getOrderStatusText = (status) => {
  const textMap = {
    'created': '已创建',
    'assigned': '已分配',
    'charging': '充电中',
    'completed': '已完成',
    'cancelled': '已取消',
    'waiting': '等候中',
    'queuing': '排队中'
  }
  return textMap[status] || status
}

// 检查是否可以管理车辆
const canManageVehicle = (vehicle) => {
  if (!vehicle) return false
  return vehicle.status === '等候' || vehicle.status === '充电中' || 
         vehicle.status === 'waiting' || vehicle.status === 'charging'
}

// 管理操作方法
const cancelQueue = async (vehicle) => {
  if (!vehicle.queue_id) {
    // 从queueData中查找对应的queue_id
    const queueItem = queueData.value.find(q => 
      q.vehicle && q.vehicle.id === vehicle.id && 
      (q.status === 'waiting' || q.status === 'queuing')
    )
    if (!queueItem) {
      ElMessage.error('找不到对应的排队记录')
      return
    }
    vehicle.queue_id = queueItem.id
  }

  try {
    await ElMessageBox.confirm(
      `确定要取消车辆 "${vehicle.license_plate}" 的排队吗？`,
      '确认取消排队',
      {
        type: 'warning',
        confirmButtonText: '确认取消',
        cancelButtonText: '保留排队'
      }
    )

    // 设置加载状态
    vehicle.cancelling = true

    await api.delete(`/admin/queue/${vehicle.queue_id}/cancel`)
    
    ElMessage.success(`已取消车辆 ${vehicle.license_plate} 的排队`)
    console.log(`✅ 取消排队成功: ${vehicle.license_plate}`)
    
    // 刷新数据
    await fetchAllData()
    
    // 关闭弹窗
    vehicleDetailVisible.value = false
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消排队失败:', error)
      ElMessage.error('取消排队失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    vehicle.cancelling = false
  }
}

const stopCharging = async (vehicle) => {
  if (!vehicle.queue_id) {
    // 从queueData中查找对应的queue_id
    const queueItem = queueData.value.find(q => 
      q.vehicle && q.vehicle.id === vehicle.id && q.status === 'charging'
    )
    if (!queueItem) {
      ElMessage.error('找不到对应的充电记录')
      return
    }
    vehicle.queue_id = queueItem.id
  }

  try {
    await ElMessageBox.confirm(
      `确定要强制停止车辆 "${vehicle.license_plate}" 的充电吗？\n系统将自动计算费用并生成充电记录。`,
      '确认停止充电',
      {
        type: 'warning',
        confirmButtonText: '确认停止',
        cancelButtonText: '继续充电'
      }
    )

    // 设置加载状态
    vehicle.stopping = true

    const response = await api.post(`/admin/queue/${vehicle.queue_id}/stop-charging`)
    
    ElMessage.success(`已停止车辆 ${vehicle.license_plate} 的充电`)
    console.log(`✅ 停止充电成功: ${vehicle.license_plate}`, response)
    
    // 显示充电记录信息
    if (response.charging_record) {
      ElMessage.info(
        `充电记录已生成：${response.charging_record.record_number}，` +
        `充电时长 ${response.charging_record.duration_hours}h，` +
        `费用 ¥${response.charging_record.total_fee}`
      )
    }
    
    // 刷新数据
    await fetchAllData()
    
    // 关闭弹窗
    vehicleDetailVisible.value = false
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('停止充电失败:', error)
      ElMessage.error('停止充电失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    vehicle.stopping = false
  }
}



// 生命周期
onMounted(async () => {
  console.log('🚀 充电场景页面已挂载，开始初始化...')
  
  try {
    await refreshScene()
    
    // 如果开启自动刷新，启动定时器
    if (autoRefresh.value) {
      startAutoRefresh()
    }
    
    console.log('✅ 页面初始化完成')
  } catch (error) {
    console.error('❌ 页面初始化失败:', error)
    ElMessage.error('页面初始化失败，请刷新重试')
  }
})

// 组件卸载时清除定时器
onUnmounted(() => {
  stopAutoRefresh()
  console.log('🧹 组件卸载，清理资源')
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
.stat-color.fast-waiting { background: #409EFF; }
.stat-color.trickle-waiting { background: #E6A23C; }
.stat-color.fast-charging { background: #67C23A; }
.stat-color.trickle-charging { background: #F56C6C; }
.stat-color.total { background: #303133; }

.scene-main {
  display: grid;
  grid-template-columns: 1fr 1fr 2fr;
  gap: 20px;
  min-height: 900px;
  max-height: calc(100vh - 300px);
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
  overflow: hidden; /* 确保内容不会溢出 */
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
  /* 优化滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

/* 暂留区专用布局 - 从上到下紧凑排列 */
.stay-area .vehicle-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 10px; /* 行间距8px, 列间距10px */
  align-content: flex-start;
  justify-content: flex-start;
}

.vehicle-grid::-webkit-scrollbar {
  width: 6px;
}

.vehicle-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.vehicle-grid::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.vehicle-grid::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 等候区样式 */
.waiting-area {
  border-left: 4px solid #409EFF;
}

/* 双栏布局 */
.waiting-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  height: 100%;
}

.waiting-column {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
}

.waiting-column.fast {
  border-left: 3px solid #409EFF;
}

.waiting-column.trickle {
  border-left: 3px solid #E6A23C;
}

.column-header {
  padding: 10px 12px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.column-header h4 {
  margin: 0;
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

.column-count {
  font-size: 12px;
  color: #606266;
}

.column-content {
  padding: 10px;
  height: calc(100% - 45px);
  overflow-y: auto;
}

.empty-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 150px;
  color: #c0c4cc;
  gap: 8px;
}

.empty-column span {
  font-size: 12px;
}

.queue-line {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  overflow-y: auto;
  /* 优化滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.queue-line::-webkit-scrollbar {
  width: 6px;
}

.queue-line::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.queue-line::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.queue-line::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 充电区样式 */
.charging-area {
  border-left: 4px solid #67C23A;
}

.charging-section {
  margin-bottom: 30px;
}

.charging-section h4 {
  margin: 0 0 15px 0;
  padding: 10px 15px;
  background: #f8f9fa;
  border-radius: 6px;
  color: #303133;
  font-size: 14px;
  border-left: 3px solid #67C23A;
}

.charging-section.fast h4 {
  border-left-color: #409EFF;
}

.charging-section.trickle h4 {
  border-left-color: #E6A23C;
}

.charging-piles {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: calc(50vh - 200px);
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

/* 为WebKit浏览器优化滚动条 */
.charging-piles::-webkit-scrollbar {
  width: 8px;
}

.charging-piles::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.charging-piles::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.charging-piles::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
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

/* 新的充电桩样式 */
.charging-pile.fast {
  border-left: 3px solid #409EFF;
}

.charging-pile.trickle {
  border-left: 3px solid #E6A23C;
}

.pile-header h5 {
  margin: 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.pile-power {
  color: #606266;
  font-size: 12px;
  font-weight: 500;
}

/* 可滑动的排队容器 */
.pile-queue-container {
  position: relative;
}

.queue-scroll {
  display: flex;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  padding-bottom: 10px;
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.queue-scroll::-webkit-scrollbar {
  height: 6px;
}

.queue-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.queue-scroll::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.queue-scroll::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.queue-spots {
  display: flex;
  gap: 10px;
  min-width: max-content;
}

.scroll-hint {
  text-align: center;
  color: #909399;
  font-size: 11px;
  margin-top: 5px;
}

.pile-spots {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.charging-spot {
  border: 2px solid #e4e7ed;
  border-radius: 6px;
  padding: 10px;
  min-width: 120px;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.charging-spot.active {
  border-color: #67C23A;
  border-width: 3px;
  background: #f0f9ff;
}

.charging-spot.queue {
  border-style: dashed;
  border-color: #409EFF;
}

.spot-label {
  position: absolute;
  top: 5px;
  left: 5px;
  font-size: 10px;
  color: #909399;
  background: white;
  padding: 2px 4px;
  border-radius: 2px;
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
  position: relative;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: vehicleEnter 0.6s ease-out forwards;
  opacity: 0;
  transform: translateY(20px);
  min-width: 80px;
  max-width: 100px;
}

/* 暂留区车辆样式 - 小矩形固定大小 */
.stay-area .vehicle-item {
  padding: 6px 8px;
  width: 120px !important;
  height: 60px !important;
  min-width: unset;
  max-width: unset;
  border: 2px solid #909399 !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.vehicle-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}



/* 车辆详情弹窗样式 */
.vehicle-detail {
  .owner-info {
    margin-top: 20px;
    
    h4 {
      color: #333;
      margin-bottom: 10px;
    }
  }
  
  .charging-order-info {
    margin-top: 20px;
    
    h4 {
      color: #333;
      margin-bottom: 10px;
      border-bottom: 2px solid #409EFF;
      padding-bottom: 8px;
    }
  }
  
  .management-actions {
    margin-top: 20px;
    
    .action-buttons {
      display: flex;
      gap: 10px;
      justify-content: flex-start;
      
      .el-button {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }
}

/* 订单弹窗中的订单号样式 */
.el-descriptions .order-number,
.charging-order-info .order-number {
  font-family: 'Courier New', monospace;
  font-weight: bold;
  color: #409EFF;
  background: #f0f9ff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  position: static !important;
  width: auto !important;
  height: auto !important;
  display: inline !important;
}

/* 订单弹窗中的队列号样式 */
.el-descriptions .queue-number,
.charging-order-info .queue-number {
  font-family: 'Courier New', monospace;
  font-weight: bold;
  color: #E6A23C;
  background: #fdf6ec;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  position: static !important;
  width: auto !important;
  height: auto !important;
  display: inline !important;
}

/* 充电订单信息容器 */
.charging-order-info {
  font-size: 14px;
}

.charging-order-info .el-descriptions {
  font-size: 14px;
}

.charging-order-info .el-descriptions-item__label {
  font-size: 14px !important;
}

.charging-order-info .el-descriptions-item__content {
  font-size: 14px !important;
}

.charging-duration-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.remaining-time-info {
  display: flex;
  align-items: center;
  gap: 5px;
}

.pile-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.pile-info-row .remaining-time {
  flex: 1;
  min-width: 0;
}

.pile-info-row .pile-power {
  flex-shrink: 0;
  font-weight: bold;
  color: #409EFF;
}

.estimated-duration {
  font-size: 12px;
  opacity: 0.8;
}

/* 描述列表标签样式 */
:deep(.order-label) {
  color: #409EFF !important;
  font-weight: 600;
}

:deep(.queue-label) {
  color: #E6A23C !important;
  font-weight: 600;
}

.vehicle-item.stay {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border: 2px solid #909399;
}

.vehicle-item.waiting.fast {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border: 1px solid #409EFF;
}

.vehicle-item.waiting.trickle {
  background: linear-gradient(135deg, #fff3e0, #ffcc80);
  border: 1px solid #E6A23C;
}

.vehicle-item.queuing {
  background: linear-gradient(135deg, #f3e5f5, #ce93d8);
  border: 1px solid #9c27b0;
}

.vehicle-item.charging {
  background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
  border: 1px solid #67C23A;
}

.vehicle-icon {
  text-align: center;
  font-size: 20px;
  margin-bottom: 6px;
}

/* 暂留区车辆图标 - 小矩形紧凑样式 */
.stay-area .vehicle-icon {
  font-size: 16px;
  margin-bottom: 1px;
}

.vehicle-item.stay .vehicle-icon { color: #909399; }
.vehicle-item.waiting.fast .vehicle-icon { color: #409EFF; }
.vehicle-item.waiting.trickle .vehicle-icon { color: #E6A23C; }
.vehicle-item.queuing .vehicle-icon { color: #9c27b0; }
.vehicle-item.charging .vehicle-icon { color: #67C23A; }

.vehicle-info {
  text-align: center;
}

.vehicle-plate {
  font-weight: bold;
  color: #303133;
  margin-bottom: 3px;
  font-size: 11px;
}

.charging-time {
  font-size: 9px;
  color: #67C23A;
  font-weight: bold;
  margin-bottom: 3px;
  line-height: 1;
}

.vehicle-status {
  color: #606266;
  font-size: 10px;
  margin-bottom: 3px;
}

/* 暂留区车辆信息 - 小矩形紧凑样式 */
.stay-area .vehicle-plate {
  font-size: 15px;
  margin-bottom: 6px;
  line-height: 1.2;
}

.stay-area .vehicle-status {
  font-size: 10px;
  margin-bottom: 5px;
  line-height: 1;
}

.charging-progress {
  margin-top: 5px;
}

/* 车辆上的排队号徽章样式 */
.vehicle-item .queue-number {
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

/* 空区域样式 */
.empty-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #c0c4cc;
  gap: 10px;
}

/* 排队位置指示器 */
.queue-position {
  position: absolute;
  top: -8px;
  left: -8px;
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

.queue-position-indicator {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #9c27b0;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: bold;
}

/* 充电指示器 */
.charging-indicator {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #67C23A;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s infinite;
}

.charging-icon {
  font-size: 12px;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
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