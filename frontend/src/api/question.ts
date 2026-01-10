import request from '@/utils/request'
import type { Question, QuestionCreateDTO, QuestionUpdateDTO } from '@/types/question'

/**
 * 创建题目
 */
export function createQuestion(data: QuestionCreateDTO): Promise<Question> {
  return request.post('/questions', data)
}

/**
 * 获取所有题目列表
 */
export function getAllQuestions(): Promise<Question[]> {
  return request.get('/questions')
}

/**
 * 根据ID获取题目详情
 */
export function getQuestionById(id: number): Promise<Question> {
  return request.get(`/questions/${id}`)
}

/**
 * 根据考试ID获取题目列表
 */
export function getQuestionsByExamId(examId: number): Promise<Question[]> {
  return request.get(`/questions/exam/${examId}`)
}

/**
 * 根据考试ID和类型获取题目列表
 */
export function getQuestionsByExamIdAndType(
  examId: number,
  type: string
): Promise<Question[]> {
  return request.get(`/questions/exam/${examId}/type/${type}`)
}

/**
 * 更新题目
 */
export function updateQuestion(id: number, data: QuestionUpdateDTO): Promise<Question> {
  return request.put(`/questions/${id}`, data)
}

/**
 * 删除题目
 */
export function deleteQuestion(id: number): Promise<void> {
  return request.delete(`/questions/${id}`)
}

