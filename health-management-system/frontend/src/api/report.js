import request from '@/utils/request'
import { getToken } from '@/utils/auth'

// Python AI服务基础URL
const AI_SERVICE_BASE = '/ai-service/api/v1'

/**
 * 获取报告列表
 * @param {string} userId - 用户ID
 */
export function getReports(userId) {
  return request({
    url: '/report/list',
    method: 'get',
    params: { userId }
  })
}

/**
 * 上传体检报告PDF
 * @param {FormData} formData - 包含文件和表单数据的FormData对象
 */
export function uploadReport(formData) {
  return request({
    url: '/report/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取报告详情
 */
export function getReportDetail(reportId) {
  return request({
    url: `/report/${reportId}`,
    method: 'get'
  })
}

/**
 * AI解读报告
 * 调用Python AI服务，上传PDF文件进行解析分析
 */
export async function analyzeReport(reportId, userId) {
  // 先获取报告详情
  const detail = await getReportDetail(reportId)
  console.log('报告详情响应:', detail)

  // 处理两种可能的响应结构
  let report
  
  if (detail.code === 200 && detail.data) {
    // 结构1: 标准响应格式
    report = detail.data.report
  } else if (detail.report) {
    // 结构2: 直接返回report对象
    report = detail.report
  } else {
    throw new Error('获取报告详情失败')
  }

  // 获取PDF文件URL
  const fileUrl = report.fileUrl || report.file_url
  if (!fileUrl) {
    throw new Error('报告文件不存在')
  }

  // 下载PDF文件
  console.log('下载PDF文件:', fileUrl)
  const fileResponse = await fetch(fileUrl)
  if (!fileResponse.ok) {
    throw new Error('下载报告文件失败')
  }

  // 将文件转换为Blob
  const fileBlob = await fileResponse.blob()
  const fileName = report.fileName || report.file_name || `report_${reportId}.pdf`
  const file = new File([fileBlob], fileName, { type: 'application/pdf' })

  // 使用Kimi API上传并分析PDF文件
  console.log('上传PDF到Kimi API进行分析')
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${AI_SERVICE_BASE}/report/analyze-file?report_type=general`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`
    },
    body: formData
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'AI分析失败')
  }

  const result = await response.json()
  if (result.code === 200) {
    // 构造分析结果文本
    const analysisData = result.data
    const analysisText = formatAnalysisResult(analysisData)
    
    // 保存AI分析结果到后端
    await saveAnalysisResult(reportId, {
      analysis: analysisText,
      summary: analysisData.report_summary?.overall_assessment || '',
      suggestions: analysisData.health_suggestions?.map(s => s.suggestion).join('\n') || ''
    })
    return result.data
  }
  throw new Error(result.message || '报告解读失败')
}

/**
 * 格式化分析结果为文本
 */
function formatAnalysisResult(data) {
  const sections = []
  
  // 报告摘要
  if (data.report_summary) {
    sections.push(`报告类型：${data.report_summary.report_type || '体检报告'}`)
    sections.push(`体检日期：${data.report_summary.exam_date || '-'}`)
    sections.push(`体检中心：${data.report_summary.exam_center || '-'}`)
    sections.push(`总体评估：${data.report_summary.overall_assessment || '-'}`)
  }
  
  // 异常指标
  if (data.abnormal_findings && data.abnormal_findings.length > 0) {
    sections.push('\n【异常指标】')
    data.abnormal_findings.forEach((item, index) => {
      sections.push(`${index + 1}. ${item.indicator_name}: ${item.value} (参考范围: ${item.reference_range})`)
      sections.push(`   临床意义：${item.clinical_significance || '-'}`)
    })
  }
  
  // 健康建议
  if (data.health_suggestions && data.health_suggestions.length > 0) {
    sections.push('\n【健康建议】')
    data.health_suggestions.forEach((item, index) => {
      sections.push(`${index + 1}. ${item.category || '一般建议'}`)
      sections.push(`   ${item.suggestion || '-'}`)
    })
  }
  
  // 随访建议
  if (data.follow_up) {
    sections.push('\n【随访建议】')
    sections.push(`建议复查项目：${data.follow_up.recommended_tests || '-'}`)
    sections.push(`建议复查时间：${data.follow_up.timeframe || '-'}`)
    sections.push(`注意事项：${data.follow_up.notes || '-'}`)
  }
  
  return sections.join('\n')
}

/**
 * 保存AI分析结果
 * @param {string} reportId - 报告ID
 * @param {Object} analysisData - 分析数据
 */
export function saveAnalysisResult(reportId, analysisData) {
  return request({
    url: `/report/${reportId}/analysis`,
    method: 'post',
    data: analysisData
  })
}

/**
 * 删除报告
 * @param {string} reportId - 报告ID
 */
export function deleteReport(reportId) {
  return request({
    url: `/report/${reportId}`,
    method: 'delete'
  })
}

/**
 * 上传并分析医疗报告文件（使用 Kimi API）
 * @param {File} file - 报告文件
 * @param {string} reportType - 报告类型
 */
export async function analyzeMedicalReportFile(file, reportType = 'general') {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${AI_SERVICE_BASE}/report/analyze-file?report_type=${reportType}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`
    },
    body: formData
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '文件分析失败')
  }

  return await response.json()
}

/**
 * 获取医疗报告分析模板
 */
export async function getAnalysisTemplate() {
  const response = await fetch(`${AI_SERVICE_BASE}/report/analysis-template`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    }
  })

  if (!response.ok) {
    throw new Error('获取分析模板失败')
  }

  return await response.json()
}
