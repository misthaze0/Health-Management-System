<!--
  ImageCropper.vue - 图片裁剪组件
  
  功能说明：
  - 支持图片裁剪、缩放、旋转
  - 支持固定比例裁剪
  - 裁剪完成后输出 Blob 对象
  
  使用示例：
  <ImageCropper
    :image-url="imageUrl"
    :aspect-ratio="16/9"
    @crop="handleCrop"
    @cancel="handleCancel"
  />
-->
<template>
  <div class="image-cropper">
    <!-- 裁剪区域 -->
    <div class="cropper-container">
      <vue-cropper
        ref="cropperRef"
        :img="imageUrl"
        :output-size="1"
        :output-type="outputType"
        :info="true"
        :can-scale="true"
        :auto-crop="true"
        :auto-crop-width="cropWidth"
        :auto-crop-height="cropHeight"
        :fixed="fixed"
        :fixed-number="fixedNumber"
        :fixed-box="false"
        :center-box="true"
        :can-move="true"
        :can-move-box="true"
        :original="false"
        :info-true="true"
        :max-img-size="3000"
        :enlarge="1"
        :mode="'contain'"
        @real-time="handleRealTime"
      />
    </div>

    <!-- 工具栏 -->
    <div class="cropper-toolbar">
      <div class="toolbar-section">
        <el-tooltip content="放大" placement="top">
          <el-button :icon="ZoomIn" circle size="small" @click="zoom(0.1)" />
        </el-tooltip>
        <el-tooltip content="缩小" placement="top">
          <el-button :icon="ZoomOut" circle size="small" @click="zoom(-0.1)" />
        </el-tooltip>
        <el-tooltip content="向左旋转" placement="top">
          <el-button :icon="RefreshLeft" circle size="small" @click="rotateLeft" />
        </el-tooltip>
        <el-tooltip content="向右旋转" placement="top">
          <el-button :icon="RefreshRight" circle size="small" @click="rotateRight" />
        </el-tooltip>
        <el-tooltip content="重置" placement="top">
          <el-button :icon="Refresh" circle size="small" @click="reset" />
        </el-tooltip>
      </div>

      <!-- 预览区域 -->
      <div v-if="showPreview" class="preview-section">
        <div class="preview-label">预览</div>
        <div class="preview-box" :style="previewStyle">
          <img :src="previewUrl" v-if="previewUrl" />
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="cropper-actions">
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" :loading="cropping" @click="handleConfirm">
        确认裁剪
      </el-button>
    </div>
  </div>
</template>

<script setup>
/**
 * ImageCropper 组件
 * @description 图片裁剪组件，基于 vue-cropper
 */
import { ref, computed } from 'vue'
import { ZoomIn, ZoomOut, RefreshLeft, RefreshRight, Refresh } from '@element-plus/icons-vue'
import 'vue-cropper/dist/index.css'
import { VueCropper } from 'vue-cropper'

// 定义组件 props
const props = defineProps({
  /**
   * 图片地址（可以是 URL 或 base64）
   */
  imageUrl: {
    type: String,
    required: true
  },
  /**
   * 裁剪框宽度（像素）
   */
  cropWidth: {
    type: Number,
    default: 300
  },
  /**
   * 裁剪框高度（像素）
   */
  cropHeight: {
    type: Number,
    default: 180
  },
  /**
   * 是否固定比例
   */
  fixed: {
    type: Boolean,
    default: true
  },
  /**
   * 固定比例 [宽, 高] - 默认 21:9 宽屏比例
   */
  fixedNumber: {
    type: Array,
    default: () => [21, 9]
  },
  /**
   * 输出图片类型
   */
  outputType: {
    type: String,
    default: 'png'
  },
  /**
   * 是否显示预览
   */
  showPreview: {
    type: Boolean,
    default: true
  }
})

// 定义组件事件
const emit = defineEmits(['crop', 'cancel'])

// 裁剪组件引用
const cropperRef = ref(null)

// 裁剪状态
const cropping = ref(false)

// 预览图片 URL
const previewUrl = ref('')

// 预览样式
const previewStyle = computed(() => {
  const ratio = props.fixedNumber[0] / props.fixedNumber[1]
  const width = 120
  const height = width / ratio
  return {
    width: `${width}px`,
    height: `${height}px`
  }
})

/**
 * 处理实时预览
 */
const handleRealTime = (data) => {
  if (cropperRef.value) {
    cropperRef.value.getCropData((cropData) => {
      previewUrl.value = cropData
    })
  }
}

/**
 * 放大/缩小
 * @param {number} scale - 缩放比例
 */
const zoom = (scale) => {
  cropperRef.value?.changeScale(scale)
}

/**
 * 向左旋转
 */
const rotateLeft = () => {
  cropperRef.value?.rotateLeft()
}

/**
 * 向右旋转
 */
const rotateRight = () => {
  cropperRef.value?.rotateRight()
}

/**
 * 重置裁剪区域
 */
const reset = () => {
  cropperRef.value?.refresh()
}

/**
 * 处理确认裁剪
 */
const handleConfirm = () => {
  cropping.value = true
  
  cropperRef.value?.getCropBlob((blob) => {
    cropping.value = false
    emit('crop', blob)
  })
}

/**
 * 处理取消
 */
const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.image-cropper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cropper-container {
  width: 100%;
  height: 400px;
  background-color: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

.cropper-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.toolbar-section {
  display: flex;
  gap: 8px;
}

.preview-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview-label {
  font-size: 12px;
  color: #606266;
}

.preview-box {
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
  background-color: #fff;
}

.preview-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cropper-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  .cropper-container {
    height: 300px;
  }

  .cropper-toolbar {
    flex-direction: column;
    gap: 12px;
  }

  .toolbar-section {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
