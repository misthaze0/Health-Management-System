/**
 * 文章公开API模块
 * 提供前端展示用的文章相关接口
 *
 * @module api/article
 * @author Health Management System
 * @since 1.0.0
 */

import request from '@/utils/request'

/**
 * 获取启用的文章列表
 * 用于前端展示，只返回已启用的文章
 *
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 * @param {string} params.category - 分类筛选
 * @returns {Promise<Object>} 文章列表
 */
export function getArticles(params = {}) {
  console.log('[API] 开始获取文章列表, 参数:', params)
  return request({
    url: '/articles/list',
    method: 'get',
    params
  }).then(response => {
    console.log('[API] 获取文章列表成功:', response)
    return response
  }).catch(error => {
    console.error('[API] 获取文章列表失败:', error.message)
    throw error
  })
}

/**
 * 获取文章详情
 *
 * @param {number|string} id - 文章ID
 * @returns {Promise<Object>} 文章详情
 */
export function getArticle(id) {
  console.log('[API] 开始获取文章详情, id:', id)
  return request({
    url: `/articles/${id}`,
    method: 'get'
  }).then(response => {
    console.log('[API] 获取文章详情成功:', response)
    return response
  }).catch(error => {
    console.error('[API] 获取文章详情失败:', error.message)
    throw error
  })
}

/**
 * 获取轮播图文章
 * 返回标记为轮播的启用文章
 *
 * @returns {Promise<Array>} 轮播图文章列表
 */
export function getCarousel() {
  console.log('[API] 开始获取轮播图文章')
  return request({
    url: '/articles/carousel',
    method: 'get'
  }).then(response => {
    console.log('[API] 获取轮播图成功:', response)
    return response
  }).catch(error => {
    console.error('[API] 获取轮播图失败:', error.message, error)
    throw error
  })
}

/**
 * 获取文章分类列表
 *
 * @returns {Promise<Array>} 分类列表
 */
export function getCategories() {
  console.log('[API] 开始获取文章分类')
  return request({
    url: '/articles/categories',
    method: 'get'
  }).then(response => {
    console.log('[API] 获取分类成功:', response)
    return response
  }).catch(error => {
    console.error('[API] 获取分类失败:', error.message)
    throw error
  })
}

/**
 * 搜索文章
 *
 * @param {string} keyword - 搜索关键词
 * @param {Object} params - 其他查询参数
 * @returns {Promise<Object>} 搜索结果
 */
export function searchArticles(keyword, params = {}) {
  console.log('[API] 开始搜索文章, 关键词:', keyword)
  return request({
    url: '/articles/search',
    method: 'get',
    params: {
      keyword,
      ...params
    }
  }).then(response => {
    console.log('[API] 搜索文章成功:', response)
    return response
  }).catch(error => {
    console.error('[API] 搜索文章失败:', error.message)
    throw error
  })
}

/**
 * 获取推荐阅读文章
 *
 * @param {number} limit - 数量限制
 * @returns {Promise<Array>} 推荐文章列表
 */
export function getRecommendedArticles(limit = 5) {
  console.log('[API] 开始获取推荐文章, 数量:', limit)
  return request({
    url: '/articles/recommended',
    method: 'get',
    params: { limit }
  }).then(response => {
    console.log('[API] 获取推荐文章成功:', response)
    return response
  }).catch(error => {
    console.error('[API] 获取推荐文章失败:', error.message)
    throw error
  })
}
