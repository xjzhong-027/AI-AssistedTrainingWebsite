import request from '@/utils/request'

/**
 * 查询考勤记录
 * @param classId 班级ID（必填）
 * @param week 周次（必填）
 */
export function queryAttendance(classId: number, week: number): Promise<any[]> {
  return request.get('/query/attendance/', {
    params: { class_id: classId, week }
  })
}

/**
 * 查询学习记录
 * @param params 查询参数
 */
export function queryLearningRecords(params?: {
  student_id?: number
  class_id?: number
  unit_type?: 'exam' | 'practice'
}): Promise<any[]> {
  return request.get('/query/learning-records/', { params })
}

/**
 * 获取班级统计数据
 * @param classId 班级ID
 */
export function getClassStatistics(classId: number): Promise<any> {
  return request.get(`/query/statistics/class/${classId}/`)
}

/**
 * 获取单元统计数据
 * @param unitId 单元ID
 * @param classId 班级ID（可选）
 */
export function getUnitStatistics(unitId: number, classId?: number): Promise<any> {
  const params = classId ? { class_id: classId } : undefined
  return request.get(`/query/statistics/unit/${unitId}/`, { params })
}

/**
 * 获取逾期扣分规则列表
 */
export function getOverdueRules(): Promise<any[]> {
  return request.get('/query/overdue-rules/')
}

/**
 * 获取逾期扣分规则详情
 * @param ruleId 规则ID
 */
export function getOverdueRuleDetail(ruleId: number): Promise<any> {
  return request.get(`/query/overdue-rules/${ruleId}/`)
}
