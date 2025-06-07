<template>
  <div class="config-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统配置管理</span>
          <div class="header-actions">
            <el-button @click="refreshConfigs" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="showBatchUpdate" type="primary">
              <el-icon><Edit /></el-icon>
              批量编辑
            </el-button>
            <el-button @click="exportConfig" type="success">
              <el-icon><Download /></el-icon>
              导出配置
            </el-button>
          </div>
        </div>
      </template>

      <!-- 配置分类标签页 -->
      <el-tabs v-model="activeCategory" @tab-change="handleCategoryChange">
        <el-tab-pane 
          v-for="(label, key) in categories" 
          :key="key" 
          :label="label" 
          :name="key"
        >
          <div class="config-category">
            <!-- 配置项列表 -->
            <el-table 
              :data="filteredConfigs" 
              style="width: 100%" 
              v-loading="loading"
              empty-text="暂无配置数据"
            >
              <el-table-column prop="config_key" label="配置键" width="200">
                <template #default="scope">
                  <el-tag size="small">{{ scope.row.config_key.split('.')[1] }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="描述" min-width="150" />
              <el-table-column prop="config_value" label="当前值" min-width="200">
                <template #default="scope">
                  <div class="config-value">
                    <span v-if="scope.row.config_type === 'boolean'">
                      <el-tag :type="getBooleanValue(scope.row.config_value) ? 'success' : 'danger'">
                        {{ getBooleanValue(scope.row.config_value) ? '启用' : '禁用' }}
                      </el-tag>
                    </span>
                    <span v-else-if="scope.row.config_type === 'json'">
                      <el-button size="small" text @click="showJsonValue(scope.row)">
                        查看JSON
                      </el-button>
                    </span>
                    <span v-else>{{ scope.row.config_value }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="config_type" label="类型" width="100">
                <template #default="scope">
                  <el-tag size="small" :type="getTypeColor(scope.row.config_type)">
                    {{ scope.row.config_type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_active" label="状态" width="80">
                <template #default="scope">
                  <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
                    {{ scope.row.is_active ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="scope">
                  <el-button size="small" @click="editConfig(scope.row)">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteConfig(scope.row)">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 编辑配置对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="isEditing ? '编辑配置' : '新增配置'" 
      width="600px"
    >
      <el-form 
        :model="editForm" 
        :rules="editRules" 
        ref="editFormRef" 
        label-width="100px"
      >
        <el-form-item label="配置键" prop="config_key">
          <el-input 
            v-model="editForm.config_key" 
            :disabled="isEditing"
            placeholder="例如: system.max_users"
          />
        </el-form-item>
        <el-form-item label="配置类型" prop="config_type">
          <el-select 
            v-model="editForm.config_type" 
            :disabled="isEditing"
            style="width: 100%"
          >
            <el-option label="字符串" value="string" />
            <el-option label="整数" value="integer" />
            <el-option label="浮点数" value="float" />
            <el-option label="布尔值" value="boolean" />
            <el-option label="JSON" value="json" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置值" prop="config_value">
          <el-input 
            v-if="editForm.config_type !== 'boolean' && editForm.config_type !== 'json'"
            v-model="editForm.config_value" 
            placeholder="请输入配置值"
          />
          <el-switch 
            v-else-if="editForm.config_type === 'boolean'"
            v-model="editForm.booleanValue"
            active-text="启用"
            inactive-text="禁用"
          />
          <el-input 
            v-else-if="editForm.config_type === 'json'"
            v-model="editForm.config_value"
            type="textarea"
            :rows="6"
            placeholder="请输入有效的JSON格式"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="editForm.category" style="width: 100%">
            <el-option 
              v-for="(label, key) in categories" 
              :key="key"
              :label="label" 
              :value="key" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="editForm.description" 
            type="textarea"
            placeholder="请输入配置项描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch 
            v-model="editForm.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveConfig" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- JSON查看对话框 -->
    <el-dialog v-model="jsonDialogVisible" title="JSON配置值" width="800px">
      <el-input 
        v-model="jsonValue" 
        type="textarea" 
        :rows="15" 
        readonly
        style="font-family: 'Courier New', monospace;"
      />
    </el-dialog>

    <!-- 批量编辑对话框 -->
    <el-dialog v-model="batchDialogVisible" title="批量编辑配置" width="90%" fullscreen>
      <div class="batch-edit-container">
        <div class="batch-edit-toolbar">
          <el-button @click="selectAllConfigs" type="primary" size="small">
            全选
          </el-button>
          <el-button @click="unselectAllConfigs" size="small">
            取消全选
          </el-button>
          <el-button @click="saveBatchConfigs" type="success" :loading="batchSaving">
            <el-icon><Check /></el-icon>
            保存更改
          </el-button>
        </div>
        
        <el-table 
          :data="allConfigs" 
          style="width: 100%" 
          @selection-change="handleBatchSelection"
          max-height="600px"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="config_key" label="配置键" width="200" />
          <el-table-column prop="description" label="描述" width="150" />
          <el-table-column label="当前值" width="200">
            <template #default="scope">
              <el-input 
                v-if="scope.row.config_type !== 'boolean'"
                v-model="scope.row.config_value"
                size="small"
              />
              <el-switch 
                v-else
                v-model="scope.row.booleanValue"
                size="small"
              />
            </template>
          </el-table-column>
          <el-table-column prop="config_type" label="类型" width="100" />
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-switch 
                v-model="scope.row.is_active"
                size="small"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  Edit, 
  Delete, 
  Download, 
  Check 
} from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const batchSaving = ref(false)
const allConfigs = ref([])
const categories = ref({})
const activeCategory = ref('charging_piles')

// 对话框状态
const editDialogVisible = ref(false)
const jsonDialogVisible = ref(false)
const batchDialogVisible = ref(false)
const isEditing = ref(false)
const jsonValue = ref('')

// 编辑表单
const editForm = reactive({
  config_key: '',
  config_value: '',
  config_type: 'string',
  description: '',
  category: '',
  is_active: true,
  booleanValue: false
})

// 批量编辑
const selectedConfigs = ref([])

// 表单引用
const editFormRef = ref()

// 表单验证规则
const editRules = {
  config_key: [
    { required: true, message: '请输入配置键', trigger: 'blur' }
  ],
  config_value: [
    { required: true, message: '请输入配置值', trigger: 'blur' }
  ],
  config_type: [
    { required: true, message: '请选择配置类型', trigger: 'change' }
  ],
  category: [
    { required: true, message: '请选择配置分类', trigger: 'change' }
  ]
}

// 计算属性
const filteredConfigs = computed(() => {
  return allConfigs.value.filter(config => config.category === activeCategory.value)
})

// 方法
const fetchCategories = async () => {
  try {
    const response = await api.get('/admin/config/categories')
    categories.value = response
  } catch (error) {
    console.error('获取配置分类失败:', error)
    ElMessage.error('获取配置分类失败')
  }
}

const fetchConfigs = async (category = null) => {
  loading.value = true
  try {
    const url = category ? `/admin/config/?category=${category}` : '/admin/config/'
    const response = await api.get(url)
    
    // 处理布尔值
    allConfigs.value = response.map(config => ({
      ...config,
      booleanValue: config.config_type === 'boolean' ? getBooleanValue(config.config_value) : false
    }))
    
    console.log('✅ 配置数据获取成功，数量:', allConfigs.value.length)
  } catch (error) {
    console.error('获取配置失败:', error)
    ElMessage.error('获取配置失败')
  } finally {
    loading.value = false
  }
}

const refreshConfigs = () => {
  fetchConfigs()
}

const handleCategoryChange = (category) => {
  activeCategory.value = category
}

const editConfig = (config) => {
  isEditing.value = true
  Object.assign(editForm, {
    ...config,
    booleanValue: config.config_type === 'boolean' ? getBooleanValue(config.config_value) : false
  })
  editDialogVisible.value = true
}

const deleteConfig = async (config) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除配置项 "${config.config_key}" 吗？`,
      '确认删除',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )
    
    await api.delete(`/admin/config/${config.config_key}`)
    ElMessage.success('配置删除成功')
    await fetchConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除配置失败:', error)
      ElMessage.error('删除配置失败')
    }
  }
}

const saveConfig = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    saving.value = true
    
    // 处理配置值
    let configValue = editForm.config_value
    if (editForm.config_type === 'boolean') {
      configValue = editForm.booleanValue ? 'true' : 'false'
    }
    
    const updateData = {
      config_value: configValue,
      description: editForm.description,
      is_active: editForm.is_active
    }
    
    if (isEditing.value) {
      // 更新配置
      await api.put(`/admin/config/${editForm.config_key}`, updateData)
      ElMessage.success('配置更新成功')
    } else {
      // 创建配置
      await api.post('/admin/config/', {
        ...editForm,
        config_value: configValue
      })
      ElMessage.success('配置创建成功')
    }
    
    editDialogVisible.value = false
    await fetchConfigs()
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  } finally {
    saving.value = false
  }
}

const showJsonValue = (config) => {
  try {
    const parsed = JSON.parse(config.config_value)
    jsonValue.value = JSON.stringify(parsed, null, 2)
  } catch (error) {
    jsonValue.value = config.config_value
  }
  jsonDialogVisible.value = true
}

const getBooleanValue = (value) => {
  return value === 'true' || value === '1' || value === true
}

const getTypeColor = (type) => {
  const colors = {
    'string': 'primary',
    'integer': 'success',
    'float': 'warning',
    'boolean': 'info',
    'json': 'danger'
  }
  return colors[type] || 'primary'
}

const showBatchUpdate = () => {
  batchDialogVisible.value = true
}

const handleBatchSelection = (selection) => {
  selectedConfigs.value = selection
}

const selectAllConfigs = () => {
  // 这里需要通过ref访问table组件的toggleAllSelection方法
  selectedConfigs.value = [...allConfigs.value]
}

const unselectAllConfigs = () => {
  selectedConfigs.value = []
}

const saveBatchConfigs = async () => {
  if (selectedConfigs.value.length === 0) {
    ElMessage.warning('请选择要更新的配置项')
    return
  }
  
  try {
    batchSaving.value = true
    
    const updates = selectedConfigs.value.map(config => ({
      config_key: config.config_key,
      config_value: config.config_type === 'boolean' 
        ? (config.booleanValue ? 'true' : 'false')
        : config.config_value,
      description: config.description,
      is_active: config.is_active
    }))
    
    const response = await api.post('/admin/config/batch-update', updates)
    
    if (response.success_count > 0) {
      ElMessage.success(`成功更新 ${response.success_count} 个配置项`)
    }
    
    if (response.error_count > 0) {
      ElMessage.warning(`${response.error_count} 个配置项更新失败`)
    }
    
    batchDialogVisible.value = false
    await fetchConfigs()
  } catch (error) {
    console.error('批量更新配置失败:', error)
    ElMessage.error('批量更新配置失败')
  } finally {
    batchSaving.value = false
  }
}

const exportConfig = async () => {
  try {
    const response = await api.get('/admin/config/export/yaml')
    
    // 创建下载链接
    const blob = new Blob([response.yaml_content], { type: 'text/yaml' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `system_config_${new Date().toISOString().split('T')[0]}.yaml`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('配置导出成功')
  } catch (error) {
    console.error('导出配置失败:', error)
    ElMessage.error('导出配置失败')
  }
}

// 生命周期
onMounted(async () => {
  console.log('🚀 配置管理页面已挂载，开始加载数据...')
  await Promise.all([
    fetchCategories(),
    fetchConfigs()
  ])
  console.log('✅ 配置管理页面初始化完成')
})
</script>

<style scoped>
.config-management {
  padding: 0;
  min-height: calc(100vh - 140px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.config-category {
  margin-top: 20px;
}

.config-value {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.batch-edit-container {
  height: 100%;
}

.batch-edit-toolbar {
  margin-bottom: 20px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.el-table {
  border-radius: 4px;
}

.el-card {
  min-height: 600px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    gap: 5px;
  }
  
  .batch-edit-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
}
</style> 