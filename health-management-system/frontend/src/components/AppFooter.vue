<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-links">
        <a href="#">用户协议</a>
        <span class="divider">|</span>
        <a href="#">隐私政策</a>
        <span class="divider">|</span>
        <a href="#">帮助中心</a>
        <span class="divider">|</span>
        <a href="#">网站地图</a>
      </div>
      <p class="footer-copyright">© 2020-2024 久物健康科技有限公司 版权所有 | 浙ICP备2024XXXXXX号</p>
    </div>
  </footer>
</template>

<script setup>
// 通用页脚组件
</script>

<style scoped>
.app-footer {
  background: #1a1a2e;
  padding: 24px 0;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.footer-links a {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: #1890ff;
}

.divider {
  color: rgba(255, 255, 255, 0.2);
  font-size: 12px;
}

.footer-copyright {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  margin: 0;
}

@media screen and (max-width: 768px) {
  .footer-links {
    flex-wrap: wrap;
    gap: 8px 16px;
  }
  
  .divider {
    display: none;
  }
}
</style>
