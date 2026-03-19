/**
 * 管理员API模块
 * 提供文章管理相关的接口
 *
 * @module api/admin
 * @author Health Management System
 * @since 1.0.0
 */

import request from '@/utils/request'

/**
 * 获取文章列表（管理员）
 * 支持分页、筛选和搜索
 *
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 * @param {string} params.keyword - 搜索关键词
 * @param {string} params.category - 分类筛选
 * @param {string} params.status - 状态筛选
 * @returns {Promise<Object>} 文章列表和分页信息
 */
export function getArticles(params) {
  return request({
    url: '/admin/articles',
    method: 'get',
    params
  })
}

/**
 * 获取文章详情
 *
 * @param {number|string} id - 文章ID
 * @returns {Promise<Object>} 文章详情
 */
export function getArticle(id) {
  return request({
    url: `/admin/articles/${id}`,
    method: 'get'
  })
}

/**
 * 创建文章
 *
 * @param {Object} data - 文章数据
 * @param {string} data.title - 文章标题
 * @param {string} data.content - 文章内容
 * @param {string} data.summary - 文章摘要
 * @param {string} data.category - 文章分类
 * @param {string} data.coverImage - 封面图片URL
 * @param {string} data.status - 文章状态
 * @returns {Promise<Object>} 创建结果
 */
export function createArticle(data) {
  return request({
    url: '/admin/articles',
    method: 'post',
    data
  })
}

/**
 * 更新文章
 *
 * @param {number|string} id - 文章ID
 * @param {Object} data - 文章数据
 * @returns {Promise<Object>} 更新结果
 */
export function updateArticle(id, data) {
  return request({
    url: `/admin/articles/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除文章
 *
 * @param {number|string} id - 文章ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteArticle(id) {
  return request({
    url: `/admin/articles/${id}`,
    method: 'delete'
  })
}

/**
 * 上传图片
 * 用于文章封面或内容中的图片
 *
 * @param {File} file - 图片文件
 * @returns {Promise<Object>} 上传结果，包含图片URL
 */
export function uploadImage(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/admin/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 批量删除文章
 *
 * @param {Array<number|string>} ids - 文章ID数组
 * @returns {Promise<Object>} 删除结果
 */
export function batchDeleteArticles(ids) {
  return request({
    url: '/admin/articles/batch',
    method: 'delete',
    data: { ids }
  })
}

/**
 * 更新文章状态
 *
 * @param {number|string} id - 文章ID
 * @param {string} status - 新状态
 * @returns {Promise<Object>} 更新结果
 */
export function updateArticleStatus(id, status) {
  return request({
    url: `/admin/articles/${id}/status`,
    method: 'patch',
    data: { status }
  })
}

/**
 * 获取轮播图列表
 * 用于管理后台获取所有轮播图
 *
 * @returns {Promise<Array>} 轮播图列表
 */
export function getCarouselList() {
  return request({
    url: '/admin/carousel',
    method: 'get'
  })
}

/**
 * 获取轮播图详情
 *
 * @param {number|string} id - 轮播图ID
 * @returns {Promise<Object>} 轮播图详情
 */
export function getCarouselDetail(id) {
  return request({
    url: `/admin/carousel/${id}`,
    method: 'get'
  })
}

/**
 * 创建轮播图
 *
 * @param {Object} data - 轮播图数据
 * @param {string} data.title - 标题
 * @param {string} data.content - 内容
 * @param {string} data.imageUrl - 图片URL
 * @param {number} data.sortOrder - 排序号
 * @returns {Promise<Object>} 创建结果
 */
export function createCarousel(data) {
  return request({
    url: '/admin/carousel',
    method: 'post',
    data
  })
}

/**
 * 更新轮播图
 *
 * @param {number|string} id - 轮播图ID
 * @param {Object} data - 轮播图数据
 * @returns {Promise<Object>} 更新结果
 */
export function updateCarousel(id, data) {
  return request({
    url: `/admin/carousel/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除轮播图
 *
 * @param {number|string} id - 轮播图ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteCarousel(id) {
  return request({
    url: `/admin/carousel/${id}`,
    method: 'delete'
  })
}

/**
 * 批量删除轮播图
 *
 * @param {Array<number|string>} ids - 轮播图ID数组
 * @returns {Promise<Object>} 删除结果
 */
export function batchDeleteCarousel(ids) {
  return request({
    url: '/admin/carousel/batch',
    method: 'delete',
    data: { ids }
  })
}

/**
 * 更新轮播图排序
 * 用于调整轮播图的显示顺序
 *
 * @param {Array<{id: number, sortOrder: number}>} sortList - 排序列表
 * @returns {Promise<Object>} 更新结果
 */
export function updateCarouselSort(sortList) {
  return request({
    url: '/admin/carousel/sort',
    method: 'put',
    data: sortList
  })
}
