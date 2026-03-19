<!--
  SectionTitle.vue - 统一区块标题组件
  
  功能说明：
  - 用于页面各区块的标题展示
  - 左侧带有蓝色竖条装饰
  - 支持主标题、副标题和图标
  
  使用示例：
  <SectionTitle 
    title="健康数据概览" 
    subtitle="实时监测您的健康指标"
    icon="Monitor"
  />
-->
<template>
  <div class="section-title">
    <!-- 左侧蓝色装饰条 -->
    <div class="section-title__decorator"></div>
    
    <!-- 内容区域 -->
    <div class="section-title__content">
      <!-- 图标 -->
      <el-icon v-if="icon" class="section-title__icon" :size="24">
        <component :is="icon" />
      </el-icon>
      
      <!-- 文字区域 -->
      <div class="section-title__text">
        <h2 class="section-title__main">{{ title }}</h2>
        <p v-if="subtitle" class="section-title__sub">{{ subtitle }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * SectionTitle 组件
 * @description 统一区块标题组件，带左侧装饰条
 */

// 定义组件 props
const props = defineProps({
  /**
   * 主标题文字
   */
  title: {
    type: String,
    required: true
  },
  /**
   * 副标题文字
   */
  subtitle: {
    type: String,
    default: ''
  },
  /**
   * 图标名称（Element Plus 图标）
   */
  icon: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
/* 主容器 */
.section-title {
  display: flex;
  align-items: stretch;
  margin-bottom: 24px;
}

/* 左侧蓝色装饰条 */
.section-title__decorator {
  width: 4px;
  background: var(--primary-color, #409eff);
  border-radius: 2px;
  margin-right: 12px;
  flex-shrink: 0;
}

/* 内容区域 */
.section-title__content {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 图标样式 */
.section-title__icon {
  color: var(--primary-color, #409eff);
  flex-shrink: 0;
}

/* 文字区域 */
.section-title__text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 主标题 */
.section-title__main {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary, #303133);
  margin: 0;
  line-height: 1.3;
}

/* 副标题 */
.section-title__sub {
  font-size: 14px;
  color: var(--text-secondary, #909399);
  margin: 0;
  line-height: 1.4;
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  .section-title__main {
    font-size: 20px;
  }
  
  .section-title__sub {
    font-size: 12px;
  }
  
  .section-title__decorator {
    width: 3px;
    margin-right: 8px;
  }
}
</style>
