import request from '@/utils/request'

// 用户登录
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

// 用户注册
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/user/info',
    method: 'get'
  })
}

// 更新用户信息
export function updateUserInfo(data) {
  return request({
    url: '/user/info',
    method: 'put',
    data
  })
}

// 修改密码
export function changePassword(data) {
  return request({
    url: '/user/password',
    method: 'put',
    data
  })
}

// 上传头像
export function uploadAvatar(data) {
  return request({
    url: '/user/avatar',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 绑定手机号
export function bindPhone(data) {
  return request({
    url: '/user/bind-phone',
    method: 'post',
    data
  })
}

// 绑定邮箱
export function bindEmail(data) {
  return request({
    url: '/user/bind-email',
    method: 'post',
    data
  })
}

// 删除账号
export function deleteAccount(data) {
  return request({
    url: '/user/account',
    method: 'delete',
    data
  })
}
