import request from '@/utils/request'

/**
 * 学生类型（根据后端API响应）
 */
export interface Student {
  id: number
  name: string
  student_id?: string
  email?: string
  phone?: string
  class_id?: number
  class_name?: string
}

/**
 * 获取所有学生列表
 */
export function getStudents(): Promise<Student[]> {
  return request.get('/users/students/')
}

/**
 * 根据ID获取学生详情
 */
export function getStudentById(id: number): Promise<Student> {
  return request.get(`/users/students/${id}/`)
}

/**
 * 搜索学生
 */
export function searchStudents(keyword: string): Promise<Student[]> {
  return request.get('/users/students/', { params: { keyword } })
}

/**
 * 获取班级学生列表
 */
export function getClassStudents(classId: number): Promise<Student[]> {
  return request.get(`/users/classes/${classId}/students/`)
}
