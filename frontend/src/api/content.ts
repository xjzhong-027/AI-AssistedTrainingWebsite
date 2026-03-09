import request from '@/utils/request'

/**
 * 媒体素材类型
 */
export interface MediaMaterial {
  id: number
  title: string
  theme?: string
  abstract?: string
  keywords?: string
  transcript?: string
  media_url?: string
  image_url?: string
}

/**
 * 单元类型
 */
export interface Unit {
  id: number
  title: string
  name?: string  // 兼容旧字段
  unit_name?: string  // 兼容旧字段
  type: 'exam' | 'practice' | 'task' | 'quiz'
  unit_type?: 'exam' | 'practice' | 'task' | 'quiz'  // 兼容旧字段
  class_id?: number
  class_name?: string
  order?: number
  pages?: any[]
  week?: number  // 周次
  status?: string  // 状态：未设置、未开始、进行中、已结束、已发布
}

/**
 * 获取所有媒体素材列表
 */
export function getAllMediaMaterials(): Promise<MediaMaterial[]> {
  return request.get('/content/media-materials/')
}

/**
 * 根据ID获取媒体素材详情
 */
export function getMediaMaterialById(id: number): Promise<MediaMaterial> {
  return request.get(`/content/media-materials/${id}/`)
}

/**
 * 创建媒体素材
 */
export function createMediaMaterial(data: {
  title: string
  theme?: string
  abstract?: string
  keywords?: string
  transcript?: string
  media_url?: string
  image_url?: string
}): Promise<MediaMaterial> {
  return request.post('/content/media-materials/', data)
}

/**
 * 上传媒体文件（音频/视频），返回可存入 media_url 的相对路径
 */
export function uploadMediaFile(file: File): Promise<{ media_url: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/content/media-materials/upload-media/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 上传图片，返回可存入 image_url 的相对路径
 */
export function uploadMaterialImage(file: File): Promise<{ image_url: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/content/media-materials/upload-image/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 获取所有单元列表
 * @param classId 可选，按班级筛选
 * @param unitType 可选，按类型筛选（exam/practice/task/quiz）
 */
export function getAllUnits(
  classId?: number,
  unitType?: 'exam' | 'practice' | 'task' | 'quiz'
): Promise<Unit[]> {
  const params: any = {}
  if (classId) params.class_id = classId
  if (unitType) params.unit_type = unitType
  return request.get('/content/units/', { params })
}

/**
 * 根据ID获取单元详情
 */
export function getUnitById(id: number): Promise<Unit> {
  return request.get(`/content/units/${id}/`)
}

/**
 * 获取单元的所有页面
 */
export function getPagesByUnit(unitId: number): Promise<any[]> {
  return request.get(`/content/units/${unitId}/pages/`)
}

/**
 * 根据 ID 获取试卷页面详情
 */
export function getPageById(pageId: number): Promise<any> {
  return request.get(`/content/pages/${pageId}/`)
}

/**
 * 获取页面的所有大题（包含小题）
 */
export function getPageQuestions(pageId: number): Promise<any[]> {
  return request.get(`/content/pages/${pageId}/questions/`)
}

/**
 * 删除媒体素材
 */
export function deleteMediaMaterial(id: number): Promise<void> {
  return request.delete(`/content/media-materials/${id}/`)
}

/**
 * 删除单元（考试/练习）
 */
export function deleteUnit(id: number): Promise<void> {
  return request.delete(`/content/units/${id}/`)
}

/**
 * 更新单元
 */
export function updateUnit(id: number, data: {
  title?: string
  class_id?: number
  order?: number
  week?: number
}): Promise<Unit> {
  return request.put(`/content/units/${id}/`, data)
}

/**
 * 创建单元（任务包）
 */
export function createUnit(data: {
  class_id: number
  title: string
  type: 'exam' | 'practice'
  order?: number
  week?: number
}): Promise<Unit> {
  return request.post('/content/units/', data)
}

/**
 * 获取媒体素材关联的所有大题
 */
export function getMaterialQuestions(materialId: number): Promise<any[]> {
  return request.get(`/content/media-materials/${materialId}/questions/`)
}

/**
 * 语音识别：上传媒体文件，提取 transcript（同时保存文件，返回 media_url）
 */
export function transcribeMedia(file: File): Promise<{ transcript: string; media_url: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/content/transcribe-media/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000
  })
}

/**
 * AI 智能分析素材：根据 transcript 解析 title、theme、abstract、keywords
 */
export function analyzeMaterial(transcript: string): Promise<{ title: string; theme: string; abstract: string; keywords: string }> {
  return request.post('/content/analyze-material/', { transcript }, { timeout: 60000 })
}

/**
 * 批量导入选择题
 */
export function batchImportChoices(materialId: number, questions: Array<{
  question_text: string
  option_A: string
  option_B: string
  option_C: string
  option_D: string
  correct_answer: string
  score: number
}>): Promise<{ count: number }> {
  return request.post(`/content/media-materials/${materialId}/batch-import-choices/`, { questions })
}

/**
 * 在媒体素材下创建题目（大题+小题+选项）
 */
export function createMaterialQuestion(materialId: number, data: {
  question_type: 'choice' | 'matching' | 'correction' | 'comprehension' | 'text'
  question_text: string
  maximum_play?: number
  minimum_play?: number
  no_media?: boolean
  sub_questions: Array<{
    question_text: string
    answer: string
    score?: number
    tips?: string
    analysis?: string
    options?: Array<{ option_label?: string; option_content: string; is_answer?: boolean }>
    matching_options?: Array<{ option_label?: string; option_content: string }>
    corrections?: Array<{ type: string; index?: number }>
  }>
}): Promise<any> {
  return request.post(`/content/media-materials/${materialId}/questions/`, data)
}

/**
 * 创建试卷页（组卷：在指定任务包下新建一页并关联大题）
 */
export function createPaperPage(data: {
  unit_id: number
  text?: string
  order?: number
  limited_time?: number
  can_modify?: boolean
  main_question_ids: number[]
}): Promise<any> {
  return request.post('/content/pages/', data)
}


