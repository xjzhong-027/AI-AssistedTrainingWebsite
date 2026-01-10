import request from '@/utils/request'

/**
 * 公告类型（根据后端API响应）
 */
export interface Announcement {
  id: number
  a_title: string
  a_content: string
  sender_name?: string
  sender_id?: number
  created_at: string
  updated_at?: string
  isRead?: boolean
  receivers?: Array<{
    student_id: number
    student_name: string
  }>
}

/**
 * 创建公告DTO（根据后端API要求）
 */
export interface AnnouncementCreateDTO {
  a_title: string
  a_content: string
  receiver_student_ids: number[]
}

/**
 * 更新公告DTO（根据后端API要求）
 */
export interface AnnouncementUpdateDTO {
  a_title?: string
  a_content?: string
  receiver_student_ids?: number[]
}

/**
 * 获取所有公告列表
 */
export function getAllAnnouncements(): Promise<Announcement[]> {
  return request.get('/announcements/')
}

/**
 * 获取学生的公告列表
 */
export function getStudentAnnouncements(studentId?: number): Promise<Announcement[]> {
  const params = studentId ? { student_id: studentId } : {}
  return request.get('/announcements/', { params })
}

/**
 * 获取教师创建的公告列表
 */
export function getTeacherAnnouncements(): Promise<Announcement[]> {
  return request.get('/announcements/')
}

/**
 * 根据ID获取公告详情
 */
export function getAnnouncementById(id: number): Promise<Announcement> {
  return request.get(`/announcements/${id}/`)
}

/**
 * 创建公告
 */
export function createAnnouncement(data: AnnouncementCreateDTO): Promise<Announcement> {
  return request.post('/announcements/create/', data)
}

/**
 * 更新公告
 */
export function updateAnnouncement(id: number, data: AnnouncementUpdateDTO): Promise<Announcement> {
  return request.put(`/announcements/${id}/update/`, data)
}

/**
 * 删除公告
 */
export function deleteAnnouncement(id: number): Promise<void> {
  return request.delete(`/announcements/${id}/delete/`)
}

/**
 * 标记公告为已读
 */
export function markAnnouncementAsRead(announcementId: number): Promise<void> {
  return request.post(`/announcements/${announcementId}/mark-as-read/`)
}

/**
 * 标记公告为未读
 */
export function markAnnouncementAsUnread(announcementId: number): Promise<void> {
  return request.post(`/announcements/${announcementId}/mark-unread/`)
}

