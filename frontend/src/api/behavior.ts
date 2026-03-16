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

// 学生周度行为评分（BSA-IFM）
export interface StudentBehaviorScore {
  student_id: number
  period: { start: string; end: string }
  dimensions: { S_A: number; S_B: number; S_C: number; S_D: number }
  F_score: number
  P_score: number
  growth_bonus: number
  feedback: string
}

// 班级行为排名项
export interface ClassRankingItem {
  student_id: number
  name: string
  F_score: number
  rank: number
}

// 获取当前学生的行为统计概览
export function getStudentBehaviorSummary(): Promise<StudentBehaviorSummary> {
  return request.get('/behavior/student/summary/')
}

// 获取当前学生的周度行为评分
export function getStudentBehaviorScore(periodStart?: string): Promise<StudentBehaviorScore | null> {
  const params = periodStart ? { period_start: periodStart } : {}
  return request.get('/behavior/student/score/', { params })
}

// 获取班级行为评分排名
export function getClassBehaviorRanking(classId: number, periodStart?: string): Promise<{
  class_id: number
  period_start: string
  ranking: ClassRankingItem[]
}> {
  const params: Record<string, string | number> = { class_id: classId }
  if (periodStart) params.period_start = periodStart
  return request.get('/behavior/class/ranking/', { params })
}

// 教师端触发周度行为评分计算
export function calculateWeeklyScores(periodStart?: string): Promise<{
  period_start: string
  period_end: string
  updated_count: number
}> {
  return request.post('/behavior/calculate-weekly/', { period_start: periodStart })
}

