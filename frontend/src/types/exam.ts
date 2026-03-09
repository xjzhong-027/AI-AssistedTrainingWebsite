/**
 * 考试相关类型定义
 */

/**
 * 前端统一使用的考试状态枚举
 *
 * - NOT_STARTED：未开始
 * - IN_PROGRESS：进行中 / 可进入考试（尚未提交）
 * - ENDED：已结束 / 已提交
 * - PUBLISHED：已发布但暂未到开始时间（预留）
 * - UNKNOWN：状态未知（后端未设置或兼容旧数据）
 */
export type ExamStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'ENDED' | 'PUBLISHED' | 'UNKNOWN'

/**
 * 考试任务视图（以 Unit 为中心）
 * 对应后端 ELW.models.Unit + TimeManagement 的前端投影
 */
export interface ExamTask {
  /** 任务包 ID（Unit.id），同时作为考试路由参数 */
  id: number
  /** 任务 / 考试标题 */
  title: string
  /** 描述文案（目前后端未直接提供，前端可按需填充） */
  description?: string
  /** 班级信息（来自 UnitSerializer） */
  classId?: number
  className?: string
  /** 开放周次（Week），0 表示始终开放 */
  week?: number | null
  /** 统一后的状态枚举 */
  status: ExamStatus
  /** 时长限制（分钟），优先来自 TimeManagement.duration */
  duration?: number | null
  /** 页面数量（PaperPage 数量） */
  pageCount?: number | null
  /** 原始状态文本（如：未开始 / 进行中 / 已结束 / 已发布 / 未设置），用于展示或调试 */
  rawStatusText?: string
  /** 计划/实际开始与结束时间（兼容字段，字符串时间戳） */
  startTime?: string
  endTime?: string
}

/**
 * 当前学生在某个考试任务上的作答记录概要
 * 对应后端 accessment.models.StudentExamRecord 的前端精简视图
 */
export interface ExamRecordSummary {
  /** 学生考试记录 ID（StudentExamRecord.id） */
  examRecordId?: number
  submitted: boolean
  score?: number | null
  startedAt?: string
  finishedAt?: string
}

/**
 * 考试列表项：任务 +（可选）学生记录
 */
export interface ExamListItem {
  task: ExamTask
  record?: ExamRecordSummary
}

/**
 * 旧版 Exam 类型（兼容历史代码，表示基于 /api/v1/exams/ 的视图）
 * 新代码应优先使用 ExamTask / ExamRecordSummary / ExamListItem。
 */
export interface Exam {
  id: number
  title: string
  description?: string
  creatorId: number
  startTime: string
  endTime: string
  duration: number
  status: ExamStatus
  createdAt: string
  updatedAt: string
}

export interface ExamCreateDTO {
  title: string
  description?: string
  creatorId: number
  startTime: string
  endTime: string
  duration: number
}

export interface ExamUpdateDTO {
  title?: string
  description?: string
  startTime?: string
  endTime?: string
  duration?: number
}

