import request from '@/utils/request'

/**
 * 获取健康记录列表
 * @param {Object} params - 查询参数
 * @param {string} params.metricType - 指标类型
 * @param {string} params.startDate - 开始日期
 * @param {string} params.endDate - 结束日期
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getHealthRecords(params) {
  return request({
    url: '/health/records',
    method: 'get',
    params
  })
}

/**
 * 获取健康统计数据
 * @param {Object} params - 查询参数
 * @param {string} params.metricType - 指标类型
 * @param {string} params.startDate - 开始日期
 * @param {string} params.endDate - 结束日期
 */
export function getHealthStatistics(params) {
  return request({
    url: '/health/statistics',
    method: 'get',
    params
  })
}

/**
 * 获取最新指标数据
 * @param {string} metricType - 指标类型（可选）
 */
export function getLatestMetrics(metricType) {
  return request({
    url: '/health/latest',
    method: 'get',
    params: metricType ? { metricType } : {}
  })
}

/**
 * 添加健康记录
 * @param {Object} data - 健康记录数据
 * @param {string} data.metricType - 指标类型
 * @param {number} data.metricValue - 指标值
 * @param {string} data.recordDate - 记录日期
 * @param {string} data.notes - 备注
 */
export function addHealthRecord(data) {
  return request({
    url: '/health/records',
    method: 'post',
    data
  })
}

/**
 * 更新健康记录
 * @param {number} recordId - 记录ID
 * @param {Object} data - 健康记录数据
 */
export function updateHealthRecord(recordId, data) {
  return request({
    url: `/health/records/${recordId}`,
    method: 'put',
    data
  })
}

/**
 * 删除健康记录
 * @param {number} recordId - 记录ID
 */
export function deleteHealthRecord(recordId) {
  return request({
    url: `/health/records/${recordId}`,
    method: 'delete'
  })
}

/**
 * 批量删除健康记录
 * @param {number[]} recordIds - 记录ID数组
 */
export function batchDeleteHealthRecords(recordIds) {
  return request({
    url: '/health/records/batch',
    method: 'delete',
    data: { recordIds }
  })
}

/**
 * 按日期范围删除健康记录
 * @param {Object} params - 删除参数
 * @param {string} params.startDate - 开始日期
 * @param {string} params.endDate - 结束日期
 * @param {string[]} params.metricTypes - 指标类型数组（可选）
 */
export function deleteHealthRecordsByDateRange(params) {
  return request({
    url: '/health/records/by-date-range',
    method: 'delete',
    data: params
  })
}

/**
 * 指标类型常量定义
 */
export const MetricTypes = {
  // 身体指标
  RESTING_HEART_RATE: 'resting_heart_rate',
  SPO2: 'spo2',
  HRV: 'hrv',
  SLEEP_EFFICIENCY: 'sleep_efficiency',
  DEEP_SLEEP: 'deep_sleep',
  RESPIRATORY_RATE: 'respiratory_rate',
  NIGHT_HR_VARIABILITY: 'night_hr_variability',
  // 运动指标
  STEPS: 'steps',
  CALORIES: 'calories',
  EXERCISE_DURATION: 'exercise_duration'
}

/**
 * 指标类型显示名称映射
 */
export const MetricTypeLabels = {
  [MetricTypes.RESTING_HEART_RATE]: '静息心率',
  [MetricTypes.SPO2]: '夜间血氧',
  [MetricTypes.HRV]: '心率变异性',
  [MetricTypes.SLEEP_EFFICIENCY]: '睡眠效率',
  [MetricTypes.DEEP_SLEEP]: '深睡占比',
  [MetricTypes.RESPIRATORY_RATE]: '呼吸频率',
  [MetricTypes.NIGHT_HR_VARIABILITY]: '夜间心率波动',
  [MetricTypes.STEPS]: '步数',
  [MetricTypes.CALORIES]: '卡路里',
  [MetricTypes.EXERCISE_DURATION]: '运动时长'
}

/**
 * 指标单位映射
 */
export const MetricTypeUnits = {
  [MetricTypes.RESTING_HEART_RATE]: 'bpm',
  [MetricTypes.SPO2]: '%',
  [MetricTypes.HRV]: 'ms',
  [MetricTypes.SLEEP_EFFICIENCY]: '%',
  [MetricTypes.DEEP_SLEEP]: '%',
  [MetricTypes.RESPIRATORY_RATE]: '次/分',
  [MetricTypes.NIGHT_HR_VARIABILITY]: 'bpm',
  [MetricTypes.STEPS]: '步',
  [MetricTypes.CALORIES]: 'kcal',
  [MetricTypes.EXERCISE_DURATION]: '分钟'
}

/**
 * 指标正常范围定义
 */
export const MetricTypeRanges = {
  [MetricTypes.RESTING_HEART_RATE]: { min: 60, max: 100, label: '60-100' },
  [MetricTypes.SPO2]: { min: 95, max: 100, label: '95-100%' },
  [MetricTypes.HRV]: { min: 20, max: 200, label: '20-200ms' },
  [MetricTypes.SLEEP_EFFICIENCY]: { min: 85, max: 95, label: '85-95%' },
  [MetricTypes.DEEP_SLEEP]: { min: 15, max: 25, label: '15-25%' },
  [MetricTypes.RESPIRATORY_RATE]: { min: 12, max: 20, label: '12-20次/分' },
  [MetricTypes.NIGHT_HR_VARIABILITY]: { min: 50, max: 90, label: '50-90bpm' },
  [MetricTypes.STEPS]: { min: 6000, max: 10000, label: '6000-10000步' },
  [MetricTypes.CALORIES]: { min: 300, max: 500, label: '300-500kcal' },
  [MetricTypes.EXERCISE_DURATION]: { min: 30, max: 60, label: '30-60分钟' }
}
