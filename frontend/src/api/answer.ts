import request from '@/utils/request'
import type { ExamRecord, Answer, AnswerSubmitDTO, AnswerBatchSubmitDTO } from '@/types/answer'

/**
 * 参加考试
 */
export function participateExam(examId: number, studentId: number): Promise<ExamRecord> {
  return request.post(`/exams/${examId}/participate`, { studentId })
}

/**
 * 提交单个答案
 */
export function submitAnswer(data: AnswerSubmitDTO): Promise<Answer> {
  return request.post('/answers', data)
}

/**
 * 批量提交答案
 */
export function batchSubmitAnswers(data: AnswerBatchSubmitDTO): Promise<Answer[]> {
  return request.post('/answers/batch', data)
}

/**
 * 提交考试
 */
export function submitExam(examRecordId: number): Promise<ExamRecord> {
  return request.post(`/exam-records/${examRecordId}/submit`)
}

/**
 * 根据考试记录ID获取答案列表
 */
export function getAnswersByExamRecordId(examRecordId: number): Promise<Answer[]> {
  return request.get('/answers', { params: { examRecordId } })
}

/**
 * 根据ID获取答案
 */
export function getAnswerById(id: number): Promise<Answer> {
  return request.get(`/answers/${id}`)
}

/**
 * 获取考试记录
 */
export function getExamRecordById(examRecordId: number): Promise<ExamRecord> {
  return request.get(`/exam-records/${examRecordId}`)
}

