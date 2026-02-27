import request from '@/utils/request'

/**
 * 单元（练习/考试）类型
 */
export interface Unit {
  id: number
  unit_name: string
  unit_type: 'exam' | 'practice'
  class_id: number
  media_material_id: number
  pages: Page[]
}

/**
 * 页面类型
 */
export interface Page {
  id: number
  unit_id: number
  page_order: number
  time_limit: number
}

/**
 * 考试记录类型（根据后端API响应）
 */
export interface ExamRecord {
  id: number
  student_id: number
  unit_id: number
  unit_name?: string
  unit_type?: 'exam' | 'practice'
  status: string
  start_time: string
  submit_time?: string
  total_score?: number
}

/**
 * 学生练习成绩类型（从考试记录中提取）
 */
export interface PracticeScore {
  id: number
  practice: string
  totalScore: number
  startedAt: string
  finishedAt?: string
}

/**
 * 获取所有练习列表（根据后端API，练习是unit_type=practice的单元）
 */
export function getAllPractices(classId?: number): Promise<Unit[]> {
  const params = classId ? { class_id: classId, unit_type: 'practice' } : { unit_type: 'practice' }
  return request.get('/content/units/', { params })
}

/**
 * 根据ID获取练习详情
 */
export function getPracticeById(id: number): Promise<Unit> {
  return request.get(`/content/units/${id}/`)
}

/**
 * 开始练习（使用考试API，因为练习和考试使用相同的流程）
 */
export function startPractice(unitId: number): Promise<ExamRecord> {
  return request.post(`/exams/${unitId}/start/`)
}

/** 后端返回的原始记录格式（与 Exam API 序列化器一致） */
interface RawExamRecord {
  id: number
  unit_id: number
  unit_name?: string
  unit_type?: string
  started_at?: string
  finished_at?: string
  score?: number
  submitted?: boolean
  [key: string]: unknown
}

function toExamRecord(raw: RawExamRecord): ExamRecord {
  return {
    id: raw.id,
    student_id: 0,
    unit_id: raw.unit_id,
    unit_name: raw.unit_name,
    unit_type: raw.unit_type as 'exam' | 'practice',
    status: raw.submitted ? 'completed' : 'in-progress',
    start_time: raw.started_at || '',
    submit_time: raw.finished_at,
    total_score: raw.score
  }
}

/**
 * 获取学生的练习记录（从考试记录中筛选unit_type=practice）
 */
export function getStudentPracticeRecords(studentId?: number): Promise<ExamRecord[]> {
  const params = studentId ? { student_id: studentId, unit_type: 'practice' } : { unit_type: 'practice' }
  return request.get<RawExamRecord[]>('/exams/', { params }).then(rows => (rows || []).map(toExamRecord))
}

/**
 * 获取学生的练习成绩（从考试记录中提取并转换格式）
 */
export function getStudentPracticeScores(studentId?: number): Promise<PracticeScore[]> {
  return getStudentPracticeRecords(studentId).then(records => {
    return records.map(record => ({
      id: record.id,
      practice: record.unit_name || `练习 ${record.unit_id}`, // 从记录中获取单元名称
      totalScore: record.total_score || 0,
      startedAt: record.start_time, // 使用start_time字段
      finishedAt: record.submit_time // 使用submit_time字段
    }))
  })
}

