<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-left">
        <h2>智能充电桩系统</h2>
      </div>
      <div class="header-center">
        <SystemClock />
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ authStore.user?.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container>
      <el-aside class="layout-aside">
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/user/dashboard">
            <el-icon><Odometer /></el-icon>
            <span>仪表板</span>
          </el-menu-item>
          <el-menu-item index="/user/charging">
            <el-icon><Lightning /></el-icon>
            <span>充电请求</span>
          </el-menu-item>
          <el-menu-item index="/user/queue">
            <el-icon><Clock /></el-icon>
            <span>排队状态</span>
          </el-menu-item>
          <el-menu-item index="/user/records">
            <el-icon><Document /></el-icon>
            <span>充电记录</span>
          </el-menu-item>
          <el-menu-item index="/user/vehicles">
            <el-icon><Van /></el-icon>
            <span>车辆管理</span>
          </el-menu-item>
          <el-menu-item index="/user/vehicle-monitoring">
            <el-icon><Monitor /></el-icon>
            <span>车辆监控</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
    
    <!-- 全局日志组件 -->
    <GlobalLogger />
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage } from 'element-plus'
import SystemClock from '@/components/SystemClock.vue'
import GlobalLogger from '@/components/GlobalLogger.vue'
import { 
  User, 
  ArrowDown, 
  Odometer, 
  Lightning, 
  Clock, 
  Document, 
  Van,
  Monitor
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-left h2 {
  color: #333;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #333;
}

.user-info .el-icon {
  margin: 0 5px;
}

.layout-aside {
  width: 200px;
  background: #f5f5f5;
}

.sidebar-menu {
  border: none;
  background: #f5f5f5;
}

.layout-main {
  background: #f0f2f5;
  padding: 20px;
  padding-bottom: 200px; /* 为日志组件留出空间 */
}
</style> 