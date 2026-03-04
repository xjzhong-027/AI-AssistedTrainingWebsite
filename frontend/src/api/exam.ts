import request from '@/utils/request'
import type { Exam, ExamCreateDTO, ExamUpdateDTO } from '@/types/exam'

/**
 * 创建考试
 */
export function createExam(data: ExamCreateDTO): Promise<Exam> {
  return request.post('/exams', data)
}

/**
 * 获取考试/练习列表（根据后端API）
 * @param studentId 可选，学生ID
 * @param unitType 可选，'exam' 或 'practice'
 */
export function getAllExams(studentId?: number, unitType?: 'exam' | 'practice'): Promise<Exam[]> {
  const params: any = {}
  if (studentId) params.student_id = studentId
  if (unitType) params.unit_type = unitType
  return request.get('/exams/', { params })
}

/**
 * 根据ID获取考试详情
 */
export function getExamById(id: number): Promise<Exam> {
  return request.get(`/exams/${id}/`)
}

/**
 * 开始考试/练习
 * @param unitId 单元ID（注意：这里传入的是unit_id，不是exam_id）
 */
export function startExam(unitId: number): Promise<Exam> {
  return request.post(`/exams/${unitId}/start/`)
}

/**
 * 获取考试页面
 * @param examId 考试记录ID
 * @param pageOrder 页面顺序（不是页面ID）
 */
export function getExamPage(examId: number, pageOrder: number): Promise<any> {
  return request.get(`/exams/${examId}/pages/${pageOrder}/`)
}

/**
 * 保存答案
 * @param pageRecordId 页面记录ID（不是页面ID）
 * @param answers 答案数组
 * @param remainingTime 剩余时间（秒），可选，用于倒计时
 */
export function saveAnswers(
  pageRecordId: number,
  answers: Array<{ sub_question_id: number; text: string; index?: number; type?: string }>,
  remainingTime?: number
): Promise<any> {
  const body: { answers: typeof answers; remaining_time?: number } = { answers }
  if (remainingTime !== undefined && remainingTime !== null) {
    body.remaining_time = remainingTime
  }
  return request.post(`/exams/pages/${pageRecordId}/answers/`, body)
}

/**
 * 提交考试/练习
 * @param unitId 单元 ID（任务包/考试 ID，即开始时的 unit_id），不是 exam_record_id
 */
export function submitExam(unitId: number): Promise<Exam> {
  return request.post(`/exams/${unitId}/submit/`)
}

/**
 * 获取考试结果
 */
export function getExamResult(examId: number): Promise<any> {
  return request.get(`/exams/${examId}/result/`)
}

/**
 * 根据创建者获取考试列表（兼容旧接口）
 */
export function getExamsByCreatorId(creatorId: number): Promise<Exam[]> {
  return getAllExams()
}

/**
 * 根据状态获取考试列表（兼容旧接口）
 */
export function getExamsByStatus(status: string): Promise<Exam[]> {
  return getAllExams()
}

/**
 * 更新考试信息
 */
export function updateExam(id: number, data: ExamUpdateDTO): Promise<Exam> {
  return request.put(`/exams/${id}`, data)
}

/**
 * 更新考试状态
 */
export function updateExamStatus(id: number, status: string): Promise<Exam> {
  return request.put(`/exams/${id}/status`, { status })
}

/**
 * 删除考试
 */
export function deleteExam(id: number): Promise<void> {
  return request.delete(`/exams/${id}`)
}

/**
 * 更新媒体播放记录
 * @param examId 考试记录ID（注意：这里传入的是exam_record_id，不是unit_id）
 * @param data 播放记录数据
 */
export function updateMediaPlayRecord(
  examId: number,
  data: {
    main_question_id: number
    media_material_id?: number
    play_count?: number
    last_pause_time?: number
  }
): Promise<any> {
  return request.post(`/exams/${examId}/media-play/`, data)
}
