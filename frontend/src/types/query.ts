/**
 * 考勤记录
 */
export interface AttendanceRecord {
  id: number
  student_id: number
  student_name: string
  class_id: number
  week: number
  attendance_status: 'present' | 'absent' | 'late' | 'leave'
  created_at: string
}

/**
 * 学习记录
 */
export interface LearningRecord {
  id: number
  student_id: number
  student_name: string
  unit_id: number
  unit_name: string
  unit_type: 'exam' | 'practice'
  score: number
  total_score: number
  completion_time: string
  created_at: string
}

/**
 * 班级统计数据
 */
export interface ClassStatistics {
  class_id: number
  class_name: string
  total_students: number
  completed_students: number
  completion_rate: number
  average_score: number
  exam_count: number
  practice_count: number
}

/**
 * 单元统计数据
 */
export interface UnitStatistics {
  unit_id: number
  unit_name: string
  total_students: number
  completed_students: number
  completion_rate: number
  average_score: number
  highest_score: number
  lowest_score: number
  class_id?: number
  class_name?: string
}

/**
 * 逾期扣分规则
 */
export interface OverdueRule {
  id: number
  name: string
  description: string
  is_default: boolean
  periods: OverduePeriod[]
  created_at: string
  updated_at: string
}

/**
 * 逾期扣分时间段
 */
export interface OverduePeriod {
  id: number
  rule_id: number
  start_hours: number
  end_hours: number
  deduction_rate: number
  description: string
}
