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
        empty-text="暂无用户数据"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="phone" label="电话" width="150">
          <template #default="scope">
            {{ scope.row.phone || '未设置' }}
          </template>
        </el-table-column>
        <el-table-column label="角色" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_admin ? 'danger' : 'primary'">
              {{ scope.row.is_admin ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="车辆数量" width="100">
          <template #default="scope">
            <el-badge :value="scope.row.vehicle_count" class="item">
              <el-icon><Van /></el-icon>
            </el-badge>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '正常' : '禁用' }}
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
              :type="scope.row.is_active ? 'warning' : 'success'"
              @click="toggleUserStatus(scope.row)"
            >
              {{ scope.row.is_active ? '禁用' : '启用' }}
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
                  <el-tag :type="selectedUser.is_active ? 'success' : 'danger'">
                    {{ selectedUser.is_active ? '正常' : '禁用' }}
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
                  {{ selectedUser.vehicle_count }}辆
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
                {{ scope.row.battery_capacity }}kWh
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

        <!-- 最近充电记录 -->
        <el-card shadow="never" style="margin-top: 20px;" v-if="selectedUser.recent_records && selectedUser.recent_records.length > 0">
          <template #header>
            <span>最近充电记录</span>
          </template>
          <el-table 
            :data="selectedUser.recent_records" 
            style="width: 100%"
            empty-text="暂无充电记录"
          >
            <el-table-column prop="record_number" label="记录编号" width="150" />
            <el-table-column prop="charging_amount" label="充电量" width="100">
              <template #default="scope">
                {{ scope.row.charging_amount }}度
              </template>
            </el-table-column>
            <el-table-column prop="total_fee" label="费用" width="100">
              <template #default="scope">
                ¥{{ scope.row.total_fee }}
              </template>
            </el-table-column>
            <el-table-column prop="start_time" label="开始时间" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.start_time) }}
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
    users.value = response.map(user => ({
      ...user,
      vehicle_count: user.vehicles ? user.vehicles.length : 0
    }))
    console.log('获取用户列表成功，数量:', users.value.length)
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
  } catch (error) {
    ElMessage.error('获取用户详情失败')
  } finally {
    loading.value = false
  }
}

const toggleUserStatus = async (user) => {
  const action = user.is_active ? '禁用' : '启用'
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
      is_active: !user.is_active
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

// 生命周期
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-filters {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.user-detail {
  max-height: 600px;
  overflow-y: auto;
}

.item {
  margin-right: 4px;
}
</style> 