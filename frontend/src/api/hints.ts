import request from '@/utils/request'

/** 请求提示参数（与后端 API 一致） */
export interface HintRequestParams {
  sub_question_id: number
  level: 1 | 2 | 3
  student_answer?: string
  transcript?: string
  context?: { practice_id?: number; page_id?: number }
}

/** 请求提示返回（与后端 Result.success data 一致） */
export interface HintRequestResponse {
  content: string
  level: number
  log_id: number
  request_time: string
}

/** 提示日志项（含当时 AI 回复内容） */
export interface HintLogItem {
  id: number
  sub_question_id: number
  level: number
  hint_content: string
  request_time: string
}

export const hintsApi = {
  /** 请求分级提示 */
  request: (params: HintRequestParams) =>
    request.post<HintRequestResponse>('/hints/request/', params),

  /** 查询本人提示请求日志 */
  log: (params?: { sub_question_id?: number; limit?: number }) =>
    request.get<HintLogItem[]>('/hints/log/', { params }),
}
