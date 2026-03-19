import request from '@/utils/request'

// 获取体检预约列表
export function getAppointments() {
  return request({
    url: '/physical-exam/appointments',
    method: 'get'
  })
}

// 创建体检预约
export function createAppointment(data) {
  return request({
    url: '/physical-exam/appointments',
    method: 'post',
    data
  })
}

// 更新体检预约
export function updateAppointment(appointmentId, data) {
  return request({
    url: `/physical-exam/appointments/${appointmentId}`,
    method: 'put',
    data
  })
}

// 取消体检预约
export function cancelAppointment(appointmentId) {
  return request({
    url: `/physical-exam/appointments/${appointmentId}/cancel`,
    method: 'put'
  })
}

// 获取体检报告列表
export function getReports() {
  return request({
    url: '/physical-exam/reports',
    method: 'get'
  })
}

// 获取体检报告详情
export function getReportDetail(reportId) {
  return request({
    url: `/physical-exam/reports/${reportId}`,
    method: 'get'
  })
}

// 上传体检报告
export function uploadReport(data) {
  return request({
    url: '/physical-exam/reports/upload',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
