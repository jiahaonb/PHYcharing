import api from '@/utils/api'

export const userApi = {
  // 车辆管理
  getVehicles: () => api.get('/users/vehicles'),
  createVehicle: (data) => api.post('/users/vehicles', data),
  updateVehicle: (id, data) => api.put(`/users/vehicles/${id}`, data),
  deleteVehicle: (id) => api.delete(`/users/vehicles/${id}`),
  getVehicle: (id) => api.get(`/users/vehicles/${id}`),

  // 车辆监控
  getVehicleMonitoring: () => api.get('/users/vehicles-monitoring'),
  getVehicleDetail: (vehicleId) => api.get(`/users/vehicles/${vehicleId}/detail`),
  endVehicleCharging: (vehicleId) => api.post(`/users/vehicles/${vehicleId}/end-charging`),

  // 队列状态
  getUserQueue: () => api.get('/users/queue/status'),
  
  // 充电配置
  getChargingConfig: () => api.get('/users/charging/config')
}

export const chargingApi = {
  // 充电请求
  submitRequest: (data) => api.post('/charging/request', data),
  getUserQueue: () => api.get('/charging/queue'),
  getQueueInfo: (queueId) => api.get(`/charging/queue/${queueId}`),
  getWaitingCount: (mode) => api.get(`/charging/waiting-count/${mode}`),
  modifyRequest: (queueId, data) => api.put(`/charging/modify/${queueId}`, data),
  cancelCharging: (queueId) => api.delete(`/charging/cancel/${queueId}`),
  
  // 充电记录
  getRecords: () => api.get('/charging/records'),
  getRecord: (recordId) => api.get(`/charging/records/${recordId}`)
} 