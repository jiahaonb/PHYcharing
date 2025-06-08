<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <div>
            <el-button @click="fetchUsers" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索过滤器 -->
      <div class="search-filters">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input
              v-model="searchQuery"
              placeholder="搜索用户名或邮箱"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-select 
              v-model="statusFilter" 
              placeholder="用户状态"
              clearable
              @change="handleSearch"
            >
              <el-option label="全部" value="" />
              <el-option label="管理员" value="admin" />
              <el-option label="普通用户" value="user" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select 
              v-model="vehicleFilter" 
              placeholder="车辆状态"
              clearable
              @change="handleSearch"
            >
              <el-option label="全部" value="" />
              <el-option label="有车辆" value="has_vehicles" />
              <el-option label="无车辆" value="no_vehicles" />
            </el-select>
          </el-col>
        </el-row>
      </div>

      <!-- 用户列表 -->
      <el-table 
        :data="filteredUsers" 
        style="width: 100%" 
        v-loading="loading"
        element-loading-text="正在加载用户数据..."
        element-loading-spinner="el-icon-loading"
        empty-text="暂无用户数据"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="用户信息" width="280">
          <template #default="scope">
            <div class="user-info-cell">
              <div class="user-main">
                <div class="username">{{ scope.row.username }}</div>
                <div class="user-details">
                  <div class="email">{{ scope.row.email }}</div>
                  <div class="phone">{{ scope.row.phone || '未设置电话' }}</div>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_admin ? 'danger' : 'primary'">
              {{ scope.row.is_admin ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="车辆数量" width="120">
          <template #default="scope">
            <div class="vehicle-info-cell">
              <el-badge :value="scope.row.vehicle_count || 0" class="item vehicle-badge">
                <el-icon size="24"><Van /></el-icon>
              </el-badge>
              <div class="vehicle-text">
                <div class="vehicle-count">{{ scope.row.vehicle_count || 0 }}辆</div>
                <div class="vehicle-label">车辆</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="160">
          <template #default="scope">
            <div class="time-cell">
              <div class="date">{{ formatDate(scope.row.created_at) }}</div>
              <div class="time">{{ formatTime(scope.row.created_at) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="(scope.row.is_active !== false) ? 'success' : 'danger'">
              {{ (scope.row.is_active !== false) ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewUserDetail(scope.row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button 
              size="small" 
              :type="(scope.row.is_active !== false) ? 'warning' : 'success'"
              @click="toggleUserStatus(scope.row)"
            >
              {{ (scope.row.is_active !== false) ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalUsers"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 用户详情对话框 -->
    <el-dialog 
      v-model="userDetailVisible" 
      title="用户详细信息" 
      width="800px"
    >
      <div v-if="selectedUser" class="user-detail">
        <!-- 基本信息 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card shadow="never">
              <template #header>
                <span>基本信息</span>
              </template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="用户ID">
                  {{ selectedUser.id }}
                </el-descriptions-item>
                <el-descriptions-item label="用户名">
                  {{ selectedUser.username }}
                </el-descriptions-item>
                <el-descriptions-item label="邮箱">
                  {{ selectedUser.email }}
                </el-descriptions-item>
                <el-descriptions-item label="电话">
                  {{ selectedUser.phone || '未设置' }}
                </el-descriptions-item>
                <el-descriptions-item label="角色">
                  <el-tag :type="selectedUser.is_admin ? 'danger' : 'primary'">
                    {{ selectedUser.is_admin ? '管理员' : '普通用户' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag :type="(selectedUser.is_active !== false) ? 'success' : 'danger'">
                    {{ (selectedUser.is_active !== false) ? '正常' : '禁用' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="注册时间">
                  {{ formatDateTime(selectedUser.created_at) }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card shadow="never">
              <template #header>
                <span>统计信息</span>
              </template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="车辆数量">
                  {{ selectedUser.vehicle_count || 0 }}辆
                </el-descriptions-item>
                <el-descriptions-item label="充电次数">
                  {{ selectedUser.charging_count || 0 }}次
                </el-descriptions-item>
                <el-descriptions-item label="总充电量">
                  {{ selectedUser.total_energy || 0 }}度
                </el-descriptions-item>
                <el-descriptions-item label="总费用">
                  ¥{{ selectedUser.total_cost || 0 }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
        </el-row>

        <!-- 车辆信息 -->
        <el-card shadow="never" style="margin-top: 20px;" v-if="selectedUser.vehicles && selectedUser.vehicles.length > 0">
          <template #header>
            <span>名下车辆 ({{ selectedUser.vehicles.length }}辆)</span>
          </template>
          <el-table 
            :data="selectedUser.vehicles" 
            style="width: 100%"
            empty-text="该用户暂无车辆"
          >
            <el-table-column prop="license_plate" label="车牌号" width="150" />
            <el-table-column prop="model" label="车型" width="150">
              <template #default="scope">
                {{ scope.row.model || '未设置' }}
              </template>
            </el-table-column>
            <el-table-column prop="battery_capacity" label="电池容量" width="120">
              <template #default="scope">
                {{ scope.row.battery_capacity }}度
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="添加时间" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-tag type="success">正常</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 充电详单 -->
        <el-card shadow="never" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>用户充电详单</span>
              <el-button type="primary" size="small" @click="viewUserOrders">
                查看全部详单
              </el-button>
            </div>
          </template>
          <el-table 
            :data="userOrders" 
            v-loading="ordersLoading"
            style="width: 100%"
            empty-text="暂无充电详单"
          >
            <el-table-column prop="record_number" label="订单编号" width="150" />
            <el-table-column prop="vehicle" label="车牌号" width="120">
              <template #default="scope">
                {{ scope.row.vehicle?.license_plate }}
              </template>
            </el-table-column>
                          <el-table-column prop="charging_amount" label="充电量(度)" width="100" />
            <el-table-column prop="total_fee" label="总费用" width="100">
              <template #default="scope">
                <span class="total-fee">
                  {{ scope.row.total_fee ? `¥${scope.row.total_fee}` : '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getOrderStatusType(scope.row.status)" size="small">
                  {{ getOrderStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="150">
              <template #default="scope">
                {{ formatDateTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button
                  type="text"
                  size="small"
                  @click="viewOrderDetail(scope.row)"
                >
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  Search, 
  View, 
  Van 
} from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const users = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const vehicleFilter = ref('')
const userDetailVisible = ref(false)
const selectedUser = ref(null)

// 充电详单相关
const userOrders = ref([])
const ordersLoading = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const totalUsers = ref(0)

// 计算属性
const filteredUsers = computed(() => {
  let result = users.value

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(user => 
      user.username.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query)
    )
  }

  // 状态过滤
  if (statusFilter.value === 'admin') {
    result = result.filter(user => user.is_admin)
  } else if (statusFilter.value === 'user') {
    result = result.filter(user => !user.is_admin)
  }

  // 车辆过滤
  if (vehicleFilter.value === 'has_vehicles') {
    result = result.filter(user => user.vehicle_count > 0)
  } else if (vehicleFilter.value === 'no_vehicles') {
    result = result.filter(user => user.vehicle_count === 0)
  }

  totalUsers.value = result.length
  
  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 方法
const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/users')
    console.log('API响应数据:', response) // 调试信息
    
    // 直接使用后端返回的数据，不做额外处理
    users.value = response || []
    
    console.log('获取用户列表成功，数量:', users.value.length)
    if (users.value.length > 0) {
      console.log('用户数据样例:', users.value[0]) // 调试信息
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const fetchUserDetail = async (userId) => {
  try {
    const response = await api.get(`/admin/users/${userId}/detail`)
    return response
  } catch (error) {
    console.error('获取用户详情失败:', error)
    throw error
  }
}

const viewUserDetail = async (user) => {
  try {
    loading.value = true
    const userDetail = await fetchUserDetail(user.id)
    selectedUser.value = userDetail
    userDetailVisible.value = true
    
    // 同时获取用户的充电详单
    fetchUserOrders(user.id)
  } catch (error) {
    ElMessage.error('获取用户详情失败')
  } finally {
    loading.value = false
  }
}

// 获取用户充电详单
const fetchUserOrders = async (userId) => {
  ordersLoading.value = true
  try {
    const response = await api.get(`/admin/users/${userId}/charging-orders?limit=10`)
    userOrders.value = response.data || []
  } catch (error) {
    console.error('获取用户充电详单失败:', error)
    userOrders.value = []
  } finally {
    ordersLoading.value = false
  }
}

// 查看用户全部详单
const viewUserOrders = () => {
  if (selectedUser.value) {
    // 跳转到详单管理页面，并传递用户ID作为过滤条件
    const route = `/admin/charging-orders?username=${selectedUser.value.username}`
    window.open(route, '_blank')
  }
}

// 查看订单详情
const viewOrderDetail = (order) => {
  // 这里可以打开一个订单详情弹窗或跳转到详情页
  console.log('查看订单详情:', order)
}

// 获取订单状态类型
const getOrderStatusType = (status) => {
  const typeMap = {
    'created': '',
    'assigned': 'warning',
    'charging': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return typeMap[status] || ''
}

// 获取订单状态文本
const getOrderStatusText = (status) => {
  const textMap = {
    'created': '已创建',
    'assigned': '已分配',
    'charging': '充电中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return textMap[status] || status
}

const toggleUserStatus = async (user) => {
  const isActive = user.is_active !== false
  const action = isActive ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${user.username}" 吗？`,
      `确认${action}`,
      {
        type: 'warning',
        confirmButtonText: action,
        cancelButtonText: '取消'
      }
    )
    
    await api.put(`/admin/users/${user.id}/status`, {
      is_active: !isActive
    })
    
    ElMessage.success(`用户${action}成功`)
    await fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(`${action}用户失败:`, error)
      ElMessage.error(`${action}用户失败`)
    }
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const formatTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生命周期
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
}

.search-filters {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.user-detail {
  max-height: 600px;
  overflow-y: auto;
  padding: 10px 0;
}

.item {
  margin-right: 4px;
}

.total-fee {
  color: #e6a23c;
  font-weight: bold;
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header) {
  background-color: #fafafa;
}

:deep(.el-table__row) {
  height: 80px; /* 增加行高 */
}

:deep(.el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

:deep(.el-table td) {
  padding: 16px 12px !important; /* 增加单元格内边距 */
  vertical-align: middle;
}

:deep(.el-table th) {
  padding: 16px 12px !important; /* 增加表头内边距 */
  height: 60px;
}

/* 卡片样式优化 */
:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

:deep(.el-card__header) {
  background-color: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

/* 对话框样式优化 */
:deep(.el-dialog) {
  border-radius: 8px;
}

:deep(.el-dialog__header) {
  background-color: #fafafa;
  border-radius: 8px 8px 0 0;
}

/* 按钮样式优化 */
:deep(.el-button) {
  border-radius: 6px;
}

/* 标签样式优化 */
:deep(.el-tag) {
  border-radius: 4px;
}

/* 分页样式优化 */
:deep(.el-pagination) {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-management {
    padding: 10px;
  }
  
  :deep(.el-table) {
    font-size: 12px;
  }
  
  .search-filters {
    padding: 12px;
  }
  
  :deep(.el-col) {
    margin-bottom: 10px;
  }
}

/* 空状态优化 */
:deep(.el-table__empty-block) {
  padding: 40px 0;
}

:deep(.el-empty) {
  padding: 40px 0;
}

/* 加载状态优化 */
:deep(.el-loading-mask) {
  border-radius: 8px;
}

/* 用户信息单元格样式 */
.user-info-cell {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.user-main {
  flex: 1;
}

.username {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.email {
  font-size: 13px;
  color: #606266;
}

.phone {
  font-size: 12px;
  color: #909399;
}

/* 车辆信息单元格样式 */
.vehicle-info-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 0;
}

.vehicle-badge {
  flex-shrink: 0;
}

.vehicle-text {
  text-align: center;
  margin-left: 8px;
}

.vehicle-count {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 2px;
}

.vehicle-label {
  font-size: 12px;
  color: #909399;
}

/* 时间显示样式 */
.time-cell {
  text-align: center;
  padding: 8px 0;
}

.date {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
}

.time {
  font-size: 12px;
  color: #909399;
}
</style> 