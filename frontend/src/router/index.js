import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue')
  },
  {
    path: '/user',
    name: 'UserLayout',
    component: () => import('@/layouts/UserLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'UserDashboard',
        component: () => import('@/views/user/Dashboard.vue')
      },
      {
        path: 'charging',
        name: 'ChargingRequest',
        component: () => import('@/views/user/ChargingRequest.vue')
      },
      {
        path: 'queue',
        name: 'QueueStatus',
        component: () => import('@/views/user/QueueStatus.vue')
      },
      {
        path: 'records',
        name: 'ChargingRecords',
        component: () => import('@/views/user/ChargingRecords.vue')
      },
      {
        path: 'vehicles',
        name: 'VehicleManagement',
        component: () => import('@/views/user/VehicleManagement.vue')
      },
      {
        path: 'vehicle-monitoring',
        name: 'VehicleMonitoring',
        component: () => import('@/views/user/VehicleMonitoring.vue')
      }
    ]
  },
  {
    path: '/admin',
    name: 'AdminLayout',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/charging-scene',
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue')
      },
      {
        path: 'piles',
        name: 'PileManagement',
        component: () => import('@/views/admin/PileManagement.vue')
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/admin/Reports.vue')
      },
      {
        path: 'vehicles',
        name: 'AdminVehicleManagement',
        component: () => import('@/views/admin/VehicleManagement.vue')
      },
      {
        path: 'queue-monitoring',
        name: 'QueueMonitoring',
        component: () => import('@/views/admin/QueueMonitoring.vue')
      },
      {
        path: 'charging-scene',
        name: 'ChargingSceneAnimation',
        component: () => import('@/views/admin/ChargingSceneAnimation.vue')
      },
      {
        path: 'config',
        name: 'ConfigManagement',
        component: () => import('@/views/admin/ConfigManagement.vue')
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/UserManagement.vue')
      },
      {
        path: 'orders',
        name: 'OrderManagement',
        component: () => import('@/views/admin/OrderManagement.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.user?.is_admin) {
    next('/user/dashboard')
  } else {
    next()
  }
})

export default router 