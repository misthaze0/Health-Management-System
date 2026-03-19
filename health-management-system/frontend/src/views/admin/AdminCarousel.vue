<template>
  <!-- 轮播图管理页面（支持图片裁剪） -->
  <div class="admin-carousel">
    <!-- 页面标题卡片 -->
    <el-card class="page-header" shadow="never">
      <div class="header-content">
        <div class="title-section">
          <h2 class="page-title">轮播图管理</h2>
          <p class="page-desc">
            管理首页轮播图，最多支持5张轮播图
            <el-tag v-if="carouselList.length >= 5" type="danger" size="small" class="limit-tag">
              已达上限
            </el-tag>
            <el-tag v-else type="info" size="small" class="limit-tag">
              当前 {{ carouselList.length }}/5
            </el-tag>
          </p>
        </div>
        <el-button
          type="primary"
          :icon="Plus"
          @click="handleAdd"
          :disabled="carouselList.length >= 5"
        >
          新增轮播图
        </el-button>
      </div>
    </el-card>

    <!-- 提示信息 -->
    <el-alert
      v-if="carouselList.length >= 5"
      title="轮播图数量已达上限（5张），如需添加新轮播图，请先删除现有轮播图"
      type="warning"
      :closable="false"
      show-icon
      class="limit-alert"
    />

    <!-- 轮播图列表 -->
    <el-card class="carousel-card" shadow="never" v-loading="loading">
      <el-empty v-if="carouselList.length === 0 && !loading" description="暂无轮播图，请点击上方按钮添加" />
      
      <div v-else class="carousel-list">
        <div
          v-for="(item, index) in carouselList"
          :key="item.id"
          class="carousel-item"
        >
          <!-- 序号标识 -->
          <div class="order-badge">{{ index + 1 }}</div>
          
          <!-- 轮播图内容 -->
          <div class="carousel-content">
            <!-- 图片区域 -->
            <div class="image-section">
              <el-image
                v-if="item.imageUrl"
                :src="getImageUrl(item.imageUrl)"
                fit="cover"
                class="carousel-image"
                @error="handleImageError"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon :size="30" color="#909399"><Picture /></el-icon>
                    <span>加载失败</span>
                  </div>
                </template>
              </el-image>
              <div v-else class="no-image">
                <el-icon :size="40" color="#909399"><Picture /></el-icon>
                <span>暂无图片</span>
              </div>
            </div>
            
            <!-- 信息区域 -->
            <div class="info-section">
              <h3 class="carousel-title">{{ item.title }}</h3>
              <p class="carousel-content-text">{{ item.content }}</p>
              <div class="carousel-meta">
                <el-tag size="small" type="success" v-if="item.status === 1">已启用</el-tag>
                <el-tag size="small" type="info" v-else>已禁用</el-tag>
                <span class="sort-order">排序: {{ item.sortOrder }}</span>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="action-section">
            <el-button-group>
              <el-button
                type="primary"
                size="small"
                :icon="Edit"
                @click="handleEdit(item)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="handleDelete(item)"
              >
                删除
              </el-button>
            </el-button-group>
            <div class="sort-buttons">
              <el-button
                type="info"
                size="small"
                :icon="ArrowUp"
                :disabled="index === 0"
                @click="handleMoveUp(index)"
              >
                上移
              </el-button>
              <el-button
                type="info"
                size="small"
                :icon="ArrowDown"
                :disabled="index === carouselList.length - 1"
                @click="handleMoveDown(index)"
              >
                下移
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 编辑/新增对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑轮播图' : '新增轮播图'"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="carouselForm"
        :rules="formRules"
        label-width="100px"
      >
        <!-- 标题 -->
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="carouselForm.title"
            placeholder="请输入轮播图标题"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <!-- 内容 -->
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="carouselForm.content"
            type="textarea"
            :rows="3"
            placeholder="请输入轮播图内容描述"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <!-- 排序号 -->
        <el-form-item label="排序号" prop="sortOrder">
          <el-input-number
            v-model="carouselForm.sortOrder"
            :min="1"
            :max="100"
            placeholder="请输入排序号"
          />
          <span class="form-tip">数字越小，排序越靠前</span>
        </el-form-item>
        
        <!-- 图片上传（带裁剪） -->
        <el-form-item label="轮播图" prop="imageUrl">
          <!-- 图片预览/上传区域 -->
          <div v-if="!showCropper" class="upload-wrapper">
            <div 
              v-if="carouselForm.imageUrl" 
              class="image-preview"
              @click="triggerFileInput"
            >
              <el-image :src="getImageUrl(carouselForm.imageUrl)" fit="cover" />
              <div class="image-overlay">
                <el-icon><Plus /></el-icon>
                <span>更换图片</span>
              </div>
            </div>
            <div v-else class="upload-placeholder" @click="triggerFileInput">
              <el-icon :size="40"><Plus /></el-icon>
              <div class="upload-text">点击上传图片</div>
              <div class="upload-tip">支持 JPG、PNG 格式，最大 100MB</div>
            </div>
            <!-- 隐藏的文件输入 -->
            <input
              ref="fileInputRef"
              type="file"
              accept="image/*"
              style="display: none"
              @change="handleFileChange"
            />
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="handleDialogCancel">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 图片裁剪对话框 -->
    <el-dialog
      v-model="cropperVisible"
      title="裁剪图片"
      width="800px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      destroy-on-close
    >
      <ImageCropper
        v-if="cropperVisible && cropImageUrl"
        :image-url="cropImageUrl"
        :crop-width="840"
        :crop-height="360"
        :fixed="true"
        :fixed-number="[21, 9]"
        output-type="jpeg"
        @crop="handleCropConfirm"
        @cancel="handleCropCancel"
      />
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * AdminCarousel.vue - 轮播图管理页面（支持图片裁剪）
 * 管理首页轮播图，支持图片上传和裁剪
 */
import { ref, reactive, onMounted } from 'vue'
import {
  Plus,
  Edit,
  Delete,
  ArrowUp,
  ArrowDown,
  Picture
} from '@element-plus/icons-vue'
import { getToken } from '@/utils/auth'
import { getImageUrl } from '@/utils/image'
import ImageCropper from '@/components/ImageCropper.vue'
import {
  getCarouselList,
  createCarousel,
  updateCarousel,
  deleteCarousel,
  updateCarouselSort
} from '@/api/admin'

// 加载状态
const loading = ref(false)

// 对话框显示状态
const dialogVisible = ref(false)

// 裁剪对话框显示状态
const cropperVisible = ref(false)

// 是否编辑模式
const isEdit = ref(false)

// 保存状态
const saving = ref(false)

// 表单引用
const formRef = ref(null)

// 文件输入引用
const fileInputRef = ref(null)

// 轮播图列表
const carouselList = ref([])

// 轮播图表单
const carouselForm = reactive({
  id: null,
  title: '',
  content: '',
  imageUrl: '',
  sortOrder: 1,
  status: 1
})

// 裁剪图片 URL
const cropImageUrl = ref('')

// 是否显示裁剪器
const showCropper = ref(false)

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入内容', trigger: 'blur' },
    { min: 5, max: 200, message: '长度在 5 到 200 个字符', trigger: 'blur' }
  ],
  sortOrder: [
    { required: true, message: '请输入排序号', trigger: 'blur' }
  ],
  imageUrl: [
    { required: true, message: '请上传轮播图图片', trigger: 'change' }
  ]
}

/**
 * 获取轮播图列表
 */
const fetchCarouselList = async () => {
  loading.value = true
  try {
    const res = await getCarouselList()
    carouselList.value = res || []
  } catch (error) {
    ElMessage.error('获取轮播图列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

/**
 * 处理图片加载错误
 */
const handleImageError = (error) => {
  console.error('图片加载失败:', error)
}

/**
 * 处理新增
 */
const handleAdd = () => {
  if (carouselList.value.length >= 5) {
    ElMessage.warning('轮播图数量已达上限（5张）')
    return
  }
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

/**
 * 处理编辑
 */
const handleEdit = (item) => {
  isEdit.value = true
  Object.assign(carouselForm, item)
  dialogVisible.value = true
}

/**
 * 处理删除
 */
const handleDelete = async (item) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除轮播图 "${item.title}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteCarousel(item.id)
    const index = carouselList.value.findIndex(i => i.id === item.id)
    if (index > -1) {
      carouselList.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除轮播图失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

/**
 * 保存轮播图排序到后端
 */
const saveCarouselSort = async () => {
  try {
    const sortList = carouselList.value.map((item, index) => ({
      id: item.id,
      sortOrder: index + 1
    }))
    
    await updateCarouselSort(sortList)
    ElMessage.success('排序已保存')
  } catch (error) {
    console.error('保存排序失败:', error)
    ElMessage.error('保存排序失败')
  }
}

/**
 * 处理上移
 */
const handleMoveUp = async (index) => {
  if (index === 0) return
  const temp = carouselList.value[index]
  carouselList.value[index] = carouselList.value[index - 1]
  carouselList.value[index - 1] = temp
  await saveCarouselSort()
}

/**
 * 处理下移
 */
const handleMoveDown = async (index) => {
  if (index === carouselList.value.length - 1) return
  const temp = carouselList.value[index]
  carouselList.value[index] = carouselList.value[index + 1]
  carouselList.value[index + 1] = temp
  await saveCarouselSort()
}

/**
 * 重置表单
 */
const resetForm = () => {
  carouselForm.id = null
  carouselForm.title = ''
  carouselForm.content = ''
  carouselForm.imageUrl = ''
  carouselForm.sortOrder = carouselList.value.length + 1
  carouselForm.status = 1
  showCropper.value = false
  cropImageUrl.value = ''
}

/**
 * 触发文件选择
 */
const triggerFileInput = () => {
  fileInputRef.value?.click()
}

/**
 * 处理文件选择变化
 */
const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 验证文件类型
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    event.target.value = ''
    return
  }

  // 验证文件大小（最大 100MB）
  const isLt100M = file.size / 1024 / 1024 < 100
    if (!isLt100M) {
      ElMessage.error('图片大小不能超过 100MB!')
      event.target.value = ''
      return
    }

  // 读取文件并显示裁剪对话框
  const reader = new FileReader()
  reader.onload = (e) => {
    cropImageUrl.value = e.target.result
    cropperVisible.value = true
  }
  reader.readAsDataURL(file)

  // 清空 input 值，允许重复选择同一文件
  event.target.value = ''
}

/**
 * 处理裁剪确认
 */
const handleCropConfirm = async (blob) => {
  try {
    // 创建 FormData
    const formData = new FormData()
    formData.append('file', blob, 'carousel.jpg')

    // 构建上传 URL
    const baseUrl = import.meta.env.VITE_API_BASE_URL || ''
    const uploadUrl = baseUrl 
      ? `${baseUrl}/admin/upload?type=carousel`
      : '/api/admin/upload?type=carousel'

    // 上传裁剪后的图片
    const response = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
      body: formData
    })

    const result = await response.json()

    if (result.code === 200) {
      carouselForm.imageUrl = result.data.url
      ElMessage.success('图片上传成功')
      cropperVisible.value = false
      cropImageUrl.value = ''
    } else {
      ElMessage.error(result.message || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('图片上传失败，请重试')
  }
}

/**
 * 处理裁剪取消
 */
const handleCropCancel = () => {
  cropperVisible.value = false
  cropImageUrl.value = ''
}

/**
 * 处理对话框取消
 */
const handleDialogCancel = () => {
  dialogVisible.value = false
  showCropper.value = false
  cropImageUrl.value = ''
}

/**
 * 构建提交数据
 */
const buildSubmitData = (formData) => {
  return {
    title: formData.title,
    content: formData.content,
    imageUrl: formData.imageUrl,
    sortOrder: formData.sortOrder,
    status: formData.status
  }
}

/**
 * 处理保存
 */
const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const submitData = buildSubmitData(carouselForm)
    
    if (isEdit.value) {
      // 更新轮播图
      await updateCarousel(carouselForm.id, submitData)
      const index = carouselList.value.findIndex(i => i.id === carouselForm.id)
      if (index > -1) {
        carouselList.value[index] = { 
          ...carouselForm,
          ...submitData
        }
      }
      ElMessage.success('修改成功')
    } else {
      // 创建轮播图
      const res = await createCarousel(submitData)
      carouselList.value.push({
        ...submitData,
        id: res?.id || Date.now()
      })
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    // 重新获取列表以确保数据同步
    await fetchCarouselList()
  } catch (error) {
    ElMessage.error(isEdit.value ? '修改失败' : '添加失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchCarouselList()
})
</script>

<style scoped>
/* 页面容器 */
.admin-carousel {
  padding: 0;
}

/* 页面头部卡片 */
.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  .page-title {
    margin: 0 0 8px;
    font-size: 20px;
    font-weight: 600;
    color: #303133;
  }

  .page-desc {
    margin: 0;
    font-size: 14px;
    color: #909399;
    display: flex;
    align-items: center;
    gap: 10px;
  }
}

.limit-tag {
  margin-left: 8px;
}

/* 上限提示 */
.limit-alert {
  margin-bottom: 20px;
}

/* 轮播图卡片 */
.carousel-card {
  min-height: 400px;
}

/* 轮播图列表 */
.carousel-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 轮播图项 */
.carousel-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  position: relative;
  gap: 20px;
}

/* 序号标识 */
.order-badge {
  width: 32px;
  height: 32px;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

/* 轮播图内容 */
.carousel-content {
  flex: 1;
  display: flex;
  gap: 20px;
}

/* 图片区域 - 21:9 宽屏比例 */
.image-section {
  width: 210px;
  height: 90px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-image {
  width: 100%;
  height: 100%;
}

.no-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 12px;
}

/* 信息区域 */
.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.carousel-title {
  margin: 0 0 10px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.carousel-content-text {
  margin: 0 0 15px;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.carousel-meta {
  display: flex;
  align-items: center;
  gap: 15px;
}

.sort-order {
  font-size: 13px;
  color: #909399;
}

/* 操作区域 */
.action-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
}

.sort-buttons {
  display: flex;
  gap: 8px;
}

/* 表单提示 */
.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

/* 图片上传样式 - 21:9 宽屏比例 */
.upload-wrapper {
  width: 315px;
  height: 135px;
}

.upload-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8c939d;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.3s;

  &:hover {
    border-color: #409EFF;
  }

  .upload-text {
    margin-top: 10px;
    font-size: 14px;
  }

  .upload-tip {
    margin-top: 5px;
    font-size: 12px;
    color: #c0c4cc;
  }
}

.image-preview {
  width: 100%;
  height: 100%;
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;

  .el-image {
    width: 100%;
    height: 100%;
  }

  .image-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    opacity: 0;
    transition: opacity 0.3s;

    &:hover {
      opacity: 1;
    }
  }
}

/* 图片加载失败样式 */
.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  font-size: 12px;
  gap: 8px;
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  .carousel-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .carousel-content {
    flex-direction: column;
    width: 100%;
  }

  .image-section {
    width: 100%;
    height: 128px;
  }

  .action-section {
    flex-direction: row;
    width: 100%;
    justify-content: space-between;
  }

  .upload-wrapper {
    width: 100%;
    max-width: 300px;
  }
}
</style>
