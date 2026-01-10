/**
 * 考试相关类型定义
 */

export type ExamStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'ENDED'

export interface Exam {
  id: number
  title: string
  description?: string
  creatorId: number
  startTime: string
  endTime: string
  duration: number
  status: ExamStatus
  createdAt: string
  updatedAt: string
}

export interface ExamCreateDTO {
  title: string
  description?: string
  creatorId: number
  startTime: string
  endTime: string
  duration: number
}

export interface ExamUpdateDTO {
  title?: string
  description?: string
  startTime?: string
  endTime?: string
  duration?: number
}

