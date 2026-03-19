<template>
  <router-view />
</template>

<script setup>
</script>

<style>
/* ============================================
   全局 CSS 变量定义
   ============================================ */
:root {
  /* 品牌色 */
  --primary-color: #1890ff;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --danger-color: #f5222d;

  /* 文字色 */
  --text-primary: #333333;
  --text-secondary: #666666;
  --text-muted: #999999;

  /* 边框与背景 */
  --border-color: #e8e8e8;
  --bg-color: #f5f7fa;
  --white: #ffffff;

  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;

  /* 阴影 */
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.12);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.16);
}

/* ============================================
   全局样式重置
   ============================================ */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-primary);
  background-color: var(--bg-color);
}

/* ============================================
   过渡动画 - Fade 淡入淡出
   ============================================ */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ============================================
   过渡动画 - Slide Up 上滑进入
   ============================================ */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* ============================================
   过渡动画 - Scale In 缩放进入
   ============================================ */
.scale-in-enter-active,
.scale-in-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.scale-in-enter-from,
.scale-in-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* ============================================
   响应式断点样式注释
   ============================================ */
/*
   断点说明：
   - 移动端: < 768px
   - 平板端: 768px - 1024px
   - 桌面端: 1024px - 1440px
   - 大屏端: >= 1440px

   使用示例：
   @media (max-width: 768px) {
     // 移动端样式
   }

   @media (min-width: 768px) and (max-width: 1024px) {
     // 平板端样式
   }

   @media (min-width: 1024px) {
     // 桌面端及以上样式
   }
*/
</style>
