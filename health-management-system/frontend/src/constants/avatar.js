// 头像配置常量

// AI 医生头像 - 使用本地 SVG 或备用服务
export const AI_DOCTOR_AVATAR = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iNTAiIGZpbGw9IiM0MDlFRkYiLz4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjQwIiByPSIyMCIgZmlsbD0iI2ZmZiIvPgogIDxjaXJjbGUgY3g9IjUwIiBjeT0iODAiIHI9IjI1IiBmaWxsPSIjZmZmIi8+CiAgPGNpcmNsZSBjeD0iNDIiIGN5PSIzOCIgcj0iMyIgZmlsbD0iIzMzMyIvPgogIDxjaXJjbGUgY3g9IjU4IiBjeT0iMzgiIHI9IjMiIGZpbGw9IiMzMzMiLz4KICA8cGF0aCBkPSJNNDUgNDhRNTAgNTIgNTUgNDgiIHN0cm9rZT0iIzMzMyIgc3Ryb2tlLXdpZHRoPSIyIiBmaWxsPSJub25lIi8+Cjwvc3ZnPg=='

// 用户默认头像
export const getUserAvatar = (username = 'user') => {
  // 使用 UI Avatars 作为备用服务（更稳定）
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(username)}&background=random&color=fff&size=128`
}

// 头像加载失败时的处理
export const handleAvatarError = (e) => {
  e.target.src = AI_DOCTOR_AVATAR
}
