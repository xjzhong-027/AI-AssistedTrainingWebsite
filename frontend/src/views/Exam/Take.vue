<template>
  <div class="exam-take">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div>
            <h3>{{ exam?.title }}</h3>
            <div class="exam-info">
              <span>剩余时间：</span>
              <el-tag :type="timeLeftType" size="large" style="font-size: 16px; padding: 0 10px">
                {{ formatTimeLeft(timeLeft) }}
              </el-tag>
            </div>
          </div>
          <el-button type="danger" @click="handleSubmit" :disabled="submitting">
            提交考试
          </el-button>
        </div>
      </template>

      <div v-if="exam && questions.length > 0" class="exam-content">
        <!-- 题目导航 -->
        <div class="question-nav">
          <div class="nav-title">题目导航</div>
          <div class="nav-buttons">
            <el-button
              v-for="(q, index) in questions"
              :key="q.id"
              :type="getQuestionButtonType(index)"
              :icon="getQuestionIcon(index)"
              circle
              @click="currentIndex = index"
            >
              {{ index + 1 }}
            </el-button>
          </div>
        </div>

        <!-- 答题区域 -->
        <div class="answer-area">
          <div class="question-header">
            <span class="question-number">第 {{ currentIndex + 1 }} 题 / 共 {{ questions.length }} 题</span>
            <span class="question-score">分值：{{ currentQuestion.score }} 分</span>
          </div>

          <div class="question-content">
            <div class="question-type">
              <el-tag>{{ getQuestionTypeText(currentQuestion.type) }}</el-tag>
            </div>
            <div class="question-text">{{ currentQuestion.content }}</div>

            <!-- 单选题 -->
            <div v-if="currentQuestion.type === 'SINGLE_CHOICE'" class="answer-options">
              <el-radio-group v-model="answers[currentIndex]">
                <el-radio
                  v-for="(option, index) in getParsedOptions(currentQuestion.options)"
                  :key="index"
                  :label="String.fromCharCode(65 + index)"
                  style="display: block; margin-bottom: 15px"
                >
                  <strong>{{ String.fromCharCode(65 + index) }}.</strong> {{ option }}
                </el-radio>
              </el-radio-group>
            </div>

            <!-- 多选题 -->
            <div v-if="currentQuestion.type === 'MULTIPLE_CHOICE'" class="answer-options">
              <el-checkbox-group v-model="answers[currentIndex]">
                <el-checkbox
                  v-for="(option, index) in getParsedOptions(currentQuestion.options)"
                  :key="index"
                  :label="String.fromCharCode(65 + index)"
                  style="display: block; margin-bottom: 15px"
                >
                  <strong>{{ String.fromCharCode(65 + index) }}.</strong> {{ option }}
                </el-checkbox>
              </el-checkbox-group>
            </div>

            <!-- 判断题 -->
            <div v-if="currentQuestion.type === 'TRUE_FALSE'" class="answer-options">
              <el-radio-group v-model="answers[currentIndex]">
                <el-radio label="A" style="display: block; margin-bottom: 15px">A. 正确</el-radio>
                <el-radio label="B" style="display: block; margin-bottom: 15px">B. 错误</el-radio>
              </el-radio-group>
            </div>

            <!-- 简答题 -->
            <div v-if="currentQuestion.type === 'SHORT_ANSWER'" class="answer-textarea">
              <el-input
                v-model="answers[currentIndex]"
                type="textarea"
                :rows="10"
                placeholder="请输入您的答案"
                maxlength="2000"
                show-word-limit
              />
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="question-actions">
            <el-button :disabled="currentIndex === 0" @click="prevQuestion">上一题</el-button>
            <el-button type="primary" @click="saveAnswer">保存答案</el-button>
            <el-button :disabled="currentIndex === questions.length - 1" @click="nextQuestion">
              下一题
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExamById } from '@/api/exam'
import { getQuestionsByExamId } from '@/api/question'
import { participateExam, submitAnswer, submitExam, getExamRecordById } from '@/api/answer'
import { useUserStore } from '@/stores/user'
import { formatDuration } from '@/utils/format'
import type { Exam } from '@/types/exam'
import type { Question } from '@/types/question'
import type { ExamRecord } from '@/types/answer'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const exam = ref<Exam | null>(null)
const questions = ref<Question[]>([])
const examRecord = ref<ExamRecord | null>(null)
const currentIndex = ref(0)
const answers = ref<(string | string[])[]>([])
const timeLeft = ref(0) // 剩余时间（秒）
let timer: number | null = null

const currentQuestion = computed(() => questions.value[currentIndex.value] || questions.value[0])

// 格式化剩余时间
const formatTimeLeft = (seconds: number): string => {
  if (seconds <= 0) return '00:00:00'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

const timeLeftType = computed(() => {
  if (timeLeft.value <= 300) return 'danger' // 5分钟
  if (timeLeft.value <= 600) return 'warning' // 10分钟
  return 'success'
})

// 获取题目类型文本
const getQuestionTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    SINGLE_CHOICE: '单选题',
    MULTIPLE_CHOICE: '多选题',
    TRUE_FALSE: '判断题',
    SHORT_ANSWER: '简答题'
  }
  return typeMap[type] || type
}

// 解析选项
const getParsedOptions = (optionsStr?: string): string[] => {
  if (!optionsStr) return []
  try {
    return JSON.parse(optionsStr)
  } catch {
    return []
  }
}

// 获取题目按钮类型
const getQuestionButtonType = (index: number): string => {
  if (index === currentIndex.value) return 'primary'
  if (answers.value[index] && answers.value[index] !== '') return 'success'
  return 'default'
}

// 获取题目图标
const getQuestionIcon = (index: number) => {
  if (answers.value[index] && answers.value[index] !== '') return 'Check'
  return ''
}

// 上一题
const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

// 下一题
const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
  }
}

// 保存答案
const saveAnswer = async () => {
  if (!examRecord.value) return

  const answer = answers.value[currentIndex.value]
  if (!answer || (Array.isArray(answer) && answer.length === 0)) {
    ElMessage.warning('请先选择或输入答案')
    return
  }

  try {
    const answerContent = Array.isArray(answer) ? answer.join(',') : answer
    await submitAnswer({
      examRecordId: examRecord.value.id,
      questionId: currentQuestion.value.id,
      answerContent
    })
    ElMessage.success('答案已保存')
  } catch (error) {
    console.error('保存答案失败', error)
  }
}

// 提交考试
const handleSubmit = async () => {
  if (!examRecord.value) return

  try {
    await ElMessageBox.confirm('确定要提交考试吗？提交后将无法修改答案。', '提示', {
      confirmButtonText: '确定提交',
      cancelButtonText: '取消',
      type: 'warning'
    })

    submitting.value = true
    await submitExam(examRecord.value.id)
    
    // 自动计算成绩
    try {
      const { calculateScore } = await import('@/api/score')
      await calculateScore(examRecord.value.id)
      ElMessage.success('考试提交成功，成绩已自动计算')
    } catch (error) {
      console.error('计算成绩失败', error)
      ElMessage.warning('考试提交成功，但成绩计算失败，请稍后查看')
    }
    
    router.push('/scores')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交失败', error)
    }
  } finally {
    submitting.value = false
  }
}

// 初始化
const init = async () => {
  const examId = Number(route.params.id)
  if (!examId || !userStore.userInfo?.id) {
    router.push('/exams')
    return
  }

  loading.value = true
  try {
    // 加载考试信息
    exam.value = await getExamById(examId)
    if (!exam.value) {
      ElMessage.error('考试不存在')
      router.push('/exams')
      return
    }

    // 加载题目
    questions.value = await getQuestionsByExamId(examId)
    if (questions.value.length === 0) {
      ElMessage.error('该考试暂无题目')
      router.push('/exams')
      return
    }

    // 初始化答案数组
    answers.value = new Array(questions.value.length).fill('')

    // 参加考试
    examRecord.value = await participateExam(examId, userStore.userInfo.id)

    // 计算剩余时间（分钟转秒）
    const durationSeconds = exam.value.duration * 60
    const startTime = new Date(examRecord.value.startTime).getTime()
    const now = Date.now()
    const elapsed = Math.floor((now - startTime) / 1000)
    timeLeft.value = Math.max(0, durationSeconds - elapsed)

    // 启动倒计时
    timer = window.setInterval(() => {
      timeLeft.value--
      if (timeLeft.value <= 0) {
        if (timer) clearInterval(timer)
        ElMessage.warning('考试时间已到，将自动提交')
        handleSubmit()
      }
    }, 1000)
  } catch (error) {
    console.error('初始化失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  init()
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
.exam-take {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0 0 10px 0;
}

.exam-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.exam-content {
  display: flex;
  gap: 20px;
}

.question-nav {
  width: 200px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.nav-title {
  font-weight: bold;
  margin-bottom: 15px;
}

.nav-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.answer-area {
  flex: 1;
}

.question-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.question-number {
  font-weight: bold;
  font-size: 16px;
}

.question-score {
  color: #409eff;
  font-weight: bold;
}

.question-content {
  margin-bottom: 30px;
}

.question-type {
  margin-bottom: 15px;
}

.question-text {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.answer-options {
  padding: 20px;
}

.answer-textarea {
  padding: 20px;
}

.question-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}
</style>
