import Cookies from 'js-cookie'

const TokenKey = 'health-management-token'

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
  return Cookies.set(TokenKey, token, { expires: 1 }) // 1天有效期
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}
