import request from '@/utils/request'

/**
 * 聊天请求参数
 */
export interface ChatRequest {
  message: string
  context?: {
    practice_id?: number
    page_id?: number
    sub_question_id?: number
  }
}

/**
 * 聊天响应（对接 /api/v1/scoring/chat/）
 */
export interface ChatResponse {
  reply: string
  timestamp: string
}

/**
 * 发送消息并获取 AI 回复（火山引擎）
 * POST /api/v1/scoring/chat/
 */
export function sendChatMessage(data: ChatRequest): Promise<ChatResponse> {
  return request.post<ChatResponse>('/scoring/chat/', {
    message: data.message,
    context: data.context
  })
}
