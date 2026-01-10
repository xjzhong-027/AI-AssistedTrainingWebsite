/**
 * 用户相关类型定义
 */

export type UserRole = 'STUDENT' | 'TEACHER' | 'ADMIN'

export interface User {
  id: number
  username: string
  realName: string
  email: string
  role: UserRole
  createdAt: string
  updatedAt: string
}

export interface UserRegisterDTO {
  username: string
  password: string
  realName: string
  email: string
  role: UserRole
}

export interface UserUpdateDTO {
  realName?: string
  email?: string
}

