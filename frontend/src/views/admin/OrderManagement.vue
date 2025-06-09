<template>
  <div class="order-management">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <h1>订单管理</h1>
      <div class="header-actions">
        <el-select v-model="statusFilter" @change="fetchOrders" placeholder="筛选状态" clearable>
          <el-option label="全部" value="" />
          <el-option label="等待中" value="waiting" />
          <el-option label="排队中" value="queuing" />
          <el-option label="充电中" value="charging" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-button @click="fetchOrders" :icon="Refresh">刷新</el-button>
        <el-button @click="batchComplete" type="danger" :disabled="selectedOrders.length === 0">
          批量完成 ({{ selectedOrders.length }})
        </el-button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-row">
      <el-card class="stat-card">
        <div class="stat-item">
          <span class="stat-label">总订单数</span>
          <span class="stat-value">{{ totalOrders }}</span>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <span class="stat-label">活跃订单</span>
          <span class="stat-value active">{{ activeOrdersCount }}</span>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <span class="stat-label">已完成</span>
          <span class="stat-value completed">{{ completedOrdersCount }}</span>
        </div>
      </el-card>
    </div>

    <!-- 订单表格 -->
    <el-card class="table-card">
      <el-table 
        v-loading="loading"
        :data="orders" 
        @selection-change="handleSelectionChange"
        stripe
        border
        height="600"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="订单ID" width="80" />
        <el-table-column prop="queue_number" label="队列编号" width="120" />
        <el-table-column prop="license_plate" label="车牌号" width="120" />
        <el-table-column prop="username" label="用户" width="100" />
        <el-table-column prop="charging_mode" label="充电模式" width="100">
          <template #default="{ row }">
            <el-tag :type="row.charging_mode === 'fast' ? 'danger' : 'primary'">
              {{ row.charging_mode === 'fast' ? '快充' : '慢充' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="charging_pile_name" label="充电桩" width="120" />
        <el-table-column prop="charging_amount" label="充电量(kWh)" width="120" />

        <el-table-column prop="total_amount" label="计划充电量" width="120">
          <template #default="{ row }">
            {{ row.total_amount ? row.total_amount.toFixed(2) + ' kWh' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="actual_charging_amount" label="实际充电量" width="120">
          <template #default="{ row }">
            {{ row.actual_charging_amount ? row.actual_charging_amount.toFixed(2) + ' kWh' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_fee" label="计划费用" width="100">
          <template #default="{ row }">
            {{ row.total_fee ? '¥' + row.total_fee.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="actual_total_fee" label="实际费用" width="100">
          <template #default="{ row }">
            {{ row.actual_total_fee ? '¥' + row.actual_total_fee.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column prop="updated_at" label="更新时间" width="160" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status !== 'completed'"
              @click="completeOrder(row)" 
              type="danger" 
              size="small"
            >
              强制完成
            </el-button>
            <el-button 
              @click="viewOrderDetail(row)" 
              type="primary" 
              size="small"
              link
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 订单详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="订单详情" width="600px">
      <div v-if="selectedOrder" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单ID">{{ selectedOrder.id }}</el-descriptions-item>
          <el-descriptions-item label="队列编号">{{ selectedOrder.queue_number }}</el-descriptions-item>
          <el-descriptions-item label="充电记录编号">{{ selectedOrder.record_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="车牌号">{{ selectedOrder.license_plate }}</el-descriptions-item>
          <el-descriptions-item label="用户">{{ selectedOrder.username }}</el-descriptions-item>
          <el-descriptions-item label="充电模式">
            <el-tag :type="selectedOrder.charging_mode === 'fast' ? 'danger' : 'primary'">
              {{ selectedOrder.charging_mode === 'fast' ? '快充' : '慢充' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getStatusTagType(selectedOrder.status)">
              {{ getStatusText(selectedOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="充电桩">{{ selectedOrder.charging_pile_name }}</el-descriptions-item>
          <el-descriptions-item label="计划充电量">{{ selectedOrder.charging_amount }} kWh</el-descriptions-item>
          <el-descriptions-item label="计划总费用">{{ selectedOrder.total_fee ? '¥' + selectedOrder.total_fee.toFixed(2) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="实际充电量">{{ selectedOrder.actual_charging_amount ? selectedOrder.actual_charging_amount.toFixed(2) + ' kWh' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="实际充电费">{{ selectedOrder.actual_electricity_fee ? '¥' + selectedOrder.actual_electricity_fee.toFixed(2) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="实际服务费">{{ selectedOrder.actual_service_fee ? '¥' + selectedOrder.actual_service_fee.toFixed(2) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="实际总费用">{{ selectedOrder.actual_total_fee ? '¥' + selectedOrder.actual_total_fee.toFixed(2) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ selectedOrder.start_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ selectedOrder.end_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedOrder.created_at }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ selectedOrder.updated_at }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button 
          v-if="selectedOrder && selectedOrder.status !== 'completed'"
          @click="completeOrderFromDetail" 
          type="danger"
        >
          强制完成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const orders = ref([])
const totalOrders = ref(0)
const statusFilter = ref('')
const selectedOrders = ref([])
const detailDialogVisible = ref(false)
const selectedOrder = ref(null)

// 计算属性
const activeOrdersCount = computed(() => {
  return orders.value.filter(order => 
    ['waiting', 'queuing', 'charging'].includes(order.status)
  ).length
})

const completedOrdersCount = computed(() => {
  return orders.value.filter(order => order.status === 'completed').length
})

// 状态文本映射
const getStatusText = (status) => {
  const statusMap = {
    'waiting': '等待中',
    'queuing': '排队中', 
    'charging': '充电中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

// 状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    'waiting': 'info',
    'queuing': 'warning',
    'charging': 'success', 
    'completed': '',
    'cancelled': 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取订单列表
const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    
    const response = await api.get('/admin/orders', { params })
    orders.value = response.orders || []
    totalOrders.value = response.total || 0
    
    console.log('✅ 获取订单列表成功:', { total: totalOrders.value })
  } catch (error) {
    console.error('获取订单列表失败:', error)
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

// 完成单个订单
const completeOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确定要强制完成订单 ${order.queue_number} (${order.license_plate}) 吗？`,
      '强制完成确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    const response = await api.post(`/admin/orders/${order.id}/complete`)
    ElMessage.success(response.message || '订单已强制完成')
    
    // 刷新列表
    await fetchOrders()
    
    // 如果详情弹窗开着，关闭它
    if (detailDialogVisible.value && selectedOrder.value?.id === order.id) {
      detailDialogVisible.value = false
    }
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('强制完成订单失败:', error)
      ElMessage.error('强制完成订单失败')
    }
  }
}

// 从详情弹窗完成订单
const completeOrderFromDetail = async () => {
  if (selectedOrder.value) {
    await completeOrder(selectedOrder.value)
  }
}

// 批量完成订单
const batchComplete = async () => {
  if (selectedOrders.value.length === 0) {
    ElMessage.warning('请选择要完成的订单')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要强制完成选中的 ${selectedOrders.value.length} 个订单吗？`,
      '批量完成确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // 批量完成
    const promises = selectedOrders.value.map(order => 
      api.post(`/admin/orders/${order.id}/complete`)
    )
    
    await Promise.all(promises)
    ElMessage.success(`成功完成 ${selectedOrders.value.length} 个订单`)
    
    // 清空选择并刷新
    selectedOrders.value = []
    await fetchOrders()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量完成订单失败:', error)
      ElMessage.error('批量完成订单失败')
    }
  }
}

// 处理表格选择变化
const handleSelectionChange = (selection) => {
  selectedOrders.value = selection.filter(order => 
    order.status !== 'completed'
  )
}

// 查看订单详情
const viewOrderDetail = (order) => {
  selectedOrder.value = order
  detailDialogVisible.value = true
}

// 组件挂载
onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.order-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-value.active {
  color: #E6A23C;
}

.stat-value.completed {
  color: #67C23A;
}

.table-card {
  margin-bottom: 20px;
}

.order-detail {
  max-height: 500px;
  overflow-y: auto;
}

:deep(.el-descriptions__body) {
  background-color: #fafafa;
}

:deep(.el-descriptions__label) {
  font-weight: bold;
  width: 120px;
}
</style> 