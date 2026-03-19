<template>
  <!-- 文章编辑页面 -->
  <div class="admin-article-edit">
    <!-- 页面头部 -->
    <el-card class="page-header" shadow="never">
      <div class="header-content">
        <div class="title-section">
          <h2 class="page-title">{{ isEdit ? '编辑文章' : '新增文章' }}</h2>
          <p class="page-desc">{{ isEdit ? '修改文章内容和设置' : '创建新的文章' }}</p>
        </div>
        <div class="header-actions">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" :icon="Check" :loading="saving" @click="handleSave">
            保存
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 编辑表单 -->
    <el-form
      ref="formRef"
      :model="articleForm"
      :rules="formRules"
      label-width="100px"
      class="article-form"
    >
      <el-row :gutter="20">
        <!-- 左侧主要内容区 -->
        <el-col :span="16">
          <el-card shadow="never">
            <template #header>
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>基本信息</span>
              </div>
            </template>

            <!-- 文章标题 -->
            <el-form-item label="文章标题" prop="title">
              <el-input
                v-model="articleForm.title"
                placeholder="请输入文章标题"
                maxlength="100"
                show-word-limit
                clearable
              />
            </el-form-item>

            <!-- 文章摘要 -->
            <el-form-item label="文章摘要" prop="summary">
              <el-input
                v-model="articleForm.summary"
                type="textarea"
                :rows="3"
                placeholder="请输入文章摘要，简要描述文章内容"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>

            <!-- 文章内容 -->
            <el-form-item label="文章内容" prop="content">
              <!-- 富文本编辑器区域 -->
              <div class="editor-wrapper">
                <div ref="editorRef" class="rich-editor"></div>
              </div>
            </el-form-item>
          </el-card>
        </el-col>

        <!-- 右侧设置区 -->
        <el-col :span="8">
          <!-- 发布设置 -->
          <el-card shadow="never" class="settings-card">
            <template #header>
              <div class="card-header">
                <el-icon><Setting /></el-icon>
                <span>发布设置</span>
              </div>
            </template>

            <!-- 文章分类 -->
            <el-form-item label="分类" prop="category">
              <el-select
                v-model="articleForm.category"
                placeholder="请选择分类"
                style="width: 100%"
              >
                <el-option
                  v-for="item in categoryOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>

            <!-- 文章标签 -->
            <el-form-item label="标签" prop="tags">
              <el-select
                v-model="articleForm.tags"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="请选择或输入标签"
                style="width: 100%"
              >
                <el-option
                  v-for="item in tagOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>

            <!-- 发布状态 -->
            <el-form-item label="发布状态" prop="status">
              <el-radio-group v-model="articleForm.status">
                <el-radio :value="1">立即发布</el-radio>
                <el-radio :value="0">保存草稿</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 置顶开关 -->
            <el-form-item label="置顶">
              <el-switch
                v-model="articleForm.isTop"
                active-text="是"
                inactive-text="否"
                inline-prompt
              />
            </el-form-item>
          </el-card>

          <!-- 封面设置 -->
          <el-card shadow="never" class="settings-card">
            <template #header>
              <div class="card-header">
                <el-icon><Picture /></el-icon>
                <span>封面设置</span>
              </div>
            </template>

            <!-- 封面图片上传 -->
            <el-form-item label="封面图片" prop="imageUrl">
              <el-upload
                class="cover-uploader"
                action="/api/admin/upload?type=cover"
                :headers="{ Authorization: `Bearer ${getToken()}` }"
                :show-file-list="false"
                :on-success="handleCoverSuccess"
                :on-error="handleCoverError"
                :before-upload="beforeCoverUpload"
                accept="image/*"
              >
                <div v-if="articleForm.imageUrl" class="cover-preview">
                  <el-image :src="getImageUrl(articleForm.imageUrl)" fit="cover" />
                  <div class="cover-actions">
                    <el-icon class="action-icon" @click.stop="handleRemoveCover">
                      <Delete />
                    </el-icon>
                  </div>
                </div>
                <div v-else class="upload-placeholder">
                  <el-icon class="upload-icon"><Plus /></el-icon>
                  <div class="upload-text">点击上传封面</div>
                  <div class="upload-hint">建议尺寸 800x450</div>
                </div>
              </el-upload>
            </el-form-item>

            <!-- 封面图片URL输入 -->
            <el-form-item label="图片链接">
              <el-input
                v-model="articleForm.imageUrl"
                placeholder="或输入图片URL"
                clearable
              />
            </el-form-item>
          </el-card>

          <!-- SEO设置 -->
          <el-card shadow="never" class="settings-card">
            <template #header>
              <div class="card-header">
                <el-icon><Promotion /></el-icon>
                <span>SEO设置</span>
              </div>
            </template>

            <!-- SEO标题 -->
            <el-form-item label="SEO标题">
              <el-input
                v-model="articleForm.seoTitle"
                placeholder="请输入SEO标题"
                maxlength="60"
                show-word-limit
              />
            </el-form-item>

            <!-- SEO关键词 -->
            <el-form-item label="SEO关键词">
              <el-input
                v-model="articleForm.seoKeywords"
                placeholder="请输入SEO关键词，用逗号分隔"
              />
            </el-form-item>

            <!-- SEO描述 -->
            <el-form-item label="SEO描述">
              <el-input
                v-model="articleForm.seoDescription"
                type="textarea"
                :rows="3"
                placeholder="请输入SEO描述"
                maxlength="160"
                show-word-limit
              />
            </el-form-item>
          </el-card>
        </el-col>
      </el-row>
    </el-form>
  </div>
</template>

<script setup>
/**
 * AdminArticleEdit.vue - 文章编辑页面
 * 提供文章新增和编辑功能，包含富文本编辑器、图片上传等
 */
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Check,
  Document,
  Setting,
  Picture,
  Promotion,
  Plus,
  Delete
} from '@element-plus/icons-vue'
import { getToken } from '@/utils/auth'
import { getImageUrl } from '@/utils/image'
import request from '@/utils/request'
import Vditor from 'vditor'
import 'vditor/dist/index.css'

// 路由实例
const route = useRoute()
const router = useRouter()

// 表单引用
const formRef = ref(null)

// 编辑器引用
const editorRef = ref(null)

// Vditor 实例
let vditor = null

// 保存状态
const saving = ref(false)

// 判断是否为编辑模式
const isEdit = computed(() => !!route.params.id)

// 文章ID
const articleId = computed(() => route.params.id)

// 分类选项
const categoryOptions = [
  { label: '健康资讯', value: 'health' },
  { label: '疾病科普', value: 'disease' },
  { label: '饮食建议', value: 'diet' },
  { label: '运动指导', value: 'exercise' },
  { label: '心理健康', value: 'mental' },
  { label: '用药指南', value: 'medication' }
]

// 标签选项
const tagOptions = [
  '高血压', '糖尿病', '心脏病', '健康饮食', '运动健身',
  '心理健康', '中医养生', '西药知识', '体检指南', '慢病管理'
]

// 文章表单数据
const articleForm = reactive({
  title: '',
  summary: '',
  content: '',
  category: '',
  tags: [],
  status: 0,
  isTop: false,
  imageUrl: '',  // 后端数据库字段为 imageUrl，与 cover 保持一致
  seoTitle: '',
  seoKeywords: '',
  seoDescription: ''
})

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  summary: [
    { required: true, message: '请输入文章摘要', trigger: 'blur' },
    { max: 200, message: '摘要长度不能超过 200 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入文章内容', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择文章分类', trigger: 'change' }
  ]
}

/**
 * 获取文章详情
 */
const fetchArticleDetail = async () => {
  if (!isEdit.value) return

  console.log('[DEBUG] 开始获取文章详情, articleId:', articleId.value)

  try {
    const requestUrl = `/admin/articles/${articleId.value}`
    console.log('[DEBUG] 请求URL:', requestUrl)

    // 调用真实API获取文章详情
    const data = await request.get(requestUrl)

    console.log('[DEBUG] 获取文章详情响应:', data)

    // 填充表单数据
    Object.assign(articleForm, data)

    console.log('[DEBUG] 表单数据已填充:', articleForm)

    ElMessage.success('获取文章详情成功')
  } catch (error) {
    console.error('[DEBUG] 获取文章详情失败:', error)
    console.error('[DEBUG] 错误详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      config: error.config
    })
    ElMessage.error('获取文章详情失败: ' + (error.response?.data?.message || error.message))
  }
}

/**
 * 处理封面上传成功
 * @param {Object} response - 上传响应
 */
const handleCoverSuccess = (response) => {
  console.log('[DEBUG ArticleEdit] 封面上传原始响应:', response)

  // el-upload 直接接收后端返回的 JSON，需要解析
  let result = response
  if (typeof response === 'string') {
    try {
      result = JSON.parse(response)
    } catch (e) {
      console.error('[DEBUG ArticleEdit] 解析响应失败:', e)
      ElMessage.error('上传响应格式错误')
      return
    }
  }

  console.log('[DEBUG ArticleEdit] 解析后的响应:', result)

  if (result.code === 200) {
    articleForm.imageUrl = result.data.url
    console.log('[DEBUG ArticleEdit] 封面URL已设置:', articleForm.imageUrl)
    ElMessage.success('封面上传成功')
  } else {
    console.error('[DEBUG ArticleEdit] 上传失败:', result.message)
    ElMessage.error(result.message || '上传失败')
  }
}

/**
 * 处理封面上传失败
 * @param {Error} error - 错误对象
 */
const handleCoverError = () => {
  ElMessage.error('封面上传失败，请重试')
}

/**
 * 封面上传前的验证
 * @param {File} file - 文件对象
 */
const beforeCoverUpload = (file) => {
  // 验证文件类型
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }

  // 验证文件大小（最大 5MB）
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB！')
    return false
  }

  return true
}

/**
 * 处理移除封面
 */
const handleRemoveCover = () => {
  articleForm.imageUrl = ''
  ElMessage.success('封面已移除')
}

/**
 * 处理取消
 */
const handleCancel = () => {
  ElMessageBox.confirm(
    '确定要取消编辑吗？未保存的内容将会丢失。',
    '确认取消',
    {
      confirmButtonText: '确定',
      cancelButtonText: '继续编辑',
      type: 'warning'
    }
  )
    .then(() => {
      router.back()
    })
    .catch(() => {})
}

/**
 * 处理保存
 */
const handleSave = async () => {
  console.log('[DEBUG] 开始保存文章, isEdit:', isEdit.value)

  // 表单验证
  const valid = await formRef.value.validate().catch(() => false)
  console.log('[DEBUG] 表单验证结果:', valid)
  if (!valid) {
    ElMessage.warning('请检查表单填写是否正确')
    return
  }

  // 验证内容
  if (!articleForm.content.trim()) {
    ElMessage.warning('请输入文章内容')
    return
  }

  saving.value = true
  try {
    // 准备提交数据
    const submitData = {
      ...articleForm,
      // 如果SEO标题为空，使用文章标题
      seoTitle: articleForm.seoTitle || articleForm.title,
      // 如果SEO描述为空，使用文章摘要
      seoDescription: articleForm.seoDescription || articleForm.summary
    }

    console.log('[DEBUG] 准备提交的数据:', submitData)

    // 调用真实API
    let res
    if (isEdit.value) {
      const updateUrl = `/admin/articles/${articleId.value}`
      console.log('[DEBUG] 更新文章URL:', updateUrl)
      res = await request.put(updateUrl, submitData)
    } else {
      const createUrl = '/admin/articles'
      console.log('[DEBUG] 创建文章URL:', createUrl)
      res = await request.post(createUrl, submitData)
    }

    console.log('[DEBUG] 保存文章响应:', res)

    ElMessage.success(isEdit.value ? '文章更新成功' : '文章创建成功')

    // 返回列表页
    router.push('/admin/articles')
  } catch (error) {
    console.error('[DEBUG] 保存文章失败:', error)
    console.error('[DEBUG] 错误详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      config: error.config
    })
    ElMessage.error((isEdit.value ? '文章更新失败: ' : '文章创建失败: ') + (error.response?.data?.message || error.message))
  } finally {
    saving.value = false
  }
}

/**
 * 初始化 Vditor 编辑器
 */
const initEditor = () => {
  if (!editorRef.value) return

  vditor = new Vditor(editorRef.value, {
    height: 500,
    mode: 'wysiwyg', // 所见即所得模式
    theme: 'classic',
    lang: 'zh_CN',
    placeholder: '请输入文章内容...',
    toolbarConfig: {
      pin: true
    },
    cache: {
      enable: false
    },
    after: () => {
      // 编辑器初始化完成后设置内容
      vditor.setValue(articleForm.content || '')
    },
    input: (value) => {
      // 内容变化时同步到表单
      articleForm.content = value
    },
    upload: {
      url: '/api/admin/upload',
      headers: {
        Authorization: `Bearer ${getToken()}`
      },
      fieldName: 'file',
      multiple: false,
      accept: 'image/*',
      format: (files, responseText) => {
        const res = JSON.parse(responseText)
        if (res.code === 200) {
          // 返回 Vditor 需要的格式
          return JSON.stringify({
            msg: '',
            code: 0,
            data: {
              errFiles: [],
              succMap: {
                [files[0].name]: getImageUrl(res.data.url)
              }
            }
          })
        }
        return JSON.stringify({
          msg: res.message || '上传失败',
          code: 1,
          data: {}
        })
      }
    }
  })
}

/**
 * 销毁编辑器
 */
const destroyEditor = () => {
  if (vditor) {
    vditor.destroy()
    vditor = null
  }
}

// 组件挂载时初始化
onMounted(async () => {
  // 先初始化编辑器
  nextTick(() => {
    initEditor()
  })
  // 等待数据加载完成后再设置编辑器内容
  await fetchArticleDetail()
  // 数据加载完成后，如果编辑器已初始化，则设置内容
  if (vditor && articleForm.content) {
    vditor.setValue(articleForm.content)
  }
})

// 组件卸载时销毁编辑器
onUnmounted(() => {
  destroyEditor()
})
</script>

<style scoped>
/* 页面容器 */
.admin-article-edit {
  padding: 0;
}

/* 页面头部 */
.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.page-desc {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 文章表单 */
.article-form {
  margin-top: 20px;
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

/* 设置卡片间距 */
.settings-card {
  margin-bottom: 20px;
}

.settings-card:last-child {
  margin-bottom: 0;
}

/* 编辑器包装器 */
.editor-wrapper {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-height: 400px;
  margin-bottom: 10px;
}

.rich-editor {
  min-height: 400px;
  padding: 12px;
}

/* 内容文本域 */
.content-textarea :deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

/* 封面上传器 */
.cover-uploader {
  width: 100%;
}

.cover-uploader :deep(.el-upload) {
  width: 100%;
}

/* 封面预览 */
.cover-preview {
  position: relative;
  width: 100%;
  height: 180px;
  border-radius: 6px;
  overflow: hidden;
}

.cover-preview .el-image {
  width: 100%;
  height: 100%;
}

.cover-actions {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.cover-preview:hover .cover-actions {
  opacity: 1;
}

.action-icon {
  font-size: 24px;
  color: #fff;
  cursor: pointer;
  padding: 10px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  transition: background-color 0.3s;
}

.action-icon:hover {
  background-color: rgba(255, 255, 255, 0.4);
}

/* 上传占位符 */
.upload-placeholder {
  width: 100%;
  height: 180px;
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-placeholder:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 40px;
  color: #909399;
  margin-bottom: 10px;
}

.upload-text {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

/* 响应式适配 */
@media screen and (max-width: 1200px) {
  .article-form .el-row {
    flex-direction: column;
  }

  .article-form .el-col {
    width: 100%;
    max-width: 100%;
    flex: 0 0 100%;
  }

  .settings-card {
    margin-top: 20px;
  }
}

@media screen and (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
