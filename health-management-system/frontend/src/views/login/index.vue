<template>
  <div class="login-container">
    <!-- Prism 动态背景 -->
    <PrismBackground
      :height="3"
      :base-width="5"
      animation-type="rotate"
      :glow="0.8"
      :noise="0"
      :scale="3.5"
      :time-scale="0.5"
      :bloom="1"
    />

    <!-- 登录卡片 -->
    <div class="login-box" :class="{ 'shake-animation': shakeAnimation }">
      <div class="login-header">
        <h2 class="animate-slide-up delay-1">久物健康</h2>
        <p class="subtitle animate-slide-up delay-2">JIUWU HEALTH</p>
      </div>
      
      <el-tabs v-model="activeTab" class="login-tabs animate-slide-up delay-3">
        <!-- 登录表单 -->
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
          >
            <el-form-item prop="username" class="form-item-animated">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                :prefix-icon="User"
                size="large"
                class="animated-input"
              />
            </el-form-item>
            
            <el-form-item prop="password" class="form-item-animated">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                :prefix-icon="Lock"
                size="large"
                show-password
                @keyup.enter="handleLogin"
                class="animated-input"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-button hover-scale"
                :loading="loading"
                @click="handleLogin"
              >
                <span v-if="!loading">登 录</span>
                <span v-else>登录中...</span>
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 注册表单 -->
        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="login-form"
          >
            <el-form-item prop="username" class="form-item-animated">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名"
                :prefix-icon="User"
                size="large"
                class="animated-input"
              />
            </el-form-item>
            
            <el-form-item prop="password" class="form-item-animated">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码"
                :prefix-icon="Lock"
                size="large"
                show-password
                class="animated-input"
              />
            </el-form-item>
            
            <el-form-item prop="confirmPassword" class="form-item-animated">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                :prefix-icon="Lock"
                size="large"
                show-password
                class="animated-input"
              />
            </el-form-item>

            <!-- 角色选择 -->
            <el-form-item prop="roleCode" class="form-item-animated">
              <el-select
                v-model="registerForm.roleCode"
                placeholder="选择角色"
                size="large"
                class="animated-input role-select"
              >
                <el-option label="普通用户" value="user" />
                <el-option label="医生" value="doctor" />
                <el-option label="管理员" value="admin" />
              </el-select>
            </el-form-item>

            <!-- 管理员邀请码 -->
            <el-form-item
              v-if="registerForm.roleCode === 'admin'"
              prop="inviteCode"
              class="form-item-animated"
            >
              <el-input
                v-model="registerForm.inviteCode"
                placeholder="请输入管理员邀请码"
                :prefix-icon="Key"
                size="large"
                class="animated-input"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-button hover-scale"
                :loading="loading"
                @click="handleRegister"
              >
                <span v-if="!loading">注 册</span>
                <span v-else>注册中...</span>
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <!-- 装饰性元素 -->
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Key, FirstAidKit } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import PrismBackground from '@/components/PrismBackground.vue'

const router = useRouter()
const userStore = useUserStore()

// 登录框摇晃动画状态
const shakeAnimation = ref(false)

const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref()
const registerFormRef = ref()

// 登录表单
const loginForm = reactive({
  username: '',
  password: ''
})

// 登录验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

// 注册表单
const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  roleCode: 'user', // 默认为普通用户
  inviteCode: ''
})

// 注册验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 20, message: '用户名长度4-20位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度6-20位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}



// 触发摇晃动画
const triggerShake = () => {
  shakeAnimation.value = true
  setTimeout(() => {
    shakeAnimation.value = false
  }, 400)
}

// 登录处理
const handleLogin = async () => {
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) {
    // 表单验证失败时添加摇晃动画
    triggerShake()
    return
  }

  loading.value = true
  try {
    await userStore.login(loginForm)
    ElMessage.success('登录成功')

    // 检查是否有跳转前的页面路径
    const redirectPath = localStorage.getItem('redirectPath')
    if (redirectPath) {
      localStorage.removeItem('redirectPath')
      await router.push(redirectPath)
    } else {
      await router.push('/dashboard')
    }
  } catch (error) {
    ElMessage.error(error.message || '登录失败')
    // 错误摇晃动画
    triggerShake()
  } finally {
    loading.value = false
  }
}

// 注册处理
const handleRegister = async () => {
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) {
    triggerShake()
    return
  }

  loading.value = true
  try {
    await userStore.register(registerForm)
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    registerFormRef.value.resetFields()
  } catch (error) {
    ElMessage.error(error.message || '注册失败')
    triggerShake()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  // 纯黑色背景
  background: #000000;
  position: relative;
  overflow: hidden;
}

.login-box {
  width: 420px;
  padding: 40px;
  // 半透明黑色毛玻璃效果
  background: rgba(0, 0, 0, 0.6);
  // 圆角改为 20px
  border-radius: 20px;
  // 阴影改为深色
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  position: relative;
  z-index: 10;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  // 入场动画
  animation: slideUp 0.8s ease-out;

  // 摇晃动画
  &.shake-animation {
    animation: shake 0.4s ease-out;
  }
}

// 入场动画
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 摇晃动画
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-10px); }
  40% { transform: translateX(10px); }
  60% { transform: translateX(-10px); }
  80% { transform: translateX(10px); }
}

// 支持减少动画偏好
@media (prefers-reduced-motion: reduce) {
  .login-box {
    animation: none;
  }
  
  .login-box.shake-animation {
    animation: none;
    // 使用视觉反馈替代动画
    border: 2px solid #f56c6c;
  }
  
  .animate-bounce-in,
  .animate-slide-up,
  .delay-1,
  .delay-2,
  .delay-3 {
    animation: none;
    opacity: 1;
    transform: none;
  }
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-size: 28px;
  margin-bottom: 5px;
  font-weight: 600;
  // 银色闪光文字效果 - 参考 ShinyText 组件
  color: #b5b5b5;
  position: relative;
  display: inline-block;
}

.login-header h2::before {
  content: '久物健康';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    transparent 0%,
    transparent 40%,
    #ffffff 50%,
    transparent 60%,
    transparent 100%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shine-sweep 2s linear infinite;
  pointer-events: none;
}

@keyframes shine-sweep {
  0% {
    background-position: 150% center;
  }
  100% {
    background-position: -50% center;
  }
}

.login-header .subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 3px;
  font-weight: 400;
  margin-bottom: 10px;
}

.login-tabs {
  margin-top: 20px;

  :deep(.el-tabs__header) {
    margin-bottom: 25px;
  }

  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background-color: rgba(255, 255, 255, 0.1);
  }

  :deep(.el-tabs__item) {
    font-size: 16px;
    padding: 0 20px;
    color: rgba(255, 255, 255, 0.6);

    &.is-active {
      font-weight: 600;
      // 选中标签颜色改为白色
      color: #ffffff;
    }

    &:hover {
      color: rgba(255, 255, 255, 0.8);
    }
  }

  // 标签下划线颜色改为白色
  :deep(.el-tabs__active-bar) {
    background-color: #ffffff;
  }
}

.login-form {
  margin-top: 10px;
}

.form-item-animated {
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateX(5px);
  }
}

.animated-input {
  :deep(.el-input__wrapper) {
    // 输入框圆角改为 10px
    border-radius: 10px;
    transition: all 0.3s ease;
    // 深色半透明背景
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.1);

    &:hover, &:focus-within {
      // 聚焦时阴影改为白色系
      box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
      background: rgba(255, 255, 255, 0.15);
    }

    // 输入框文字颜色
    .el-input__inner {
      color: #ffffff;

      &::placeholder {
        color: rgba(255, 255, 255, 0.5);
      }
    }

    // 图标颜色
    .el-input__icon {
      color: rgba(255, 255, 255, 0.6);
    }
  }

  // 输入框聚焦时边框颜色改为白色
  :deep(.el-input__inner) {
    &:focus {
      border-color: rgba(255, 255, 255, 0.3);
    }
  }
}

.login-button {
  width: 100%;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  height: 44px;
  // 纯蓝色背景
  background: #2563eb;
  border: none;
  transition: all 0.3s ease;

  &:hover {
    // 悬停阴影改为蓝色
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
  }
}

// 装饰圆圈
.decoration-circle {
  position: absolute;
  border-radius: 50%;
  // 装饰圆圈改为蓝绿色系
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.1), rgba(54, 207, 201, 0.1));
  pointer-events: none;
}

.circle-1 {
  width: 150px;
  height: 150px;
  top: -50px;
  right: -50px;
  animation: pulse 4s ease-in-out infinite;
}

.circle-2 {
  width: 100px;
  height: 100px;
  bottom: -30px;
  left: -30px;
  animation: pulse 4s ease-in-out infinite 2s;
}

// 动画类
.animate-bounce-in {
  animation: bounceIn 0.8s ease-out forwards;
}

.animate-slide-up {
  opacity: 0;
  animation: slideUp 0.6s ease-out forwards;
}

.delay-1 {
  animation-delay: 0.1s;
}

.delay-2 {
  animation-delay: 0.2s;
}

.delay-3 {
  animation-delay: 0.3s;
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}
</style>
