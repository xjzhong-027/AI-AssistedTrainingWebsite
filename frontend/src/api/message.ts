import request from '@/utils/request'

/**
 * 消息类型
 */
export interface Message {
  id: number
  content: string
  sender: string
  senderId: number
  receiverId: number
  createdAt: string
  isRead: boolean
  readAt?: string
}

/**
 * 发送消息DTO
 */
export interface MessageCreateDTO {
  receiver: string
  content: string
}

/**
 * 获取所有消息列表（当前用户的消息）
 */
export function getAllMessages(): Promise<Message[]> {
  return request.get('/messages/')
}

/**
 * 获取当前用户的消息列表（与getAllMessages相同，因为API只返回当前用户的消息）
 */
export function getMyMessages(): Promise<Message[]> {
  return request.get('/messages/')
}

/**
 * 根据ID获取消息详情
 */
export function getMessageById(id: number): Promise<Message> {
  return request.get(`/messages/${id}/`)
}

/**
 * 发送消息
 */
export function sendMessage(data: MessageCreateDTO): Promise<Message> {
  return request.post('/messages/create/', data)
}

/**
 * 标记消息为已读
 */
export function markMessageAsRead(messageId: number): Promise<void> {
  return request.post(`/messages/${messageId}/mark-as-read/`)
}

/**
 * 标记所有消息为已读
 */
export function markAllMessagesAsRead(): Promise<void> {
  return request.post('/messages/mark-all-as-read/')
}

/**
 * 删除消息
 */
export function deleteMessage(id: number): Promise<void> {
  return request.delete(`/messages/${id}/`)
}

