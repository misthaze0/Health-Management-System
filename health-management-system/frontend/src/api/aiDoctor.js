import request from '@/utils/request'
import { getToken } from '@/utils/auth'

// Python AI服务基础URL
const AI_SERVICE_BASE = '/ai-service/api/v1'

/**
 * 发送消息（流式）- 统一走Python AI服务
 * 自动保存对话历史
 */
export async function sendMessageStream(data, onMessage, onError, onComplete) {
  const url = `${AI_SERVICE_BASE}/chat`

  console.log('[Stream] Starting request to:', url)
  console.log('[Stream] Request data:', data)

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify(data)
    })

    console.log('[Stream] Response status:', response.status)
    console.log('[Stream] Response headers:', [...response.headers.entries()])

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // 获取会话ID（从响应头中）
    const sessionId = response.headers.get('X-Session-Id')
    console.log('[Stream] Session ID:', sessionId)

    // 使用更简单的读取方式
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        console.log('[Stream] Reader done')
        onComplete && onComplete(sessionId)
        break
      }

      const text = decoder.decode(value, { stream: true })
      console.log('[Stream] Received raw:', JSON.stringify(text))

      buffer += text
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmedLine = line.trim()
        if (trimmedLine.startsWith('data: ')) {
          const dataContent = trimmedLine.slice(6)
          if (dataContent === '[DONE]') {
            console.log('[Stream] Received [DONE]')
            onComplete && onComplete(sessionId)
            return
          }
          onMessage && onMessage(dataContent)
        }
      }
    }
  } catch (error) {
    console.error('[Stream] Error:', error)
    onError && onError(error)
  }
}

/**
 * 获取AI模型信息
 */
export async function getModelInfo() {
  const response = await fetch(`${AI_SERVICE_BASE}/model/info`)
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '获取模型信息失败')
}

/**
 * 获取所有可用的AI模型列表
 */
export async function getAvailableModels() {
  const response = await fetch(`${AI_SERVICE_BASE}/models`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`
    }
  })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '获取模型列表失败')
}

/**
 * 切换AI模型
 * @param {string} modelId - 要切换的模型ID
 */
export async function switchModel(modelId) {
  const response = await fetch(`${AI_SERVICE_BASE}/model/switch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify({ model_id: modelId })
  })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '切换模型失败')
}

/**
 * 获取用户的模型偏好
 */
export async function getUserModelPreference() {
  const response = await fetch(`${AI_SERVICE_BASE}/model/preference`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`
    }
  })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '获取模型偏好失败')
}

// ==================== 对话历史管理API ====================

/**
 * 获取用户的对话历史
 * 用户ID从JWT Token中自动获取
 */
export async function getChatHistory(limit = 50) {
  const response = await fetch(`${AI_SERVICE_BASE}/history?limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`
    }
  })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '获取对话历史失败')
}

/**
 * 获取指定会话的对话历史
 * 用户ID从JWT Token中自动获取
 */
export async function getSessionHistory(sessionId, limit = 50) {
  const encodedSessionId = encodeURIComponent(sessionId)
  const response = await fetch(`${AI_SERVICE_BASE}/history/${encodedSessionId}?limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`
    }
  })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '获取会话历史失败')
}

/**
 * 保存对话历史（手动保存，通常不需要，因为流式接口已自动保存）
 */
export async function saveChatHistory(data) {
  const response = await fetch(`${AI_SERVICE_BASE}/chat/save`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '保存对话历史失败')
}

/**
 * 删除单条对话记录
 * 用户ID从JWT Token中自动获取
 */
export async function deleteChatHistoryById(recordId) {
  const response = await fetch(`${AI_SERVICE_BASE}/history/${recordId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${getToken()}`
    }
  })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '删除对话记录失败')
}

/**
 * 批量删除对话记录
 * 用户ID从JWT Token中自动获取
 */
export async function deleteChatHistoryBatch(ids, sessionId = null) {
  const response = await fetch(`${AI_SERVICE_BASE}/history/delete`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify({ ids, session_id: sessionId })
  })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '批量删除对话记录失败')
}

/**
 * 清空用户的所有对话历史
 * 用户ID从JWT Token中自动获取
 */
export async function clearAllChatHistory() {
  const token = getToken()
  if (!token) {
    throw new Error('用户未登录')
  }
  
  // 使用POST方法替代DELETE，避免某些浏览器的请求问题
  const response = await fetch(`${AI_SERVICE_BASE}/history/clear-all`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  })
  
  if (!response.ok) {
    const errorText = await response.text()
    console.error('清空历史API错误:', response.status, errorText)
    throw new Error(`HTTP error! status: ${response.status}, ${errorText}`)
  }
  
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '清空对话历史失败')
}

/**
 * 获取用户的会话列表
 * 用户ID从JWT Token中自动获取
 */
export async function getUserSessions(limit = 20) {
  const token = getToken()
  if (!token) {
    throw new Error('用户未登录')
  }
  
  const response = await fetch(`${AI_SERVICE_BASE}/sessions?limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  
  if (!response.ok) {
    const errorText = await response.text()
    console.error('获取会话列表API错误:', response.status, errorText)
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '获取会话列表失败')
}

// ==================== 健康数据分析API ====================

/**
 * 分析健康数据
 */
export async function analyzeHealthData(data) {
  const response = await fetch(`${AI_SERVICE_BASE}/analyze/health`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '健康数据分析失败')
}

/**
 * 生成体检报告解读
 */
export async function generateHealthReport(data) {
  const response = await fetch(`${AI_SERVICE_BASE}/report/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '生成报告失败')
}

/**
 * 健康风险评估
 */
export async function assessHealthRisk(data) {
  const response = await fetch(`${AI_SERVICE_BASE}/risk/assess`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const result = await response.json()
  if (result.code === 200) {
    return result.data
  }
  throw new Error(result.message || '风险评估失败')
}
