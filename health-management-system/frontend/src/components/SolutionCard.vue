<!--
  SolutionCard.vue - 解决方案卡片组件
  
  功能说明：
  - 用于展示解决方案或功能模块
  - 带有图标、标题和描述
  - 悬停时有上浮效果
  
  使用示例：
  <SolutionCard 
    title="智能血糖监测"
    description="实时追踪血糖变化，AI智能分析趋势"
    icon="FirstAidKit"
    color="#e6a23c"
  />
-->
<template>
  <div class="solution-card" :style="cardStyle">
    <!-- 图标区域 -->
    <div class="solution-card__icon-wrapper" :style="iconStyle">
      <el-icon class="solution-card__icon" :size="32">
        <component :is="iconComponent" />
      </el-icon>
    </div>
    
    <!-- 内容区域 -->
    <div class="solution-card__content">
      <h3 class="solution-card__title">{{ title }}</h3>
      <p class="solution-card__description">{{ description }}</p>
    </div>
    
    <!-- 箭头指示器 -->
    <div class="solution-card__arrow">
      <el-icon :size="20">
        <ArrowRight />
      </el-icon>
    </div>
  </div>
</template>

<script setup>
/**
 * SolutionCard 组件
 * @description 解决方案卡片，展示功能模块
 */
import { computed } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'
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
    default: 'Box'
  },
  /**
   * 颜色主题
   */
  color: {
    type: String,
    default: '#409eff'
  }
})

// 获取图标组件
const iconComponent = computed(() => {
  return ElementPlusIconsVue[props.icon] || ElementPlusIconsVue.Box
})

// 卡片样式
const cardStyle = computed(() => ({
  '--solution-card-color': props.color
}))

// 图标区域样式
const iconStyle = computed(() => ({
  background: `linear-gradient(135deg, ${props.color}15, ${props.color}30)`,
  color: props.color
}))
</script>

<style scoped>
/* 主容器 */
.solution-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: var(--card-bg, #ffffff);
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

/* 悬停效果 */
.solution-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* 图标区域 */
.solution-card__icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  flex-shrink: 0;
}

/* 图标 */
.solution-card__icon {
  /* 无动画 */
}

/* 内容区域 */
.solution-card__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 标题 */
.solution-card__title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #303133);
  margin: 0;
  line-height: 1.4;
}

/* 描述 */
.solution-card__description {
  font-size: 14px;
  color: var(--text-secondary, #909399);
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 箭头指示器 */
.solution-card__arrow {
  color: var(--text-placeholder, #c0c4cc);
  opacity: 0.6;
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  .solution-card {
    padding: 16px;
    gap: 12px;
  }
  
  .solution-card__icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 12px;
  }
  
  .solution-card__title {
    font-size: 16px;
  }
  
  .solution-card__description {
    font-size: 12px;
    -webkit-line-clamp: 1;
  }
  
  .solution-card__arrow {
    display: none;
  }
}
</style>
