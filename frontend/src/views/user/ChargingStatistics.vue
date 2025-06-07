<template>
  <div class="charging-statistics">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>充电消费统计</span>
          <div>
            <el-select v-model="selectedYear" placeholder="选择年份" style="width: 120px; margin-right: 10px">
              <el-option v-for="year in availableYears" :key="year" :label="year + '年'" :value="year" />
            </el-select>
          </div>
        </div>
      </template>
      
      <div v-loading="loading">
        <!-- 消费图表 -->
        <div class="chart-container">
          <v-chart class="chart" :option="chartOption" autoresize />
        </div>
        
        <!-- 统计卡片 -->
        <el-row :gutter="20" class="statistics-cards">
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <template #header>
                <div class="card-header-small">
                  <span>总充电次数</span>
                </div>
              </template>
              <div class="stat-value">{{ statistics.totalCount || 0 }}</div>
              <div class="stat-desc">本年度充电总次数</div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <template #header>
                <div class="card-header-small">
                  <span>总充电量</span>
                </div>
              </template>
              <div class="stat-value">{{ formatNumber(statistics.totalEnergy) || 0 }} <span class="stat-unit">度</span></div>
              <div class="stat-desc">本年度充电总电量</div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <template #header>
                <div class="card-header-small">
                  <span>总费用</span>
                </div>
              </template>
              <div class="stat-value">{{ formatNumber(statistics.totalFee) || 0 }} <span class="stat-unit">元</span></div>
              <div class="stat-desc">本年度充电总费用</div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <template #header>
                <div class="card-header-small">
                  <span>平均单价</span>
                </div>
              </template>
              <div class="stat-value">{{ formatNumber(statistics.averagePrice) || 0 }} <span class="stat-unit">元/度</span></div>
              <div class="stat-desc">本年度平均电价</div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 详细数据表格 -->
        <div class="data-table-container">
          <h3>月度详情</h3>
          <el-table :data="monthlyData" style="width: 100%">
            <el-table-column label="月份" min-width="80">
              <template #default="scope">
                {{ scope.row.month }}月
              </template>
            </el-table-column>
            <el-table-column label="充电次数" min-width="100">
              <template #default="scope">
                {{ scope.row.count }}次
              </template>
            </el-table-column>
            <el-table-column label="充电量" min-width="100">
              <template #default="scope">
                {{ formatNumber(scope.row.energy) }}度
              </template>
            </el-table-column>
            <el-table-column label="电费" min-width="100">
              <template #default="scope">
                {{ formatNumber(scope.row.electricityFee) }}元
              </template>
            </el-table-column>
            <el-table-column label="服务费" min-width="100">
              <template #default="scope">
                {{ formatNumber(scope.row.serviceFee) }}元
              </template>
            </el-table-column>
            <el-table-column label="总费用" min-width="100">
              <template #default="scope">
                <span class="highlight-value">{{ formatNumber(scope.row.totalFee) }}元</span>
              </template>
            </el-table-column>
            <el-table-column label="平均单价" min-width="100">
              <template #default="scope">
                {{ formatNumber(scope.row.averagePrice) }}元/度
              </template>
            </el-table-column>
            <el-table-column label="充电时段分布" min-width="180">
              <template #default="scope">
                <el-progress
                  :percentage="getPeakPercentage(scope.row)"
                  :color="customColors"
                  :format="() => '峰时: ' + scope.row.peakCount + '次'"
                  :stroke-width="15"
                  style="margin-bottom: 5px"
                />
                <el-progress
                  :percentage="getNormalPercentage(scope.row)"
                  :color="customColors"
                  :format="() => '平时: ' + scope.row.normalCount + '次'"
                  :stroke-width="15"
                  style="margin-bottom: 5px"
                />
                <el-progress
                  :percentage="getValleyPercentage(scope.row)"
                  :color="customColors"
                  :format="() => '谷时: ' + scope.row.valleyCount + '次'"
                  :stroke-width="15"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 时段分布图表 -->
        <div class="chart-container">
          <h3>充电时段分布</h3>
          <v-chart class="chart" :option="pieChartOption" autoresize />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 数据和状态
const loading = ref(false)
const selectedYear = ref(new Date().getFullYear())
const records = ref([])
const monthlyData = ref([])
const statistics = ref({
  totalCount: 0,
  totalEnergy: 0,
  totalFee: 0,
  averagePrice: 0
})

// 自定义颜色
const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 }
]

// 计算可选的年份（当前年份和前2年）
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear, currentYear - 1, currentYear - 2]
})

// 获取充电记录
const fetchRecords = async () => {
  loading.value = true
  try {
    const response = await api.get('/charging/records')
    records.value = response
    processData()
  } catch (error) {
    console.error('获取充电记录失败:', error)
    ElMessage.error('获取充电记录失败')
  } finally {
    loading.value = false
  }
}

// 处理数据，按月份统计
const processData = () => {
  const year = selectedYear.value
  const yearRecords = records.value.filter(record => 
    new Date(record.start_time).getFullYear() === year
  )
  
  // 初始化月度数据
  const months = Array.from({ length: 12 }, (_, i) => ({
    month: i + 1,
    count: 0,
    energy: 0,
    electricityFee: 0,
    serviceFee: 0,
    totalFee: 0,
    peakCount: 0,
    normalCount: 0,
    valleyCount: 0,
    averagePrice: 0
  }))
  
  // 统计每月数据
  yearRecords.forEach(record => {
    const month = new Date(record.start_time).getMonth()
    months[month].count++
    months[month].energy += record.charging_amount
    months[month].electricityFee += record.electricity_fee
    months[month].serviceFee += record.service_fee
    months[month].totalFee += record.total_fee
    
    // 统计时段分布
    if (record.time_period === 'peak') {
      months[month].peakCount++
    } else if (record.time_period === 'normal') {
      months[month].normalCount++
    } else if (record.time_period === 'valley') {
      months[month].valleyCount++
    }
  })
  
  // 计算平均单价
  months.forEach(month => {
    if (month.energy > 0) {
      month.averagePrice = month.totalFee / month.energy
    }
  })
  
  monthlyData.value = months
  
  // 计算年度统计
  statistics.value = {
    totalCount: yearRecords.length,
    totalEnergy: yearRecords.reduce((sum, record) => sum + record.charging_amount, 0),
    totalFee: yearRecords.reduce((sum, record) => sum + record.total_fee, 0),
    averagePrice: 0
  }
  
  if (statistics.value.totalEnergy > 0) {
    statistics.value.averagePrice = statistics.value.totalFee / statistics.value.totalEnergy
  }
}

// 计算充电时段百分比
const getPeakPercentage = (row) => {
  const total = row.peakCount + row.normalCount + row.valleyCount
  return total === 0 ? 0 : Math.round((row.peakCount / total) * 100)
}

const getNormalPercentage = (row) => {
  const total = row.peakCount + row.normalCount + row.valleyCount
  return total === 0 ? 0 : Math.round((row.normalCount / total) * 100)
}

const getValleyPercentage = (row) => {
  const total = row.peakCount + row.normalCount + row.valleyCount
  return total === 0 ? 0 : Math.round((row.valleyCount / total) * 100)
}

// 格式化数字
const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  return parseFloat(num).toFixed(2)
}

// 图表配置
const chartOption = computed(() => {
  const months = monthlyData.value.map(item => item.month + '月')
  const energyData = monthlyData.value.map(item => item.energy)
  const feeData = monthlyData.value.map(item => item.totalFee)
  
  return {
    title: {
      text: selectedYear.value + '年充电消费趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['充电量(度)', '费用(元)'],
      bottom: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months
    },
    yAxis: [
      {
        type: 'value',
        name: '充电量(度)',
        position: 'left'
      },
      {
        type: 'value',
        name: '费用(元)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '充电量(度)',
        type: 'bar',
        data: energyData,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '费用(元)',
        type: 'line',
        yAxisIndex: 1,
        data: feeData,
        itemStyle: {
          color: '#F56C6C'
        },
        lineStyle: {
          width: 3
        },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  }
})

// 饼图配置
const pieChartOption = computed(() => {
  // 汇总所有月份的时段数据
  const totalPeak = monthlyData.value.reduce((sum, month) => sum + month.peakCount, 0)
  const totalNormal = monthlyData.value.reduce((sum, month) => sum + month.normalCount, 0)
  const totalValley = monthlyData.value.reduce((sum, month) => sum + month.valleyCount, 0)
  
  return {
    title: {
      text: selectedYear.value + '年充电时段分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: '0%',
      data: ['峰时', '平时', '谷时']
    },
    series: [
      {
        name: '充电时段',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: totalPeak, name: '峰时', itemStyle: { color: '#F56C6C' } },
          { value: totalNormal, name: '平时', itemStyle: { color: '#E6A23C' } },
          { value: totalValley, name: '谷时', itemStyle: { color: '#67C23A' } }
        ]
      }
    ]
  }
})

// 监听年份变化重新处理数据
watch(selectedYear, () => {
  processData()
})

// 组件挂载时获取数据
onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.charging-statistics {
  padding: 0;
  min-height: calc(100vh - 140px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header-small {
  font-size: 14px;
  color: #606266;
}

.chart-container {
  margin: 20px 0;
  padding: 10px;
  background-color: #fff;
  border-radius: 4px;
}

.chart {
  height: 400px;
}

.statistics-cards {
  margin: 20px 0;
}

.stat-card {
  text-align: center;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  margin: 10px 0;
}

.stat-unit {
  font-size: 14px;
  color: #909399;
}

.stat-desc {
  font-size: 12px;
  color: #909399;
}

.data-table-container {
  margin: 30px 0;
}

.data-table-container h3 {
  margin-bottom: 15px;
  padding-left: 10px;
  border-left: 4px solid #409EFF;
}

.highlight-value {
  font-weight: bold;
  color: #F56C6C;
}
</style> 