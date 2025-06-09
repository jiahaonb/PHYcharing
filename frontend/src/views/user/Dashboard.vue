<template>
  <div class="dashboard">
    <h1>用户仪表板</h1>
    
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#409eff"><Lightning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalCharging }}</div>
              <div class="stat-label">总充电次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#67c23a"><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalDuration.toFixed(1) }}h</div>
              <div class="stat-label">总充电时长</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#e6a23c"><Coin /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">¥{{ stats.totalFee.toFixed(2) }}</div>
              <div class="stat-label">总消费金额</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#f56c6c"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.activeOrders }}</div>
              <div class="stat-label">当前订单数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="content-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>当前用户订单</span>
              <el-button type="primary" @click="refreshOrders">刷新</el-button>
            </div>
          </template>
          
          <div v-if="currentOrders.length === 0" class="empty-state">
            <el-empty description="暂无活跃订单" />
          </div>
          
          <div v-else>
            <div v-for="order in currentOrders" :key="order.id" class="order-item">
              <div class="order-info">
                <div class="order-number">{{ order.record_number }}</div>
                <div class="order-details">
                  <div>充电量: {{ order.charging_amount }}度</div>
                  <div>状态: {{ getOrderStatusText(order.status) }}</div>
                  <div v-if="order.total_fee">费用: ¥{{ order.total_fee.toFixed(2) }}</div>
                  <div>创建时间: {{ formatDate(order.created_at) }}</div>
                </div>
              </div>
              <div class="order-actions">
                <el-button size="small" @click="viewOrderDetail(order)">查看详情</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近充电记录</span>
              <router-link to="/user/records">
                <el-button type="text">查看全部</el-button>
              </router-link>
            </div>
          </template>
          
          <div v-if="recentRecords.length === 0" class="empty-state">
            <el-empty description="暂无充电记录" />
          </div>
          
          <div v-else>
            <div v-for="record in recentRecords" :key="record.id" class="record-item">
              <div class="record-info">
                <div class="record-number">{{ record.record_number }}</div>
                <div class="record-details">
                  <div>充电量: {{ record.charging_amount }}度</div>
                  <div>费用: ¥{{ record.total_fee.toFixed(2) }}</div>
                  <div>时间: {{ formatDate(record.start_time) }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 订单详情弹窗 -->
    <el-dialog 
      v-model="orderDetailVisible" 
      :title="`订单详情 - ${selectedOrder?.record_number}`"
      width="600px"
      @close="closeOrderDetail"
    >
      <div v-if="selectedOrder" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单编号">
            {{ selectedOrder.record_number }}
          </el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getOrderStatusType(selectedOrder.status)">
              {{ getOrderStatusText(selectedOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="计划充电量">
            {{ selectedOrder.charging_amount }}度
          </el-descriptions-item>
          <el-descriptions-item label="实际充电量" v-if="selectedOrder.actual_charging_amount">
            <span class="actual-amount">{{ selectedOrder.actual_charging_amount.toFixed(2) }}度</span>
          </el-descriptions-item>
          <el-descriptions-item label="充电模式">
            {{ selectedOrder.charging_mode === 'FAST' ? '快充' : '慢充' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(selectedOrder.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间" v-if="selectedOrder.start_time">
            {{ formatDate(selectedOrder.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间" v-if="selectedOrder.end_time">
            {{ formatDate(selectedOrder.end_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="充电时长" v-if="selectedOrder.charging_duration">
            {{ selectedOrder.charging_duration.toFixed(2) }}小时
          </el-descriptions-item>
          <el-descriptions-item label="计划电费" v-if="selectedOrder.electricity_fee">
            ¥{{ selectedOrder.electricity_fee.toFixed(2) }}
          </el-descriptions-item>
          <el-descriptions-item label="实际电费" v-if="selectedOrder.actual_electricity_fee">
            <span class="actual-fee">¥{{ selectedOrder.actual_electricity_fee.toFixed(2) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="计划服务费" v-if="selectedOrder.service_fee">
            ¥{{ selectedOrder.service_fee.toFixed(2) }}
          </el-descriptions-item>
          <el-descriptions-item label="实际服务费" v-if="selectedOrder.actual_service_fee">
            <span class="actual-fee">¥{{ selectedOrder.actual_service_fee.toFixed(2) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="计划总费用" v-if="selectedOrder.total_fee">
            ¥{{ selectedOrder.total_fee.toFixed(2) }}
          </el-descriptions-item>
          <el-descriptions-item label="实际总费用" v-if="selectedOrder.actual_total_fee">
            <span class="actual-total-fee">¥{{ selectedOrder.actual_total_fee.toFixed(2) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="单价" v-if="selectedOrder.unit_price">
            {{ selectedOrder.unit_price }}元/度
          </el-descriptions-item>
          <el-descriptions-item label="时段" v-if="selectedOrder.time_period">
            {{ selectedOrder.time_period }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const stats = reactive({
  totalCharging: 0,
  totalDuration: 0,
  totalFee: 0,
  activeOrders: 0
})

const currentOrders = ref([])
const recentRecords = ref([])
const orderDetailVisible = ref(false)
const selectedOrder = ref(null)

const getOrderStatusText = (status) => {
  const statusMap = {
    created: '已创建',
    assigned: '已分配',
    charging: '充电中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const getOrderStatusType = (status) => {
  const typeMap = {
    created: 'info',
    assigned: 'warning',
    charging: 'success',
    completed: 'success',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const fetchStats = async () => {
  try {
    // 获取充电记录统计
    const records = await api.get('/charging/records')
    
    if (records && Array.isArray(records)) {
      stats.totalCharging = records.length
      stats.totalDuration = records.reduce((sum, record) => {
        const duration = record.charging_duration || 0
        return sum + duration
      }, 0)
      stats.totalFee = records.reduce((sum, record) => {
        const fee = record.total_fee || 0
        return sum + fee
      }, 0)
      
      // 统计活跃订单数（未完成的订单）
      const activeOrdersCount = records.filter(record => 
        record.status && !['completed', 'cancelled'].includes(record.status)
      ).length
      stats.activeOrders = activeOrdersCount
      
      // 获取最近记录（只显示已完成的记录）
      const completedRecords = records.filter(record => 
        record.status === 'completed' && 
        record.start_time && 
        record.total_fee
      )
      recentRecords.value = completedRecords.slice(0, 5)
    } else {
      // 如果没有记录或记录格式不正确，设置默认值
      stats.totalCharging = 0
      stats.totalDuration = 0
      stats.totalFee = 0
      stats.activeOrders = 0
      recentRecords.value = []
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    // 设置默认值
    stats.totalCharging = 0
    stats.totalDuration = 0
    stats.totalFee = 0
    stats.activeOrders = 0
    recentRecords.value = []
  }
}

const fetchCurrentOrders = async () => {
  try {
    // 获取当前用户的所有订单
    const records = await api.get('/charging/records')
    
    if (records && Array.isArray(records)) {
      // 过滤出活跃的订单（未完成的订单）
      const activeOrders = records.filter(record => 
        record.status && !['completed', 'cancelled'].includes(record.status)
      )
      
      // 按创建时间倒序排列
      currentOrders.value = activeOrders.sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      ).slice(0, 10) // 只显示最近10个活跃订单
    } else {
      currentOrders.value = []
    }
  } catch (error) {
    console.error('获取当前订单失败:', error)
    currentOrders.value = []
  }
}

const refreshOrders = () => {
  fetchCurrentOrders()
  fetchStats() // 同时刷新统计数据
  ElMessage.success('订单状态已刷新')
}

const viewOrderDetail = (order) => {
  selectedOrder.value = order
  orderDetailVisible.value = true
}

const closeOrderDetail = () => {
  orderDetailVisible.value = false
  selectedOrder.value = null
}

onMounted(() => {
  fetchStats()
  fetchCurrentOrders()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.content-row {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.order-item, .record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.order-item:last-child, .record-item:last-child {
  border-bottom: none;
}

.order-number, .record-number {
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.order-details, .record-details {
  font-size: 14px;
  color: #666;
}

.order-details div, .record-details div {
  margin-bottom: 2px;
}

.order-detail {
  padding: 10px 0;
}

.total-fee {
  font-weight: bold;
  color: #e6a23c;
  font-size: 16px;
}

.actual-amount {
  font-weight: bold;
  color: #67c23a;
}

.actual-fee {
  font-weight: bold;
  color: #409eff;
}

.actual-total-fee {
  font-weight: bold;
  color: #e6a23c;
  font-size: 16px;
}
</style> 