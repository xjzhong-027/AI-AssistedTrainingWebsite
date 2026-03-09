import type { ExamStatus, ExamListItem, ExamTask } from '@/types/exam'
import type { Unit } from '@/api/content'

/**
 * 将后端 UnitSerializer.status（中文）转换为前端统一的 ExamStatus 枚举
 *
 * 后端可能返回：
 * - '未开始'
 * - '进行中'
 * - '已结束'
 * - '已发布'
 * - '未设置'
 */
export function mapUnitStatusToExamStatus(unitStatus?: string | null): ExamStatus {
  const text = (unitStatus || '').trim()
  switch (text) {
    case '未开始':
      return 'NOT_STARTED'
    case '进行中':
      return 'IN_PROGRESS'
    case '已结束':
      return 'ENDED'
    case '已发布':
      return 'PUBLISHED'
    default:
      return 'UNKNOWN'
  }
}

/**
 * 判断当前学生是否可以进入某个考试
 *
 * 规则（当前实现）：
 * - 已提交（record.submitted=true）视为不能再次进入
 * - 状态为 ENDED 时不能进入
 * - 其他状态（NOT_STARTED / IN_PROGRESS / PUBLISHED / UNKNOWN）默认允许进入，
 *   具体时间窗口控制由后端 TimeManagement + /exams/{id}/start/ 决定。
 */
export function canEnterExam(exam: ExamListItem, now: Date = new Date()): boolean {
  const { task, record } = exam

  if (record?.submitted) {
    return false
  }

  if (task.status === 'ENDED') {
    return false
  }

  // 目前不过度在前端限制时间窗口，交由后端控制；
  // 预留扩展点：后续可结合 exam.task.startTime / endTime 与 now 做更精细的判断。
  return true
}

/**
 * 将内容模块的 Unit 序列化结果转换为 ExamTask
 */
export function mapUnitToExamTask(unit: Unit): ExamTask {
  const title = unit.title || unit.unit_name || unit.name || '未命名考试'

  return {
    id: unit.id,
    title,
    description: '',
    classId: unit.class_id,
    className: unit.class_name,
    week: unit.week ?? null,
    status: mapUnitStatusToExamStatus(unit.status),
    duration: null,
    pageCount: Array.isArray(unit.pages) ? unit.pages.length : null,
    rawStatusText: unit.status,
    startTime: undefined,
    endTime: undefined
  }
}

