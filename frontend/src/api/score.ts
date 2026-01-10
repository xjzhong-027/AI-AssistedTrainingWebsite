import request from '@/utils/request'
import type { Score } from '@/types/score'

/**
 * 计算成绩
 */
export function calculateScore(examRecordId: number): Promise<Score> {
  return request.post(`/scores/calculate/${examRecordId}`)
}

/**
 * 手动评分
 */
export function manualGrade(id: number, manualScore: number): Promise<Score> {
  return request.put(`/scores/${id}/manual`, null, { params: { manualScore } })
}

/**
 * 根据ID获取成绩
 */
export function getScoreById(id: number): Promise<Score> {
  return request.get(`/scores/${id}`)
}

/**
 * 根据考试记录ID获取成绩
 */
export function getScoreByExamRecordId(examRecordId: number): Promise<Score> {
  return request.get(`/scores/exam-record/${examRecordId}`)
}

/**
 * 根据考试ID获取成绩列表
 */
export function getScoresByExamId(examId: number): Promise<Score[]> {
  return request.get(`/scores/exam/${examId}`)
}

/**
 * 获取成绩统计
 */
export function getScoreStatistics(examId: number): Promise<any> {
  return request.get(`/scores/exam/${examId}/statistics`)
}

