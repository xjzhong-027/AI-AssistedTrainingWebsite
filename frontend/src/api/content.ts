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
  type: 'exam' | 'practice'
  unit_type?: 'exam' | 'practice'  // 兼容旧字段
  class_id?: number
  class_name?: string
  order?: number
  pages?: any[]
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
 * 获取所有单元列表
 */
export function getAllUnits(classId?: number): Promise<Unit[]> {
  const params = classId ? { class_id: classId } : {}
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
}): Promise<Unit> {
  return request.post('/content/units/', data)
}

/**
 * 获取媒体素材关联的所有大题
 */
export function getMaterialQuestions(materialId: number): Promise<any[]> {
  return request.get(`/content/media-materials/${materialId}/questions/`)
}


