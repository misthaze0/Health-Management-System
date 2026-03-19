<template>
  <div class="ai-doctor-container">
    <!-- 页面头部 - 参考体检机构hero-section设计 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">AI HEALTH MANAGER</div>
        <h1 class="hero-title">AI健康管理师</h1>
        <p class="hero-subtitle">Intelligent Health Assistant</p>
        <div class="hero-desc">
          <p>基于先进AI技术，为您提供专业健康咨询</p>
          <p>个性化健康建议，让健康管理更智能</p>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat-item model-selector" @click="openModelSwitchDialog" title="点击切换模型">
          <span class="stat-value">{{ modelInfo?.display_name || 'AI' }}</span>
          <span class="stat-label">
            当前模型
            <el-icon class="switch-icon"><Switch /></el-icon>
          </span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value status-indicator" :class="{ active: !loading }"></span>
          <span class="stat-label">{{ loading ? '思考中' : '在线' }}</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value">{{ Math.floor(messages.length / 2) }}</span>
          <span class="stat-label">对话轮次</span>
        </div>
      </div>
      <!-- 装饰性背景元素 -->
      <div class="hero-decoration">
        <div class="deco-ring ring-1"></div>
        <div class="deco-ring ring-2"></div>
        <div class="deco-ring ring-3"></div>
      </div>
    </section>

    <!-- Evil Eye 动态眼睛区域 -->
    <div class="evil-eye-section">
      <EvilEye
        eye-color="#2563eb"
        :intensity="1.3"
        :pupil-size="0.9"
        :iris-width="0.35"
        :glow-intensity="0.3"
        :scale="0.9"
        :noise-scale="1.0"
        :pupil-follow="0.6"
        :flame-speed="0.9"
        background-color="#000000"
      />
      <div class="evil-eye-label">
        <span class="label-text">AI AGENT</span>
        <span class="label-sub">Intelligent Core</span>
      </div>
    </div>

    <!-- 聊天区域 - 直接嵌入在 Evil Eye 下方 -->
    <div class="chat-terminal-section">
      <!-- 终端工具栏 -->
      <div class="terminal-toolbar">
        <div class="toolbar-left">
          <el-tooltip content="开启后，AI将搜索互联网获取最新信息" placement="bottom">
            <el-switch
              v-model="enableWebSearch"
              active-text="联网"
              :active-icon="Search"
              inline-prompt
              class="web-search-switch"
            />
          </el-tooltip>
          <el-button 
            type="primary" 
            link
            size="small"
            @click="createNewChat"
            class="toolbar-btn"
          >
            <el-icon><Plus /></el-icon>
            新对话
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-button 
            type="danger" 
            link
            size="small"
            @click="showManageDialog"
            :disabled="messages.length === 0"
            class="toolbar-btn"
          >
            <el-icon><Delete /></el-icon>
            管理消息
          </el-button>
          <!-- 历史会话列表 -->
          <el-popover
            v-if="chatSessions.length > 0"
            placement="bottom"
            :width="300"
            trigger="click"
            popper-class="session-popover"
          >
            <template #reference>
              <el-button type="info" link size="small" class="toolbar-btn">
                <el-icon><Clock /></el-icon>
                历史记录 ({{ chatSessions.length }})
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
            </template>
            <div class="session-list">
              <div class="session-list-header">
                <span>历史会话</span>
                <el-button 
                  type="danger" 
                  link 
                  size="small"
                  @click="handleClearAllSessions"
                >
                  清空全部
                </el-button>
              </div>
              <div 
                v-for="session in chatSessions.slice(0, 10)" 
                :key="session.id"
                :class="['session-list-item', { active: currentSessionId === session.id }]"
              >
                <div class="session-info" @click="switchSession(session.id)">
                  <span class="session-title">{{ session.title }}</span>
                  <span class="session-time">{{ formatTime(session.lastTime) }}</span>
                </div>
                <el-button
                  type="danger"
                  link
                  size="small"
                  class="session-delete-btn"
                  @click.stop="deleteSession(session.id)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </el-popover>
        </div>
      </div>

      <!-- 消息区域 -->
      <div ref="messageListRef" class="terminal-messages">
        <!-- 欢迎页面 -->
        <div v-if="messages.length === 0" class="welcome-terminal">
          <div class="terminal-header">
            <span class="terminal-prompt">$</span>
            <span class="terminal-text">欢迎使用 AI 健康管理师</span>
          </div>
          <div class="terminal-info">
            <p><span class="terminal-prompt">></span> 基于先进的AI技术，为您提供专业健康咨询</p>
            <p><span class="terminal-prompt">></span> 支持症状咨询、饮食建议、运动指导等</p>
          </div>
          <!-- 快捷问题 -->
          <div class="quick-commands">
            <div class="command-item" v-for="q in quickQuestions" :key="q" @click="sendQuickQuestion(q)">
              <span class="terminal-prompt">$</span>
              <span class="command-text">{{ q }}</span>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <template v-else>
          <div class="terminal-message-list">
            <div
              v-for="(msg, index) in messages"
              :key="msg.id || index"
              :class="['terminal-msg', msg.role === 'user' ? 'user' : 'ai']"
            >
              <div class="msg-header">
                <span class="msg-role">{{ msg.role === 'user' ? 'user@jiuwu' : 'ai@xuanji' }}</span>
                <span class="msg-time">{{ formatTime(msg.time) }}</span>
              </div>
              <div class="msg-content" v-html="formatMessage(msg.content)"></div>
            </div>
            
            <!-- AI正在输入 -->
            <div v-if="loading" class="terminal-msg ai">
              <div class="msg-header">
                <span class="msg-role">ai@xuanji</span>
              </div>
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 输入区域 - 终端样式 -->
      <div class="terminal-input-wrapper">
        <span class="input-prompt">$</span>
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="2"
          placeholder="输入您的问题..."
          resize="none"
          @keydown="handleKeyDown"
          class="terminal-input"
        />
        <button
          type="button"
          :disabled="!inputMessage.trim() || loading"
          @click="handleSendMessage"
          class="terminal-send-btn"
        >
          <el-icon><Promotion /></el-icon>
        </button>
      </div>
    </div>

    <!-- 消息管理对话框 -->
    <el-dialog
      v-model="manageDialogVisible"
      title="管理对话消息"
      width="550px"
      :close-on-click-modal="false"
      class="manage-dialog"
    >
      <div class="manage-content">
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          show-icon
          class="manage-hint"
        >
          <template #default>
            选择要删除的对话轮次，每轮包含用户提问和AI回复。<br>
            删除消息可以释放token空间，避免超出限制。
          </template>
        </el-alert>
        
        <div class="rounds-list">
          <div 
            v-for="(round, idx) in messageRounds" 
            :key="idx"
            class="round-card"
            :class="{ selected: selectedRounds.has(round.userIndex) }"
            @click="toggleSelectRound(round.userIndex)"
          >
            <el-checkbox :model-value="selectedRounds.has(round.userIndex)" />
            <div class="round-info">
              <div class="round-header">
                <span class="round-number">第 {{ idx + 1 }} 轮对话</span>
                <span class="round-badge">{{ round.preview.length }} 字</span>
              </div>
              <div class="round-preview">{{ round.preview }}</div>
            </div>
          </div>
        </div>

        <div v-if="messageRounds.length === 0" class="empty-rounds">
          <el-empty description="暂无对话消息" />
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="manageDialogVisible = false">取消</el-button>
          <el-button
            type="danger"
            @click="deleteSelectedRounds"
            :disabled="selectedRounds.size === 0"
          >
            <el-icon><Delete /></el-icon>
            删除选中 ({{ selectedRounds.size }})
          </el-button>
          <el-button type="warning" @click="clearAllHistory">
            <el-icon><DeleteFilled /></el-icon>
            清空全部
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 模型切换对话框 -->
    <el-dialog
      v-model="modelSwitchDialogVisible"
      title="切换AI模型"
      width="600px"
      :close-on-click-modal="false"
      class="model-switch-dialog"
    >
      <div class="model-list">
        <div
          v-for="model in availableModels"
          :key="model.id"
          class="model-card"
          :class="{
            'is-selected': selectedModelId === model.id,
            'is-current': modelInfo?.model === model.id,
            'is-recommended': model.recommended
          }"
          @click="selectedModelId = model.id"
        >
          <div class="model-header">
            <div class="model-name">{{ model.name }}</div>
            <div class="model-badges">
              <el-tag v-if="model.recommended" type="success" size="small" effect="dark">推荐</el-tag>
              <el-tag v-if="modelInfo?.model === model.id" type="primary" size="small" effect="plain">当前</el-tag>
            </div>
          </div>
          <div class="model-description">{{ model.description }}</div>
          <div class="model-features">
            <el-tag
              v-for="feature in model.features"
              :key="feature"
              size="small"
              effect="plain"
              class="feature-tag"
            >
              {{ feature }}
            </el-tag>
          </div>
          <div class="model-context">
            <el-icon><Document /></el-icon>
            <span>上下文: {{ formatContextLength(model.context_length) }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeModelSwitchDialog">取消</el-button>
          <el-button
            type="primary"
            @click="confirmSwitchModel"
            :loading="switchingModel"
            :disabled="!selectedModelId || selectedModelId === modelInfo?.model"
          >
            <el-icon><Switch /></el-icon>
            切换模型
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Delete, DeleteFilled, Cpu, Search, Switch,
  ChatLineRound, ChatRound, Plus, Document, ArrowRight, ArrowDown,
  Clock, Star, Reading, Edit, DocumentChecked, MoreFilled,
  Food, Basketball, FirstAidKit, Promotion
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import {
  sendMessageStream,
  getChatHistory,
  getModelInfo,
  getAvailableModels,
  switchModel,
  deleteChatHistoryBatch,
  clearAllChatHistory,
  getUserSessions
} from '@/api/aiDoctor'
import { getArticles } from '@/api/article'
import { useUserStore } from '@/stores/user'
import { useAuth } from '@/composables/useAuth'
import { AI_DOCTOR_AVATAR, getUserAvatar } from '@/constants/avatar'
import { getImageUrl } from '@/utils/image'
import EvilEye from '@/components/EvilEye.vue'

const router = useRouter()
const { username } = useAuth()
const userStore = useUserStore()

// 数据
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messageListRef = ref(null)
const currentSessionId = ref('')
const isStreaming = ref(false)
const modelInfo = ref(null)
const availableModels = ref([])
const modelSwitchDialogVisible = ref(false)
const selectedModelId = ref('')
const switchingModel = ref(false)
const enableWebSearch = ref(false)

// 左侧栏数据
const chatSessions = ref([])
const recommendedArticles = ref([])

// 消息管理
const manageDialogVisible = ref(false)
const selectedRounds = ref(new Set())

// 用户头像（响应式）
const userAvatar = computed(() => getUserAvatar(username.value))

// 计算对话轮次列表
const messageRounds = computed(() => {
  const rounds = []
  for (let i = 0; i < messages.value.length; i++) {
    if (messages.value[i].role === 'user') {
      const userMsg = messages.value[i]
      rounds.push({
        userIndex: i,
        userId: userMsg.id,
        preview: userMsg.content.slice(0, 50) + (userMsg.content.length > 50 ? '...' : '')
      })
    }
  }
  return rounds
})

// 快捷问题
const quickQuestions = [
  '我的血糖偏高，应该怎么调整饮食？',
  '糖尿病患者适合什么运动？',
  '如何预防高血压？',
  '每天应该喝多少水？',
  '如何改善睡眠质量？',
  '2024年最新的糖尿病治疗指南是什么？',
  '近期有哪些健康养生的新研究？'
]

// 加载模型信息（优先使用localStorage中的用户偏好）
const loadModelInfo = async () => {
  try {
    // 先从localStorage获取用户偏好
    const savedModelId = localStorage.getItem('preferred_model_id')
    const savedModelName = localStorage.getItem('preferred_model_name')

    if (savedModelId && savedModelName) {
      // 使用localStorage中保存的模型
      modelInfo.value = {
        model: savedModelId,
        display_name: savedModelName,
        provider: 'Moonshot AI',
        supports_web_search: true,
        is_user_preference: true
      }
      console.log('使用本地保存的模型偏好:', savedModelName)
    } else {
      // 如果没有本地偏好，获取默认模型信息
      const data = await getModelInfo()
      modelInfo.value = data
    }
  } catch (error) {
    console.error('加载模型信息失败:', error)
    // 失败时尝试获取默认模型
    try {
      const data = await getModelInfo()
      modelInfo.value = data
    } catch (e) {
      console.error('获取默认模型也失败:', e)
    }
  }
}

// 加载可用模型列表
const loadAvailableModels = async () => {
  try {
    const data = await getAvailableModels()
    availableModels.value = data.models || []
  } catch (error) {
    console.error('加载模型列表失败:', error)
  }
}

// 打开模型切换对话框
const openModelSwitchDialog = () => {
  selectedModelId.value = modelInfo.value?.model || ''
  modelSwitchDialogVisible.value = true
}

// 关闭模型切换对话框
const closeModelSwitchDialog = () => {
  modelSwitchDialogVisible.value = false
  selectedModelId.value = ''
}

// 执行模型切换
const confirmSwitchModel = async () => {
  if (!selectedModelId.value) {
    ElMessage.warning('请选择一个模型')
    return
  }

  switchingModel.value = true
  try {
    const result = await switchModel(selectedModelId.value)
    ElMessage.success(`已切换到 ${result.display_name}`)

    // 保存到localStorage（前端持久化）
    localStorage.setItem('preferred_model_id', selectedModelId.value)
    localStorage.setItem('preferred_model_name', result.display_name)

    // 更新当前模型信息
    await loadModelInfo()

    // 关闭对话框
    closeModelSwitchDialog()

    // 提示用户新对话将使用新模型
    ElMessage.info('新对话将使用切换后的模型')
  } catch (error) {
    console.error('切换模型失败:', error)
    ElMessage.error(error.message || '切换模型失败')
  } finally {
    switchingModel.value = false
  }
}

// 加载历史会话列表
const loadChatSessions = async () => {
  try {
    const sessions = await getUserSessions(20)
    chatSessions.value = sessions || []
  } catch (error) {
    console.error('加载会话列表失败:', error)
    chatSessions.value = []
  }
}

// 加载推荐文章
const loadRecommendedArticles = async () => {
  try {
    const res = await getArticles({ page: 1, pageSize: 5 })
    recommendedArticles.value = res?.list?.slice(0, 4) || []
  } catch (error) {
    console.error('加载推荐文章失败:', error)
  }
}

// 创建新对话
const createNewChat = () => {
  currentSessionId.value = ''
  messages.value = []
  ElMessage.success('已创建新对话')
}

// 切换会话
const switchSession = (sessionId) => {
  currentSessionId.value = sessionId
  loadHistory()
}

// 删除单个会话
const deleteSession = async (sessionId, showConfirm = true) => {
  try {
    if (showConfirm) {
      await ElMessageBox.confirm(
        '确定要删除这个会话吗？此操作不可恢复。',
        '确认删除',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    }

    try {
      // 获取会话中的所有消息
      const { getSessionHistory } = await import('@/api/aiDoctor')
      const sessionMessages = await getSessionHistory(sessionId, 100)
      const messageList = Array.isArray(sessionMessages) ? sessionMessages : (sessionMessages?.list || [])

      // 删除后端数据
      if (messageList.length > 0) {
        const idsToDelete = messageList.map(msg => msg.id).filter(id => id)
        if (idsToDelete.length > 0) {
          await deleteChatHistoryBatch(idsToDelete, sessionId)
        }
      }
    } catch (apiError) {
      console.warn('后端删除失败，仅从前端移除:', apiError)
    }

    // 从前端列表移除
    chatSessions.value = chatSessions.value.filter(s => s.id !== sessionId)

    // 如果删除的是当前会话，创建新对话
    if (currentSessionId.value === sessionId) {
      createNewChat()
    }

    if (showConfirm) {
      ElMessage.success('已删除会话')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除会话失败:', error)
      if (showConfirm) {
        ElMessage.error('删除会话失败')
      }
    }
  }
}

// 清空所有会话
const handleClearAllSessions = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有历史会话吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 调用后端API清空历史
    try {
      await clearAllChatHistory()
    } catch (apiError) {
      console.error('清空后端历史失败:', apiError)
    }

    // 清空前端列表
    chatSessions.value = []
    createNewChat()
    ElMessage.success('已清空所有历史会话')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空历史失败:', error)
    }
  }
}

// 处理历史会话下拉菜单命令（已废弃，保留用于兼容）
const handleSessionCommand = async (command) => {
  if (command === 'clear-all') {
    await handleClearAllSessions()
  } else {
    // 切换到指定会话
    switchSession(command)
  }
}

// 处理历史会话操作
const handleHistoryCommand = async (command, sessionId) => {
  if (command === 'delete') {
    try {
      await ElMessageBox.confirm(
        '确定要删除这个会话吗？此操作不可恢复。',
        '确认删除',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      try {
        const { getSessionHistory, deleteChatHistoryBatch } = await import('@/api/aiDoctor')
        const sessionMessages = await getSessionHistory(sessionId, 100)
        const messageList = Array.isArray(sessionMessages) ? sessionMessages : (sessionMessages?.list || [])
        
        if (messageList.length > 0) {
          const idsToDelete = messageList.map(msg => msg.id).filter(id => id)
          if (idsToDelete.length > 0) {
            await deleteChatHistoryBatch(idsToDelete, sessionId)
          }
        }
      } catch (apiError) {
        console.warn('后端删除失败，仅从前端移除:', apiError)
      }
      
      chatSessions.value = chatSessions.value.filter(s => s.id !== sessionId)
      if (currentSessionId.value === sessionId) {
        createNewChat()
      }
      ElMessage.success('已删除会话')
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除会话失败:', error)
        ElMessage.error('删除会话失败')
      }
    }
  } else if (command === 'rename') {
    ElMessage.info('重命名功能开发中...')
  }
}

// 跳转到文章列表
const goToArticles = () => {
  router.push('/articles')
}

// 讨论文章
const discussArticle = (article) => {
  inputMessage.value = `我想了解一下这篇文章：${article.title}`
  handleSendMessage()
}

// 加载历史消息
const loadHistory = async () => {
  try {
    const userId = userStore.userInfo?.id
    if (!userId) {
      console.warn('用户未登录，无法加载历史消息')
      return
    }
    
    let history
    if (currentSessionId.value) {
      const { getSessionHistory } = await import('@/api/aiDoctor')
      history = await getSessionHistory(currentSessionId.value, 50)
    } else {
      history = await getChatHistory(50)
    }
    
    const historyList = Array.isArray(history) ? history : (history?.list || [])
    
    const sortedHistory = historyList.sort((a, b) => {
      const timeA = new Date(a.create_time || a.time).getTime()
      const timeB = new Date(b.create_time || b.time).getTime()
      return timeA - timeB
    })
    
    messages.value = sortedHistory.map(h => ({
      id: h.id,
      role: h.message_role === 1 ? 'user' : 'assistant',
      content: h.message_content,
      time: h.create_time || h.time,
      sessionId: h.session_id
    }))
    scrollToBottom()
  } catch (error) {
    console.error('加载历史消息失败:', error)
  }
}

// 显示管理对话框
const showManageDialog = () => {
  selectedRounds.value = new Set()
  manageDialogVisible.value = true
}

// 切换选择状态
const toggleSelectRound = (userIndex) => {
  if (selectedRounds.value.has(userIndex)) {
    selectedRounds.value.delete(userIndex)
  } else {
    selectedRounds.value.add(userIndex)
  }
  selectedRounds.value = new Set(selectedRounds.value)
}

// 删除选中的轮次
const deleteSelectedRounds = async () => {
  try {
    const count = selectedRounds.value.size
    await ElMessageBox.confirm(
      `确定要删除选中的 ${count} 轮对话吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const userId = userStore.userInfo?.id
    if (!userId) {
      ElMessage.warning('用户未登录')
      return
    }
    
    const idsToDelete = []
    const indicesToDelete = []
    
    for (const userIndex of selectedRounds.value) {
      const userMsg = messages.value[userIndex]
      const aiMsg = messages.value[userIndex + 1]
      
      if (userMsg?.id) idsToDelete.push(userMsg.id)
      if (aiMsg?.id) idsToDelete.push(aiMsg.id)
      
      indicesToDelete.push(userIndex)
    }
    
    if (idsToDelete.length > 0) {
      try {
        await deleteChatHistoryBatch(idsToDelete, currentSessionId.value)
      } catch (error) {
        console.error('后端删除失败:', error)
      }
    }

    indicesToDelete.sort((a, b) => b - a)
    console.log('删除前列表长度:', messages.value.length, '要删除的索引:', indicesToDelete)
    for (const userIndex of indicesToDelete) {
      messages.value.splice(userIndex, 2)
    }
    console.log('删除后列表长度:', messages.value.length)

    // 检查是否是最后一个对话，如果是则删除会话
    if (messages.value.length === 0 && currentSessionId.value) {
      console.log('消息为空，删除会话:', currentSessionId.value)
      await deleteSession(currentSessionId.value, false)
      ElMessage.success(`已删除 ${count} 轮对话，会话已清空`)
    } else {
      ElMessage.success(`已删除 ${count} 轮对话`)
    }

    selectedRounds.value = new Set()
    manageDialogVisible.value = false
    console.log('对话框已关闭')
  } catch (error) {
    // 取消删除
  }
}

// 删除单轮对话
const deleteRound = async (userIndex) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这轮对话吗？将同时删除用户提问和AI回复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const userId = userStore.userInfo?.id
    if (!userId) {
      ElMessage.warning('用户未登录')
      return
    }

    const userMsg = messages.value[userIndex]
    const aiMsg = messages.value[userIndex + 1]

    const idsToDelete = []
    if (userMsg?.id) idsToDelete.push(userMsg.id)
    if (aiMsg?.id) idsToDelete.push(aiMsg.id)

    if (idsToDelete.length > 0) {
      try {
        await deleteChatHistoryBatch(idsToDelete, currentSessionId.value)
      } catch (error) {
        console.error('后端删除失败:', error)
      }
    }

    messages.value.splice(userIndex, 2)

    // 检查是否是最后一个对话，如果是则删除会话
    if (messages.value.length === 0 && currentSessionId.value) {
      await deleteSession(currentSessionId.value, false)
      ElMessage.success('已删除该轮对话，会话已清空')
    } else {
      ElMessage.success('已删除该轮对话')
    }
  } catch (error) {
    // 取消
  }
}

// 清空所有历史
const clearAllHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有对话记录吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'danger'
      }
    )
    
    const userId = userStore.userInfo?.id
    if (!userId) {
      ElMessage.warning('用户未登录')
      return
    }
    
    try {
      await clearAllChatHistory(userId)
    } catch (error) {
      console.error('后端清空失败:', error)
    }
    
    messages.value = []
    selectedRounds.value = new Set()
    manageDialogVisible.value = false
    ElMessage.success('已清空所有对话')
  } catch (error) {
    // 取消
  }
}

// 处理键盘事件
const handleKeyDown = (e) => {
  if (e.key === 'Enter') {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault()
      const start = e.target.selectionStart
      const end = e.target.selectionEnd
      const value = inputMessage.value
      inputMessage.value = value.substring(0, start) + '\n' + value.substring(end)
      nextTick(() => {
        e.target.selectionStart = e.target.selectionEnd = start + 1
      })
    } else {
      e.preventDefault()
      handleSendMessage()
    }
  }
}

// 发送消息（流式）
const handleSendMessage = async () => {
  const content = inputMessage.value.trim()
  if (!content || loading.value || isStreaming.value) return

  const tempUserMsg = {
    role: 'user',
    content: content,
    time: new Date()
  }
  messages.value.push(tempUserMsg)

  inputMessage.value = ''
  loading.value = true
  isStreaming.value = true
  scrollToBottom()

  const aiMessageIndex = messages.value.length
  const tempAiMsg = {
    role: 'assistant',
    content: '',
    time: new Date()
  }
  messages.value.push(tempAiMsg)

  try {
    const userId = userStore.userInfo?.id
    if (!userId) {
      ElMessage.warning('用户未登录')
      return
    }
    
    const MAX_HISTORY_ROUNDS = 10
    const allHistory = messages.value.slice(0, -1)
    const chatHistory = allHistory.slice(-MAX_HISTORY_ROUNDS * 2).map(msg => ({
      role: msg.role,
      content: msg.content
    }))

    const requestData = {
      user_id: String(userId),
      question: content,
      sessionId: currentSessionId.value || undefined,
      chat_history: chatHistory.length > 0 ? chatHistory : undefined,
      enable_web_search: enableWebSearch.value,
      save_history: true
    }

    await sendMessageStream(
      requestData,
      (chunk) => {
        messages.value[aiMessageIndex].content += chunk
        scrollToBottom()
      },
      (error) => {
        console.error('流式输出错误:', error)
        const errorStr = String(error)
        if (errorStr.includes('token') || errorStr.includes('exceeded') || errorStr.includes('limit')) {
          showTokenLimitWarning()
        } else {
          ElMessage.error('AI回复失败，请重试')
        }
        messages.value.splice(aiMessageIndex, 1)
        loading.value = false
        isStreaming.value = false
      },
      async (responseSessionId) => {
        loading.value = false
        isStreaming.value = false
        scrollToBottom()

        console.log('AI回复完成, responseSessionId:', responseSessionId, 'currentSessionId:', currentSessionId.value)

        const isNewSession = responseSessionId && !currentSessionId.value
        if (isNewSession) {
          currentSessionId.value = responseSessionId
          console.log('新会话创建, sessionId:', responseSessionId)
        }

        try {
          const currentMessages = [...messages.value]
          console.log('重新加载历史前, messages数量:', messages.value.length)

          // 如果是新会话，等待一段时间让后端保存数据
          if (isNewSession) {
            console.log('新会话，等待1秒后加载历史...')
            await new Promise(resolve => setTimeout(resolve, 1000))
          }

          await loadHistory()
          console.log('重新加载历史后, messages数量:', messages.value.length, 'currentSessionId:', currentSessionId.value)

          // 如果加载后消息为空，但之前有消息，则恢复当前消息
          if (messages.value.length === 0 && currentMessages.length > 0) {
            console.log('历史加载为空，恢复当前消息')
            messages.value = currentMessages
          }

          if (isNewSession && responseSessionId) {
            const firstUserMsg = currentMessages.find(m => m.role === 'user')
            const title = firstUserMsg
              ? (firstUserMsg.content.slice(0, 20) + (firstUserMsg.content.length > 20 ? '...' : ''))
              : '新对话'

            const exists = chatSessions.value.some(s => s.id === responseSessionId)
            if (!exists) {
              chatSessions.value.unshift({
                id: responseSessionId,
                title: title,
                lastTime: new Date(),
                messageCount: messages.value.length
              })
              console.log('新会话添加到列表:', responseSessionId)
            }
          } else if (responseSessionId) {
            const sessionIndex = chatSessions.value.findIndex(s => s.id === responseSessionId)
            if (sessionIndex !== -1) {
              chatSessions.value[sessionIndex].lastTime = new Date()
              chatSessions.value[sessionIndex].messageCount = messages.value.length
              const session = chatSessions.value.splice(sessionIndex, 1)[0]
              chatSessions.value.unshift(session)
            }
          }

          setTimeout(async () => {
            await loadChatSessions()
          }, 500)
        } catch (error) {
          console.error('重新加载历史失败:', error)
        }
      }
    )
  } catch (error) {
    console.error('发送失败:', error)
    const errorStr = String(error)
    if (errorStr.includes('token') || errorStr.includes('exceeded') || errorStr.includes('limit')) {
      showTokenLimitWarning()
    } else {
      ElMessage.error('发送失败，请重试')
    }
    messages.value.splice(aiMessageIndex - 1, 2)
    loading.value = false
    isStreaming.value = false
  }
}

// 显示token超限警告弹窗
const showTokenLimitWarning = () => {
  ElMessageBox.alert(
    `<div style="text-align: left;">
      <p><strong>对话内容过长</strong></p>
      <p style="margin-top: 10px;">当前对话历史已超出AI模型的token限制（8192）。</p>
      <p style="margin-top: 10px;">建议：</p>
      <ul style="margin-top: 5px; padding-left: 20px;">
        <li>点击"管理消息"删除部分历史对话</li>
        <li>或点击"清空对话"重新开始</li>
      </ul>
    </div>`,
    'Token限制提示',
    {
      confirmButtonText: '去管理消息',
      cancelButtonText: '我知道了',
      showCancelButton: true,
      dangerouslyUseHTMLString: true,
      type: 'warning',
      callback: (action) => {
        if (action === 'confirm') {
          showManageDialog()
        }
      }
    }
  )
}

// 发送快捷问题
const sendQuickQuestion = (question) => {
  inputMessage.value = question
  handleSendMessage()
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 格式化消息
const formatMessage = (content) => {
  if (!content) return ''
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

// 格式化时间
const formatTime = (time) => {
  return dayjs(time).format('HH:mm')
}

// 监听消息变化，自动滚动
watch(messages, scrollToBottom, { deep: true })

// 格式化上下文长度
const formatContextLength = (length) => {
  if (length >= 1000) {
    return (length / 1000) + 'K'
  }
  return length
}

onMounted(async () => {
  // 先恢复用户信息
  if (!userStore.userInfo && userStore.isLoggedIn) {
    try {
      await userStore.fetchUserInfo()
    } catch (error) {
      console.warn('恢复用户信息失败:', error)
    }
  }

  loadHistory()
  loadModelInfo()
  loadAvailableModels()
  loadChatSessions()
  loadRecommendedArticles()
})
</script>

<style scoped lang="scss">
// ==================== CSS 变量定义 ====================
:root {
  --primary-color: #1890ff;
  --primary-gradient: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  --primary-light: #e6f7ff;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #e2e8f0;
  --border-color: #e2e8f0;
  --border-radius: 16px;
  --border-radius-sm: 12px;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
  --transition-fast: 0.2s ease;
  --transition-normal: 0.3s ease;
}

// ==================== 页面头部 Hero Section ====================
.hero-section {
  position: relative;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  padding: 40px 48px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  overflow: hidden;
  min-height: 180px;

  .hero-content {
    position: relative;
    z-index: 2;
    max-width: 600px;

    .hero-badge {
      display: inline-block;
      padding: 6px 16px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      color: #60a5fa;
      letter-spacing: 2px;
      margin-bottom: 16px;
      backdrop-filter: blur(10px);
    }

    .hero-title {
      font-size: 36px;
      font-weight: 700;
      color: #ffffff;
      margin: 0 0 8px 0;
      letter-spacing: -0.5px;
    }

    .hero-subtitle {
      font-size: 16px;
      color: #94a3b8;
      margin: 0 0 16px 0;
      font-weight: 400;
      letter-spacing: 1px;
    }

    .hero-desc {
      p {
        margin: 0;
        font-size: 14px;
        color: #cbd5e1;
        line-height: 1.6;

        &:first-child {
          margin-bottom: 4px;
        }
      }
    }
  }

  .hero-stats {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 24px;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 20px 32px;

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;

      &.model-selector {
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 8px;
        transition: all 0.3s ease;

        &:hover {
          background: rgba(255, 255, 255, 0.1);

          .switch-icon {
            opacity: 1;
            transform: rotate(180deg);
          }
        }

        .switch-icon {
          margin-left: 4px;
          font-size: 10px;
          opacity: 0.6;
          transition: all 0.3s ease;
        }
      }

      .stat-value {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;

        &.status-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: #ef4444;
          box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);

          &.active {
            background: #10b981;
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
            animation: pulse 2s infinite;
          }
        }
      }

      .stat-label {
        font-size: 12px;
        color: #94a3b8;
        font-weight: 500;
        display: flex;
        align-items: center;
      }
    }

    .stat-divider {
      width: 1px;
      height: 40px;
      background: rgba(255, 255, 255, 0.1);
    }
  }

  // 装饰性背景元素
  .hero-decoration {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    overflow: hidden;

    .deco-ring {
      position: absolute;
      border-radius: 50%;
      border: 1px solid rgba(96, 165, 250, 0.15);

      &.ring-1 {
        width: 300px;
        height: 300px;
        top: -100px;
        right: 200px;
        animation: float 8s ease-in-out infinite;
      }

      &.ring-2 {
        width: 200px;
        height: 200px;
        bottom: -50px;
        right: 100px;
        animation: float 6s ease-in-out infinite reverse;
      }

      &.ring-3 {
        width: 150px;
        height: 150px;
        top: 50%;
        right: 300px;
        transform: translateY(-50%);
        animation: pulse 4s ease-in-out infinite;
      }
    }
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(5deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

// ==================== Evil Eye 区域 ====================
.evil-eye-section {
  position: relative;
  background: #000000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;

  > canvas {
    width: 100% !important;
    height: 450px !important;
    display: block;
  }

  .evil-eye-label {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    margin-top: 20px;

    .label-text {
      font-size: 14px;
      font-weight: 700;
      color: #3b82f6;
      letter-spacing: 6px;
      text-shadow: 0 0 15px rgba(59, 130, 246, 0.6);
    }

    .label-sub {
      font-size: 12px;
      color: #64748b;
      letter-spacing: 3px;
    }
  }
}

// ==================== 终端式聊天区域 ====================
.chat-terminal-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #0a0a0a;
  overflow: hidden;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

// 终端工具栏
.terminal-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: #0d0d0d;
  border-bottom: 1px solid #222;

  .toolbar-left,
  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .toolbar-btn {
    color: #888;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;

    &:hover {
      color: #00d4aa;
    }

    .el-icon {
      margin-right: 4px;
    }
  }

  .web-search-switch {
    :deep(.el-switch__core) {
      background: #333;
      border-color: #444;
    }

    :deep(.el-switch.is-checked .el-switch__core) {
      background: #00d4aa;
      border-color: #00d4aa;
    }

    :deep(.el-switch__inner) {
      font-size: 12px;
    }
  }
}

// 历史记录下拉菜单样式
// 会话列表面板
.session-list {
  max-height: 400px;
  overflow-y: auto;

  .session-list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid #333;
    font-size: 14px;
    color: #888;
  }

  .session-list-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid #222;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background: #1a1a2e;
    }

    &.active {
      background: rgba(0, 212, 170, 0.1);

      .session-title {
        color: #00d4aa;
      }
    }

    .session-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;
      overflow: hidden;

      .session-title {
        font-size: 13px;
        color: #e0e0e0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .session-time {
        font-size: 11px;
        color: #666;
      }
    }

    .session-delete-btn {
      padding: 4px 8px;
      opacity: 0;
      transition: opacity 0.2s;

      &:hover {
        color: #f56c6c;
      }
    }

    &:hover .session-delete-btn {
      opacity: 1;
    }
  }
}

// 兼容旧样式
.session-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 200px;

  .session-title {
    font-size: 13px;
    color: #e0e0e0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .session-time {
    font-size: 11px;
    color: #666;
  }
}

.active-session {
  background: rgba(0, 212, 170, 0.1) !important;
  color: #00d4aa !important;
}

.terminal-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  background: #0a0a0a;
}

// 欢迎页面 - 终端风格
.welcome-terminal {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;

  .terminal-header {
    margin-bottom: 24px;

    .terminal-prompt {
      color: #00d4aa;
      font-weight: bold;
      margin-right: 12px;
    }

    .terminal-text {
      color: #e0e0e0;
      font-size: 18px;
      font-weight: 600;
    }
  }

  .terminal-info {
    margin-bottom: 32px;

    p {
      color: #888;
      font-size: 14px;
      margin: 8px 0;
      line-height: 1.6;

      .terminal-prompt {
        color: #00d4aa;
        margin-right: 8px;
      }
    }
  }

  .quick-commands {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .command-item {
      display: flex;
      align-items: center;
      padding: 12px 16px;
      background: #1a1a2e;
      border: 1px solid #333;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        border-color: #00d4aa;
        background: #1f1f3a;
      }

      .terminal-prompt {
        color: #00d4aa;
        font-weight: bold;
        margin-right: 12px;
      }

      .command-text {
        color: #e0e0e0;
        font-size: 14px;
      }
    }
  }
}

// 消息列表 - 终端风格
.terminal-message-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.terminal-msg {
  padding: 16px;
  border-radius: 4px;
  border-left: 3px solid;

  &.user {
    background: #1a1a2e;
    border-left-color: #00d4aa;

    .msg-role {
      color: #00d4aa;
    }
  }

  &.ai {
    background: #0d0d0d;
    border-left-color: #3b82f6;

    .msg-role {
      color: #3b82f6;
    }
  }

  .msg-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;

    .msg-role {
      font-size: 12px;
      font-weight: 600;
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }

    .msg-time {
      font-size: 11px;
      color: #666;
    }
  }

  .msg-content {
    color: #e0e0e0;
    font-size: 14px;
    line-height: 1.7;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;

    :deep(br) {
      display: block;
      margin: 4px 0;
    }
  }
}

// 终端输入区域
.terminal-input-wrapper {
  display: flex;
  align-items: flex-end;
  padding: 16px 24px 24px;
  background: #0d0d0d;
  border-top: 1px solid #222;
  gap: 12px;

  .input-prompt {
    color: #00d4aa;
    font-weight: bold;
    font-size: 16px;
    padding-bottom: 10px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  }

  .terminal-input {
    flex: 1;

    :deep(.el-textarea__inner) {
      background: #1a1a2e;
      border: 1px solid #333;
      border-radius: 4px;
      color: #e0e0e0;
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
      font-size: 14px;
      padding: 10px 14px;

      &::placeholder {
        color: #666;
      }

      &:focus {
        border-color: #00d4aa;
        box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.1);
      }
    }
  }

  .terminal-send-btn {
    width: 44px;
    height: 44px;
    border-radius: 4px;
    background: #00d4aa;
    border: none;
    color: #0a0a0a;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;

    &:hover:not(:disabled) {
      background: #00b894;
      transform: translateY(-1px);
    }

    &:disabled {
      background: #333;
      color: #666;
      cursor: not-allowed;
    }

    .el-icon {
      font-size: 18px;
    }
  }
}

// ==================== 主内容区域（已废弃）====================
.main-content {
  display: none;
}

// ==================== 左侧边栏 ====================
.ai-sidebar {
  width: 300px;
  background: #111111;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }
}

// 新建对话按钮区域
.new-chat-section {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);

  .new-chat-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 14px 20px;
    background: #2563eb;
    border: none;
    border-radius: 12px;
    color: white;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: #1d4ed8;
    }

    &:active {
      background: #1e40af;
    }

    .btn-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      background: rgba(255, 255, 255, 0.15);
      border-radius: 6px;
    }
  }
}

// 侧边栏区块
.sidebar-section {
  padding: 20px;

  &.history-section {
    flex: 1;
    overflow-y: auto;
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 600;
      color: #9ca3af;

      .el-icon {
        font-size: 16px;
        color: #3b82f6;
      }
    }
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #9ca3af;
    margin-bottom: 16px;

    .el-icon {
      font-size: 16px;
      color: #3b82f6;
    }

    .more-btn {
      margin-left: auto;
      font-size: 12px;
      font-weight: 500;
    }
  }
}

// 历史会话列表
.history-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid transparent;

  &:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.1);

    .history-menu {
      opacity: 1;
    }
  }

  &.active {
    background: rgba(37, 99, 235, 0.15);
    border-color: rgba(37, 99, 235, 0.3);

    .history-icon {
      background: #2563eb;
      color: white;
    }

    .history-name {
      color: #60a5fa;
      font-weight: 600;
    }
  }

  .history-icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    color: #9ca3af;
    font-size: 16px;
    transition: all var(--transition-fast);
  }

  .history-content {
    flex: 1;
    min-width: 0;

    .history-name {
      font-size: 13px;
      color: #e5e7eb;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-weight: 500;
    }

    .history-meta {
      font-size: 11px;
      color: #6b7280;
      margin-top: 2px;
    }
  }

  .history-menu {
    opacity: 0;
    transition: opacity var(--transition-fast);

    .menu-icon {
      padding: 4px;
      border-radius: 4px;
      color: var(--text-secondary);
      font-size: 14px;
      cursor: pointer;

      &:hover {
        background: var(--bg-tertiary);
        color: var(--text-primary);
      }
    }
  }
}

.empty-history {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 0;
  color: #6b7280;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;

  p {
    margin-top: 12px;
    font-size: 13px;
  }
}

// 快捷功能
.quick-features {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.feature-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;

  &:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.1);
  }

  &:active {
    background: rgba(255, 255, 255, 0.08);
  }

  .feature-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    font-size: 20px;

    &.blue {
      background: #2563eb;
      color: white;
    }

    &.green {
      background: #059669;
      color: white;
    }

    &.orange {
      background: #d97706;
      color: white;
    }

    &.purple {
      background: #7c3aed;
      color: white;
    }
  }

  span {
    font-size: 12px;
    color: #9ca3af;
    font-weight: 600;
  }
}

// 健康资讯
.articles-section {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.articles-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.article-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;

  &:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .article-image {
    width: 56px;
    height: 56px;
    border-radius: 8px;
    overflow: hidden;
    flex-shrink: 0;

    .el-image {
      width: 100%;
      height: 100%;
    }

    .image-fallback {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.06);
      color: #6b7280;
    }
  }

  .article-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;

    .article-title {
      font-size: 13px;
      color: #e5e7eb;
      line-height: 1.5;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      font-weight: 500;
    }

    .article-tag {
      display: inline-block;
      margin-top: 6px;
      padding: 3px 10px;
      font-size: 10px;
      border-radius: 20px;
      width: fit-content;
      font-weight: 600;
      letter-spacing: 0.3px;

      &.success {
        background: #059669;
        color: white;
      }

      &.warning {
        background: #d97706;
        color: white;
      }

      &.info {
        background: #2563eb;
        color: white;
      }
    }
  }
}

// ==================== 主聊天区域 ====================
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #0a0a0a 0%, #111111 50%, #0a0a0a 100%);
  overflow-y: auto;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      radial-gradient(ellipse at 20% 0%, rgba(37, 99, 235, 0.08) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 100%, rgba(37, 99, 235, 0.05) 0%, transparent 50%);
    pointer-events: none;
  }
}

// 聊天头部
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(17, 17, 17, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px);
  position: relative;
  z-index: 1;

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;

    .ai-avatar {
      position: relative;

      .online-badge {
        position: absolute;
        bottom: 0;
        right: 0;
        width: 10px;
        height: 10px;
        background: #10b981;
        border: 2px solid #111111;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
      }
    }

    .header-info {
      h2 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #e5e7eb;
        letter-spacing: 1px;
      }

      .header-tags {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 4px;

        .tag {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 3px 10px;
          font-size: 11px;
          border-radius: 20px;
          font-weight: 500;

          &.model {
            background: rgba(37, 99, 235, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(37, 99, 235, 0.3);
          }

          &.web-search {
            background: rgba(37, 99, 235, 0.1);
            color: #3b82f6;
            border: 1px solid rgba(59, 130, 246, 0.2);
          }

          .el-icon {
            font-size: 11px;
          }
        }
      }
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}

// 消息容器 - 移除内部滚动，由外部控制
.message-container {
  flex: 1;
  overflow: visible;
  padding: 24px;
  position: relative;
  z-index: 1;
}

// 欢迎页面
.welcome-section {
  max-width: 700px;
  margin: 0 auto;
  padding: 32px 0;

  .welcome-header {
    text-align: center;
    margin-bottom: 40px;

    .welcome-avatar {
      position: relative;
      display: inline-block;
      margin-bottom: 20px;

      .avatar-glow {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 120px;
        height: 120px;
        background: radial-gradient(circle, rgba(37, 99, 235, 0.4) 0%, transparent 70%);
        border-radius: 50%;
        filter: blur(15px);
        animation: pulse-glow 3s ease-in-out infinite;
      }
    }

    h1 {
      margin: 0 0 10px;
      font-size: 28px;
      font-weight: 600;
      color: #e5e7eb;
      letter-spacing: 4px;
      text-shadow: 0 0 30px rgba(37, 99, 235, 0.5);
    }

    .welcome-subtitle {
      margin: 0;
      font-size: 14px;
      color: #6b7280;
    }
  }
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.4; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.7; transform: translate(-50%, -50%) scale(1.1); }
}

// 快捷问题区域
.quick-questions-section {
  text-align: center;

  h3 {
    margin: 0 0 16px;
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
  }

  .question-tags {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }

  .question-tag {
    cursor: pointer;
    padding: 10px 18px;
    font-size: 13px;
    border-radius: 20px;
    transition: all var(--transition-fast);
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #9ca3af;

    &:hover {
      color: #60a5fa;
      border-color: rgba(37, 99, 235, 0.4);
      background: rgba(37, 99, 235, 0.1);
      box-shadow: 0 0 20px rgba(37, 99, 235, 0.15);
    }
  }
}

.web-search-notice {
  margin-top: 24px;
}

// 消息列表
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.message-wrapper {
  display: flex;
  gap: 12px;

  &.user {
    flex-direction: row-reverse;

    .message-content {
      align-items: flex-end;

      .message-bubble {
        background: #1a1a2e;
        color: #00d4aa;
        border-radius: 4px;
        border: 1px solid #00d4aa;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
      }
    }
  }

  &.ai {
    .message-content {
      align-items: flex-start;

      .message-bubble {
        background: #0d0d0d;
        color: #e0e0e0;
        border-radius: 4px;
        border: 1px solid #333;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
      }
    }
  }

  .message-avatar {
    flex-shrink: 0;
  }

  .message-content {
    display: flex;
    flex-direction: column;
    max-width: 75%;

    .message-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
      padding: 0 4px;

      .message-author {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-primary);
      }

      .message-time {
        font-size: 11px;
        color: var(--text-tertiary);
      }
    }

    .message-bubble {
      padding: 12px 16px;
      font-size: 14px;
      line-height: 1.6;
      word-break: break-word;
    }

    .message-actions {
      margin-top: 6px;
      opacity: 0;
      transition: opacity var(--transition-fast);
    }

    &:hover .message-actions {
      opacity: 1;
    }
  }
}

// 正在输入指示器
.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 16px;
  background: #ffffff;
  border-radius: 16px 16px 16px 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);

  span {
    width: 8px;
    height: 8px;
    background: #d1d5db;
    border-radius: 50%;
    animation: typing 1.4s infinite;

    &:nth-child(2) {
      animation-delay: 0.2s;
    }

    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

.web-search-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 5px 12px;
  background: #dbeafe;
  color: #2563eb;
  font-size: 11px;
  border-radius: 20px;

  .el-icon {
    font-size: 12px;
  }
}

// ==================== 输入区域（终端代码样式）====================
.input-wrapper {
  position: relative;
  display: flex;
  align-items: flex-end;
  background: #0d0d0d;
  border-radius: 8px;
  border: 1px solid #333;
  padding: 12px 16px;
  transition: all 0.3s ease;
  max-width: 800px;
  margin: 16px 24px 24px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;

  &::before {
    content: '>';
    color: #00d4aa;
    font-weight: bold;
    margin-right: 12px;
    font-size: 16px;
    flex-shrink: 0;
  }

  &:hover {
    border-color: #555;
    box-shadow: 0 0 0 1px rgba(0, 212, 170, 0.1);
  }

  &:focus-within {
    border-color: #00d4aa;
    box-shadow: 
      0 0 0 2px rgba(0, 212, 170, 0.15),
      inset 0 1px 0 rgba(0, 212, 170, 0.05);
  }
}

.chat-input {
  flex: 1;

  :deep(.el-textarea__inner) {
    border: none;
    background: transparent;
    padding: 0;
    font-size: 14px;
    line-height: 1.6;
    resize: none;
    box-shadow: none;
    color: #e0e0e0;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;

    &::placeholder {
      color: #666;
    }
  }
}

// 发送按钮（保持原有样式）
.send-btn-custom {
  font-family: inherit;
  font-size: 14px;
  background: var(--primary-color);
  color: white;
  padding: 0.7em 1.2em;
  padding-left: 0.9em;
  display: flex;
  align-items: center;
  border: none;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
  cursor: pointer;
  margin-left: 14px;
  flex-shrink: 0;
  height: 44px;

  &:disabled {
    background: #d1d5db;
    cursor: not-allowed;
  }

  span {
    display: block;
    margin-left: 0.3em;
    transition: all 0.3s ease-in-out;
  }

  svg {
    display: block;
    transform-origin: center center;
    transition: transform 0.3s ease-in-out;
  }

  &:not(:disabled):hover .svg-wrapper {
    animation: fly-1 0.6s ease-in-out infinite alternate;
  }

  &:not(:disabled):hover svg {
    transform: translateX(1.2em) rotate(45deg) scale(1.1);
  }

  &:not(:disabled):hover span {
    transform: translateX(5em);
  }

  &:not(:disabled):active {
    transform: scale(0.95);
  }
}

@keyframes fly-1 {
  from {
    transform: translateY(0.1em);
  }
  to {
    transform: translateY(-0.1em);
  }
}

// ==================== 消息管理对话框 ====================
.manage-dialog {
  :deep(.el-dialog__header) {
    padding: 20px 24px;
    border-bottom: 1px solid #e5e7eb;

    .el-dialog__title {
      font-weight: 600;
    }
  }

  :deep(.el-dialog__body) {
    padding: 20px 24px;
  }

  :deep(.el-dialog__footer) {
    padding: 16px 24px;
    border-top: 1px solid #e5e7eb;
  }
}

.manage-content {
  max-height: 400px;
  overflow-y: auto;
}

.manage-hint {
  margin-bottom: 16px;
}

.rounds-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.round-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: var(--bg-secondary);
  border: 2px solid transparent;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover {
    background: #e5e7eb;
  }

  &.selected {
    border-color: var(--primary-color);
    background: var(--primary-light);
  }

  .round-info {
    flex: 1;

    .round-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;

      .round-number {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary);
      }

      .round-badge {
        font-size: 11px;
        padding: 2px 8px;
        background: #e5e7eb;
        color: var(--text-secondary);
        border-radius: 10px;
      }
    }

    .round-preview {
      font-size: 14px;
      color: var(--text-secondary);
      line-height: 1.5;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
  }
}

.empty-rounds {
  padding: 40px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// ==================== 响应式适配 ====================
@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    padding: 24px;
    gap: 24px;

    .hero-content {
      text-align: center;

      .hero-title {
        font-size: 28px;
      }
    }

    .hero-stats {
      padding: 16px 24px;
    }

    .hero-decoration {
      display: none;
    }
  }

  .main-content {
    height: calc(100vh - 220px);
  }

  .ai-sidebar {
    display: none;
  }

  .message-wrapper {
    .message-content {
      max-width: 85%;
    }
  }
}

// ==================== 模型切换对话框样式 ====================
.model-switch-dialog {
  .model-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-height: 500px;
    overflow-y: auto;
    padding-right: 8px;

    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-track {
      background: #f1f5f9;
      border-radius: 3px;
    }

    &::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 3px;

      &:hover {
        background: #94a3b8;
      }
    }
  }

  .model-card {
    padding: 16px;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #ffffff;

    &:hover {
      border-color: #3b82f6;
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
      transform: translateY(-2px);
    }

    &.is-selected {
      border-color: #3b82f6;
      background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }

    &.is-current {
      border-color: #10b981;
      background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    }

    &.is-recommended {
      position: relative;

      &::before {
        content: '';
        position: absolute;
        top: -2px;
        right: -2px;
        width: 0;
        height: 0;
        border-style: solid;
        border-width: 0 24px 24px 0;
        border-color: transparent #10b981 transparent transparent;
        border-radius: 0 12px 0 0;
      }
    }

    .model-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .model-name {
        font-size: 16px;
        font-weight: 600;
        color: #1e293b;
      }

      .model-badges {
        display: flex;
        gap: 6px;
      }
    }

    .model-description {
      font-size: 13px;
      color: #64748b;
      margin-bottom: 12px;
      line-height: 1.5;
    }

    .model-features {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 10px;

      .feature-tag {
        font-size: 11px;
      }
    }

    .model-context {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: #94a3b8;

      .el-icon {
        font-size: 14px;
      }
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}
</style>