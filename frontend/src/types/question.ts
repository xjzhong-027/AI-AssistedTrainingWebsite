/**
 * 题目相关类型定义
 */

export type QuestionType = 'SINGLE_CHOICE' | 'MULTIPLE_CHOICE' | 'TRUE_FALSE' | 'SHORT_ANSWER'

export interface Question {
  id: number
  examId: number
  type: QuestionType
  content: string
  options?: string // JSON格式字符串
  correctAnswer?: string
  score: number
  createdAt: string
  updatedAt: string
}

export interface QuestionCreateDTO {
  examId: number
  type: QuestionType
  content: string
  options?: string
  correctAnswer?: string
  score: number
}

export interface QuestionUpdateDTO {
  content?: string
  options?: string
  correctAnswer?: string
  score?: number
}

