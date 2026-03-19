<!--
  FeatureCard.vue - 功能特性卡片组件
  
  功能说明：
  - 用于展示功能特性
  - 图标区域使用渐变背景
  - 文字居中显示
  - 悬停时有放大和阴影效果
  
  使用示例：
  <FeatureCard 
    title="AI智能分析"
    description="基于深度学习的健康数据分析"
    icon="Cpu"
    gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
  />
-->
<template>
  <div class="feature-card">
    <!-- 图标区域 -->
    <div class="feature-card__icon-wrapper" :style="iconWrapperStyle">
      <el-icon class="feature-card__icon" :size="36">
        <component :is="iconComponent" />
      </el-icon>
    </div>
    
    <!-- 内容区域 -->
    <div class="feature-card__content">
      <h3 class="feature-card__title">{{ title }}</h3>
      <p class="feature-card__description">{{ description }}</p>
    </div>
  </div>
</template>

<script setup>
/**
 * FeatureCard 组件
 * @description 功能特性卡片，用于展示产品特性
 */
import { computed } from 'vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 定义组件 props
const props = defineProps({
  /**
   * 标题
   */
  title: {
    type: String,
    required: true
  },
  /**
   * 描述文字
   */
  description: {
    type: String,
    required: true
  },
  /**
   * 图标名称（Element Plus 图标）
   */
  icon: {
    type: String,
    default: 'Star'
  },
  /**
   * 渐变背景（CSS gradient）- 默认蓝白渐变
   */
  gradient: {
    type: String,
    default: 'linear-gradient(135deg, #1890ff 0%, #69c0ff 100%)'
  }
})

// 获取图标组件
const iconComponent = computed(() => {
  return ElementPlusIconsVue[props.icon] || ElementPlusIconsVue.Star
})

// 图标区域样式
const iconWrapperStyle = computed(() => ({
  background: props.gradient
}))
</script>

<style scoped>
/* 主容器 */
.feature-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 32px 24px;
  background: var(--card-bg, #ffffff);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s ease;
  cursor: pointer;
  height: 100%;
}

/* 悬停效果 */
.feature-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

/* 图标区域 */
.feature-card__icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 20px;
  margin-bottom: 20px;
  color: #ffffff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

/* 图标 */
.feature-card__icon {
  /* 无动画 */
}

/* 标题 */
.feature-card__title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #303133);
  margin: 0 0 12px;
  line-height: 1.4;
}

/* 描述 */
.feature-card__description {
  font-size: 14px;
  color: var(--text-secondary, #909399);
  margin: 0;
  line-height: 1.6;
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  .feature-card {
    padding: 24px 16px;
  }
  
  .feature-card__icon-wrapper {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    margin-bottom: 16px;
  }
  
  .feature-card__title {
    font-size: 16px;
    margin-bottom: 8px;
  }
  
  .feature-card__description {
    font-size: 12px;
  }
}
</style>
