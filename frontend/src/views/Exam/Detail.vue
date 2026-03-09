<template>
  <div class="exam-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>考试详情</span>
          <div>
            <el-button @click="goBack">返回</el-button>
            <el-button
              v-if="userStore.isTeacher()"
              type="primary"
              @click="goTeacherUnitDetail"
            >
              查看任务
            </el-button>
            <el-button
              v-if="userStore.isStudent() && canStartExam"
              type="success"
              @click="takeExam"
            >
              开始考试
            </el-button>
            <el-button
              v-if="userStore.isStudent() && examRecord?.submitted"
              type="primary"
              @click="viewResult"
            >
              查看结果
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="examTask" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="考试ID">{{ examTask.id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(examTask.status)">{{ getStatusText(examTask.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="考试标题" :span="2">{{ examTask.title }}</el-descriptions-item>
          <el-descriptions-item label="考试描述" :span="2">
            {{ examTask.description || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ examRecord?.startedAt ? formatDateTime(examRecord.startedAt) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ examRecord?.finishedAt ? formatDateTime(examRecord.finishedAt) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="页数">
            {{ examTask.pageCount ?? '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="本次得分">
            {{ examRecord?.score != null ? examRecord.score + ' 分' : examRecord ? '未出分' : '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 题目列表 -->
        <div v-if="userStore.isTeacher()" style="margin-top: 30px">
          <el-divider>题目列表</el-divider>
          <el-button type="primary" @click="goCreateQuestion">
            <el-icon><Plus /></el-icon>
            添加题目
          </el-button>
          <el-table :data="questions" style="width: 100%; margin-top: 20px" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="type" label="类型" width="120">
              <template #default="{ row }">
                {{ getQuestionTypeText(row.type) }}
              </template>
            </el-table-column>
            <el-table-column prop="content" label="题目内容" min-width="200" show-overflow-tooltip />
            <el-table-column prop="score" label="分值" width="80" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewQuestion(row.id)">查看</el-button>
                <el-button link type="warning" @click="editQuestion(row.id)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getExamResult } from '@/api/exam'
import { getUnitById } from '@/api/content'
import { getQuestionsByExamId } from '@/api/question'
import { formatDateTime } from '@/utils/format'
import { canEnterExam, mapUnitToExamTask } from '@/utils/exam-utils'
import type { ExamTask, ExamRecordSummary, ExamListItem, ExamStatus } from '@/types/exam'
import type { Question } from '@/types/question'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const examTask = ref<ExamTask | null>(null)
const examRecord = ref<ExamRecordSummary | null>(null)
const questions = ref<Question[]>([])

const canStartExam = computed(() => {
  if (!examTask.value) return false
  const item: ExamListItem = {
    task: examTask.value,
    record: examRecord.value || undefined
  }
  return canEnterExam(item)
})

// 加载考试详情
const loadExam = async () => {
  const id = Number(route.params.id)
  if (!id) {
    ElMessage.error('考试ID无效')
    router.push('/exams')
    return
  }

  loading.value = true
  try {
    // 任务信息（Unit）
    const unit = await getUnitById(id)
    examTask.value = mapUnitToExamTask(unit)

    // 当前学生的考试记录（仅学生端可用）
    if (userStore.isStudent()) {
      try {
        const result: any = await getExamResult(id)
        examRecord.value = {
          examRecordId: result.id,
          submitted: Boolean(result.submitted),
          score: result.score ?? null,
          startedAt: result.started_at,
          finishedAt: result.finished_at
        }
      } catch (error: any) {
        // 没有记录时不报错，视为尚未开始考试
        console.warn('当前学生尚无考试记录或无法获取结果', error)
      }
    }

    if (userStore.isTeacher()) {
      questions.value = await getQuestionsByExamId(id)
    }
  } catch (error) {
    console.error('加载考试详情失败', error)
  } finally {
    loading.value = false
  }
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    NOT_STARTED: '未开始',
    IN_PROGRESS: '进行中',
    ENDED: '已结束',
    PUBLISHED: '已发布',
    UNKNOWN: '未知'
  }
  return statusMap[status] || status
}

const getStatusType = (status: string): string => {
  const typeMap: Record<string, string> = {
    NOT_STARTED: 'info',
    IN_PROGRESS: 'success',
    ENDED: 'warning',
    PUBLISHED: 'info',
    UNKNOWN: 'info'
  }
  // 默认用 'info'，避免传入空字符串导致 ElTag 报错
  return typeMap[status] || 'info'
}

const getQuestionTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    SINGLE_CHOICE: '单选题',
    MULTIPLE_CHOICE: '多选题',
    TRUE_FALSE: '判断题',
    SHORT_ANSWER: '简答题'
  }
  return typeMap[type] || type
}

const goBack = () => {
  router.push('/exams')
}

const goTeacherUnitDetail = () => {
  if (!examTask.value) return
  router.push(`/teacher/units/${examTask.value.id}`)
}

const takeExam = () => {
  if (!examTask.value) return
  router.push(`/exams/${examTask.value.id}/take`)
}

const viewResult = () => {
  if (!examTask.value) return
  router.push(`/exams/${examTask.value.id}/result`)
}

const goCreateQuestion = () => {
  if (!examTask.value) return
  router.push(`/questions/create?examId=${examTask.value.id}`)
}

const viewQuestion = (id: number) => {
  router.push(`/questions/${id}`)
}

const editQuestion = (id: number) => {
  router.push(`/questions/${id}/edit`)
}

onMounted(() => {
  loadExam()
})
</script>

<style scoped>
.exam-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-content {
  padding: 20px 0;
}
</style>
