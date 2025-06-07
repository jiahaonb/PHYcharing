<template>
  <div class="reports">
    <el-card>
      <template #header>
        <span>数据报表</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>收入统计</span>
            </template>
            <div ref="revenueChart" style="height: 400px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>使用统计</span>
            </template>
            <div ref="usageChart" style="height: 400px;"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card>
            <template #header>
              <span>充电记录</span>
            </template>
            <el-table :data="chargingRecords" style="width: 100%">
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="user" label="用户" width="120" />
              <el-table-column prop="pile" label="充电桩" width="120" />
              <el-table-column prop="duration" label="充电时长" width="120" />
              <el-table-column prop="energy" label="充电量(kWh)" width="120" />
              <el-table-column prop="cost" label="费用(元)" width="120" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const revenueChart = ref()
const usageChart = ref()

const chargingRecords = ref([
  { date: '2024-01-15', user: '张三', pile: 'FC001', duration: '2小时30分', energy: 75.0, cost: 52.5 },
  { date: '2024-01-15', user: '李四', pile: 'SC001', duration: '5小时15分', energy: 36.8, cost: 25.8 },
  { date: '2024-01-14', user: '王五', pile: 'FC002', duration: '1小时45分', energy: 52.5, cost: 36.8 },
])

const initCharts = () => {
  if (revenueChart.value) {
    const chart = echarts.init(revenueChart.value)
    chart.setOption({
      title: { text: '月度收入趋势' },
      tooltip: { trigger: 'axis' },
      xAxis: { 
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [15000, 18000, 22000, 20000, 25000, 28000],
        type: 'line',
        smooth: true
      }]
    })
  }

  if (usageChart.value) {
    const chart = echarts.init(usageChart.value)
    chart.setOption({
      title: { text: '充电桩使用率' },
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '50%',
        data: [
          { value: 35, name: '快充桩' },
          { value: 65, name: '慢充桩' }
        ]
      }]
    })
  }
}

onMounted(() => {
  nextTick(() => {
    initCharts()
  })
})
</script>

<style scoped>
.reports {
  padding: 0;
}
</style> 