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
              <el-radio-group v-model="requestForm.charging_mode">
                <el-radio label="fast">快充 (30度/小时)</el-radio>
                <el-radio label="trickle">慢充 (10度/小时)</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="充电量" prop="requested_amount">
              <el-input-number
                v-model="requestForm.requested_amount"
                :min="1"
                :max="selectedVehicle?.battery_capacity || 100"
                :step="1"
                style="width: 100%"
              />
              <div class="amount-info">
                <span>单位: 度 (kWh)</span>
                <span v-if="selectedVehicle">
                  最大: {{ selectedVehicle.battery_capacity }}度
                </span>
              </div>
            </el-form-item>
            
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
import api from '@/utils/api'

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

const onVehicleChange = () => {
  if (selectedVehicle.value) {
    // 重置充电量为合理值
    requestForm.requested_amount = Math.min(10, selectedVehicle.value.battery_capacity)
  }
}

const fetchVehicles = async () => {
  try {
    vehicles.value = await api.get('/users/vehicles')
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
</style> 