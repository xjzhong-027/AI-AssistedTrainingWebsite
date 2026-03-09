import request from '@/utils/request'

// 学生行为统计概览
export interface StudentBehaviorSummary {
  total_exams: number
  completed_exams: number
  total_practices: number
  completed_practices: number
  total_media_plays: number
  hint_count: number
  login_count_last_7_days: number
}

// 获取当前学生的行为统计概览
export function getStudentBehaviorSummary(): Promise<StudentBehaviorSummary> {
  return request.get('/behavior/student/summary/')
}

