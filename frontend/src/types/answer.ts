/**
 * 答题相关类型定义
 */

export interface ExamRecord {
  id: number
  examId: number
  studentId: number
  startTime: string
  submitTime?: string
  status: 'IN_PROGRESS' | 'SUBMITTED'
  createdAt: string
  updatedAt: string
}

export interface Answer {
  id: number
  examRecordId: number
  questionId: number
  answerContent: string
  isCorrect?: boolean
  score?: number
  createdAt: string
  updatedAt: string
}

export interface AnswerSubmitDTO {
  examRecordId: number
  questionId: number
  answerContent: string
}

export interface AnswerBatchSubmitDTO {
  examRecordId: number
  answers: AnswerSubmitDTO[]
}

