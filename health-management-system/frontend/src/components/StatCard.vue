<!--
  StatCard.vue - 统计数据卡片组件
  
  功能说明：
  - 用于展示关键统计数据
  - 支持自定义颜色主题
  - 带有阴影和悬停效果
  
  使用示例：
  <StatCard 
    :value="128"
    label="健康报告"
    icon="Document"
    color="#67c23a"
  />
-->
<template>
  <div class="stat-card" :style="cardStyle">
    <!-- 图标区域 -->
    <div class="stat-card__icon-wrapper" :style="iconStyle">
      <el-icon class="stat-card__icon" :size="28">
        <component :is="iconComponent" />
      </el-icon>
    </div>
    
    <!-- 数据区域 -->
    <div class="stat-card__content">
      <div class="stat-card__value" :style="valueStyle">{{ formattedValue }}</div>
      <div class="stat-card__label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
/**
 * StatCard 组件
 * @description 统计数据卡片，用于展示关键指标
 */
import { computed } from 'vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 定义组件 props
const props = defineProps({
  /**
   * 数值
   */
  value: {
    type: [Number, String],
    required: true
  },
  /**
   * 标签文字
   */
  label: {
    type: String,
    required: true
  },
  /**
   * 图标名称（Element Plus 图标）
   */
  icon: {
    type: String,
    default: 'DataLine'
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
  return ElementPlusIconsVue[props.icon] || ElementPlusIconsVue.DataLine
})

// 格式化数值显示
const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString('zh-CN')
  }
  return props.value
})

// 卡片样式
const cardStyle = computed(() => ({
  '--stat-card-color': props.color
}))

// 图标区域样式（渐变背景）
const iconStyle = computed(() => ({
  background: `linear-gradient(135deg, ${props.color}20, ${props.color}40)`,
  color: props.color
}))

// 数值样式
const valueStyle = computed(() => ({
  color: props.color
}))
</script>

<style scoped>
/* 主容器 */
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: var(--card-bg, #ffffff);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s ease;
  cursor: pointer;
}

/* 悬停效果 */
.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* 图标区域 */
.stat-card__icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  flex-shrink: 0;
}

/* 图标 */
.stat-card__icon {
  /* 无动画 */
}

/* 内容区域 */
.stat-card__content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

/* 数值 */
.stat-card__value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
}

/* 标签 */
.stat-card__label {
  font-size: 14px;
  color: var(--text-secondary, #909399);
  font-weight: 500;
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  .stat-card {
    padding: 16px 20px;
    gap: 12px;
  }
  
  .stat-card__icon-wrapper {
    width: 48px;
    height: 48px;
  }
  
  .stat-card__value {
    font-size: 24px;
  }
  
  .stat-card__label {
    font-size: 12px;
  }
}
</style>
