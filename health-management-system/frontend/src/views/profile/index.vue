<template>
  <div class="profile-container">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">个人中心</h1>
        <p class="page-subtitle">Profile Center</p>
      </div>
    </div>

    <div class="profile-layout">
      <!-- 左侧：用户信息卡片 -->
      <div class="profile-sidebar">
        <!-- 头像卡片 -->
        <div class="avatar-card">
          <div class="avatar-wrapper">
            <el-avatar
              :size="100"
              :src="getAvatarUrl(userInfo.avatar) || defaultAvatar"
              class="user-avatar"
            />
            <div class="avatar-overlay" @click="handleAvatarClick">
              <el-icon v-if="!uploadingAvatar"><Camera /></el-icon>
              <el-icon v-else class="uploading-icon"><Loading /></el-icon>
              <span>{{ uploadingAvatar ? '上传中...' : '更换头像' }}</span>
            </div>
            <!-- 隐藏的文件输入 -->
            <input
              ref="avatarInputRef"
              type="file"
              accept="image/*"
              style="display: none"
              @change="handleAvatarChange"
            />
          </div>
          <h3 class="user-name">{{ userInfo.realName || userInfo.username || '用户' }}</h3>
          <p class="user-role">{{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}</p>
          <div class="user-status">
            <span class="status-dot"></span>
            <span>在线</span>
          </div>
        </div>

        <!-- 快捷菜单 -->
        <div class="quick-menu">
          <div 
            v-for="item in menuItems" 
            :key="item.key"
            :class="['menu-item', { active: activeTab === item.key }]"
            @click="activeTab = item.key"
          >
            <el-icon size="18"><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </div>
        </div>
      </div>

      <!-- 右侧：内容区域 -->
      <div class="profile-content">
        <!-- 基本信息 -->
        <div v-show="activeTab === 'basic'" class="content-panel">
          <div class="panel-header">
            <h3>基本信息</h3>
            <el-button type="primary" class="edit-btn" @click="handleEdit">
              <el-icon><Edit /></el-icon>
              编辑资料
            </el-button>
          </div>
          
          <div class="info-grid">
            <div class="info-item">
              <div class="info-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="info-content">
                <label>用户名</label>
                <span>{{ userInfo.username || '未设置' }}</span>
              </div>
            </div>
            
            <div class="info-item">
              <div class="info-icon">
                <el-icon><Avatar /></el-icon>
              </div>
              <div class="info-content">
                <label>真实姓名</label>
                <span>{{ userInfo.realName || '未设置' }}</span>
              </div>
            </div>
            
            <div class="info-item">
              <div class="info-icon">
                <el-icon><Message /></el-icon>
              </div>
              <div class="info-content">
                <label>电子邮箱</label>
                <span>{{ userInfo.email || '未设置' }}</span>
              </div>
            </div>
            
            <div class="info-item">
              <div class="info-icon">
                <el-icon><Phone /></el-icon>
              </div>
              <div class="info-content">
                <label>手机号码</label>
                <span>{{ userInfo.phone || '未设置' }}</span>
              </div>
            </div>
            
            <div class="info-item">
              <div class="info-icon">
                <el-icon><Male /></el-icon>
              </div>
              <div class="info-content">
                <label>性别</label>
                <span>{{ getGenderText(userInfo.gender) }}</span>
              </div>
            </div>
            
            <div class="info-item">
              <div class="info-icon">
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="info-content">
                <label>出生日期</label>
                <span>{{ userInfo.birthday || '未设置' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 账号安全 -->
        <div v-show="activeTab === 'security'" class="content-panel">
          <div class="panel-header">
            <h3>账号安全</h3>
          </div>
          
          <div class="security-list">
            <div class="security-item">
              <div class="security-info">
                <div class="security-icon">
                  <el-icon><Lock /></el-icon>
                </div>
                <div class="security-content">
                  <h4>登录密码</h4>
                  <p>定期更换密码可以保护您的账号安全</p>
                </div>
              </div>
              <el-button type="primary" plain @click="handleChangePassword">修改</el-button>
            </div>
            
            <div class="security-item">
              <div class="security-info">
                <div class="security-icon">
                  <el-icon><Cellphone /></el-icon>
                </div>
                <div class="security-content">
                  <h4>手机绑定</h4>
                  <p>{{ userInfo.phone ? `已绑定：${maskPhone(userInfo.phone)}` : '未绑定手机号' }}</p>
                </div>
              </div>
              <el-button type="primary" plain @click="handleBindPhone">
                {{ userInfo.phone ? '更换' : '绑定' }}
              </el-button>
            </div>
            
            <div class="security-item">
              <div class="security-info">
                <div class="security-icon">
                  <el-icon><Message /></el-icon>
                </div>
                <div class="security-content">
                  <h4>邮箱绑定</h4>
                  <p>{{ userInfo.email ? `已绑定：${maskEmail(userInfo.email)}` : '未绑定邮箱' }}</p>
                </div>
              </div>
              <el-button type="primary" plain @click="handleBindEmail">
                {{ userInfo.email ? '更换' : '绑定' }}
              </el-button>
            </div>

            <div class="security-item danger">
              <div class="security-info">
                <div class="security-icon danger-icon">
                  <el-icon><Delete /></el-icon>
                </div>
                <div class="security-content">
                  <h4>删除账号</h4>
                  <p>删除后账号将无法恢复，请谨慎操作</p>
                </div>
              </div>
              <el-button type="danger" plain @click="handleDeleteAccount">删除</el-button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 编辑资料对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑个人资料"
      width="500px"
      class="profile-dialog"
      destroy-on-close
    >
      <el-form :model="form" label-width="80px" class="profile-form">
        <el-form-item label="真实姓名">
          <el-input v-model="form.realName" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号码" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender" style="width: 100%">
            <el-option label="未知" :value="0" />
            <el-option label="男" :value="1" />
            <el-option label="女" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker
            v-model="form.birthday"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="400px"
      class="profile-dialog"
      destroy-on-close
    >
      <el-form :model="passwordForm" label-width="100px" class="profile-form">
        <el-form-item label="原密码">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码（6-20位）" show-password />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePasswordSave" :loading="changingPassword">确认修改</el-button>
      </template>
    </el-dialog>

    <!-- 绑定手机对话框 -->
    <el-dialog
      v-model="phoneDialogVisible"
      :title="userInfo.phone ? '更换手机号' : '绑定手机号'"
      width="400px"
      class="profile-dialog"
      destroy-on-close
    >
      <el-form :model="phoneForm" label-width="100px" class="profile-form">
        <el-form-item label="手机号">
          <el-input v-model="phoneForm.phone" placeholder="请输入手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="验证码">
          <div style="display: flex; gap: 12px;">
            <el-input v-model="phoneForm.verifyCode" placeholder="请输入验证码" maxlength="6" style="flex: 1;" />
            <el-button type="primary" :loading="sendingPhoneCode" @click="sendPhoneCode" :disabled="sendingPhoneCode">
              {{ sendingPhoneCode ? '发送中' : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="phoneDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePhoneSave" :loading="bindingPhone">确认绑定</el-button>
      </template>
    </el-dialog>

    <!-- 绑定邮箱对话框 -->
    <el-dialog
      v-model="emailDialogVisible"
      :title="userInfo.email ? '更换邮箱' : '绑定邮箱'"
      width="400px"
      class="profile-dialog"
      destroy-on-close
    >
      <el-form :model="emailForm" label-width="100px" class="profile-form">
        <el-form-item label="邮箱地址">
          <el-input v-model="emailForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="验证码">
          <div style="display: flex; gap: 12px;">
            <el-input v-model="emailForm.verifyCode" placeholder="请输入验证码" maxlength="6" style="flex: 1;" />
            <el-button type="primary" :loading="sendingEmailCode" @click="sendEmailCode" :disabled="sendingEmailCode">
              {{ sendingEmailCode ? '发送中' : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="emailDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEmailSave" :loading="bindingEmail">确认绑定</el-button>
      </template>
    </el-dialog>

    <!-- 删除账号对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除账号"
      width="450px"
      class="profile-dialog delete-dialog"
      destroy-on-close
    >
      <div class="delete-warning">
        <el-icon size="48" color="#ff4d4f"><Warning /></el-icon>
        <h4>警告：此操作不可恢复</h4>
        <p>删除账号后，您的所有数据将被永久删除，包括：</p>
        <ul>
          <li>个人资料和设置</li>
          <li>健康数据记录</li>
          <li>体检报告</li>
          <li>AI对话历史</li>
        </ul>
      </div>
      <el-form :model="deleteForm" label-width="100px" class="profile-form">
        <el-form-item label="登录密码">
          <el-input v-model="deleteForm.password" type="password" placeholder="请输入登录密码验证身份" show-password />
        </el-form-item>
        <el-form-item label="确认删除">
          <el-input v-model="deleteForm.confirmText" placeholder="请输入“删除账号”以确认" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="handleDeleteConfirm" :loading="deleting">确认删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getUserInfo, updateUserInfo, changePassword, bindPhone, bindEmail, deleteAccount, uploadAvatar } from '@/api/user'
import { useUserStore } from '@/stores/user'
import { getAvatarUrl } from '@/utils/image'
import {
  User,
  Avatar,
  Message,
  Phone,
  Male,
  Calendar,
  Edit,
  Lock,
  Cellphone,
  Camera,
  Collection,
  Warning,
  List,
  Delete,
  Loading
} from '@element-plus/icons-vue'

const { userInfo: storeUserInfo, checkLoginStatus } = useAuth()
const userStore = useUserStore()
const dialogVisible = ref(false)
const saving = ref(false)
const activeTab = ref('basic')
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 本地用户信息
const userInfo = ref({})

// 菜单项
const menuItems = [
  { key: 'basic', label: '基本信息', icon: 'User' },
  { key: 'security', label: '账号安全', icon: 'Lock' }
]



// 监听 store 中的用户信息变化
watch(() => storeUserInfo.value, (newVal) => {
  if (newVal) {
    userInfo.value = newVal
  }
}, { immediate: true, deep: true })

const form = ref({
  realName: '',
  email: '',
  phone: '',
  gender: 0,
  birthday: ''
})

// 加载用户信息
const loadUserInfo = async () => {
  if (!checkLoginStatus()) {
    ElMessage.warning('请先登录')
    return
  }
  
  if (!storeUserInfo.value) {
    try {
      const res = await getUserInfo()
      userInfo.value = res
    } catch (error) {
      ElMessage.error('加载用户信息失败: ' + (error.message || '未知错误'))
    }
  }
}

const getGenderText = (gender) => {
  const map = { 0: '未知', 1: '男', 2: '女' }
  return map[gender] || '未知'
}

const maskPhone = (phone) => {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const maskEmail = (email) => {
  if (!email) return ''
  const [name, domain] = email.split('@')
  const maskedName = name.length > 2 
    ? name.slice(0, 2) + '***' 
    : name.slice(0, 1) + '***'
  return `${maskedName}@${domain}`
}

const handleEdit = () => {
  form.value = {
    realName: userInfo.value.realName || '',
    email: userInfo.value.email || '',
    phone: userInfo.value.phone || '',
    gender: userInfo.value.gender || 0,
    birthday: userInfo.value.birthday || ''
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    const res = await updateUserInfo(form.value)
    userStore.setUserInfo(res)
    userInfo.value = res
    ElMessage.success('保存成功')
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 修改密码相关
const passwordDialogVisible = ref(false)
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const changingPassword = ref(false)

const handleChangePassword = () => {
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  passwordDialogVisible.value = true
}

const handlePasswordSave = async () => {
  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  if (passwordForm.value.newPassword.length < 6) {
    ElMessage.warning('新密码长度不能少于6位')
    return
  }

  changingPassword.value = true
  try {
    await changePassword({
      oldPassword: passwordForm.value.oldPassword,
      newPassword: passwordForm.value.newPassword,
      confirmPassword: passwordForm.value.confirmPassword
    })
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

// 绑定手机相关
const phoneDialogVisible = ref(false)
const phoneForm = ref({
  phone: '',
  verifyCode: ''
})
const bindingPhone = ref(false)
const sendingPhoneCode = ref(false)

const handleBindPhone = () => {
  phoneForm.value = {
    phone: '',
    verifyCode: ''
  }
  phoneDialogVisible.value = true
}

const sendPhoneCode = async () => {
  if (!phoneForm.value.phone || !/^1[3-9]\d{9}$/.test(phoneForm.value.phone)) {
    ElMessage.warning('请输入正确的手机号')
    return
  }
  sendingPhoneCode.value = true
  // 模拟发送验证码
  setTimeout(() => {
    ElMessage.success('验证码已发送（演示模式：任意6位数字）')
    sendingPhoneCode.value = false
  }, 1000)
}

const handlePhoneSave = async () => {
  if (!phoneForm.value.phone || !phoneForm.value.verifyCode) {
    ElMessage.warning('请填写完整信息')
    return
  }

  bindingPhone.value = true
  try {
    const res = await bindPhone({
      phone: phoneForm.value.phone,
      verifyCode: phoneForm.value.verifyCode
    })
    userStore.setUserInfo(res)
    userInfo.value = res
    ElMessage.success('手机号绑定成功')
    phoneDialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '手机号绑定失败')
  } finally {
    bindingPhone.value = false
  }
}

// 绑定邮箱相关
const emailDialogVisible = ref(false)
const emailForm = ref({
  email: '',
  verifyCode: ''
})
const bindingEmail = ref(false)
const sendingEmailCode = ref(false)

const handleBindEmail = () => {
  emailForm.value = {
    email: '',
    verifyCode: ''
  }
  emailDialogVisible.value = true
}

const sendEmailCode = async () => {
  if (!emailForm.value.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailForm.value.email)) {
    ElMessage.warning('请输入正确的邮箱地址')
    return
  }
  sendingEmailCode.value = true
  // 模拟发送验证码
  setTimeout(() => {
    ElMessage.success('验证码已发送（演示模式：任意6位数字）')
    sendingEmailCode.value = false
  }, 1000)
}

const handleEmailSave = async () => {
  if (!emailForm.value.email || !emailForm.value.verifyCode) {
    ElMessage.warning('请填写完整信息')
    return
  }

  bindingEmail.value = true
  try {
    const res = await bindEmail({
      email: emailForm.value.email,
      verifyCode: emailForm.value.verifyCode
    })
    userStore.setUserInfo(res)
    userInfo.value = res
    ElMessage.success('邮箱绑定成功')
    emailDialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '邮箱绑定失败')
  } finally {
    bindingEmail.value = false
  }
}

// 头像上传相关
const avatarInputRef = ref(null)
const uploadingAvatar = ref(false)

const handleAvatarClick = () => {
  // 触发文件选择
  avatarInputRef.value?.click()
}

const handleAvatarChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }

  // 验证文件大小（限制5MB）
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过5MB')
    return
  }

  uploadingAvatar.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)

    console.log('[Avatar Upload] 开始上传头像:', file.name, file.size)
    const res = await uploadAvatar(formData)
    console.log('[Avatar Upload] 上传成功，返回:', res)

    // 更新本地用户信息
    userInfo.value.avatar = res
    userStore.setUserInfo({ ...userStore.userInfo, avatar: res })

    ElMessage.success('头像上传成功')
  } catch (error) {
    console.error('[Avatar Upload] 上传失败:', error)
    console.error('[Avatar Upload] 错误响应:', error.response)
    ElMessage.error(error.response?.data?.message || '头像上传失败')
  } finally {
    uploadingAvatar.value = false
    // 清空input，允许重复选择同一文件
    event.target.value = ''
  }
}

// 删除账号相关
const deleteDialogVisible = ref(false)
const deleteForm = ref({
  password: '',
  confirmText: ''
})
const deleting = ref(false)
const router = useRouter()

const handleDeleteAccount = () => {
  deleteForm.value = {
    password: '',
    confirmText: ''
  }
  deleteDialogVisible.value = true
}

const handleDeleteConfirm = async () => {
  if (!deleteForm.value.password) {
    ElMessage.warning('请输入登录密码')
    return
  }
  if (deleteForm.value.confirmText !== '删除账号') {
    ElMessage.warning('请输入正确的确认文字"删除账号"')
    return
  }

  deleting.value = true
  try {
    await deleteAccount({
      password: deleteForm.value.password,
      confirmText: deleteForm.value.confirmText
    })
    ElMessage.success('账号已删除')
    // 清除登录状态并跳转到登录页
    userStore.logout()
    router.push('/login')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '删除账号失败')
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile-container {
  min-height: calc(100vh - 84px);
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 0;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.1) 0%, rgba(54, 207, 201, 0.05) 100%);
  padding: 32px 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* 布局 */
.profile-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 40px 40px;
}

/* 左侧边栏 */
.profile-sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 头像卡片 */
.avatar-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
}

.user-avatar {
  border: 3px solid rgba(24, 144, 255, 0.3);
  box-shadow: 0 4px 20px rgba(24, 144, 255, 0.2);
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  cursor: pointer;
}

.avatar-overlay:hover {
  opacity: 1;
}

.avatar-overlay .el-icon {
  font-size: 24px;
  color: #fff;
  margin-bottom: 4px;
}

.avatar-overlay span {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.user-role {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 12px;
}

.user-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(82, 196, 26, 0.15);
  border-radius: 20px;
  font-size: 12px;
  color: #52c41a;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #52c41a;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.uploading-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 快捷菜单 */
.quick-menu {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 12px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}

.menu-item.active {
  background: rgba(24, 144, 255, 0.15);
  color: #1890ff;
}

.menu-item .el-icon {
  font-size: 18px;
}

/* 右侧内容区 */
.profile-content {
  min-height: 500px;
}

.content-panel {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 28px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.panel-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.edit-btn {
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  border: none;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s;
}

.info-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
}

.info-icon {
  width: 44px;
  height: 44px;
  background: rgba(24, 144, 255, 0.1);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1890ff;
  font-size: 20px;
}

.info-content {
  flex: 1;
}

.info-content label {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.info-content span {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

/* 安全设置 */
.security-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.security-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.security-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  background: rgba(24, 144, 255, 0.1);
  color: #1890ff;
}

.security-icon.danger-icon {
  background: rgba(255, 77, 79, 0.1);
  color: #ff4d4f;
}

.security-item.danger {
  border-color: rgba(255, 77, 79, 0.15);
}

.security-content h4 {
  font-size: 15px;
  font-weight: 500;
  color: #fff;
  margin-bottom: 4px;
}

.security-content p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* 删除账号对话框 */
.delete-warning {
  text-align: center;
  padding: 20px 0 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 24px;
}

.delete-warning .el-icon {
  margin-bottom: 16px;
}

.delete-warning h4 {
  font-size: 18px;
  font-weight: 600;
  color: #ff4d4f;
  margin-bottom: 12px;
}

.delete-warning p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 16px;
}

.delete-warning ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: inline-block;
  text-align: left;
}

.delete-warning li {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  padding: 4px 0;
  padding-left: 20px;
  position: relative;
}

.delete-warning li::before {
  content: '•';
  position: absolute;
  left: 6px;
  color: #ff4d4f;
}

/* 操作记录 */
.logs-timeline {
  position: relative;
  padding-left: 24px;
}

.logs-timeline::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: rgba(24, 144, 255, 0.2);
}

.log-item {
  position: relative;
  padding-bottom: 20px;
}

.log-dot {
  position: absolute;
  left: -20px;
  top: 6px;
  width: 10px;
  height: 10px;
  background: #1890ff;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.2);
}

.log-content {
  background: rgba(255, 255, 255, 0.03);
  padding: 16px 20px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.log-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
}

.log-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* 对话框样式 */
:deep(.profile-dialog) {
  .el-dialog__header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 20px 24px;
    margin: 0;
  }
  
  .el-dialog__title {
    color: #fff;
    font-weight: 600;
  }
  
  .el-dialog__body {
    background: #1a1a2e;
    padding: 24px;
  }
  
  .el-dialog__footer {
    background: #1a1a2e;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding: 16px 24px;
  }
}

.profile-form {
  .el-form-item__label {
    color: rgba(255, 255, 255, 0.7);
  }
  
  .el-input__wrapper {
    background: rgba(255, 255, 255, 0.05);
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  }
  
  .el-input__inner {
    color: #fff;
    background: transparent;
  }
  
  .el-input__inner::placeholder {
    color: rgba(255, 255, 255, 0.3);
  }
}

/* 响应式 */
@media screen and (max-width: 1024px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }
  
  .profile-sidebar {
    flex-direction: row;
  }
  
  .avatar-card {
    flex: 0 0 280px;
  }
  
  .quick-menu {
    flex: 1;
  }
}

@media screen and (max-width: 768px) {
  .page-header {
    padding: 24px;
  }
  
  .profile-layout {
    padding: 16px;
  }
  
  .profile-sidebar {
    flex-direction: column;
  }
  
  .avatar-card {
    flex: none;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .security-item {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
}
</style>