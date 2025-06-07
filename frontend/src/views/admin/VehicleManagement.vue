<template>
  <div class="admin-vehicle-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>所有用户车辆管理</span>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <el-table :data="vehicles" style="width: 100%; min-height: 400px;" v-loading="loading" empty-text="暂无车辆数据">
        <el-table-column prop="license_plate" label="车牌号" width="120" />
        <el-table-column prop="model" label="型号" width="180" />
        <el-table-column prop="battery_capacity" label="电池容量(kWh)" width="130" />
        <el-table-column prop="owner_username" label="车主用户名" width="120" />
        <el-table-column prop="owner_email" label="车主邮箱" width="200" />
        <el-table-column prop="created_at" label="添加时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" type="info" @click="viewDetails(scope.row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 车辆详情对话框 -->
    <el-dialog v-model="detailVisible" title="车辆详情" width="500px">
      <div v-if="selectedVehicle" class="vehicle-details">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="车牌号">
            {{ selectedVehicle.license_plate }}
          </el-descriptions-item>
          <el-descriptions-item label="型号">
            {{ selectedVehicle.model || '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="电池容量">
            {{ selectedVehicle.battery_capacity }} kWh
          </el-descriptions-item>
          <el-descriptions-item label="车主用户名">
            {{ selectedVehicle.owner_username }}
          </el-descriptions-item>
          <el-descriptions-item label="车主邮箱">
            {{ selectedVehicle.owner_email }}
          </el-descriptions-item>
          <el-descriptions-item label="添加时间">
            {{ formatDateTime(selectedVehicle.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import api from '@/utils/api'

const vehicles = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const selectedVehicle = ref(null)

// 获取所有车辆数据
const fetchVehicles = async () => {
  loading.value = true
  try {
    vehicles.value = await api.get('/admin/vehicles')
  } catch (error) {
    console.error('获取车辆列表失败:', error)
    ElMessage.error('获取车辆列表失败')
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  fetchVehicles()
}

// 查看详情
const viewDetails = (vehicle) => {
  selectedVehicle.value = vehicle
  detailVisible.value = true
}

// 格式化日期时间
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

// 页面挂载时获取数据
onMounted(() => {
  fetchVehicles()
})
</script>

<style scoped>
.admin-vehicle-management {
  padding: 0;
  min-height: calc(100vh - 140px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vehicle-details {
  margin: 20px 0;
}

/* 确保卡片有足够的高度 */
.el-card {
  min-height: 500px;
}

/* 空状态样式优化 */
.el-table__empty-block {
  background-color: #fafbfc;
  border-radius: 8px;
  padding: 60px 20px;
}

.el-table__empty-text {
  color: #909399;
  font-size: 16px;
}
</style> 