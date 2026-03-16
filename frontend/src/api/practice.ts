import axios from 'axios'
import request from '@/utils/request'

/**
 * 单元（练习/考试）类型
 */
export interface Unit {
  id: number
  unit_name: string
  unit_type: 'exam' | 'practice'
  class_id: number
  media_material_id: number
  pages: Page[]
}

/**
 * 页面类型
 */
export interface Page {
  id: number
  unit_id: number
  page_order: number
  time_limit: number
}

/**
 * 考试记录类型（根据后端API响应）
 */
export interface ExamRecord {
  id: number
  student_id: number
  unit_id: number
  unit_name?: string
  unit_type?: 'exam' | 'practice'
  status: string
  start_time: string
  submit_time?: string
  total_score?: number
}

/**
 * 学生练习成绩类型（从考试记录中提取）
 */
export interface PracticeScore {
  id: number
  practice: string
  totalScore: number
  startedAt: string
  finishedAt?: string
}

/**
 * 练习详情中的媒体信息
 */
export interface PracticeMedia {
  id: number
  url: string
  is_video: boolean
  transcript: string
}

/**
 * 练习详情中的题目信息
 */
export interface PracticeDetailQuestion {
  id: number
  question_text: string
  question_type: string
  options?: string[]
  userAnswer: string
  correctAnswer: string
  score: number | string
}

/**
 * 练习详情接口返回结构（对接 stu_practice.practice_page 的 JSON 模式）
 */
export interface PracticeDetailResponse {
  practice: {
    id: number
    title: string
    type: string
  }
  media: PracticeMedia | null
  questions: PracticeDetailQuestion[]
  answers?: Record<string | number, string>
  is_last_page?: boolean
  practice_record_id?: number
  started_at?: string | null
  ended_at?: string | null
  MEDIA_URL?: string
  play_records?: Record<string | number, number>
  remaining_time?: number | null
  blank_data?: Record<string, unknown>
  correction_data?: Record<string, unknown>
  page_submitted?: boolean
  can_modify?: boolean
  graded_answers?: Record<string | number, string>
  scores?: Record<string | number, number | string>
}

/**
 * AI 学习建议结构（供前端展示用）
 */
export interface PracticeRecommendationMaterial {
  type: 'video' | 'article'
  title: string
  url: string
}

export interface PracticeRecommendation {
  core_theme: string
  theme_motivation: string
  key_vocabulary: string[]
  materials: PracticeRecommendationMaterial[]
}

export interface PracticeRecommendationRequest {
  practice_title: string
  transcript: string
}

/**
 * 获取所有练习列表（根据后端API，练习是unit_type=practice的单元）
 */
export function getAllPractices(classId?: number): Promise<Unit[]> {
  const params = classId ? { class_id: classId, unit_type: 'practice' } : { unit_type: 'practice' }
  return request.get('/content/units/', { params })
}

/**
 * 根据ID获取练习详情
 */
export function getPracticeById(id: number): Promise<Unit> {
  return request.get(`/content/units/${id}/`)
}

/**
 * 开始练习（使用考试API，因为练习和考试使用相同的流程）
 */
export function startPractice(unitId: number): Promise<ExamRecord> {
  return request.post(`/exams/${unitId}/start/`)
}

/** 后端返回的原始记录格式（与 Exam API 序列化器一致） */
interface RawExamRecord {
  id: number
  unit_id: number
  unit_name?: string
  unit_type?: string
  started_at?: string
  finished_at?: string
  score?: number
  submitted?: boolean
  [key: string]: unknown
}

function toExamRecord(raw: RawExamRecord): ExamRecord {
  return {
    id: raw.id,
    student_id: 0,
    unit_id: raw.unit_id,
    unit_name: raw.unit_name,
    unit_type: raw.unit_type as 'exam' | 'practice',
    status: raw.submitted ? 'completed' : 'in-progress',
    start_time: raw.started_at || '',
    submit_time: raw.finished_at,
    total_score: raw.score
  }
}

/**
 * 获取学生的练习记录（从考试记录中筛选unit_type=practice）
 */
export function getStudentPracticeRecords(studentId?: number): Promise<ExamRecord[]> {
  const params = studentId ? { student_id: studentId, unit_type: 'practice' } : { unit_type: 'practice' }
  return request.get<RawExamRecord[]>('/exams/', { params }).then(rows => (rows || []).map(toExamRecord))
}

/**
 * 获取学生的练习成绩（从考试记录中提取并转换格式）
 */
export function getStudentPracticeScores(studentId?: number): Promise<PracticeScore[]> {
  return getStudentPracticeRecords(studentId).then(records => {
    return records.map(record => ({
      id: record.id,
      practice: record.unit_name || `练习 ${record.unit_id}`, // 从记录中获取单元名称
      totalScore: Number(record.total_score ?? 0) || 0,
      startedAt: record.start_time, // 使用start_time字段
      finishedAt: record.submit_time // 使用submit_time字段
    }))
  })
}

/**
 * 获取某次练习在指定页面的详情（媒体 + 每题得分等）
 *
 * 注意：这里调用的是 legacy Django 视图 `/stu_practice/practices/<practice_id>/page/<order>/`
 * 返回的是原始 JsonResponse，不经过统一的 Result 包装，因此不能使用通用的 request 实例。
 * 开发环境通过 Vite proxy 转发 /stu_practice 到后端；生产环境需配置同源或 CORS。
 */
export async function getPracticeDetail(practiceId: number, pageOrder: number): Promise<PracticeDetailResponse> {
  const token = localStorage.getItem('token') || localStorage.getItem('accessToken')
  // 开发环境用相对路径走 Vite proxy；生产环境用完整后端地址
  const baseURL = import.meta.env.VITE_API_BASE_URL || ''
  const url = baseURL ? `${baseURL}/stu_practice/practices/${practiceId}/page/${pageOrder}/` : `/stu_practice/practices/${practiceId}/page/${pageOrder}/`

  const response = await axios.get<PracticeDetailResponse>(url, {
    headers: {
      'Content-Type': 'application/json;charset=UTF-8',
      Accept: 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  })

  return response.data
}

/**
 * 基于现有 AI 学习数据接口，生成一个简单的前端侧学习建议结构
 *
 * 当前实现为轻量级启发式逻辑，后续可以替换为专门的后端推荐 API。
 */
export async function getAIRecommendation(payload: PracticeRecommendationRequest): Promise<PracticeRecommendation> {
  // 尝试从 AI 学习数据接口获取历史表现，用于丰富推荐语境
  let practiceCount = 0
  let avgScore = 0
  try {
    const learningData = await request.get<{
      practice_results: { score: number }[]
      exam_results: unknown[]
      incorrect_answers: unknown[]
      learning_trajectory: { score: number }[]
    }>('/ai/learning-data/')

    const results = learningData.practice_results || []
    practiceCount = results.length
    if (results.length > 0) {
      const total = results.reduce((sum, r) => sum + (Number(r.score) || 0), 0)
      avgScore = Math.round(total / results.length)
    }
  } catch {
    // 学习数据获取失败时，仍然返回基于文本的建议
  }

  // 从 transcript 中提取一些关键词（简单英文分词，过滤停用词）
  const text = payload.transcript || ''
  const cleanText = text.replace(/[.,!?'";:()]/g, ' ')
  const words = cleanText.split(/\s+/).filter(Boolean)
  const stopWords = new Set([
    'the',
    'a',
    'an',
    'and',
    'or',
    'but',
    'in',
    'on',
    'at',
    'to',
    'for',
    'with',
    'by',
    'from',
    'of',
    'is',
    'are',
    'was',
    'were',
    'be',
    'been',
    'being'
  ])
  const freq: Record<string, number> = {}
  for (const w of words) {
    const lower = w.toLowerCase()
    if (lower.length <= 3 || stopWords.has(lower)) continue
    freq[lower] = (freq[lower] || 0) + 1
  }
  const sortedKeywords = Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([w]) => w)

  const coreTheme =
    payload.practice_title ||
    (sortedKeywords.length > 0 ? `围绕 “${sortedKeywords[0]}” 的听力训练` : '当前听力练习主题')

  const themeMotivationParts: string[] = []
  if (practiceCount > 0) {
    themeMotivationParts.push(`你已经完成了大约 ${practiceCount} 次类似练习`)
  }
  if (avgScore > 0) {
    themeMotivationParts.push(`平均得分在 ${avgScore} 分左右`)
  }
  themeMotivationParts.push('建议继续通过短篇听力与精听来巩固本单元核心表达')

  const recommendation: PracticeRecommendation = {
    core_theme: coreTheme,
    theme_motivation: themeMotivationParts.join('，'),
    key_vocabulary: sortedKeywords,
    materials: [
      {
        type: 'video',
        title: '围绕本主题的英文访谈或对话（长度 3–5 分钟）',
        url: '#'
      },
      {
        type: 'article',
        title: '配套的中等难度英文短文，用于精读与跟读',
        url: '#'
      }
    ]
  }

  return recommendation
}


