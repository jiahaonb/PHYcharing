import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.is_admin || false
  },

  actions: {
    async login(credentials) {
      try {
        const formData = new FormData()
        formData.append('username', credentials.username)
        formData.append('password', credentials.password)
        
        const response = await api.post('/auth/login', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        console.log('登录响应:', response)
        this.token = response.access_token
        localStorage.setItem('token', this.token)
        
        // 获取用户信息
        await this.fetchUser()
        console.log('用户信息获取完成:', this.user)
        console.log('是否管理员:', this.isAdmin)
        
        return response
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },

    async register(userData) {
      try {
        const response = await api.post('/auth/register', userData)
        return response
      } catch (error) {
        throw error
      }
    },

    async fetchUser() {
      try {
        const user = await api.get('/auth/me')
        this.user = user
        localStorage.setItem('user', JSON.stringify(user))
        return user
      } catch (error) {
        this.logout()
        throw error
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
}) 