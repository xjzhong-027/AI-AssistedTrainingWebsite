/**
 * AI窗口组件类型定义
 */

export type MessageRole = 'user' | 'assistant' | 'system'

export interface Message {
  id: number | string
  role: MessageRole
  content: string
  timestamp: string
  type?: 'text' | 'grade'
}

export interface GradeResult {
  sub_question_id: number
  score: number
  max_score: number
  feedback: string
  suggestions?: string[]
  timestamp: string
}

export type WindowState = 'open' | 'minimize' | 'close'
