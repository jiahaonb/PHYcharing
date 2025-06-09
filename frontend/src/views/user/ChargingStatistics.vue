<template>
  <div class="charging-statistics">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>�������ͳ��</span>
          <div>
            <el-select v-model="selectedYear" placeholder="ѡ�����" style="width: 120px; margin-right: 10px">
              <el-option v-for="year in availableYears" :key="year" :label="year + '��'" :value="year" />
            </el-select>
          </div>
        </div>
      </template>
      
      <div v-loading="loading">
        <!-- ����ͼ�� -->
        <div class="chart-container">
          <v-chart class="chart" :option="chartOption" autoresize />
        </div>
        
        <!-- ͳ�ƿ�Ƭ -->
        <el-row :gutter="20" class="statistics-cards">
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <template #header>
                <div class="card-header-small">
                  <span>�ܳ�����</span>
                </div>
              </template>
              <div class="stat-value">{{ statistics.totalCount || 0 }}</div>
              <div class="stat-desc">����ȳ���ܴ���</div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <template #header>
                <div class="card-header-small">
                  <span>�ܳ����</span>
                </div>
              </template>
              <div class="stat-value">{{ formatNumber(statistics.totalEnergy) || 0 }} <span class="stat-unit">��</span></div>
              <div class="stat-desc">����ȳ���ܵ���</div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <template #header>
                <div class="card-header-small">
                  <span>�ܷ���</span>
                </div>
              </template>
              <div class="stat-value">{{ formatNumber(statistics.totalFee) || 0 }} <span class="stat-unit">Ԫ</span></div>
              <div class="stat-desc">����ȳ���ܷ���</div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <template #header>
                <div class="card-header-small">
                  <span>ƽ������</span>
                </div>
              </template>
              <div class="stat-value">{{ formatNumber(statistics.averagePrice) || 0 }} <span class="stat-unit">Ԫ/��</span></div>
              <div class="stat-desc">�����ƽ�����</div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- ��ϸ���ݱ��� -->
        <div class="data-table-container">
          <h3>�¶�����</h3>
          <el-table :data="monthlyData" style="width: 100%">
            <el-table-column label="�·�" min-width="80">
              <template #default="scope">
                {{ scope.row.month }}��
              </template>
            </el-table-column>
            <el-table-column label="������" min-width="100">
              <template #default="scope">
                {{ scope.row.count }}��
              </template>
            </el-table-column>
            <el-table-column label="�����" min-width="100">
              <template #default="scope">
                {{ formatNumber(scope.row.energy) }}��
              </template>
            </el-table-column>
            <el-table-column label="���" min-width="100">
              <template #default="scope">
                {{ formatNumber(scope.row.electricityFee) }}Ԫ
              </template>
            </el-table-column>
            <el-table-column label="�����" min-width="100">
              <template #default="scope">
                {{ formatNumber(scope.row.serviceFee) }}Ԫ
              </template>
            </el-table-column>
            <el-table-column label="�ܷ���" min-width="100">
              <template #default="scope">
                <span class="highlight-value">{{ formatNumber(scope.row.totalFee) }}Ԫ</span>
              </template>
            </el-table-column>
            <el-table-column label="ƽ������" min-width="100">
              <template #default="scope">
                {{ formatNumber(scope.row.averagePrice) }}Ԫ/��
              </template>
            </el-table-column>
            <el-table-column label="���ʱ�ηֲ�" min-width="180">
              <template #default="scope">
                <el-progress
                  :percentage="getPeakPercentage(scope.row)"
                  :color="customColors"
                  :format="() => '��ʱ: ' + scope.row.peakCount + '��'"
                  :stroke-width="15"
                  style="margin-bottom: 5px"
                />
                <el-progress
                  :percentage="getNormalPercentage(scope.row)"
                  :color="customColors"
                  :format="() => 'ƽʱ: ' + scope.row.normalCount + '��'"
                  :stroke-width="15"
                  style="margin-bottom: 5px"
                />
                <el-progress
                  :percentage="getValleyPercentage(scope.row)"
                  :color="customColors"
                  :format="() => '��ʱ: ' + scope.row.valleyCount + '��'"
                  :stroke-width="15"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- ʱ�ηֲ�ͼ�� -->
        <div class="chart-container">
          <h3>���ʱ�ηֲ�</h3>
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

// ע�� ECharts ���
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

// ���ݺ�״̬
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

// �Զ�����ɫ
const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 }
]

// �����ѡ����ݣ���ǰ��ݺ�ǰ2�꣩
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear, currentYear - 1, currentYear - 2]
})

// ��ȡ����¼
const fetchRecords = async () => {
  loading.value = true
  try {
    const response = await api.get('/charging/records')
    records.value = response
    processData()
  } catch (error) {
    console.error('��ȡ����¼ʧ��:', error)
    ElMessage.error('��ȡ����¼ʧ��')
  } finally {
    loading.value = false
  }
}

// �������ݣ����·�ͳ��
const processData = () => {
  const year = selectedYear.value
  const yearRecords = records.value.filter(record => 
    new Date(record.start_time).getFullYear() === year
  )
  
  // ��ʼ���¶�����
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
  
  // ͳ��ÿ������
  yearRecords.forEach(record => {
    const month = new Date(record.start_time).getMonth()
    months[month].count++
    // 使用实际数据，如果没有则使用计划数据
    const actualAmount = record.actual_charging_amount || record.charging_amount || 0
    const actualElectricityFee = parseFloat(record.actual_electricity_fee) || parseFloat(record.electricity_fee) || 0
    const actualServiceFee = parseFloat(record.actual_service_fee) || parseFloat(record.service_fee) || 0
    const actualTotalFee = parseFloat(record.actual_total_fee) || parseFloat(record.total_fee) || 0
    
    months[month].energy += actualAmount
    months[month].electricityFee += actualElectricityFee
    months[month].serviceFee += actualServiceFee
    months[month].totalFee += actualTotalFee
    
    // ͳ��ʱ�ηֲ�
    if (record.time_period === 'peak') {
      months[month].peakCount++
    } else if (record.time_period === 'normal') {
      months[month].normalCount++
    } else if (record.time_period === 'valley') {
      months[month].valleyCount++
    }
  })
  
  // ����ƽ������
  months.forEach(month => {
    if (month.energy > 0) {
      month.averagePrice = month.totalFee / month.energy
    }
  })
  
  monthlyData.value = months
  
  // �������ͳ��
  statistics.value = {
    totalCount: yearRecords.length,
    totalEnergy: yearRecords.reduce((sum, record) => sum + (record.actual_charging_amount || record.charging_amount || 0), 0),
    totalFee: yearRecords.reduce((sum, record) => sum + (parseFloat(record.actual_total_fee) || parseFloat(record.total_fee) || 0), 0),
    averagePrice: 0
  }
  
  if (statistics.value.totalEnergy > 0) {
    statistics.value.averagePrice = statistics.value.totalFee / statistics.value.totalEnergy
  }
}

// ������ʱ�ΰٷֱ�
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

// ��ʽ������
const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  return parseFloat(num).toFixed(2)
}

// ͼ������
const chartOption = computed(() => {
  const months = monthlyData.value.map(item => item.month + '��')
  const energyData = monthlyData.value.map(item => item.energy)
  const feeData = monthlyData.value.map(item => item.totalFee)
  
  return {
    title: {
      text: selectedYear.value + '������������',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['�����(��)', '����(Ԫ)'],
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
        name: '�����(��)',
        position: 'left'
      },
      {
        type: 'value',
        name: '����(Ԫ)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '�����(��)',
        type: 'bar',
        data: energyData,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '����(Ԫ)',
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

// ��ͼ����
const pieChartOption = computed(() => {
  // ���������·ݵ�ʱ������
  const totalPeak = monthlyData.value.reduce((sum, month) => sum + month.peakCount, 0)
  const totalNormal = monthlyData.value.reduce((sum, month) => sum + month.normalCount, 0)
  const totalValley = monthlyData.value.reduce((sum, month) => sum + month.valleyCount, 0)
  
  return {
    title: {
      text: selectedYear.value + '����ʱ�ηֲ�',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: '0%',
      data: ['��ʱ', 'ƽʱ', '��ʱ']
    },
    series: [
      {
        name: '���ʱ��',
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
          { value: totalPeak, name: '��ʱ', itemStyle: { color: '#F56C6C' } },
          { value: totalNormal, name: 'ƽʱ', itemStyle: { color: '#E6A23C' } },
          { value: totalValley, name: '��ʱ', itemStyle: { color: '#67C23A' } }
        ]
      }
    ]
  }
})

// ������ݱ仯���´�������
watch(selectedYear, () => {
  processData()
})

// �������ʱ��ȡ����
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