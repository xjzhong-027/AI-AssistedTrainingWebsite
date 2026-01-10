<template>
  <div class="score-list">
    <el-card>
      <template #header>
        <span>成绩列表</span>
      </template>

      <el-table v-loading="loading" :data="scoreList" style="width: 100%" stripe>
        <el-table-column prop="id" label="成绩ID" width="100" />
        <el-table-column prop="examRecordId" label="考试记录ID" width="120" />
        <el-table-column label="考试信息" min-width="200">
          <template #default="{ row }">
            {{ getExamTitle(row.examRecordId) }}
          </template>
        </el-table-column>
        <el-table-column v-if="userStore.isTeacher()" label="学生" width="120">
          <template #default="{ row }">
            {{ getStudentName(row.examRecordId) }}
          </template>
        </el-table-column>
        <el-table-column prop="totalScore" label="总分" width="100">
          <template #default="{ row }">
            <span style="font-weight: bold; color: #409eff">{{ row.totalScore }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="autoScore" label="自动评分" width="100" />
        <el-table-column prop="manualScore" label="手动评分" width="100">
          <template #default="{ row }">
            {{ row.manualScore ?? '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="isGraded" label="已评分" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isGraded ? 'success' : 'warning'">
              {{ row.isGraded ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row.id)">查看详情</el-button>
            <el-button
              v-if="userStore.isTeacher() && (!row.isGraded || row.manualScore === null)"
              link
              type="warning"
              @click="gradeScore(row.examRecordId)"
            >
              批改
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && scoreList.length === 0" description="暂无成绩数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getScoreByExamRecordId, getScoresByExamId } from '@/api/score'
import { getExamRecordById } from '@/api/answer'
import { getAllExams, getExamsByCreatorId } from '@/api/exam'
import { getUserById } from '@/api/user'
import { useUserStore } from '@/stores/user'
import type { Score } from '@/types/score'
import type { Exam } from '@/types/exam'
import type { ExamRecord } from '@/types/answer'
import type { User } from '@/types/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const scoreList = ref<Score[]>([])
const examRecordMap = ref<Map<number, ExamRecord>>(new Map())
const examMap = ref<Map<number, Exam>>(new Map())
const studentMap = ref<Map<number, User>>(new Map())

// 加载成绩列表
const loadScores = async () => {
  loading.value = true
  try {
    // 清空缓存
    examRecordMap.value.clear()
    examMap.value.clear()
    studentMap.value.clear()
    scoreList.value = []

    if (userStore.isStudent() && userStore.userInfo?.id) {
      // 学生：获取所有考试，然后查找该学生的考试记录和成绩
      const exams = await getAllExams()
      examMap.value = new Map(exams.map((exam) => [exam.id, exam]))

      for (const exam of exams) {
        try {
          // 获取该考试的所有成绩
          const scores = await getScoresByExamId(exam.id)
          
          // 筛选出该学生的成绩
          for (const score of scores) {
            try {
              const examRecord = await getExamRecordById(score.examRecordId)
              if (examRecord && examRecord.studentId === userStore.userInfo.id) {
                examRecordMap.value.set(score.examRecordId, examRecord)
                scoreList.value.push(score)
              }
            } catch (error) {
              console.error('加载考试记录失败', error)
            }
          }
        } catch (error) {
          console.error(`加载考试 ${exam.id} 的成绩失败`, error)
        }
      }
    } else if (userStore.isTeacher() && userStore.userInfo?.id) {
      // 教师：获取自己创建的所有考试的成绩
      const exams = await getExamsByCreatorId(userStore.userInfo.id)
      examMap.value = new Map(exams.map((exam) => [exam.id, exam]))

      for (const exam of exams) {
        try {
          const scores = await getScoresByExamId(exam.id)
          scoreList.value.push(...scores)

          // 加载考试记录和学生信息
          for (const score of scores) {
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
    }
  } catch (error) {
    console.error('加载成绩列表失败', error)
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

const viewDetail = (id: number) => {
  router.push(`/scores/${id}`)
}

const gradeScore = (examRecordId: number) => {
  router.push(`/scores/grade/${examRecordId}`)
}

onMounted(() => {
  loadScores()
})
</script>

<style scoped>
.score-list {
  padding: 20px;
}
</style>
