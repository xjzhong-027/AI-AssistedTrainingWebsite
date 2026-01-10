<template>
  <div class="score-grade">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>手动评分 - {{ exam?.title }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <div v-if="exam && examRecord" class="grade-content">
        <!-- 考试信息 -->
        <el-descriptions :column="2" border style="margin-bottom: 30px">
          <el-descriptions-item label="考试ID">{{ exam.id }}</el-descriptions-item>
          <el-descriptions-item label="考试记录ID">{{ examRecord.id }}</el-descriptions-item>
          <el-descriptions-item label="学生ID">{{ examRecord.studentId }}</el-descriptions-item>
          <el-descriptions-item label="提交时间">
            {{ examRecord.submitTime ? formatDateTime(examRecord.submitTime) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="自动评分（客观题）" :span="2">
            <span style="font-size: 18px; font-weight: bold; color: #409eff">
              {{ score?.autoScore || 0 }} 分
            </span>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 简答题列表 -->
        <el-divider>简答题批改</el-divider>

        <div v-if="shortAnswerQuestions.length === 0" class="no-questions">
          <el-empty description="该考试没有简答题，无需手动评分" />
        </div>

        <div v-else>
          <el-form :model="gradeForm" ref="formRef" label-width="150px">
            <div
              v-for="(question, index) in shortAnswerQuestions"
              :key="question.id"
              class="question-grade-item"
            >
              <el-card>
                <template #header>
                  <div class="question-header">
                    <span>第 {{ index + 1 }} 题（{{ question.score }} 分）</span>
                    <el-tag type="info">简答题</el-tag>
                  </div>
                </template>

                <div class="question-content">
                  <div class="question-text">
                    <strong>题目：</strong>
                    <div style="margin-top: 10px; padding: 10px; background: #f5f7fa; border-radius: 4px">
                      {{ question.content }}
                    </div>
                  </div>

                  <div class="student-answer" style="margin-top: 20px">
                    <strong>学生答案：</strong>
                    <div
                      style="
                        margin-top: 10px;
                        padding: 15px;
                        background: #fff;
                        border: 1px solid #e4e7ed;
                        border-radius: 4px;
                        min-height: 100px;
                        white-space: pre-wrap;
                      "
                    >
                      {{ getStudentAnswer(question.id) || '（未作答）' }}
                    </div>
                  </div>

                  <el-form-item
                    :label="`评分（0-${question.score}分）`"
                    :prop="`scores.${question.id}`"
                    :rules="[
                      { required: true, message: '请输入分数', trigger: 'blur' },
                      {
                        type: 'number',
                        min: 0,
                        max: question.score,
                        message: `分数必须在 0 到 ${question.score} 之间`,
                        trigger: 'blur'
                      }
                    ]"
                    style="margin-top: 20px"
                  >
                    <el-input-number
                      v-model="gradeForm.scores[question.id]"
                      :min="0"
                      :max="question.score"
                      :precision="0"
                      placeholder="请输入分数"
                      style="width: 200px"
                    />
                    <span style="margin-left: 10px; color: #909399">
                      / {{ question.score }} 分
                    </span>
                  </el-form-item>
                </div>
              </el-card>
            </div>

            <div class="grade-summary" style="margin-top: 30px">
              <el-card>
                <div style="display: flex; justify-content: space-between; align-items: center">
                  <div>
                    <div style="font-size: 14px; color: #909399">自动评分（客观题）</div>
                    <div style="font-size: 24px; font-weight: bold; color: #409eff">
                      {{ score?.autoScore || 0 }} 分
                    </div>
                  </div>
                  <div style="text-align: center">
                    <div style="font-size: 14px; color: #909399">手动评分（主观题）</div>
                    <div style="font-size: 24px; font-weight: bold; color: #67c23a">
                      {{ manualScoreTotal }} 分
                    </div>
                  </div>
                  <div style="text-align: right">
                    <div style="font-size: 14px; color: #909399">总分</div>
                    <div style="font-size: 32px; font-weight: bold; color: #e6a23c">
                      {{ totalScore }} 分
                    </div>
                  </div>
                </div>
              </el-card>
            </div>

            <div class="grade-actions" style="margin-top: 30px; text-align: center">
              <el-button type="primary" size="large" @click="handleSubmit" :loading="submitting">
                提交评分
              </el-button>
              <el-button size="large" @click="goBack">取消</el-button>
            </div>
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { getExamById } from '@/api/exam'
import { getQuestionsByExamId } from '@/api/question'
import { getExamRecordById, getAnswersByExamRecordId } from '@/api/answer'
import { getScoreByExamRecordId, manualGrade } from '@/api/score'
import { formatDateTime } from '@/utils/format'
import type { Exam } from '@/types/exam'
import type { Question } from '@/types/question'
import type { ExamRecord, Answer } from '@/types/answer'
import type { Score } from '@/types/score'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const exam = ref<Exam | null>(null)
const examRecord = ref<ExamRecord | null>(null)
const questions = ref<Question[]>([])
const answers = ref<Answer[]>([])
const score = ref<Score | null>(null)

const gradeForm = reactive<{ scores: Record<number, number> }>({
  scores: {}
})

// 筛选出简答题
const shortAnswerQuestions = computed(() => {
  return questions.value.filter((q) => q.type === 'SHORT_ANSWER')
})

// 获取学生答案
const getStudentAnswer = (questionId: number): string => {
  const answer = answers.value.find((a) => a.questionId === questionId)
  return answer?.answerContent || ''
}

// 计算手动评分总分
const manualScoreTotal = computed(() => {
  return Object.values(gradeForm.scores).reduce((sum, score) => sum + (score || 0), 0)
})

// 计算总分
const totalScore = computed(() => {
  return (score.value?.autoScore || 0) + manualScoreTotal.value
})

// 加载数据
const loadData = async () => {
  const examRecordId = Number(route.params.examRecordId)
  if (!examRecordId) {
    router.push('/scores')
    return
  }

  loading.value = true
  try {
    // 加载考试记录
    examRecord.value = await getExamRecordById(examRecordId)
    if (!examRecord.value) {
      ElMessage.error('考试记录不存在')
      router.push('/scores')
      return
    }

    // 加载考试信息
    exam.value = await getExamById(examRecord.value.examId)

    // 加载题目
    questions.value = await getQuestionsByExamId(examRecord.value.examId)

    // 加载答案
    answers.value = await getAnswersByExamRecordId(examRecordId)

    // 加载成绩，如果不存在则先计算
    try {
      score.value = await getScoreByExamRecordId(examRecordId)
    } catch (error) {
      // 如果成绩不存在，先计算成绩
      try {
        const { calculateScore } = await import('@/api/score')
        score.value = await calculateScore(examRecordId)
        ElMessage.success('成绩已自动计算')
      } catch (calcError) {
        console.error('计算成绩失败', calcError)
        ElMessage.error('计算成绩失败，请稍后重试')
      }
    }

    // 初始化评分表单（只初始化简答题）
    shortAnswerQuestions.value.forEach((q) => {
      // 如果已有答案，尝试从答案中获取已评分分数
      const answer = answers.value.find((a) => a.questionId === q.id)
      if (answer && answer.score !== null && answer.score !== undefined) {
        gradeForm.scores[q.id] = answer.score
      } else {
        gradeForm.scores[q.id] = 0
      }
    })
  } catch (error) {
    console.error('加载数据失败', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 提交评分
const handleSubmit = async () => {
  if (!formRef.value || !score.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await manualGrade(score.value.id, manualScoreTotal.value)
        ElMessage.success('评分提交成功')
        router.push(`/exams/${exam.value?.id}/scores`)
      } catch (error) {
        console.error('提交评分失败', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.score-grade {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.grade-content {
  padding: 20px 0;
}

.question-grade-item {
  margin-bottom: 20px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-content {
  padding: 10px 0;
}

.question-text {
  margin-bottom: 15px;
}

.student-answer {
  margin-top: 15px;
}

.no-questions {
  padding: 40px 0;
  text-align: center;
}
</style>

