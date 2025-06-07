<template>
  <div class="pile-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>充电桩管理</span>
          <el-button @click="fetchPiles">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input
              v-model="searchQuery"
              placeholder="搜索充电桩编号"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-select v-model="typeFilter" placeholder="桩类型" clearable @change="handleFilter">
              <el-option label="全部" value="" />
              <el-option label="快充桩" value="fast" />
              <el-option label="慢充桩" value="slow" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select v-model="statusFilter" placeholder="状态" clearable @change="handleFilter">
              <el-option label="全部" value="" />
              <el-option label="正常" value="normal" />
              <el-option label="故障" value="fault" />
              <el-option label="维护" value="maintenance" />
            </el-select>
          </el-col>
        </el-row>
      </div>

      <!-- 充电桩列表 -->
      <el-table 
        :data="filteredPiles" 
        style="width: 100%; min-height: 400px;"
        v-loading="loading"
        empty-text="暂无充电桩数据"
      >
        <el-table-column prop="id" label="桩编号" width="120" />
        <el-table-column prop="name" label="桩名称" width="150" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'fast' ? 'success' : 'info'">
              {{ scope.row.type === 'fast' ? '快充桩' : '慢充桩' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="power" label="额定功率 (kW)" width="120" />
        <el-table-column prop="location" label="位置" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="installDate" label="安装日期" width="120" />
        <el-table-column prop="lastMaintenance" label="上次维护" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              type="success"
              @click="startPile(scope.row)"
              :disabled="scope.row.status === 'normal'"
            >
              启动
            </el-button>
            <el-button 
              size="small" 
              type="warning" 
              @click="maintainPile(scope.row)"
              :disabled="scope.row.status === 'fault'"
            >
              故障
            </el-button>
            <el-button 
              size="small" 
              type="info"
              @click="stopPile(scope.row)"
            >
              停止
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
          :total="totalPiles"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑充电桩对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="pileForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="桩编号" prop="id">
          <el-input v-model="pileForm.id" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="桩名称" prop="name">
          <el-input v-model="pileForm.name" />
        </el-form-item>
        <el-form-item label="桩类型" prop="type">
          <el-select v-model="pileForm.type" placeholder="请选择桩类型">
            <el-option label="快充桩" value="fast" />
            <el-option label="慢充桩" value="slow" />
          </el-select>
        </el-form-item>
        <el-form-item label="额定功率" prop="power">
          <el-input-number
            v-model="pileForm.power"
            :min="1"
            :max="100"
            controls-position="right"
          />
          <span style="margin-left: 10px;">kW</span>
        </el-form-item>
        <el-form-item label="安装位置" prop="location">
          <el-input v-model="pileForm.location" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="pileForm.status" placeholder="请选择状态">
            <el-option label="正常" value="normal" />
            <el-option label="故障" value="fault" />
            <el-option label="维护" value="maintenance" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePile">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalPiles = ref(0)

const piles = ref([])

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const formRef = ref()

const pileForm = ref({
  id: '',
  name: '',
  type: '',
  power: 0,
  location: '',
  status: 'normal'
})

const rules = {
  id: [{ required: true, message: '请输入桩编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入桩名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择桩类型', trigger: 'change' }],
  power: [{ required: true, message: '请输入额定功率', trigger: 'blur' }],
  location: [{ required: true, message: '请输入安装位置', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

// 计算属性
const filteredPiles = computed(() => {
  let result = piles.value

  if (searchQuery.value) {
    result = result.filter(pile => 
      pile.id.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      pile.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (typeFilter.value) {
    result = result.filter(pile => pile.type === typeFilter.value)
  }

  if (statusFilter.value) {
    result = result.filter(pile => pile.status === statusFilter.value)
  }

  totalPiles.value = result.length
  return result.slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value)
})

// API调用方法
const fetchPiles = async () => {
  loading.value = true
  try {
    const data = await api.get('/admin/piles')
    
    // 转换数据格式
    piles.value = data.map(pile => ({
      id: pile.pile_number,
      name: `${pile.charging_mode === 'fast' ? '快充桩' : '慢充桩'}-${pile.pile_number}`,
      type: pile.charging_mode,
      power: pile.power,
      location: `停车位${pile.pile_number}`, // 可以后续优化
      status: pile.status,
      installDate: formatDate(pile.created_at),
      lastMaintenance: formatDate(pile.updated_at),
      originalId: pile.id, // 保存原始ID用于API调用
      ...pile
    }))
    
    totalPiles.value = piles.value.length
  } catch (error) {
    console.error('获取充电桩列表失败:', error)
    ElMessage.error('获取充电桩列表失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toISOString().split('T')[0]
}

// 方法
const getStatusType = (status) => {
  const statusMap = {
    'normal': 'success',
    'charging': 'primary',
    'fault': 'danger',  
    'maintenance': 'warning',
    'offline': 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'normal': '正常',
    'charging': '使用中',
    'fault': '故障',
    'maintenance': '维护中',
    'offline': '离线'
  }
  return statusMap[status] || '未知'
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const showAddDialog = () => {
  dialogTitle.value = '添加充电桩'
  isEdit.value = false
  dialogVisible.value = true
}

const editPile = (pile) => {
  dialogTitle.value = '编辑充电桩'
  isEdit.value = true
  pileForm.value = { ...pile }
  dialogVisible.value = true
}

const resetForm = () => {
  pileForm.value = {
    id: '',
    name: '',
    type: '',
    power: 0,
    location: '',
    status: 'normal'
  }
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const savePile = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      if (isEdit.value) {
        // 编辑逻辑
        const index = piles.value.findIndex(p => p.id === pileForm.value.id)
        if (index !== -1) {
          piles.value[index] = { ...pileForm.value }
          ElMessage.success('充电桩更新成功')
        }
      } else {
        // 添加逻辑
        const exists = piles.value.some(p => p.id === pileForm.value.id)
        if (exists) {
          ElMessage.error('充电桩编号已存在')
          return
        }
        piles.value.push({
          ...pileForm.value,
          installDate: new Date().toISOString().split('T')[0],
          lastMaintenance: new Date().toISOString().split('T')[0]
        })
        ElMessage.success('充电桩添加成功')
      }
      dialogVisible.value = false
    }
  })
}

const startPile = async (pile) => {
  try {
    await ElMessageBox.confirm(
      `确定要启动充电桩 ${pile.id} 吗？`,
      '启动确认',
      { type: 'success' }
    )
    
    await api.post(`/admin/piles/${pile.originalId}/start`)
    ElMessage.success('充电桩已启动')
    
    // 刷新数据
    await fetchPiles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('启动充电桩失败:', error)
      ElMessage.error('启动充电桩失败')
    }
  }
}

const stopPile = async (pile) => {
  try {
    await ElMessageBox.confirm(
      `确定要停止充电桩 ${pile.id} 吗？`,
      '停止确认',
      { type: 'warning' }
    )
    
    await api.post(`/admin/piles/${pile.originalId}/stop`)
    ElMessage.success('充电桩已停止')
    
    // 刷新数据
    await fetchPiles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('停止充电桩失败:', error)
      ElMessage.error('停止充电桩失败')
    }
  }
}

const maintainPile = async (pile) => {
  try {
    await ElMessageBox.confirm(
      `确定要设置充电桩 ${pile.id} 为故障状态吗？`,
      '故障确认',
      { type: 'warning' }
    )
    
    // 调用API设置故障
    await api.post(`/admin/piles/${pile.originalId}/fault`)
    ElMessage.success('充电桩已设置为故障状态')
    
    // 刷新数据
    await fetchPiles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('设置故障状态失败:', error)
      ElMessage.error('设置故障状态失败')
    }
  }
}

const deletePile = async (pile) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除充电桩 ${pile.id} 吗？此操作不可恢复！`,
      '删除确认',
      { type: 'warning' }
    )
    
    const index = piles.value.findIndex(p => p.id === pile.id)
    if (index !== -1) {
      piles.value.splice(index, 1)
    }
    
    ElMessage.success('充电桩删除成功')
  } catch {
    // 用户取消操作
  }
}

onMounted(() => {
  fetchPiles()
})
</script>

<style scoped>
.pile-management {
  padding: 0;
  min-height: calc(100vh - 140px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

/* 确保卡片有足够的高度 */
.el-card {
  min-height: 600px;
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