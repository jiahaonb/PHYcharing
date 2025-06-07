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
              <span class="value">{{ vehicle.battery_capacity }}kWh</span>
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
              <span>需求: {{ vehicle.queue_info.requested_amount }}kWh</span>
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
        <!-- 基本信息 -->
        <div class="detail-section">
          <h3>基本信息</h3>
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
                <span>{{ vehicleDetail.battery_capacity }}kWh</span>
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
        </div>

        <!-- 当前队列信息 -->
        <div v-if="vehicleDetail.current_queue" class="detail-section">
          <h3>当前充电信息</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="detail-item">
                <label>排队号:</label>
                <span>{{ vehicleDetail.current_queue.queue_number }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>充电模式:</label>
                <span>{{ vehicleDetail.current_queue.charging_mode === 'fast' ? '快充' : '慢充' }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>需求电量:</label>
                <span>{{ vehicleDetail.current_queue.requested_amount }}kWh</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>请求时间:</label>
                <span>{{ formatTime(vehicleDetail.current_queue.queue_time) }}</span>
              </div>
            </el-col>
            <el-col :span="24" v-if="vehicleDetail.current_queue.estimated_completion_time">
              <div class="detail-item">
                <label>预计完成:</label>
                <span>{{ formatTime(vehicleDetail.current_queue.estimated_completion_time) }}</span>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 充电历史 -->
        <div v-if="vehicleDetail.charging_history && vehicleDetail.charging_history.length > 0" class="detail-section">
          <h3>最近充电记录</h3>
          <el-table :data="vehicleDetail.charging_history" size="small">
            <el-table-column prop="record_number" label="记录号" width="120"/>
            <el-table-column prop="charging_amount" label="充电量(kWh)" width="100"/>
            <el-table-column prop="charging_duration" label="时长(h)" width="80"/>
            <el-table-column prop="total_fee" label="费用(元)" width="80"/>
            <el-table-column prop="end_time" label="结束时间" width="150">
              <template #default="scope">
                {{ formatTime(scope.row.end_time) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 充电请求表单 -->
        <div v-if="vehicleDetail.status_code === 'registered'" class="detail-section">
          <h3>发起充电请求</h3>
          <el-form 
            ref="chargingFormRef"
            :model="chargingForm" 
            :rules="chargingRules"
            label-width="100px"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="充电模式" prop="charging_mode">
                  <el-radio-group v-model="chargingForm.charging_mode">
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
                  />
                  <div class="form-hint">最大: {{ vehicleDetail.battery_capacity }}kWh</div>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

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

// 充电配置
const chargingConfig = ref({
  fast_charging_power: 60,
  trickle_charging_power: 7
})

// 充电请求表单
const chargingForm = reactive({
  charging_mode: 'fast',
  requested_amount: 10
})

// 充电请求表单验证规则
const chargingRules = {
  charging_mode: [
    { required: true, message: '请选择充电模式', trigger: 'change' }
  ],
  requested_amount: [
    { required: true, message: '请输入充电量', trigger: 'blur' },
    { type: 'number', min: 1, message: '充电量不能小于1kWh', trigger: 'blur' }
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
    }
  } catch (error) {
    console.error('获取充电配置失败:', error)
    // 使用默认值
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