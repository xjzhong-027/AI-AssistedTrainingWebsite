/**
 * 成绩相关类型定义
 */

export interface Score {
  id: number
  examRecordId: number
  totalScore: number
  autoScore: number
  manualScore?: number
  isGraded: boolean
  createdAt: string
  updatedAt: string
}

