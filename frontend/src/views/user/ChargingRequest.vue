<template>
  <div class="charging-request">
    <h1>充电请求</h1>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>提交充电请求</span>
            </div>
          </template>
          
          <el-form
            ref="requestFormRef"
            :model="requestForm"
            :rules="requestRules"
            label-width="120px"
          >
            <el-form-item label="选择车辆" prop="vehicle_id">
              <el-select
                v-model="requestForm.vehicle_id"
                placeholder="请选择车辆"
                style="width: 100%"
                @change="onVehicleChange"
              >
                <el-option
                  v-for="vehicle in vehicles"
                  :key="vehicle.id"
                  :label="`${vehicle.license_plate} (${vehicle.model || '未知型号'})`"
                  :value="vehicle.id"
                />
              </el-select>
              <div v-if="selectedVehicle" class="vehicle-info">
                电池容量: {{ selectedVehicle.battery_capacity }}度
              </div>
            </el-form-item>
            
            <el-form-item label="充电模式" prop="charging_mode">
              <el-radio-group v-model="requestForm.charging_mode" @change="calculateEstimates">
                <el-radio label="fast">快充 ({{ chargingPowerConfig.fast_charging_power }}度/小时)</el-radio>
                <el-radio label="trickle">慢充 ({{ chargingPowerConfig.trickle_charging_power }}度/小时)</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="充电量" prop="requested_amount">
              <el-input-number
                v-model="requestForm.requested_amount"
                :min="1"
                :max="selectedVehicle?.battery_capacity || 100"
                :step="1"
                style="width: 100%"
                @change="calculateEstimates"
              />
              <div class="amount-info">
                <span>单位: 度</span>
                <span v-if="selectedVehicle">
                  最大: {{ selectedVehicle.battery_capacity }}度
                </span>
              </div>
            </el-form-item>
            
            <!-- 预计费用和时间显示 -->
            <div v-if="estimatedCost || estimatedTime" class="estimation-display">
              <h4>预估信息</h4>
              <el-row :gutter="20">
                <el-col :span="12" v-if="estimatedTime">
                  <div class="estimate-item">
                    <span class="estimate-label">预计充电时间:</span>
                    <span class="estimate-value time">{{ estimatedTime }}</span>
                  </div>
                </el-col>
                <el-col :span="12" v-if="estimatedCost">
                  <div class="estimate-item">
                    <span class="estimate-label">预计总费用:</span>
                    <span class="estimate-value cost">¥{{ estimatedCost }}</span>
                  </div>
                </el-col>
              </el-row>
              <div class="cost-breakdown" v-if="costBreakdown">
                <div class="breakdown-row">
                  <span>电费 ({{ getCurrentTimePeriod() }}):</span>
                  <span>¥{{ costBreakdown.electricityCost }}</span>
                </div>
                <div class="breakdown-row">
                  <span>服务费:</span>
                  <span>¥{{ costBreakdown.serviceCost }}</span>
                </div>
                <div class="breakdown-note">
                  <el-text size="small" type="info">
                    *费用按当前时段电价计算，实际费用以充电完成时电价为准
                  </el-text>
                </div>
              </div>
            </div>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                @click="submitRequest"
              >
                提交请求
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>当前等待情况</span>
              <el-button type="text" @click="refreshWaitingInfo">刷新</el-button>
            </div>
          </template>
          
          <div class="waiting-info">
            <div class="waiting-item">
              <div class="waiting-label">快充等待数量:</div>
              <div class="waiting-value">{{ waitingInfo.fast }}辆</div>
            </div>
            <div class="waiting-item">
              <div class="waiting-label">慢充等待数量:</div>
              <div class="waiting-value">{{ waitingInfo.trickle }}辆</div>
            </div>
          </div>
          
          <el-divider />
          
          <div class="pricing-info">
            <h3>计费说明</h3>
            <div class="price-table">
              <div class="price-row">
                <span>峰时 (10:00-15:00, 18:00-21:00)</span>
                <span>1.0元/度</span>
              </div>
              <div class="price-row">
                <span>平时 (7:00-10:00, 15:00-18:00, 21:00-23:00)</span>
                <span>0.7元/度</span>
              </div>
              <div class="price-row">
                <span>谷时 (23:00-次日7:00)</span>
                <span>0.4元/度</span>
              </div>
              <div class="price-row">
                <span>服务费</span>
                <span>0.8元/度</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import api from '@/utils/api'

const route = useRoute()
const requestFormRef = ref()
const loading = ref(false)
const vehicles = ref([])
const waitingInfo = reactive({
  fast: 0,
  trickle: 0
})

const requestForm = reactive({
  vehicle_id: null,
  charging_mode: 'fast',
  requested_amount: 10
})

const requestRules = {
  vehicle_id: [
    { required: true, message: '请选择车辆', trigger: 'change' }
  ],
  charging_mode: [
    { required: true, message: '请选择充电模式', trigger: 'change' }
  ],
  requested_amount: [
    { required: true, message: '请输入充电量', trigger: 'blur' },
    { type: 'number', min: 1, message: '充电量不能小于1度', trigger: 'blur' }
  ]
}

const selectedVehicle = computed(() => {
  return vehicles.value.find(v => v.id === requestForm.vehicle_id)
})

const chargingPowerConfig = ref({
  fast_charging_power: 30.0,
  trickle_charging_power: 10.0
})

// 计费配置
const billingConfig = ref({
  peak_time_price: 1.0,
  normal_time_price: 0.7,
  valley_time_price: 0.4,
  service_fee_price: 0.8,
  time_periods: {
    peak_times: [[10, 15], [18, 21]],
    normal_times: [[7, 10], [15, 18], [21, 23]],
    valley_times: [[23, 7]]
  }
})

// 预计费用和时间
const estimatedCost = ref('')
const estimatedTime = ref('')
const costBreakdown = ref(null)

const fetchChargingConfig = async () => {
  try {
    // 使用用户端API获取充电桩配置
    const config = await api.get('/users/charging/config')
    chargingPowerConfig.value.fast_charging_power = config.fast_charging_power
    chargingPowerConfig.value.trickle_charging_power = config.trickle_charging_power
    
    // 同时获取计费配置
    if (config.billing) {
      billingConfig.value = {
        ...billingConfig.value,
        ...config.billing
      }
    }
  } catch (error) {
    console.error('获取充电配置失败:', error)
    // 使用默认值，不阻塞功能
    chargingPowerConfig.value = {
      fast_charging_power: 30.0,
      trickle_charging_power: 7.0
    }
  }
}

const onVehicleChange = () => {
  if (selectedVehicle.value) {
    // 重置充电量为合理值
    requestForm.requested_amount = Math.min(10, selectedVehicle.value.battery_capacity)
    // 计算预估值
    setTimeout(calculateEstimates, 100)
  }
}

// 获取当前时段
const getCurrentTimePeriod = () => {
  const hour = new Date().getHours()
  const periods = billingConfig.value.time_periods
  
  // 检查峰时
  for (const [start, end] of periods.peak_times || []) {
    if (hour >= start && hour < end) return '峰时'
  }
  
  // 检查谷时（需要处理跨日情况）
  for (const [start, end] of periods.valley_times || []) {
    if (start > end) { // 跨日情况，如23:00-7:00
      if (hour >= start || hour < end) return '谷时'
    } else {
      if (hour >= start && hour < end) return '谷时'
    }
  }
  
  // 默认为平时
  return '平时'
}

// 获取当前电价
const getCurrentElectricityPrice = () => {
  const period = getCurrentTimePeriod()
  switch (period) {
    case '峰时': return billingConfig.value.peak_time_price
    case '谷时': return billingConfig.value.valley_time_price
    default: return billingConfig.value.normal_time_price
  }
}

// 计算预计费用和时间
const calculateEstimates = () => {
  if (!requestForm.requested_amount || !requestForm.charging_mode || !selectedVehicle.value) {
    estimatedCost.value = ''
    estimatedTime.value = ''
    costBreakdown.value = null
    return
  }
  
  // 计算充电时间：充电量/充电效率 = 时间
              // 例如：50度 / 50kW = 1h = 60分钟
  const power = requestForm.charging_mode === 'fast' 
    ? chargingPowerConfig.value.fast_charging_power 
    : chargingPowerConfig.value.trickle_charging_power
  
  const timeHours = requestForm.requested_amount / power
  const totalMinutes = Math.round(timeHours * 60)
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  
  if (hours > 0) {
    estimatedTime.value = minutes > 0 ? `${hours}小时${minutes}分钟` : `${hours}小时`
  } else {
    estimatedTime.value = `${minutes}分钟`
  }
  
  // 计算费用
  const electricityPrice = getCurrentElectricityPrice()
  const serviceFeePrice = billingConfig.value.service_fee_price
  
  const electricityCost = (requestForm.requested_amount * electricityPrice).toFixed(2)
  const serviceCost = (requestForm.requested_amount * serviceFeePrice).toFixed(2)
  const totalCost = (parseFloat(electricityCost) + parseFloat(serviceCost)).toFixed(2)
  
  estimatedCost.value = totalCost
  costBreakdown.value = {
    electricityCost,
    serviceCost
  }
}

const fetchVehicles = async () => {
  try {
    vehicles.value = await api.get('/users/vehicles')
    
    // 检查URL参数，预选车辆
    const vehicleId = route.query.vehicleId
    if (vehicleId) {
      const targetVehicle = vehicles.value.find(v => v.id == vehicleId)
      if (targetVehicle) {
        requestForm.vehicle_id = targetVehicle.id
        onVehicleChange()
      }
    }
  } catch (error) {
    console.error('获取车辆列表失败:', error)
  }
}

const refreshWaitingInfo = async () => {
  try {
    const fastWaiting = await api.get('/charging/waiting-count/fast')
    const trickleWaiting = await api.get('/charging/waiting-count/trickle')
    
    waitingInfo.fast = fastWaiting.waiting_count
    waitingInfo.trickle = trickleWaiting.waiting_count
  } catch (error) {
    console.error('获取等待信息失败:', error)
  }
}

const submitRequest = async () => {
  if (!requestFormRef.value) return
  
  await requestFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await api.post('/charging/request', requestForm)
        ElMessage.success(`充电请求提交成功！排队号码: ${response.queue_number}`)
        resetForm()
        refreshWaitingInfo()
      } catch (error) {
        console.error('提交充电请求失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const resetForm = () => {
  if (requestFormRef.value) {
    requestFormRef.value.resetFields()
  }
}

onMounted(() => {
  fetchVehicles()
  refreshWaitingInfo()
  fetchChargingConfig()
})
</script>

<style scoped>
.charging-request {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vehicle-info {
  margin-top: 5px;
  font-size: 12px;
  color: #666;
}

.amount-info {
  margin-top: 5px;
  font-size: 12px;
  color: #666;
  display: flex;
  justify-content: space-between;
}

.waiting-info {
  margin-bottom: 20px;
}

.waiting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.waiting-item:last-child {
  border-bottom: none;
}

.waiting-label {
  color: #666;
}

.waiting-value {
  font-weight: bold;
  color: #409eff;
}

.pricing-info h3 {
  margin-bottom: 15px;
  color: #333;
}

.price-table {
  background: #f9f9f9;
  border-radius: 5px;
  padding: 15px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e6e6e6;
}

.price-row:last-child {
  border-bottom: none;
  font-weight: bold;
  color: #e6a23c;
}

/* 预估显示样式 */
.estimation-display {
  background: #f0f9ff;
  border: 1px solid #409eff;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.estimation-display h4 {
  margin: 0 0 12px 0;
  color: #409eff;
  font-size: 16px;
}

.estimate-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.estimate-label {
  color: #606266;
  font-weight: 500;
}

.estimate-value {
  font-weight: 600;
  color: #2c3e50;
}

.estimate-value.cost {
  color: #e6a23c;
  font-size: 18px;
}

.estimate-value.time {
  color: #67c23a;
  font-size: 16px;
}

.cost-breakdown {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #d9ecff;
}

.breakdown-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 14px;
  color: #606266;
}

.breakdown-note {
  margin-top: 8px;
  text-align: center;
}
</style> 