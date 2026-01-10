/**
 * 通用类型定义
 */

/**
 * 统一响应格式
 */
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

/**
 * 分页参数
 */
export interface PageParams {
  page?: number
  pageSize?: number
}

/**
 * 分页响应
 */
export interface PageResponse<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

