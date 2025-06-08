<template>
  <div class="vehicle-monitoring">
    <div class="page-header">
      <h2>我的车辆监控</h2>
      <p>实时监控我的车辆充电状态</p>
    </div>

    <div class="monitoring-content">
      <!-- 刷新按钮 -->
      <div class="toolbar">
        <el-button 
          type="primary" 
          @click="fetchVehicleData" 
          :loading="loading"
          icon="Refresh"
        >
          刷新数据
        </el-button>
        <span class="last-update">最后更新: {{ formatTime(lastUpdateTime) }}</span>
      </div>

      <!-- 车辆列表 -->
      <div class="vehicle-grid">
        <div 
          v-for="vehicle in vehicles" 
          :key="vehicle.id" 
          class="vehicle-card"
          :class="getStatusClass(vehicle.status_code)"
          @click="showVehicleDetail(vehicle)"
        >
          <div class="vehicle-header">
            <div class="license-plate">{{ vehicle.license_plate }}</div>
            <el-tag 
              :type="getStatusType(vehicle.status_code)" 
              size="small"
            >
              {{ vehicle.status }}
            </el-tag>
          </div>
          
          <div class="vehicle-info">
            <div class="info-item">
              <span class="label">车型:</span>
              <span class="value">{{ vehicle.model }}</span>
            </div>
            <div class="info-item">
              <span class="label">电池容量:</span>
                              <span class="value">{{ vehicle.battery_capacity }}度</span>
            </div>
            <div class="info-item">
              <span class="label">车主:</span>
              <span class="value">{{ vehicle.owner?.username || '未知' }}</span>
            </div>
            <div class="info-item" v-if="vehicle.last_charging_time">
              <span class="label">上次充电:</span>
              <span class="value">{{ formatTime(vehicle.last_charging_time) }}</span>
            </div>
          </div>

          <!-- 队列信息 -->
          <div v-if="vehicle.queue_info" class="queue-info">
            <div class="queue-number">排队号: {{ vehicle.queue_info.queue_number }}</div>
            <div class="queue-details">
              <span>模式: {{ vehicle.queue_info.charging_mode === 'fast' ? '快充' : '慢充' }}</span>
                              <span>需求: {{ vehicle.queue_info.requested_amount }}度</span>
            </div>
          </div>

          <div class="card-footer">
            <el-button size="small" type="primary" plain>查看详情</el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && vehicles.length === 0" class="empty-state">
        <el-empty description="暂无车辆数据" />
      </div>
    </div>

    <!-- 车辆详情弹窗 -->
    <el-dialog 
      v-model="showDetailDialog" 
      :title="`车辆详情 - ${selectedVehicle?.license_plate}`"
      width="600px"
      @close="closeDetailDialog"
    >
      <div v-if="vehicleDetail" class="vehicle-detail">
        <!-- 基本信息 - 可折叠 -->
        <el-collapse v-model="activePanels" class="detail-collapse">
          <el-collapse-item title="基本信息" name="basic">
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="detail-item">
                  <label>车牌号:</label>
                  <span>{{ vehicleDetail.license_plate }}</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="detail-item">
                  <label>当前状态:</label>
                  <el-tag :type="getStatusType(vehicleDetail.status_code)">
                    {{ vehicleDetail.status }}
                  </el-tag>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="detail-item">
                  <label>车型:</label>
                  <span>{{ vehicleDetail.model }}</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="detail-item">
                  <label>电池容量:</label>
                  <span>{{ vehicleDetail.battery_capacity }}度</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="detail-item">
                  <label>车主:</label>
                  <span>{{ vehicleDetail.owner?.username }}</span>
                </div>
              </el-col>
              <el-col :span="12" v-if="vehicleDetail.last_charging_time">
                <div class="detail-item">
                  <label>上次充电:</label>
                  <span>{{ formatTime(vehicleDetail.last_charging_time) }}</span>
                </div>
              </el-col>
            </el-row>
          </el-collapse-item>

          <!-- 最近充电记录 - 可折叠 -->
          <el-collapse-item 
            title="最近充电记录" 
            name="history"
            v-if="vehicleDetail.charging_history && vehicleDetail.charging_history.length > 0"
          >
            <el-table :data="vehicleDetail.charging_history" size="small">
              <el-table-column prop="record_number" label="记录号" width="120"/>
              <el-table-column prop="charging_amount" label="充电量(度)" width="100"/>
              <el-table-column prop="charging_duration" label="时长(h)" width="80"/>
              <el-table-column prop="total_fee" label="费用(元)" width="80"/>
              <el-table-column prop="end_time" label="结束时间" width="150">
                <template #default="scope">
                  {{ formatTime(scope.row.end_time) }}
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>

          <!-- 发起充电请求 - 可折叠 -->
          <el-collapse-item 
            title="发起充电请求" 
            name="request"
            v-if="vehicleDetail.status_code === 'registered'"
          >
            <el-form 
              ref="chargingFormRef"
              :model="chargingForm" 
              :rules="chargingRules"
              label-width="100px"
            >
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="充电模式" prop="charging_mode">
                    <el-radio-group v-model="chargingForm.charging_mode" @change="calculateEstimates">
                      <el-radio label="fast">快充 ({{ chargingConfig.fast_charging_power || 60 }}kW)</el-radio>
                      <el-radio label="trickle">慢充 ({{ chargingConfig.trickle_charging_power || 7 }}kW)</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="充电量" prop="requested_amount">
                    <el-input-number
                      v-model="chargingForm.requested_amount"
                      :min="1"
                      :max="vehicleDetail.battery_capacity"
                      :step="1"
                      style="width: 100%"
                      @change="calculateEstimates"
                    />
                    <div class="form-hint">最大: {{ vehicleDetail.battery_capacity }}度</div>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <!-- 预计费用和时间显示 -->
              <div v-if="estimatedCost || estimatedTime" class="estimation-display">
                <el-row :gutter="20">
                  <el-col :span="12" v-if="estimatedTime">
                    <div class="estimate-item">
                      <label>预计充电时间:</label>
                      <span class="estimate-value">{{ estimatedTime }}</span>
                    </div>
                  </el-col>
                  <el-col :span="12" v-if="estimatedCost">
                    <div class="estimate-item">
                      <label>预计总费用:</label>
                      <span class="estimate-value cost">¥{{ estimatedCost }}</span>
                    </div>
                  </el-col>
                </el-row>
                <div class="cost-breakdown" v-if="costBreakdown">
                  <div class="breakdown-item">
                    <span>电费: ¥{{ costBreakdown.electricityCost }}</span>
                    <span>服务费: ¥{{ costBreakdown.serviceCost }}</span>
                  </div>
                  <div class="breakdown-note">
                    <el-text size="small" type="info">
                      *费用按当前{{ getCurrentTimePeriod() }}电价计算，实际费用以充电完成时的电价为准
                    </el-text>
                  </div>
                </div>
              </div>
            </el-form>
          </el-collapse-item>
        </el-collapse>

        <!-- 操作按钮 -->
        <div class="detail-actions">
          <!-- 暂留状态：可以发起请求 -->
          <el-button 
            v-if="vehicleDetail.status_code === 'registered'" 
            type="primary" 
            @click="submitChargingRequest"
            :loading="actionLoading"
          >
            提交充电请求
          </el-button>
          
          <!-- 等候状态：可以修改请求 -->
          <template v-else-if="vehicleDetail.status_code === 'waiting' || vehicleDetail.status_code === 'queuing'">
            <el-button 
              type="warning" 
              @click="modifyChargingRequest"
              :loading="actionLoading"
            >
              修改请求
            </el-button>
            <el-button 
              type="danger" 
              @click="cancelChargingRequest"
              :loading="actionLoading"
            >
              取消请求
            </el-button>
          </template>
          
          <!-- 充电状态：可以结束充电 -->
          <el-button 
            v-else-if="vehicleDetail.status_code === 'charging'" 
            type="success" 
            @click="endCharging"
            :loading="actionLoading"
          >
            结束充电
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi, chargingApi } from '@/api/user'

// 响应式数据
const loading = ref(false)
const actionLoading = ref(false)
const vehicles = ref([])
const lastUpdateTime = ref(null)
const showDetailDialog = ref(false)
const selectedVehicle = ref(null)
const vehicleDetail = ref(null)
const chargingFormRef = ref()

// 折叠面板激活状态
const activePanels = ref(['basic', 'history', 'request'])

// 充电配置
const chargingConfig = ref({
  fast_charging_power: 60,
  trickle_charging_power: 7
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

// 充电请求表单
const chargingForm = reactive({
  charging_mode: 'fast',
  requested_amount: 10
})

// 预计费用和时间
const estimatedCost = ref('')
const estimatedTime = ref('')
const costBreakdown = ref(null)

// 充电请求表单验证规则
const chargingRules = {
  charging_mode: [
    { required: true, message: '请选择充电模式', trigger: 'change' }
  ],
  requested_amount: [
    { required: true, message: '请输入充电量', trigger: 'blur' },
    { type: 'number', min: 1, message: '充电量不能小于1度', trigger: 'blur' }
  ]
}

// 获取车辆监控数据
const fetchVehicleData = async () => {
  loading.value = true
  try {
    const response = await userApi.getVehicleMonitoring()
    if (response.status === 'success') {
      vehicles.value = response.data
      lastUpdateTime.value = new Date()
    } else {
      ElMessage.error(response.message || '获取车辆数据失败')
    }
  } catch (error) {
    console.error('获取车辆数据失败:', error)
    ElMessage.error('获取车辆数据失败')
  } finally {
    loading.value = false
  }
}

// 显示车辆详情
const showVehicleDetail = async (vehicle) => {
  selectedVehicle.value = vehicle
  try {
    const response = await userApi.getVehicleDetail(vehicle.id)
    if (response.status === 'success') {
      vehicleDetail.value = response.data
      
      // 如果是暂留状态，初始化充电表单
      if (response.data.status_code === 'registered') {
        chargingForm.requested_amount = Math.min(10, response.data.battery_capacity)
        // 计算初始预估值
        setTimeout(calculateEstimates, 100)
      }
      
      showDetailDialog.value = true
    } else {
      ElMessage.error(response.message || '获取车辆详情失败')
    }
  } catch (error) {
    console.error('获取车辆详情失败:', error)
    ElMessage.error('获取车辆详情失败')
  }
}

// 关闭详情弹窗
const closeDetailDialog = () => {
  showDetailDialog.value = false
  selectedVehicle.value = null
  vehicleDetail.value = null
  
  // 重置充电表单
  if (chargingFormRef.value) {
    chargingFormRef.value.resetFields()
  }
}

// 提交充电请求
const submitChargingRequest = async () => {
  if (!chargingFormRef.value) return
  
  await chargingFormRef.value.validate(async (valid) => {
    if (valid) {
      actionLoading.value = true
      try {
        const requestData = {
          vehicle_id: vehicleDetail.value.id,
          charging_mode: chargingForm.charging_mode,
          requested_amount: chargingForm.requested_amount
        }
        
        const response = await chargingApi.submitRequest(requestData)
        ElMessage.success(`充电请求提交成功！排队号码: ${response.queue_number}`)
        
        // 关闭弹窗并刷新数据
        closeDetailDialog()
        fetchVehicleData()
        
      } catch (error) {
        console.error('提交充电请求失败:', error)
        ElMessage.error('提交充电请求失败')
      } finally {
        actionLoading.value = false
      }
    }
  })
}

// 修改充电请求
const modifyChargingRequest = () => {
  if (!vehicleDetail.value.current_queue) {
    ElMessage.error('未找到当前充电请求')
    return
  }
  
  ElMessageBox.prompt('暂不支持在此处修改请求，请前往充电请求页面进行修改。', '提示', {
    confirmButtonText: '前往修改',
    cancelButtonText: '取消',
    inputType: 'hidden'
  }).then(() => {
    window.open('/user/charging-request', '_blank')
  }).catch(() => {
    // 用户取消
  })
}

// 取消充电请求
const cancelChargingRequest = async () => {
  if (!vehicleDetail.value.current_queue) {
    ElMessage.error('未找到当前充电请求')
    return
  }

  try {
    await ElMessageBox.confirm(
      '确定要取消该充电请求吗？',
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    actionLoading.value = true
    const queueId = vehicleDetail.value.current_queue.id
    const response = await chargingApi.cancelCharging(queueId)
    
    if (response.message) {
      ElMessage.success('充电请求已取消')
      closeDetailDialog()
      fetchVehicleData() // 刷新数据
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消充电请求失败:', error)
      ElMessage.error('取消充电请求失败')
    }
  } finally {
    actionLoading.value = false
  }
}

// 结束充电
const endCharging = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要结束充电吗？系统将为您生成充电详单。',
      '确认结束充电',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    actionLoading.value = true
    const vehicleId = vehicleDetail.value.id
    const response = await userApi.endVehicleCharging(vehicleId)
    
    if (response.status === 'success') {
      ElMessage.success(`充电已结束，详单号：${response.data.record_number}`)
      closeDetailDialog()
      fetchVehicleData() // 刷新数据
    } else {
      ElMessage.error(response.message || '结束充电失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('结束充电失败:', error)
      ElMessage.error('结束充电失败')
    }
  } finally {
    actionLoading.value = false
  }
}

// 获取状态样式类
const getStatusClass = (statusCode) => {
  const classMap = {
    'registered': 'status-registered',
    'waiting': 'status-waiting',
    'queuing': 'status-waiting',
    'charging': 'status-charging'
  }
  return classMap[statusCode] || 'status-registered'
}

// 获取状态标签类型
const getStatusType = (statusCode) => {
  const typeMap = {
    'registered': '',
    'waiting': 'warning',
    'queuing': 'warning',
    'charging': 'success'
  }
  return typeMap[statusCode] || ''
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取充电配置
const fetchChargingConfig = async () => {
  try {
    const config = await userApi.getChargingConfig()
    if (config.status === 'success') {
      chargingConfig.value = config.data
      // 同时获取计费配置
      if (config.data.billing) {
        billingConfig.value = {
          ...billingConfig.value,
          ...config.data.billing
        }
      }
    }
  } catch (error) {
    console.error('获取充电配置失败:', error)
    // 使用默认值
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
  if (!chargingForm.requested_amount || !chargingForm.charging_mode) {
    estimatedCost.value = ''
    estimatedTime.value = ''
    costBreakdown.value = null
    return
  }
  
  // 计算充电时间：充电量/充电效率 = 时间
  // 例如：50度 / 50kW = 1h = 60分钟
  const power = chargingForm.charging_mode === 'fast' 
    ? chargingConfig.value.fast_charging_power 
    : chargingConfig.value.trickle_charging_power
  
  const timeHours = chargingForm.requested_amount / power
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
  
  const electricityCost = (chargingForm.requested_amount * electricityPrice).toFixed(2)
  const serviceCost = (chargingForm.requested_amount * serviceFeePrice).toFixed(2)
  const totalCost = (parseFloat(electricityCost) + parseFloat(serviceCost)).toFixed(2)
  
  estimatedCost.value = totalCost
  costBreakdown.value = {
    electricityCost,
    serviceCost
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchVehicleData()
  fetchChargingConfig()
  
  // 设置定时刷新（每60秒）
  const timer = setInterval(fetchVehicleData, 60000)
  
  // 组件销毁时清理定时器
  onUnmounted(() => {
    if (timer) {
      clearInterval(timer)
    }
  })
})
</script>

<style scoped>
.vehicle-monitoring {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h2 {
  color: #2c3e50;
  margin-bottom: 5px;
}

.page-header p {
  color: #7f8c8d;
  margin: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.last-update {
  color: #8492a6;
  font-size: 14px;
}

.vehicle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.vehicle-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid #ddd;
}

.vehicle-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.vehicle-card.status-registered {
  border-left-color: #909399;
}

.vehicle-card.status-waiting {
  border-left-color: #e6a23c;
}

.vehicle-card.status-charging {
  border-left-color: #67c23a;
}

.vehicle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.license-plate {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.vehicle-info {
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-item .label {
  color: #8492a6;
  font-weight: 500;
}

.info-item .value {
  color: #2c3e50;
}

.queue-info {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 15px;
}

.queue-number {
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.queue-details {
  font-size: 12px;
  color: #8492a6;
}

.queue-details span {
  margin-right: 15px;
}

.card-footer {
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

/* 详情弹窗样式 */
.vehicle-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.detail-collapse {
  margin-bottom: 20px;
}

.detail-collapse .el-collapse-item__header {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.detail-section {
  margin-bottom: 25px;
}

.detail-section h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 2px solid #ebeef5;
}

.detail-item {
  display: flex;
  margin-bottom: 10px;
}

.detail-item label {
  width: 100px;
  color: #8492a6;
  font-weight: 500;
}

.detail-item span {
  color: #2c3e50;
}

.detail-actions {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.detail-actions .el-button {
  margin: 0 10px;
}

.form-hint {
  font-size: 12px;
  color: #8492a6;
  margin-top: 5px;
}

/* 预估显示样式 */
.estimation-display {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
  border-left: 4px solid #409eff;
}

.estimate-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.estimate-item label {
  color: #606266;
  font-weight: 500;
}

.estimate-value {
  font-weight: 600;
  color: #2c3e50;
}

.estimate-value.cost {
  color: #e6a23c;
  font-size: 16px;
}

.cost-breakdown {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.breakdown-note {
  margin-top: 8px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .vehicle-grid {
    grid-template-columns: 1fr;
  }
  
  .toolbar {
    flex-direction: column;
    gap: 10px;
  }
  
  :deep(.el-dialog) {
    width: 90% !important;
  }
}
</style> 