<template>
  <div class="charging-records">
    <div class="page-header">
      <h2>我的充电记录</h2>
      <p>查看所有充电记录，实际消费总金额：<span class="total-amount">¥{{ totalActualAmount }}</span></p>
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
          <el-button type="primary" @click="fetchRecords" :loading="loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 记录列表 -->
    <el-card class="records-card">
      <template #header>
        <div class="card-header">
          <span>充电记录列表</span>
          <div class="header-actions">
            <span class="record-count">共 {{ records.length }} 条记录</span>
            <el-button type="text" @click="fetchRecords" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table 
        :data="filteredRecords" 
        v-loading="loading"
        stripe
        border
        @row-click="showRecordDetail"
        style="cursor: pointer"
        empty-text="暂无充电记录"
      >
        <el-table-column prop="record_number" label="订单编号" width="180" fixed="left" />
        <el-table-column prop="created_at" label="订单生成时间" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="license_plate" label="车牌号" width="120" />
        <el-table-column prop="charging_mode" label="充电模式" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.charging_mode === 'fast' ? 'success' : 'warning'" size="small">
              {{ scope.row.charging_mode === 'fast' ? '快充' : '慢充' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="charging_amount" label="计划充电量" width="120">
          <template #default="scope">
            {{ scope.row.charging_amount }}度
          </template>
        </el-table-column>
        <el-table-column prop="actual_charging_amount" label="实际充电量" width="120">
          <template #default="scope">
            {{ scope.row.actual_charging_amount ? scope.row.actual_charging_amount.toFixed(2) + '度' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="charging_duration" label="充电时长" width="120">
          <template #default="scope">
            {{ formatDuration(scope.row.charging_duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="启动时间" width="160">
          <template #default="scope">
            {{ scope.row.start_time || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="停止时间" width="160">
          <template #default="scope">
            {{ scope.row.end_time || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="actual_total_fee" label="实际费用" width="120">
          <template #default="scope">
            <span class="actual-fee">
              {{ getActualFee(scope.row) }}
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
    </el-card>

    <!-- 记录详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`充电记录详情 - ${selectedRecord?.record_number}`"
      width="700px"
    >
      <div v-if="selectedRecord" class="record-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单编号">
            {{ selectedRecord.record_number }}
          </el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getStatusType(selectedRecord.status)">
              {{ getStatusText(selectedRecord.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="订单生成时间">
            {{ formatDateTime(selectedRecord.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="车牌号">
            {{ selectedRecord.license_plate }}
          </el-descriptions-item>
          <el-descriptions-item label="充电模式">
            <el-tag :type="selectedRecord.charging_mode === 'fast' ? 'success' : 'warning'">
              {{ selectedRecord.charging_mode === 'fast' ? '快充' : '慢充' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="队列号">
            {{ selectedRecord.queue_number }}
          </el-descriptions-item>
          
          <!-- 计划信息 -->
          <el-descriptions-item label="计划充电量">
            {{ selectedRecord.charging_amount }}度
          </el-descriptions-item>
          <el-descriptions-item label="计划电费">
            ¥{{ selectedRecord.electricity_fee || '0.00' }}
          </el-descriptions-item>
          <el-descriptions-item label="计划服务费">
            ¥{{ selectedRecord.service_fee || '0.00' }}
          </el-descriptions-item>
          <el-descriptions-item label="计划总费用">
            ¥{{ selectedRecord.total_fee || '0.00' }}
          </el-descriptions-item>
          
          <!-- 实际信息 -->
          <el-descriptions-item label="实际充电量">
            {{ selectedRecord.actual_charging_amount ? selectedRecord.actual_charging_amount.toFixed(2) + '度' : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="实际电费">
            {{ selectedRecord.actual_electricity_fee ? '¥' + selectedRecord.actual_electricity_fee : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="实际服务费">
            {{ selectedRecord.actual_service_fee ? '¥' + selectedRecord.actual_service_fee : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="实际总费用" :span="2">
            <span class="actual-total-fee-large">
              {{ selectedRecord.actual_total_fee ? '¥' + selectedRecord.actual_total_fee : (selectedRecord.total_fee ? '¥' + selectedRecord.total_fee : '¥0.00') }}
            </span>
          </el-descriptions-item>
          
          <!-- 时间信息 -->
          <el-descriptions-item label="充电时长">
            {{ formatDuration(selectedRecord.charging_duration) }}
          </el-descriptions-item>
          <el-descriptions-item label="剩余时间">
            {{ selectedRecord.remaining_time ? selectedRecord.remaining_time + '分钟' : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="启动时间">
            {{ selectedRecord.start_time || '未开始' }}
          </el-descriptions-item>
          <el-descriptions-item label="停止时间">
            {{ selectedRecord.end_time || '未结束' }}
          </el-descriptions-item>
          
          <!-- 价格信息 -->
          <el-descriptions-item label="电价单价">
            {{ selectedRecord.unit_price ? '¥' + selectedRecord.unit_price + '/度' : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="时段">
            {{ selectedRecord.time_period || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { chargingApi } from '@/api/user'

// 响应式数据
const loading = ref(false)
const records = ref([])
const showDetailDialog = ref(false)
const selectedRecord = ref(null)

// 搜索表单
const searchForm = reactive({
  record_number: '',
  status: '',
  date_range: null
})

// 过滤后的记录
const filteredRecords = computed(() => {
  let filtered = records.value

  if (searchForm.record_number) {
    filtered = filtered.filter(record =>
      record.record_number.toLowerCase().includes(searchForm.record_number.toLowerCase())
    )
  }

  if (searchForm.status) {
    filtered = filtered.filter(record => record.status === searchForm.status)
  }

  if (searchForm.date_range && searchForm.date_range.length === 2) {
    const startDate = new Date(searchForm.date_range[0])
    const endDate = new Date(searchForm.date_range[1])
    endDate.setHours(23, 59, 59, 999) // 设置为当天结束时间

    filtered = filtered.filter(record => {
      const recordDate = new Date(record.created_at)
      return recordDate >= startDate && recordDate <= endDate
    })
  }

  return filtered
})

// 计算用户消费总金额（实际费用）
const totalActualAmount = computed(() => {
  return records.value.reduce((total, record) => {
    const actualFee = parseFloat(record.actual_total_fee) || parseFloat(record.total_fee) || 0
    return total + actualFee
  }, 0).toFixed(2)
})

// 获取充电记录列表
const fetchRecords = async () => {
  loading.value = true
  try {
    const response = await chargingApi.getRecords()
    records.value = response || []
  } catch (error) {
    console.error('获取充电记录失败:', error)
    ElMessage.error('获取充电记录失败')
    records.value = []
  } finally {
    loading.value = false
  }
}

// 显示记录详情
const showRecordDetail = (record) => {
  selectedRecord.value = record
  showDetailDialog.value = true
}

// 获取实际费用显示
const getActualFee = (record) => {
  if (record.actual_total_fee) {
    return '¥' + record.actual_total_fee
  }
  if (record.total_fee) {
    return '¥' + record.total_fee
  }
  return '¥0.00'
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
  fetchRecords()
})
</script>

<style scoped>
.charging-records {
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
  margin-bottom: 10px;
}

.page-header p {
  color: #7f8c8d;
  margin: 0;
  font-size: 16px;
}

.total-amount {
  color: #e6a23c;
  font-weight: bold;
  font-size: 18px;
}

.filter-card {
  margin-bottom: 20px;
}

.records-card {
  background: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.record-count {
  color: #909399;
  font-size: 14px;
}

.actual-fee {
  color: #e6a23c;
  font-weight: bold;
}

.actual-total-fee-large {
  color: #e6a23c;
  font-weight: bold;
  font-size: 18px;
}

.record-detail {
  max-height: 60vh;
  overflow-y: auto;
}

/* 表格行hover效果 */
:deep(.el-table__body-wrapper .el-table__row):hover {
  background-color: #f5f7fa;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .charging-records {
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