import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

// 统一响应格式
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: '/api/v1', // 对接 Django API v1
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json;charset=UTF-8'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 添加 JWT Token 认证
    const token = localStorage.getItem('token') || localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const res = response.data

    // 如果返回的状态码为200或201，说明接口请求成功
    if (res.code === 200 || res.code === 201) {
      return res.data
    } else {
      // 否则说明有错误，显示错误信息
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  (error) => {
    console.error('响应错误', error)
    let message = '网络错误，请稍后重试'

    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          // 清除 token（与请求头读取来源一致）
          localStorage.removeItem('token')
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '资源不存在'
          break
        case 500:
          message = '服务器错误，请稍后重试'
          break
        default:
          message = error.response.data?.message || '请求失败'
      }
    } else if (error.request) {
      message = '网络连接失败，请检查网络'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default service

