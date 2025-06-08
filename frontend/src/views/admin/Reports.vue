<template>
  <div class="reports">
    <div class="page-header">
      <h2>数据报表中心</h2>
      <p>系统运营数据分析与统计</p>
    </div>

    <!-- 概览统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stat-content">
            <div class="stat-icon revenue">
              <el-icon size="40"><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">¥{{ formatNumber(stats.totalRevenue) }}</div>
              <div class="stat-label">总收入</div>
              <div class="stat-trend" :class="stats.revenueTrend > 0 ? 'up' : 'down'">
                <el-icon><ArrowUp v-if="stats.revenueTrend > 0" /><ArrowDown v-else /></el-icon>
                {{ Math.abs(stats.revenueTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stat-content">
            <div class="stat-icon orders">
              <el-icon size="40"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ formatNumber(stats.totalOrders) }}</div>
              <div class="stat-label">总订单数</div>
              <div class="stat-trend" :class="stats.ordersTrend > 0 ? 'up' : 'down'">
                <el-icon><ArrowUp v-if="stats.ordersTrend > 0" /><ArrowDown v-else /></el-icon>
                {{ Math.abs(stats.ordersTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stat-content">
            <div class="stat-icon energy">
              <el-icon size="40"><Lightning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ formatNumber(stats.totalEnergy) }}</div>
              <div class="stat-label">总充电量(度)</div>
              <div class="stat-trend" :class="stats.energyTrend > 0 ? 'up' : 'down'">
                <el-icon><ArrowUp v-if="stats.energyTrend > 0" /><ArrowDown v-else /></el-icon>
                {{ Math.abs(stats.energyTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stat-content">
            <div class="stat-icon users">
              <el-icon size="40"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ formatNumber(stats.activeUsers) }}</div>
              <div class="stat-label">活跃用户</div>
              <div class="stat-trend" :class="stats.usersTrend > 0 ? 'up' : 'down'">
                <el-icon><ArrowUp v-if="stats.usersTrend > 0" /><ArrowDown v-else /></el-icon>
                {{ Math.abs(stats.usersTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表分析 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>收入趋势分析</span>
              <el-select v-model="revenueChartPeriod" @change="fetchRevenueChart" size="small">
                <el-option label="最近7天" value="7d" />
                <el-option label="最近30天" value="30d" />
                <el-option label="最近90天" value="90d" />
              </el-select>
            </div>
          </template>
          <div ref="revenueChart" style="height: 400px;" v-loading="chartsLoading"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>充电模式分布</span>
              <el-button @click="fetchChargingModeChart" size="small" :loading="chartsLoading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <div ref="chargingModeChart" style="height: 400px;" v-loading="chartsLoading"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据筛选和搜索 -->
    <el-card class="filter-card">
      <template #header>
        <span>数据筛选</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
            style="width: 100%"
          />
        </el-col>
        <el-col :span="4">
          <el-select v-model="reportType" placeholder="报表类型" @change="handleReportTypeChange">
            <el-option label="充电详单" value="orders" />
            <el-option label="用户统计" value="users" />
            <el-option label="充电桩统计" value="piles" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索关键字"
            @input="handleSearch"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="fetchReportData" :loading="tableLoading">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="exportData" :loading="exportLoading">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
          <el-button @click="resetFilters">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>{{ getTableTitle() }}</span>
          <div>
            <el-button @click="fetchReportData" :loading="tableLoading" size="small">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 充电详单表格 -->
      <el-table 
        v-if="reportType === 'orders'"
        :data="paginatedTableData" 
        v-loading="tableLoading"
        style="width: 100%"
        stripe
        border
        row-key="id"
      >
        <el-table-column prop="record_number" label="订单编号" width="180" fixed="left" />
        <el-table-column label="用户信息" width="150">
          <template #default="scope">
            <div class="user-info">
              <div class="username">{{ scope.row.user?.username || '未知用户' }}</div>
              <div class="vehicle">{{ scope.row.vehicle?.license_plate || '未知车辆' }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="充电桩" width="120">
          <template #default="scope">
            {{ scope.row.charging_pile?.pile_number || '未分配' }}
          </template>
        </el-table-column>
        <el-table-column prop="charging_mode" label="充电模式" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.charging_mode === 'FAST' ? 'success' : 'warning'" size="small">
              {{ scope.row.charging_mode === 'FAST' ? '快充' : '慢充' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="charging_amount" label="充电量(度)" width="120">
          <template #default="scope">
            {{ scope.row.charging_amount?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="charging_duration" label="充电时长" width="120">
          <template #default="scope">
            {{ formatDuration(scope.row.charging_duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_fee" label="总费用" width="100">
          <template #default="scope">
            <span class="fee-amount">¥{{ scope.row.total_fee?.toFixed(2) || '0.00' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="time_period" label="时段" width="80">
          <template #default="scope">
            <el-tag 
              :type="getTimePeriodType(scope.row.time_period)" 
              size="small"
            >
              {{ scope.row.time_period || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewOrderDetail(scope.row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 用户统计表格 -->
      <el-table 
        v-else-if="reportType === 'users'"
        :data="paginatedTableData" 
        v-loading="tableLoading"
        style="width: 100%"
        stripe
        border
      >
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="vehicle_count" label="车辆数量" width="100">
          <template #default="scope">
            <el-badge :value="scope.row.vehicle_count || 0">
              <el-icon><Van /></el-icon>
            </el-badge>
          </template>
        </el-table-column>
        <el-table-column prop="charging_count" label="充电次数" width="100" />
        <el-table-column prop="total_energy" label="总充电量(度)" width="140">
          <template #default="scope">
            {{ scope.row.total_energy?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_cost" label="总费用" width="120">
          <template #default="scope">
            <span class="fee-amount">¥{{ scope.row.total_cost?.toFixed(2) || '0.00' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 充电桩统计表格 -->
      <el-table 
        v-else-if="reportType === 'piles'"
        :data="paginatedTableData" 
        v-loading="tableLoading"
        style="width: 100%"
        stripe
        border
      >
        <el-table-column prop="pile_number" label="充电桩编号" width="150" />
        <el-table-column prop="charging_mode" label="充电模式" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.charging_mode === 'FAST' ? 'success' : 'warning'">
              {{ scope.row.charging_mode === 'FAST' ? '快充' : '慢充' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="power" label="功率(kW)" width="100">
          <template #default="scope">
            {{ scope.row.power?.toFixed(1) || '0.0' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getPileStatusType(scope.row.status)">
              {{ getPileStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_charging_count" label="累计充电次数" width="140" />
        <el-table-column prop="total_charging_duration" label="累计充电时长(h)" width="160">
          <template #default="scope">
            {{ scope.row.total_charging_duration?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_charging_amount" label="累计充电量(度)" width="160">
          <template #default="scope">
            {{ scope.row.total_charging_amount?.toFixed(2) || '0.00' }}
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
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 订单详情弹窗 -->
    <el-dialog v-model="orderDetailVisible" title="充电订单详情" width="600px">
      <div v-if="selectedOrder" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单编号">
            {{ selectedOrder.record_number }}
          </el-descriptions-item>
          <el-descriptions-item label="充电模式">
            <el-tag :type="selectedOrder.charging_mode === 'FAST' ? 'success' : 'warning'">
              {{ selectedOrder.charging_mode === 'FAST' ? '快充' : '慢充' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="用户">
            {{ selectedOrder.user?.username || '未知用户' }}
          </el-descriptions-item>
          <el-descriptions-item label="车辆">
            {{ selectedOrder.vehicle?.license_plate || '未知车辆' }}
          </el-descriptions-item>
          <el-descriptions-item label="充电桩">
            {{ selectedOrder.charging_pile?.pile_number || '未分配' }}
          </el-descriptions-item>
          <el-descriptions-item label="充电量">
            {{ selectedOrder.charging_amount?.toFixed(2) || '0.00' }} 度
          </el-descriptions-item>
          <el-descriptions-item label="充电时长">
            {{ formatDuration(selectedOrder.charging_duration) }}
          </el-descriptions-item>
          <el-descriptions-item label="时段">
            {{ selectedOrder.time_period || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="电费">
            ¥{{ selectedOrder.electricity_fee?.toFixed(2) || '0.00' }}
          </el-descriptions-item>
          <el-descriptions-item label="服务费">
            ¥{{ selectedOrder.service_fee?.toFixed(2) || '0.00' }}
          </el-descriptions-item>
          <el-descriptions-item label="总费用" :span="2">
            <span class="total-fee">¥{{ selectedOrder.total_fee?.toFixed(2) || '0.00' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(selectedOrder.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDateTime(selectedOrder.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ formatDateTime(selectedOrder.end_time) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Money,
  Document,
  Lightning,
  User,
  ArrowUp,
  ArrowDown,
  Refresh,
  Search,
  Download,
  RefreshLeft,
  Van
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/utils/api'

// 响应式数据
const chartsLoading = ref(false)
const tableLoading = ref(false)
const exportLoading = ref(false)

// 统计数据
const stats = reactive({
  totalRevenue: 0,
  totalOrders: 0,
  totalEnergy: 0,
  activeUsers: 0,
  revenueTrend: 0,
  ordersTrend: 0,
  energyTrend: 0,
  usersTrend: 0
})

// 图表相关
const revenueChart = ref()
const chargingModeChart = ref()
const revenueChartPeriod = ref('7d')

// 筛选条件
const dateRange = ref([])
const reportType = ref('orders')
const searchKeyword = ref('')

// 表格数据
const tableData = ref([])
const allTableData = ref([]) // 存储所有数据
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 计算经过筛选的数据
const filteredTableData = computed(() => {
  let filtered = allTableData.value
  
  // 搜索筛选
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(item => {
      if (reportType.value === 'orders') {
        return (
          item.record_number?.toLowerCase().includes(keyword) ||
          item.user?.username?.toLowerCase().includes(keyword) ||
          item.vehicle?.license_plate?.toLowerCase().includes(keyword) ||
          item.charging_pile?.pile_number?.toLowerCase().includes(keyword)
        )
      } else if (reportType.value === 'users') {
        return (
          item.username?.toLowerCase().includes(keyword) ||
          item.email?.toLowerCase().includes(keyword)
        )
      } else if (reportType.value === 'piles') {
        return (
          item.pile_number?.toLowerCase().includes(keyword) ||
          item.charging_mode?.toLowerCase().includes(keyword)
        )
      }
      return false
    })
  }
  
  // 日期范围筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const [startDate, endDate] = dateRange.value
    filtered = filtered.filter(item => {
      const itemDate = new Date(item.created_at || item.queue_time || item.start_time)
      const start = new Date(startDate)
      const end = new Date(endDate)
      end.setHours(23, 59, 59, 999) // 包含结束日期的整天
      return itemDate >= start && itemDate <= end
    })
  }
  
  return filtered
})

// 计算当前页显示的数据
const paginatedTableData = computed(() => {
  const filtered = filteredTableData.value
  const start = (pagination.page - 1) * pagination.size
  const end = start + pagination.size
  return filtered.slice(start, end)
})

// 更新分页总数
const updatePagination = () => {
  pagination.total = filteredTableData.value.length
  if (pagination.page > Math.ceil(pagination.total / pagination.size)) {
    pagination.page = 1
  }
}

// 弹窗
const orderDetailVisible = ref(false)
const selectedOrder = ref(null)

// 方法
const formatNumber = (num) => {
  if (!num) return '0'
  return num.toLocaleString()
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

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

const getTimePeriodType = (period) => {
  const typeMap = { '峰时': 'danger', '平时': 'warning', '谷时': 'success' }
  return typeMap[period] || ''
}

const getPileStatusType = (status) => {
  const typeMap = { 'NORMAL': 'success', 'CHARGING': 'primary', 'FAULT': 'danger', 'OFFLINE': 'info' }
  return typeMap[status] || ''
}

const getPileStatusText = (status) => {
  const textMap = { 'NORMAL': '正常', 'CHARGING': '充电中', 'FAULT': '故障', 'OFFLINE': '离线' }
  return textMap[status] || status
}

const getTableTitle = () => {
  const titleMap = {
    'orders': '充电订单详单',
    'users': '用户充电统计',
    'piles': '充电桩运营统计'
  }
  return titleMap[reportType.value] || '数据表格'
}

// 获取概览统计
const fetchStats = async () => {
  try {
    // 获取真实统计数据
    const users = await api.get('/admin/users')
    const piles = await api.get('/admin/piles')
    
    // 计算活跃用户数
    const activeUsers = users.filter(user => user.is_active !== false).length
    
    // 获取所有订单来计算统计
    let totalOrders = 0
    let totalRevenue = 0
    let totalEnergy = 0
    
    for (const user of users) {
      try {
        const userOrders = await api.get(`/admin/users/${user.id}/charging-orders?limit=1000`)
        if (userOrders && userOrders.data) {
          totalOrders += userOrders.data.length
          
          userOrders.data.forEach(order => {
            if (order.total_fee) totalRevenue += order.total_fee
            if (order.charging_amount) totalEnergy += order.charging_amount
          })
        }
      } catch (error) {
        console.warn(`获取用户 ${user.username} 订单统计失败:`, error)
      }
    }
    
    // 更新统计数据
    stats.totalRevenue = totalRevenue
    stats.totalOrders = totalOrders
    stats.totalEnergy = totalEnergy
    stats.activeUsers = activeUsers
    
    // 趋势数据设为0（需要实现历史对比API）
    stats.revenueTrend = 0
    stats.ordersTrend = 0
    stats.energyTrend = 0
    stats.usersTrend = 0
    
      } catch (error) {
      console.error('获取统计数据失败:', error)
      // 如果API调用失败，清空数据
      stats.totalRevenue = 0
      stats.totalOrders = 0
      stats.totalEnergy = 0
      stats.activeUsers = 0
      stats.revenueTrend = 0
      stats.ordersTrend = 0
      stats.energyTrend = 0
      stats.usersTrend = 0
    }
}

// 获取收入趋势图表
const fetchRevenueChart = async () => {
  chartsLoading.value = true
  try {
    let data = []
    let labels = []
    
    try {
      if (revenueChartPeriod.value === '7d') {
        // 获取最近7天的数据
        const today = new Date()
        for (let i = 6; i >= 0; i--) {
          const date = new Date(today)
          date.setDate(date.getDate() - i)
          const dateStr = date.toISOString().split('T')[0]
          
          try {
            const dailyReport = await api.get(`/admin/reports/daily?date=${dateStr}`)
            const dailyRevenue = dailyReport.reduce((sum, report) => sum + (report.total_fee || 0), 0)
            data.push(dailyRevenue)
            labels.push(date.toLocaleDateString('zh-CN', { weekday: 'short' }))
          } catch (error) {
            console.warn(`获取${dateStr}日报表失败:`, error)
            data.push(0)
            labels.push(date.toLocaleDateString('zh-CN', { weekday: 'short' }))
          }
        }
             } else {
         // 月度数据暂时为空，需要实现月度统计API
         data = []
         labels = []
       }
         } catch (error) {
       console.error('获取收入趋势数据失败:', error)
       // 如果API调用失败，清空数据
       data = []
       labels = []
     }
    
    await nextTick()
    if (revenueChart.value) {
      const chart = echarts.init(revenueChart.value)
      
      const hasData = data.length > 0 && data.some(value => value > 0)
      
      chart.setOption({
        title: { 
          text: hasData ? '收入趋势' : '收入趋势（暂无数据）', 
          left: 'center',
          textStyle: {
            color: hasData ? '#303133' : '#909399'
          }
        },
        tooltip: hasData ? { 
          trigger: 'axis',
          formatter: (params) => {
            const value = params[0].data
            return `${params[0].name}<br/>收入: ¥${value.toFixed(2)}`
          }
        } : {},
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: labels },
        yAxis: { type: 'value', name: '金额(元)' },
        series: hasData ? [{
          data: data,
          type: 'line',
          smooth: true,
          areaStyle: { opacity: 0.3 },
          itemStyle: { color: '#409EFF' }
        }] : [],
        graphic: hasData ? [] : [{
          type: 'text',
          left: 'center',
          top: 'middle',
          style: {
            text: '暂无数据',
            fontSize: 16,
            fontWeight: 'bold',
            fill: '#909399'
          }
        }]
      })
    }
  } finally {
    chartsLoading.value = false
  }
}

// 获取充电模式分布图表
const fetchChargingModeChart = async () => {
  chartsLoading.value = true
  try {
    // 获取真实的充电模式分布数据
    let fastCount = 0
    let trickleCount = 0
    
    try {
      const users = await api.get('/admin/users')
      
      for (const user of users) {
        try {
          const userOrders = await api.get(`/admin/users/${user.id}/charging-orders?limit=1000`)
          if (userOrders && userOrders.data) {
            userOrders.data.forEach(order => {
              if (order.charging_mode === 'FAST') {
                fastCount++
              } else if (order.charging_mode === 'TRICKLE') {
                trickleCount++
              }
            })
          }
        } catch (error) {
          console.warn(`获取用户 ${user.username} 订单失败:`, error)
        }
      }
         } catch (error) {
       console.error('获取充电模式数据失败:', error)
       // 如果API调用失败，清空数据
       fastCount = 0
       trickleCount = 0
     }
    
    await nextTick()
    if (chargingModeChart.value) {
      const chart = echarts.init(chargingModeChart.value)
      
      // 如果没有数据，显示空图表
      if (fastCount === 0 && trickleCount === 0) {
        fastCount = 0
        trickleCount = 0
      }
      
      const hasData = fastCount > 0 || trickleCount > 0
      
      chart.setOption({
        title: { 
          text: hasData ? '充电模式分布' : '充电模式分布（暂无数据）', 
          left: 'center',
          textStyle: {
            color: hasData ? '#303133' : '#909399'
          }
        },
        tooltip: hasData ? { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d%})' } : {},
        legend: hasData ? { orient: 'vertical', left: 'left' } : {},
        series: hasData ? [{
          name: '充电模式',
          type: 'pie',
          radius: '60%',
          center: ['50%', '60%'],
          data: [
            { value: fastCount, name: '快充', itemStyle: { color: '#67C23A' } },
            { value: trickleCount, name: '慢充', itemStyle: { color: '#E6A23C' } }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }] : [],
        graphic: hasData ? [] : [{
          type: 'text',
          left: 'center',
          top: 'middle',
          style: {
            text: '暂无数据',
            fontSize: 16,
            fontWeight: 'bold',
            fill: '#909399'
          }
        }]
      })
    }
  } finally {
    chartsLoading.value = false
  }
}

// 获取报表数据
const fetchReportData = async () => {
  tableLoading.value = true
  try {
    if (reportType.value === 'orders') {
      // 获取所有用户的充电订单数据
      try {
        // 先获取所有用户列表
        const users = await api.get('/admin/users')
        let allOrders = []
        
        // 为每个用户获取充电详单
        for (const user of users) {
          try {
            const userOrders = await api.get(`/admin/users/${user.id}/charging-orders?limit=100`)
            if (userOrders && userOrders.data) {
              // 为每个订单添加用户信息
              const ordersWithUser = userOrders.data.map(order => ({
                ...order,
                user: {
                  id: user.id,
                  username: user.username,
                  email: user.email
                }
              }))
              allOrders = allOrders.concat(ordersWithUser)
            }
          } catch (userError) {
            console.warn(`获取用户 ${user.username} 的订单失败:`, userError)
          }
        }
        
        // 按创建时间排序
        allOrders.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        
        allTableData.value = allOrders
        pagination.total = allOrders.length
        pagination.page = 1
      } catch (orderError) {
        console.error('获取订单数据失败:', orderError)
        // 如果失败，设置空数据
        allTableData.value = []
        pagination.total = 0
      }
    } else if (reportType.value === 'users') {
      // 获取用户统计数据
      const response = await api.get('/admin/users')
      allTableData.value = response || []
      pagination.total = allTableData.value.length
      pagination.page = 1
    } else if (reportType.value === 'piles') {
      // 获取充电桩数据
      const response = await api.get('/admin/piles')
      allTableData.value = response || []
      pagination.total = allTableData.value.length
      pagination.page = 1
    }
  } catch (error) {
    console.error('获取报表数据失败:', error)
    ElMessage.error('获取数据失败')
    allTableData.value = []
    pagination.total = 0
  } finally {
    tableLoading.value = false
  }
}

// 事件处理
const handleDateChange = () => {
  pagination.page = 1
  updatePagination()
}

const handleReportTypeChange = () => {
  pagination.page = 1
  fetchReportData()
}

const handleSearch = () => {
  pagination.page = 1
  updatePagination()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  // 对于本地数据不需要重新获取
  // fetchReportData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  // 对于本地数据不需要重新获取
  // fetchReportData()
}

const resetFilters = () => {
  dateRange.value = []
  searchKeyword.value = ''
  pagination.page = 1
  updatePagination()
}

const exportData = async () => {
  exportLoading.value = true
  try {
    // 实现数据导出功能
    ElMessage.success('导出功能开发中...')
  } finally {
    exportLoading.value = false
  }
}

const viewOrderDetail = (order) => {
  selectedOrder.value = order
  orderDetailVisible.value = true
}

// 监听筛选数据变化，自动更新分页
watch(() => filteredTableData.value.length, () => {
  updatePagination()
})

// 生命周期
onMounted(async () => {
  await fetchStats()
  await fetchReportData()
  await nextTick()
  fetchRevenueChart()
  fetchChargingModeChart()
})
</script>

<style scoped>
.reports {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h2 {
  color: #2c3e50;
  margin-bottom: 5px;
  font-size: 28px;
}

.page-header p {
  color: #7f8c8d;
  margin: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-card {
  height: 140px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 10px;
}

.stat-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}

.stat-icon.revenue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.stat-icon.orders { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
.stat-icon.energy { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
.stat-icon.users { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; }

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-trend {
  display: flex;
  align-items: center;
  font-size: 12px;
  font-weight: bold;
}

.stat-trend.up { color: #67c23a; }
.stat-trend.down { color: #f56c6c; }

.charts-row {
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.user-info .username {
  font-weight: 600;
  color: #303133;
}

.user-info .vehicle {
  font-size: 12px;
  color: #909399;
}

.fee-amount {
  color: #e6a23c;
  font-weight: bold;
}

.total-fee {
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
  .reports {
    padding: 10px;
  }
  
  .stat-content {
    flex-direction: column;
    text-align: center;
  }
  
  .stat-icon {
    margin-right: 0;
    margin-bottom: 10px;
  }
}
</style> 