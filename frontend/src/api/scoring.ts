import request from '@/utils/request'

export interface AIScoringRequest {
  sub_question_id: number
  student_answer: string
  transcript?: string
}

export interface AIScoringResponse {
  score_id: number
  content_accuracy: number
  language_expression: number
  completeness: number
  logical_coherence: number
  total_score: number
  feedback: string
  suggestions: string[]
  grammar_errors: Array<{
    error: string
    correction: string
    location: string
  }>
  vocabulary_suggestions: Array<{
    word: string
    better: string
    reason: string
  }>
  score_time: string
}

export interface AIExplanationRequest {
  sub_question_id: number
  transcript?: string
}

export interface AIExplanationResponse {
  explanation_id: number
  correct_answer_explanation: string
  distractor_analysis: Array<{
    option: string
    reason: string
  }>
  key_points: string[]
  listening_tips: string
  related_knowledge: string
  generate_time: string
}

export interface AIScoreHistoryResponse {
  score_id: number
  sub_question_id: number
  question_text: string
  total_score: number
  feedback: string
  score_time: string
}

export interface AIConversationRequest {
  role: 'user' | 'assistant' | 'system'
  content: string
  context?: Record<string, any>
}

export interface AIConversationResponse {
  id: number
  role: string
  content: string
  message_time: string
}

export const scoringApi = {
  subjective: (data: AIScoringRequest) => {
    return request.post<AIScoringResponse>('/scoring/subjective/', data, { timeout: 60000 })
  },

  explanation: (data: AIExplanationRequest) => {
    return request.post<AIExplanationResponse>('/scoring/explanation/', data)
  },

  history: (params?: { sub_question_id?: number }) => {
    return request.get<AIScoreHistoryResponse[]>('/scoring/history/', { params })
  },

  conversation: {
    get: (params?: { context_id?: string }) => {
      return request.get<AIConversationResponse[]>('/scoring/conversation/', { params })
    },
    post: (data: AIConversationRequest) => {
      return request.post<AIConversationResponse>('/scoring/conversation/', data)
    }
  }
}
