<template>
  <div class="charging-records">
    <el-card>
      <template #header>
        <span>充电记录</span>
      </template>
      
      <el-table :data="records" style="width: 100%; min-height: 400px;" empty-text="暂无充电记录">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="pile" label="充电桩" width="120" />
        <el-table-column prop="startTime" label="开始时间" width="100" />
        <el-table-column prop="endTime" label="结束时间" width="100" />
        <el-table-column prop="duration" label="充电时长" width="100" />
        <el-table-column prop="energy" label="充电量(kWh)" width="120" />
        <el-table-column prop="cost" label="费用(元)" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'completed' ? 'success' : 'warning'">
              {{ scope.row.status === 'completed' ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const records = ref([

])
</script>

<style scoped>
.charging-records {
  padding: 0;
  min-height: calc(100vh - 140px);
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