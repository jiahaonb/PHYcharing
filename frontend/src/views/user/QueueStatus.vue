<template>
  <div class="queue-status">
    <div class="page-header">
      <h2>排队状态</h2>
      <p>查看和管理我的充电订单</p>
    </div>

    <div class="toolbar">
      <el-button 
        type="primary" 
        @click="refreshStatus" 
        :loading="loading"
        icon="Refresh"
      >
        刷新状态
      </el-button>
      <span class="last-update">最后更新: {{ formatTime(lastUpdateTime) }}</span>
    </div>

    <div v-loading="loading" class="content">
      <!-- 有订单时显示 -->
      <div v-if="!loading && currentOrders.length > 0" class="orders-grid">
        <div 
          v-for="order in currentOrders" 
          :key="order.id" 
          class="order-card"
          :class="getOrderClass(order.status)"
        >
          <!-- 订单头部 -->
          <div class="order-header">
            <div class="order-info">
              <div class="license-plate">{{ order.vehicle_license || '未知车辆' }}</div>
              <el-tag 
                :type="getStatusType(order.status)" 
                size="small"
              >
                {{ getStatusText(order.status) }}
              </el-tag>
            </div>
            <div class="order-number">{{ order.queue_number }}</div>
          </div>

          <!-- 订单详情 -->
          <div class="order-details">
            <div class="detail-row">
              <span class="label">充电模式:</span>
              <span class="value">{{ order.charging_mode === 'fast' ? '快充' : '慢充' }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ order.status === 'charging' ? '计划充电量:' : '充电量:' }}</span>
              <span class="value">{{ order.requested_amount }}度</span>
            </div>
            <div v-if="order.status === 'charging' && order.actual_charging_amount" class="detail-row">
              <span class="label">实际充电量:</span>
              <span class="value actual-amount">{{ order.actual_charging_amount.toFixed(2) }}度</span>
            </div>
            <div class="detail-row">
              <span class="label">位置:</span>
              <span class="value">{{ getLocationText(order) }}</span>
            </div>
            <div v-if="order.position" class="detail-row">
              <span class="label">排队位置:</span>
              <span class="value">第{{ order.position }}位</span>
            </div>
            <div v-if="order.estimated_time > 0" class="detail-row">
              <span class="label">{{ order.status === 'charging' ? '剩余时间:' : '预计等待:' }}</span>
              <span class="value" :class="{ 'remaining-time': order.status === 'charging' }">{{ order.estimated_time }}分钟</span>
            </div>
            <div v-if="order.status === 'charging' && order.remaining_time !== null && order.remaining_time !== undefined" class="detail-row">
              <span class="label">实际剩余:</span>
              <span class="value remaining-time">{{ order.remaining_time }}分钟</span>
            </div>
            <div class="detail-row">
              <span class="label">请求时间:</span>
              <span class="value">{{ formatTime(order.request_time) }}</span>
            </div>
            <div v-if="order.status === 'charging' && order.actual_total_fee" class="detail-row">
              <span class="label">实际费用:</span>
              <span class="value actual-fee">¥{{ order.actual_total_fee.toFixed(2) }}</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="order-actions">
            <!-- 等候区操作 -->
            <template v-if="order.status === 'waiting'">
              <el-button 
                type="primary" 
                size="small" 
                @click="showModifyDialog(order)"
                icon="Edit"
              >
                修改请求
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                @click="cancelOrder(order)"
                icon="Close"
              >
                取消排队
              </el-button>
            </template>

            <!-- 充电区排队操作（只能取消） -->
            <template v-else-if="order.status === 'queuing'">
              <el-button 
                type="danger" 
                size="small" 
                @click="cancelOrder(order)"
                icon="Close"
              >
                取消排队
              </el-button>
            </template>

            <!-- 充电中操作 -->
            <template v-else-if="order.status === 'charging'">
              <el-button 
                type="warning" 
                size="small" 
                @click="stopCharging(order)"
                icon="Switch"
              >
                结束充电
              </el-button>
            </template>
          </div>
        </div>
      </div>

      <!-- 无订单时显示 -->
      <div v-else-if="!loading" class="empty-state">
        <el-empty description="当前没有排队订单">
          <el-button type="primary" @click="goToCharging" icon="Lightning">
            申请充电
          </el-button>
        </el-empty>
      </div>
    </div>

    <!-- 修改请求弹窗 -->
    <el-dialog 
      v-model="showModifyFullDialog" 
      title="修改充电请求"
      width="500px"
      @close="closeModifyDialog"
    >
      <div v-if="selectedOrder" class="modify-form">
        <el-form 
          ref="modifyFormRef"
          :model="modifyForm" 
          :rules="modifyRules"
          label-width="100px"
        >
          <el-form-item label="车牌号">
            <el-input :value="selectedOrder.vehicle_license" disabled />
          </el-form-item>
          
          <el-form-item label="充电模式" prop="charging_mode">
            <el-radio-group v-model="modifyForm.charging_mode">
              <el-radio label="fast">快充</el-radio>
              <el-radio label="trickle">慢充</el-radio>
            </el-radio-group>
            <div class="form-hint">修改充电模式将重新排号</div>
          </el-form-item>
          
          <el-form-item label="充电量" prop="requested_amount">
            <el-input-number
              v-model="modifyForm.requested_amount"
              :min="1"
              :max="100"
              :step="1"
              style="width: 100%"
            />
            <div class="form-hint">单位: 度</div>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="closeModifyDialog">取消</el-button>
        <el-button 
          type="primary" 
          @click="submitModifyRequest"
          :loading="actionLoading"
        >
          确认修改
        </el-button>
      </template>
    </el-dialog>

    <!-- 仅修改充电量弹窗 -->
    <el-dialog 
      v-model="showModifyAmountOnlyDialog" 
      title="修改充电量"
      width="400px"
      @close="closeModifyAmountDialog"
    >
      <div v-if="selectedOrder" class="modify-amount-form">
        <el-form 
          ref="modifyAmountFormRef"
          :model="modifyAmountForm" 
          :rules="modifyAmountRules"
          label-width="100px"
        >
          <el-form-item label="车牌号">
            <el-input :value="selectedOrder.vehicle_license" disabled />
          </el-form-item>
          
          <el-form-item label="充电模式">
            <el-input :value="selectedOrder.charging_mode === 'fast' ? '快充' : '慢充'" disabled />
          </el-form-item>
          
          <el-form-item label="新充电量" prop="requested_amount">
            <el-input-number
              v-model="modifyAmountForm.requested_amount"
              :min="1"
              :max="100"
              :step="1"
              style="width: 100%"
            />
            <div class="form-hint">单位: 度，不重新排号</div>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="closeModifyAmountDialog">取消</el-button>
        <el-button 
          type="primary" 
          @click="submitModifyAmountOnly"
          :loading="actionLoading"
        >
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Lightning, Edit, Close, Switch } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { chargingApi } from '@/api/user'

const router = useRouter()
const loading = ref(false)
const actionLoading = ref(false)
const currentOrders = ref([])
const lastUpdateTime = ref(null)

// 修改弹窗相关
const showModifyFullDialog = ref(false)
const showModifyAmountOnlyDialog = ref(false)
const selectedOrder = ref(null)
const modifyFormRef = ref()
const modifyAmountFormRef = ref()

// 修改表单
const modifyForm = reactive({
  charging_mode: 'fast',
  requested_amount: 10
})

const modifyAmountForm = reactive({
  requested_amount: 10
})

const modifyRules = {
  charging_mode: [
    { required: true, message: '请选择充电模式', trigger: 'change' }
  ],
  requested_amount: [
    { required: true, message: '请输入充电量', trigger: 'blur' },
    { type: 'number', min: 1, message: '充电量不能小于1度', trigger: 'blur' }
  ]
}

const modifyAmountRules = {
  requested_amount: [
    { required: true, message: '请输入充电量', trigger: 'blur' },
    { type: 'number', min: 1, message: '充电量不能小于1度', trigger: 'blur' }
  ]
}

// 获取当前用户的所有排队状态
const fetchQueueStatus = async () => {
  loading.value = true
  try {
    const response = await api.get('/users/queue/status')
    
    // 为每个订单获取车辆信息
    const ordersWithVehicleInfo = await Promise.all(
      response.map(async (order) => {
        try {
          // 使用队列数据中的信息，如果没有车牌信息则获取
          if (!order.vehicle_license) {
            const vehicleResponse = await api.get(`/users/vehicles`)
            const vehicle = vehicleResponse.find(v => v.id === order.vehicle_id)
            order.vehicle_license = vehicle ? vehicle.license_plate : '未知车辆'
          }
          return order
        } catch (error) {
          console.error('获取车辆信息失败:', error)
          order.vehicle_license = '未知车辆'
          return order
        }
      })
    )
    
    currentOrders.value = ordersWithVehicleInfo
    lastUpdateTime.value = new Date()
  } catch (error) {
    console.error('获取排队状态失败:', error)
    ElMessage.error('获取排队状态失败')
  } finally {
    loading.value = false
  }
}

// 刷新状态
const refreshStatus = () => {
  fetchQueueStatus()
  ElMessage.success('状态已刷新')
}

// 显示修改请求弹窗（等候区完整修改）
const showModifyDialog = (order) => {
  selectedOrder.value = order
  modifyForm.charging_mode = order.charging_mode
  modifyForm.requested_amount = order.requested_amount
  showModifyFullDialog.value = true
}

// 显示仅修改充电量弹窗（充电区）
const showModifyAmountDialog = (order) => {
  selectedOrder.value = order
  modifyAmountForm.requested_amount = order.requested_amount
  showModifyAmountOnlyDialog.value = true
}

// 关闭修改弹窗
const closeModifyDialog = () => {
  showModifyFullDialog.value = false
  selectedOrder.value = null
  if (modifyFormRef.value) {
    modifyFormRef.value.resetFields()
  }
}

const closeModifyAmountDialog = () => {
  showModifyAmountOnlyDialog.value = false
  selectedOrder.value = null
  if (modifyAmountFormRef.value) {
    modifyAmountFormRef.value.resetFields()
  }
}

// 提交修改请求（完整修改）
const submitModifyRequest = async () => {
  if (!modifyFormRef.value) return
  
  await modifyFormRef.value.validate(async (valid) => {
    if (valid) {
      actionLoading.value = true
      try {
        await chargingApi.modifyRequest(selectedOrder.value.id, {
          charging_mode: modifyForm.charging_mode,
          requested_amount: modifyForm.requested_amount
        })
        
        ElMessage.success('充电请求修改成功')
        closeModifyDialog()
        await fetchQueueStatus()
      } catch (error) {
        console.error('修改充电请求失败:', error)
        ElMessage.error('修改充电请求失败')
      } finally {
        actionLoading.value = false
      }
    }
  })
}

// 提交仅修改充电量
const submitModifyAmountOnly = async () => {
  if (!modifyAmountFormRef.value) return
  
  await modifyAmountFormRef.value.validate(async (valid) => {
    if (valid) {
      actionLoading.value = true
      try {
        await chargingApi.modifyRequest(selectedOrder.value.id, {
          requested_amount: modifyAmountForm.requested_amount
        })
        
        ElMessage.success('充电量修改成功')
        closeModifyAmountDialog()
        await fetchQueueStatus()
      } catch (error) {
        console.error('修改充电量失败:', error)
        ElMessage.error('修改充电量失败')
      } finally {
        actionLoading.value = false
      }
    }
  })
}

// 取消订单
const cancelOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消订单 ${order.queue_number} 吗？`,
      '取消确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await chargingApi.cancelCharging(order.id)
    ElMessage.success('订单已取消')
    await fetchQueueStatus()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
      ElMessage.error('取消订单失败')
    }
  }
}

// 结束充电
const stopCharging = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确定要结束订单 ${order.queue_number} 的充电吗？`,
      '结束确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // 通过车辆API结束充电
    if (!order.vehicle_id) {
      ElMessage.error('无法获取车辆信息')
      return
    }
    
    const response = await api.post(`/users/vehicles/${order.vehicle_id}/end-charging`)
    
    if (response.status === 'success') {
      ElMessage.success(`充电已结束，详单号：${response.data.record_number}`)
      await fetchQueueStatus()
    } else {
      ElMessage.error(response.message || '结束充电失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('结束充电失败:', error)
      ElMessage.error('结束充电失败')
    }
  }
}

// 跳转到充电申请页面
const goToCharging = () => {
  router.push('/user/charging')
}

// 获取订单卡片样式类
const getOrderClass = (status) => {
  const statusMap = {
    'waiting': 'order-waiting',
    'queuing': 'order-queuing', 
    'charging': 'order-charging'
  }
  return statusMap[status] || ''
}

// 获取状态标签类型
const getStatusType = (status) => {
  const statusMap = {
    'waiting': 'warning',
    'queuing': 'info',
    'charging': 'success'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'waiting': '等候区',
    'queuing': '排队中',
    'charging': '充电中'
  }
  return statusMap[status] || '未知'
}

// 获取位置文本
const getLocationText = (order) => {
  if (order.status === 'waiting') {
    return '等候区'
  } else if (order.pile_name) {
    return order.pile_name
  } else {
    return '分配中'
  }
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 自动刷新
let refreshInterval = null

onMounted(() => {
  fetchQueueStatus()
  
  // 设置自动刷新，每30秒刷新一次
  refreshInterval = setInterval(() => {
    fetchQueueStatus()
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.queue-status {
  padding: 0;
  min-height: calc(100vh - 140px);
}

.page-header {
  margin-bottom: 20px;
  text-align: center;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.last-update {
  font-size: 12px;
  color: #909399;
}

.content {
  min-height: 400px;
}

.orders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.order-card {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #ffffff;
  transition: all 0.3s ease;
  cursor: pointer;
}

.order-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.order-waiting {
  border-color: #e6a23c;
  background: linear-gradient(135deg, #fdf6ec 0%, #ffffff 100%);
}

.order-queuing {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #ffffff 100%);
}

.order-charging {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.license-plate {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.order-number {
  font-size: 14px;
  font-weight: bold;
  color: #409eff;
  background: #ecf5ff;
  padding: 4px 8px;
  border-radius: 4px;
}

.order-details {
  margin-bottom: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 14px;
}

.detail-row .label {
  color: #606266;
  font-weight: 500;
}

.detail-row .value {
  color: #303133;
  font-weight: 600;
}

.detail-row .value.actual-amount {
  color: #67c23a;
  font-weight: bold;
}

.detail-row .value.actual-fee {
  color: #e6a23c;
  font-weight: bold;
}

.detail-row .value.remaining-time {
  color: #f56c6c;
  font-weight: bold;
}

.order-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.order-actions .el-button {
  flex: 1;
  min-width: 80px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.modify-form, .modify-amount-form {
  padding: 20px 0;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .orders-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .order-card {
    padding: 12px;
  }
  
  .license-plate {
    font-size: 16px;
  }
  
  .toolbar {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style> 