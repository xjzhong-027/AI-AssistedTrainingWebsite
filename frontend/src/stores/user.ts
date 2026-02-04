import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types/user'
import { storage } from '@/utils/storage'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  // 初始化用户信息
  const initUser = () => {
    const stored = storage.get<User>('userInfo')
    const storedToken = localStorage.getItem('token')
    const storedRefreshToken = localStorage.getItem('refreshToken')
    
    if (stored) {
      userInfo.value = stored
    }
    if (storedToken) {
      token.value = storedToken
    }
    if (storedRefreshToken) {
      refreshToken.value = storedRefreshToken
    }
  }

  // 设置用户信息和 Token
  const setUser = (user: User) => {
    userInfo.value = user
    storage.set('userInfo', user)
  }

  // 设置 Token
  const setToken = (access: string, refresh: string) => {
    if (!access || !refresh) {
      console.error('Token 不能为空')
      return
    }
    token.value = access
    refreshToken.value = refresh
    localStorage.setItem('token', access)
    localStorage.setItem('refreshToken', refresh)
  }

  // 清除用户信息和 Token
  const clearUser = () => {
    userInfo.value = null
    token.value = null
    refreshToken.value = null
    storage.remove('userInfo')
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  // 获取用户角色
  const getUserRole = (): string | null => {
    return userInfo.value?.role || null
  }

  // 检查是否为管理员
  const isAdmin = (): boolean => {
    return userInfo.value?.role === 'ADMIN'
  }

  // 检查是否为教师
  const isTeacher = (): boolean => {
    return userInfo.value?.role === 'TEACHER' || isAdmin()
  }

  // 检查是否为学生
  const isStudent = (): boolean => {
    return userInfo.value?.role === 'STUDENT'
  }

  // 初始化
  initUser()

  // 登出：清除状态，调用方负责跳转登录页
  const logout = () => {
    clearUser()
  }

  return {
    userInfo,
    token,
    refreshToken,
    setUser,
    setToken,
    clearUser,
    logout,
    getUserRole,
    isAdmin,
    isTeacher,
    isStudent
  }
})

