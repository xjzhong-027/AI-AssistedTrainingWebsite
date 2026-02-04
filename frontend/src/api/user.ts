import request from '@/utils/request'
import type { User, UserRegisterDTO, UserUpdateDTO } from '@/types/user'

/**
 * 登录接口响应类型
 */
export interface LoginResponse {
  access: string
  refresh: string
  username: string
  role: string
  user_id: number
}

/**
 * 登录请求类型
 */
export interface LoginRequest {
  username: string
  password: string
  role: 'student' | 'teacher' | 'admin'
}

/**
 * 用户登录
 */
export function login(data: LoginRequest): Promise<LoginResponse> {
  return request.post('/auth/login/', data)
}

/**
 * 刷新 Token
 */
export function refreshToken(refresh: string): Promise<{ access: string }> {
  return request.post('/auth/token/refresh/', { refresh })
}

/**
 * 用户登出
 */
export function logout(): Promise<void> {
  return request.post('/auth/logout/')
}

/**
 * 当前用户信息响应类型（后端返回的格式）
 */
export interface CurrentUserResponse {
  username: string
  role: string
  user_id: number
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser(): Promise<CurrentUserResponse> {
  return request.get('/auth/user/')
}

/**
 * 用户注册
 */
export function register(data: UserRegisterDTO): Promise<User> {
  return request.post('/users/register', data)
}

/**
 * 根据ID获取用户信息
 * 根据用户角色自动选择正确的端点
 */
export function getUserById(id: number, role?: string): Promise<User> {
  // 如果提供了角色，使用对应的端点
  if (role === 'STUDENT' || role === 'student') {
    return request.get(`/users/students/${id}/`)
  } else if (role === 'TEACHER' || role === 'teacher') {
    return request.get(`/users/teachers/${id}/`)
  }
  
  // 默认尝试学生端点（因为大多数情况下是学生）
  return request.get(`/users/students/${id}/`)
}

/**
 * 根据用户名获取用户信息
 */
export function getUserByUsername(username: string): Promise<User> {
  return request.get(`/users/username/${username}`)
}

/**
 * 更新用户信息
 */
export function updateUser(id: number, data: UserUpdateDTO): Promise<User> {
  return request.put(`/users/${id}`, data)
}

/**
 * 获取所有用户列表
 */
export function getAllUsers(): Promise<User[]> {
  return request.get('/users')
}

/**
 * 删除用户
 */
export function deleteUser(id: number): Promise<void> {
  return request.delete(`/users/${id}`)
}

/**
 * 更新学生信息
 */
export function updateStudentProfile(id: number, data: { name?: string; seat_number?: string }): Promise<User> {
  return request.put(`/users/students/${id}/update/`, data)
}

/**
 * 更新教师信息
 */
export function updateTeacherProfile(id: number, data: { name?: string }): Promise<User> {
  return request.put(`/users/teachers/${id}/update/`, data)
}

/**
 * 修改密码
 */
export function changePassword(oldPassword: string, newPassword: string): Promise<void> {
  return request.post('/auth/change-password/', {
    old_password: oldPassword,
    new_password: newPassword
  })
}

/**
 * 课程类型
 */
export interface Course {
  id: number
  year: number
  grade: string
  semester: string
}

/**
 * 获取课程列表
 */
export function getCourseList(): Promise<Course[]> {
  return request.get('/users/courses/')
}

/**
 * 创建课程
 */
export function createCourse(data: { year: number; grade: string; semester: string }): Promise<Course> {
  return request.post('/users/courses/create/', data)
}

/**
 * 教师简要类型（用于下拉等）
 */
export interface TeacherBrief {
  id: number
  username: string
  name: string
}

/**
 * 班级类型
 */
export interface Class {
  id: number
  class_name: string
  teacher_id?: number
  teacher_name?: string
  course_id?: number
  course_name?: string
  start_date?: string
  week?: number
  start_time?: string
  end_time?: string
}

/**
 * 获取教师列表
 */
export function getTeacherList(): Promise<TeacherBrief[]> {
  return request.get('/users/teachers/')
}

/**
 * 获取所有班级列表
 */
export function getAllClasses(teacherId?: number): Promise<Class[]> {
  const params = teacherId ? { teacher_id: teacherId } : {}
  return request.get('/users/classes/', { params })
}

/**
 * 根据ID获取班级详情
 */
export function getClassById(id: number): Promise<Class> {
  return request.get(`/users/classes/${id}/`)
}

/**
 * 获取班级的学生列表
 */
export function getClassStudents(classId: number): Promise<User[]> {
  return request.get(`/users/classes/${classId}/students/`)
}

/**
 * 创建班级
 */
export function createClass(data: {
  class_name: string
  course: number
  teacher: number
  start_date?: string
  week: number
  start_time: string
  end_time: string
}): Promise<Class> {
  return request.post('/users/classes/create/', data)
}

/**
 * 更新班级
 */
export function updateClass(
  classId: number,
  data: Partial<{
    class_name: string
    course: number
    teacher: number
    start_date: string
    week: number
    start_time: string
    end_time: string
  }>
): Promise<Class> {
  return request.put(`/users/classes/${classId}/update/`, data)
}
