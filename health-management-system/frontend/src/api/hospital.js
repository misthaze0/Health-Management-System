import request from '@/utils/request'

/**
 * 获取医院/体检机构列表
 */
export function getHospitals(params) {
  return request({
    url: '/hospitals',
    method: 'get',
    params
  })
}

/**
 * 获取附近医院
 * @param {Object} data - 包含 lat(纬度), lng(经度)
 */
export function getNearbyHospitals(data) {
  return request({
    url: '/hospitals/nearby',
    method: 'post',
    data
  })
}

/**
 * 获取医院详情
 */
export function getHospitalDetail(id) {
  return request({
    url: `/hospitals/${id}`,
    method: 'get'
  })
}
