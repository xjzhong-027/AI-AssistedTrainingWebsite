import request from '@/utils/request'

/**
 * 帖子类型
 */
export interface Post {
  id: number
  title: string
  content: string
  author: string
  authorId: number
  createdAt: string
  updatedAt: string
  isPublic: boolean
  commentCount: number
}

/**
 * 评论类型
 */
export interface Comment {
  id: number
  content: string
  author: string
  authorId: number
  postId: number
  createdAt: string
  updatedAt: string
}

/**
 * 创建帖子DTO
 */
export interface PostCreateDTO {
  title: string
  content: string
  isPublic: boolean
}

/**
 * 更新帖子DTO
 */
export interface PostUpdateDTO {
  title?: string
  content?: string
  isPublic?: boolean
}

/**
 * 创建评论DTO
 */
export interface CommentCreateDTO {
  content: string
  postId: number
}

/**
 * 获取所有帖子列表
 */
export function getAllPosts(params?: {
  search?: string
  main_question_id?: number
  sub_question_id?: number
}): Promise<Post[]> {
  return request.get('/forum/posts/', { params })
}

/**
 * 根据ID获取帖子详情
 */
export function getPostById(id: number): Promise<Post> {
  return request.get(`/forum/posts/${id}/`)
}

/**
 * 创建帖子
 */
export function createPost(data: PostCreateDTO): Promise<Post> {
  return request.post('/forum/posts/create/', data)
}

/**
 * 更新帖子
 */
export function updatePost(id: number, data: PostUpdateDTO): Promise<Post> {
  return request.put(`/forum/posts/${id}/update/`, data)
}

/**
 * 删除帖子
 */
export function deletePost(id: number): Promise<void> {
  return request.delete(`/forum/posts/${id}/delete/`)
}

/**
 * 获取帖子的评论列表
 */
export function getPostComments(postId: number): Promise<Comment[]> {
  return request.get(`/forum/posts/${postId}/comments/`)
}

/**
 * 创建评论
 */
export function createComment(postId: number, data: { content: string; parent_comment_id?: number }): Promise<Comment> {
  return request.post(`/forum/posts/${postId}/comments/create/`, data)
}

/**
 * 更新评论
 */
export function updateComment(commentId: number, content: string): Promise<Comment> {
  return request.put(`/forum/comments/${commentId}/update/`, { content })
}

/**
 * 删除评论
 */
export function deleteComment(commentId: number): Promise<void> {
  return request.delete(`/forum/comments/${commentId}/delete/`)
}

/**
 * 搜索帖子
 */
export function searchPosts(params: {
  title?: string
  content?: string
  author?: string
  created_at__gte?: string
  created_at__lte?: string
}): Promise<Post[]> {
  return request.get('/forum/posts/search/', { params })
}

