<template>
  <div class="score-pending">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>待批改成绩</span>
          <el-button type="primary" @click="loadPendingScores">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="pendingScores" style="width: 100%" stripe>
        <el-table-column prop="id" label="成绩ID" width="100" />
        <el-table-column prop="examRecordId" label="考试记录ID" width="120" />
        <el-table-column label="考试标题" min-width="200">
          <template #default="{ row }">
            {{ getExamTitle(row.examRecordId) }}
          </template>
        </el-table-column>
        <el-table-column label="学生" width="120">
          <template #default="{ row }">
            {{ getStudentName(row.examRecordId) }}
          </template>
        </el-table-column>
        <el-table-column prop="autoScore" label="自动评分" width="100" />
        <el-table-column prop="manualScore" label="手动评分" width="100">
          <template #default="{ row }">
            {{ row.manualScore ?? '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="totalScore" label="总分" width="100" />
        <el-table-column prop="isGraded" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isGraded ? 'success' : 'warning'">
              {{ row.isGraded ? '已批改' : '待批改' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.isGraded || row.manualScore === null"
              link
              type="warning"
              @click="gradeScore(row.examRecordId)"
            >
              批改
            </el-button>
            <el-button link type="primary" @click="viewDetail(row.id)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && pendingScores.length === 0" description="暂无待批改成绩" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { getScoresByExamId } from '@/api/score'
import { getExamsByCreatorId, getExamById } from '@/api/exam'
import { getExamRecordById } from '@/api/answer'
import { getUserById } from '@/api/user'
import { useUserStore } from '@/stores/user'
import type { Score } from '@/types/score'
import type { Exam } from '@/types/exam'
import type { ExamRecord } from '@/types/answer'
import type { User } from '@/types/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const pendingScores = ref<Score[]>([])
const examRecordMap = ref<Map<number, ExamRecord>>(new Map())
const examMap = ref<Map<number, Exam>>(new Map())
const studentMap = ref<Map<number, User>>(new Map())

// 加载待批改成绩
const loadPendingScores = async () => {
  if (!userStore.isTeacher() || !userStore.userInfo?.id) {
    return
  }

  loading.value = true
  try {
    // 清空缓存
    examRecordMap.value.clear()
    examMap.value.clear()
    studentMap.value.clear()

    // 获取教师创建的所有考试
    const exams = await getExamsByCreatorId(userStore.userInfo.id)
    examMap.value = new Map(exams.map((exam) => [exam.id, exam]))

    // 获取所有考试的成绩
    const allScores: Score[] = []
    for (const exam of exams) {
      try {
        const scores = await getScoresByExamId(exam.id)
        // 筛选出需要批改的成绩（未完成手动评分）
        const pending = scores.filter(
          (score) => !score.isGraded || score.manualScore === null
        )
        allScores.push(...pending)

        // 加载考试记录和学生信息
        for (const score of pending) {
          try {
            const examRecord = await getExamRecordById(score.examRecordId)
            if (examRecord) {
              examRecordMap.value.set(score.examRecordId, examRecord)
              if (!studentMap.value.has(examRecord.studentId)) {
                const student = await getUserById(examRecord.studentId, 'STUDENT')
                studentMap.value.set(examRecord.studentId, student)
              }
            }
          } catch (error) {
            console.error('加载考试记录失败', error)
          }
        }
      } catch (error) {
        console.error(`加载考试 ${exam.id} 的成绩失败`, error)
      }
    }

    pendingScores.value = allScores
  } catch (error) {
    console.error('加载待批改成绩失败', error)
  } finally {
    loading.value = false
  }
}

// 获取考试标题
const getExamTitle = (examRecordId: number): string => {
  const examRecord = examRecordMap.value.get(examRecordId)
  if (examRecord) {
    const exam = examMap.value.get(examRecord.examId)
    return exam?.title || '未知考试'
  }
  return '加载中...'
}

// 获取学生姓名
const getStudentName = (examRecordId: number): string => {
  const examRecord = examRecordMap.value.get(examRecordId)
  if (examRecord) {
    const student = studentMap.value.get(examRecord.studentId)
    return student?.realName || '未知学生'
  }
  return '加载中...'
}

const gradeScore = (examRecordId: number) => {
  router.push(`/scores/grade/${examRecordId}`)
}

const viewDetail = (id: number) => {
  router.push(`/scores/${id}`)
}

onMounted(() => {
  loadPendingScores()
})
</script>

<style scoped>
.score-pending {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
