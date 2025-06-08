<template>
  <div class="charging-orders">
    <div class="page-header">
      <h2>我的充电详单</h2>
      <p>查看我的所有充电详单记录</p>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.record_number"
            placeholder="输入订单编号搜索"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="searchForm.status"
            placeholder="选择订单状态"
            clearable
            style="width: 100%"
          >
            <el-option label="全部状态" value="" />
            <el-option label="已创建" value="created" />
            <el-option label="已分配" value="assigned" />
            <el-option label="充电中" value="charging" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-date-picker
            v-model="searchForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="fetchOrders" :loading="loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 详单列表 -->
    <el-card class="orders-card">
      <template #header>
        <div class="card-header">
          <span>充电详单列表</span>
          <el-button type="text" @click="fetchOrders" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table 
        :data="orders" 
        v-loading="loading"
        stripe
        border
        @row-click="showOrderDetail"
        style="cursor: pointer"
      >
        <el-table-column prop="record_number" label="订单编号" width="180" fixed="left" />
        <el-table-column prop="created_at" label="订单生成时间" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="charging_pile" label="充电桩编号" width="120">
          <template #default="scope">
            {{ scope.row.charging_pile?.pile_number || '未分配' }}
          </template>
        </el-table-column>
        <el-table-column prop="vehicle" label="车辆信息" width="140">
          <template #default="scope">
            {{ scope.row.vehicle?.license_plate }}
          </template>
        </el-table-column>
        <el-table-column prop="charging_mode" label="充电模式" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.charging_mode === 'fast' ? 'success' : 'warning'" size="small">
              {{ scope.row.charging_mode === 'fast' ? '快充' : '慢充' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="charging_amount" label="充电电量(度)" width="120" />
        <el-table-column prop="charging_duration" label="充电时长" width="120">
          <template #default="scope">
            {{ formatDuration(scope.row.charging_duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="启动时间" width="160">
          <template #default="scope">
            {{ scope.row.start_time ? formatDateTime(scope.row.start_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="停止时间" width="160">
          <template #default="scope">
            {{ scope.row.end_time ? formatDateTime(scope.row.end_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="electricity_fee" label="充电费用(元)" width="120">
          <template #default="scope">
            {{ scope.row.electricity_fee ? `¥${scope.row.electricity_fee}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="service_fee" label="服务费用(元)" width="120">
          <template #default="scope">
            {{ scope.row.service_fee ? `¥${scope.row.service_fee}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_fee" label="总费用(元)" width="120">
          <template #default="scope">
            <span class="total-fee">
              {{ scope.row.total_fee ? `¥${scope.row.total_fee}` : '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" fixed="right">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchOrders"
          @current-change="fetchOrders"
        />
      </div>
    </el-card>

    <!-- 详单详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`充电详单详情 - ${selectedOrder?.record_number}`"
      width="700px"
    >
      <div v-if="selectedOrder" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单编号">
            {{ selectedOrder.record_number }}
          </el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getStatusType(selectedOrder.status)">
              {{ getStatusText(selectedOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="订单生成时间">
            {{ formatDateTime(selectedOrder.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="充电桩编号">
            {{ selectedOrder.charging_pile?.pile_number || '未分配' }}
          </el-descriptions-item>
          <el-descriptions-item label="车辆信息">
            {{ selectedOrder.vehicle?.license_plate }} ({{ selectedOrder.vehicle?.model }})
          </el-descriptions-item>
          <el-descriptions-item label="充电模式">
            <el-tag :type="selectedOrder.charging_mode === 'fast' ? 'success' : 'warning'">
              {{ selectedOrder.charging_mode === 'fast' ? '快充' : '慢充' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="充电电量">
            {{ selectedOrder.charging_amount }} 度
          </el-descriptions-item>
          <el-descriptions-item label="充电时长">
            {{ formatDuration(selectedOrder.charging_duration) }}
          </el-descriptions-item>
          <el-descriptions-item label="启动时间">
            {{ selectedOrder.start_time ? formatDateTime(selectedOrder.start_time) : '未开始' }}
          </el-descriptions-item>
          <el-descriptions-item label="停止时间">
            {{ selectedOrder.end_time ? formatDateTime(selectedOrder.end_time) : '未结束' }}
          </el-descriptions-item>
          <el-descriptions-item label="电费单价">
            {{ selectedOrder.unit_price ? `¥${selectedOrder.unit_price}/度` : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="时段">
            {{ selectedOrder.time_period || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="充电费用">
            {{ selectedOrder.electricity_fee ? `¥${selectedOrder.electricity_fee}` : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="服务费用">
            {{ selectedOrder.service_fee ? `¥${selectedOrder.service_fee}` : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="总费用" :span="2">
            <span class="total-fee-large">
              {{ selectedOrder.total_fee ? `¥${selectedOrder.total_fee}` : '-' }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { userApi } from '@/api/user'

// 响应式数据
const loading = ref(false)
const orders = ref([])
const showDetailDialog = ref(false)
const selectedOrder = ref(null)

// 搜索表单
const searchForm = reactive({
  record_number: '',
  status: '',
  date_range: null
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取充电详单列表
const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    
    // 处理日期范围
    if (searchForm.date_range && searchForm.date_range.length === 2) {
      params.start_date = searchForm.date_range[0]
      params.end_date = searchForm.date_range[1]
    }
    
    const response = await userApi.getChargingOrders(params)
    if (response.status === 'success') {
      orders.value = response.data.items
      pagination.total = response.data.total
    } else {
      ElMessage.error(response.message || '获取充电详单失败')
    }
  } catch (error) {
    console.error('获取充电详单失败:', error)
    ElMessage.error('获取充电详单失败')
  } finally {
    loading.value = false
  }
}

// 显示详单详情
const showOrderDetail = (order) => {
  selectedOrder.value = order
  showDetailDialog.value = true
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'created': '',
    'assigned': 'warning',
    'charging': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return typeMap[status] || ''
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    'created': '已创建',
    'assigned': '已分配',
    'charging': '充电中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return textMap[status] || status
}

// 格式化时间
const formatDateTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化时长
const formatDuration = (duration) => {
  if (!duration) return '-'
  const hours = Math.floor(duration)
  const minutes = Math.round((duration - hours) * 60)
  if (hours > 0) {
    return minutes > 0 ? `${hours}小时${minutes}分钟` : `${hours}小时`
  } else {
    return `${minutes}分钟`
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.charging-orders {
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

.filter-card {
  margin-bottom: 20px;
}

.orders-card {
  background: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-fee {
  color: #e6a23c;
  font-weight: bold;
}

.total-fee-large {
  color: #e6a23c;
  font-weight: bold;
  font-size: 18px;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}

.order-detail {
  max-height: 60vh;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .charging-orders {
    padding: 10px;
  }
  
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-dialog) {
    width: 95% !important;
  }
}
</style> 