<template>
  <div class="admin-layout">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="250px" class="sidebar">
        <div class="logo">
          <el-icon><Lightning /></el-icon>
          <span>充电桩管理系统</span>
        </div>
        
        <el-menu
          :default-active="$route.path"
          class="sidebar-menu"
          @select="handleMenuSelect"
          router
        >
          <el-menu-item index="/admin/charging-scene">
            <el-icon><VideoPlay /></el-icon>
            <span>充电场景动画</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/dashboard">
            <el-icon><Monitor /></el-icon>
            <span>仪表板</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/piles">
            <el-icon><Connection /></el-icon>
            <span>充电桩管理</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/queue-monitoring">
            <el-icon><Connection /></el-icon>
            <span>队列监控</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/reports">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据报表</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/vehicles">
            <el-icon><Van /></el-icon>
            <span>车辆管理</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/config">
            <el-icon><Setting /></el-icon>
            <span>系统配置</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/users">
            <el-icon><UserFilled /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/orders">
            <el-icon><Document /></el-icon>
            <span>订单管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主要内容区域 -->
      <el-container>
        <!-- 顶部导航 -->
        <el-header class="header">
          <div class="header-left">
            <h3>{{ getPageTitle() }}</h3>
          </div>
          
          <div class="header-center">
            <SystemClock />
          </div>
          
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-icon><User /></el-icon>
                管理员
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 主内容 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
    
    <!-- 全局日志组件 -->
    <GlobalLogger />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import SystemClock from '@/components/SystemClock.vue'
import GlobalLogger from '@/components/GlobalLogger.vue'
import { 
  Lightning, 
  Monitor, 
  Connection, 
  DataAnalysis, 
  User, 
  ArrowDown,
  Van,
  VideoPlay,
  Setting,
  UserFilled,
  Document
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const handleMenuSelect = (index) => {
  router.push(index)
}

const getPageTitle = () => {
  const routeMap = {
    '/admin/dashboard': '仪表板',
    '/admin/piles': '充电桩管理',
    '/admin/queue-monitoring': '队列监控',
    '/admin/charging-scene': '充电场景动画',
    '/admin/reports': '数据报表',
    '/admin/vehicles': '车辆管理',
    '/admin/config': '系统配置',
    '/admin/users': '用户管理',
    '/admin/orders': '订单管理'
  }
  return routeMap[router.currentRoute.value.path] || '管理后台'
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      // 跳转到个人信息页面
      break
    case 'logout':
      authStore.logout()
      router.push('/login')
      break
  }
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  color: white;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #434953;
}

.logo .el-icon {
  margin-right: 10px;
  font-size: 24px;
}

.sidebar-menu {
  border: none;
  background-color: transparent;
}

.sidebar-menu .el-menu-item {
  color: #bfcbd9;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-menu-item.is-active {
  background-color: #263445;
  color: #409eff;
}

.header {
  background-color: white;
  border-bottom: 1px solid #e4e7ed;
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

.header-left h3 {
  margin: 0;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
}

.user-info .el-icon {
  margin: 0 5px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  padding-bottom: 200px; /* 为日志组件留出空间 */
}
</style> 