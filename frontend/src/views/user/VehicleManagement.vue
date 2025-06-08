<template>
  <div class="vehicle-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>车辆管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加车辆
          </el-button>
        </div>
      </template>
      
      <el-table :data="vehicles" style="width: 100%; min-height: 400px;" empty-text="暂无车辆，请添加车辆">
        <el-table-column prop="license_plate" label="车牌号" width="120" />
        <el-table-column prop="model" label="型号" width="180" />
        <el-table-column prop="battery_capacity" label="电池容量(度)" width="130" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="editVehicle(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteVehicle(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑车辆对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="vehicleForm" :rules="rules" label-width="100px">
        <el-form-item label="车牌号" prop="license_plate">
          <el-input v-model="vehicleForm.license_plate" />
        </el-form-item>
        <el-form-item label="型号" prop="model">
          <el-input v-model="vehicleForm.model" placeholder="例如：比亚迪汉EV、特斯拉Model 3" />
        </el-form-item>
        <el-form-item label="电池容量" prop="battery_capacity">
          <el-input-number v-model="vehicleForm.battery_capacity" :min="10" :max="200" :precision="1" />
          <span style="margin-left: 10px;">度</span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveVehicle">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'

const vehicles = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const formRef = ref()

const vehicleForm = ref({
  license_plate: '',
  model: '',
  battery_capacity: 50
})

const rules = {
  license_plate: [{ required: true, message: '请输入车牌号', trigger: 'blur' }],
  model: [{ required: true, message: '请输入型号', trigger: 'blur' }],
  battery_capacity: [{ required: true, message: '请输入电池容量', trigger: 'blur' }]
}

// API调用函数
const fetchVehicles = async () => {
  try {
    vehicles.value = await api.get('/users/vehicles')
  } catch (error) {
    console.error('获取车辆列表失败:', error)
    ElMessage.error('获取车辆列表失败')
  }
}

const showAddDialog = () => {
  dialogTitle.value = '添加车辆'
  isEdit.value = false
  vehicleForm.value = {
    license_plate: '',
    model: '',
    battery_capacity: 50
  }
  dialogVisible.value = true
}

const editVehicle = (vehicle) => {
  dialogTitle.value = '编辑车辆'
  isEdit.value = true
  vehicleForm.value = { ...vehicle }
  dialogVisible.value = true
}

const saveVehicle = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await api.put(`/users/vehicles/${vehicleForm.value.id}`, vehicleForm.value)
          ElMessage.success('车辆更新成功')
        } else {
          await api.post('/users/vehicles', vehicleForm.value)
          ElMessage.success('车辆添加成功')
        }
        dialogVisible.value = false
        await fetchVehicles() // 重新获取车辆列表
      } catch (error) {
        console.error('保存车辆失败:', error)
        ElMessage.error('保存车辆失败')
      }
    }
  })
}

const deleteVehicle = async (vehicle) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除车辆 ${vehicle.license_plate} 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await api.delete(`/users/vehicles/${vehicle.id}`)
    ElMessage.success('车辆删除成功')
    await fetchVehicles() // 重新获取车辆列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除车辆失败:', error)
      ElMessage.error('删除车辆失败')
    }
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchVehicles()
})
</script>

<style scoped>
.vehicle-management {
  padding: 0;
  min-height: calc(100vh - 140px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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