import request from '@/utils/request'

export interface QuestionGenerationRequest {
  material_id: number
  question_type:
    | 'choice'
    | 'matching'
    | 'fill-blank'
    | 'fill-blank-transcript'
    | 'fill-blank-summary'
    | 'comprehension'
  difficulty: 'easy' | 'medium' | 'hard'
  count: number
  focus_points?: string[]
  additional_requirements?: string
}

export interface SubQuestion {
  question_text: string
  options?: Record<string, string>
  correct_answer?: string
  answer?: string
  left_items?: Record<string, string>
  right_items?: Record<string, string>
  correct_matching?: Record<string, string>
  analysis: string
  score: number
}

export interface GeneratedQuestion {
  main_question: {
    question_text: string
    question_type: string
    maximum_play?: number
  }
  sub_questions: SubQuestion[]
}

export interface TaskStatusResponse {
  task_id: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  message: string
  questions: GeneratedQuestion[]
  suggestions?: string[]
  conversation_history?: Array<{
    role: string
    content: string
  }>
}

export interface QuestionChatRequest {
  material_id: number
  message: string
  current_questions: GeneratedQuestion[]
  conversation_history: Array<{
    role: string
    content: string
  }>
}

export interface QuestionChatResponse {
  questions: GeneratedQuestion[]
  conversation_history: Array<{
    role: string
    content: string
  }>
}

export interface QuestionApplyRequest {
  material_id: number
  questions: GeneratedQuestion[]
}

export interface QuestionApplyResponse {
  applied_questions: Array<{
    main_question_id: number
    sub_question_ids: number[]
  }>
  total_count: number
}

export const questionGenerationApi = {
  generate: (data: QuestionGenerationRequest) => {
    return request.post<{ task_id: number; status: string; message: string }>(
      '/question-generation/generate/',
      data,
      { timeout: 30000 }
    )
  },

  getStatus: (taskId: number) => {
    return request.get<TaskStatusResponse>(`/question-generation/status/${taskId}/`)
  },

  chat: (data: QuestionChatRequest) => {
    return request.post<QuestionChatResponse>('/question-generation/chat/', data, {
      timeout: 120000
    })
  },

  apply: (data: QuestionApplyRequest) => {
    return request.post<QuestionApplyResponse>('/question-generation/apply/', data)
  }
}

export function useQuestionGeneration() {
  const generateQuestions = async (
    req: QuestionGenerationRequest,
    onProgress?: (status: string, message: string) => void,
    pollInterval: number = 2000,
    maxPolls: number = 150
  ): Promise<TaskStatusResponse> => {
    const response = await questionGenerationApi.generate(req)
    const taskId = response.task_id

    let polls = 0
    while (polls < maxPolls) {
      const status = await questionGenerationApi.getStatus(taskId)

      if (onProgress) {
        onProgress(status.status, status.message)
      }

      if (status.status === 'completed') {
        return status
      }

      if (status.status === 'failed') {
        throw new Error(status.message || '题目生成失败')
      }

      await new Promise((resolve) => setTimeout(resolve, pollInterval))
      polls++
    }

    throw new Error('题目生成超时，请稍后重试')
  }

  return {
    generateQuestions,
    chatRevise: questionGenerationApi.chat,
    applyQuestions: questionGenerationApi.apply
  }
}

