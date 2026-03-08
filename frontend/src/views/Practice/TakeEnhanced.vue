<template>
  <div class="practice-take-enhanced">
    <!-- 背景装饰 -->
    <DuoBackground />

    <div class="practice-container">
      <!-- 进度卡片 -->
      <DuoCard class="progress-card duo-animate-fade-in" variant="info">
        <div class="progress-header">
          <div>
            <h3>{{ practice?.unit_name || '练习' }}</h3>
            <p class="page-info">第 {{ currentPageOrder + 1 }} / {{ totalPages }} 页</p>
          </div>
          <DuoBadge v-if="pageRecord?.remaining_time" variant="warning" size="large">
            {{ formatTime(pageRecord.remaining_time) }}
          </DuoBadge>
        </div>
        <DuoProgress
          :percentage="(currentPageOrder / totalPages) * 100"
          label="整体进度"
          variant="primary"
        />
      </DuoCard>

      <!-- 题目卡片 -->
      <DuoCard
        v-for="(mainQuestion, mainIndex) in mainQuestions"
        :key="mainQuestion.id"
        class="question-card duo-animate-slide-up"
      >
        <template #header>
          <div class="question-header">
            <h4>{{ mainIndex + 1 }}. {{ mainQuestion.question_text }}</h4>
            <DuoBadge :variant="getQuestionBadgeType(mainQuestion.question_type)">
              {{ getQuestionTypeText(mainQuestion.question_type) }}
            </DuoBadge>
          </div>
        </template>

        <!-- 媒体播放器 -->
        <div v-if="mainQuestion.media_material_id" class="media-section">
          <audio
            :ref="el => setAudioRef(el, mainQuestion.id)"
            :src="getMediaUrl(mainQuestion)"
            controls
            class="audio-player"
          ></audio>
          <div class="play-stats">
            <span>最多播放: {{ mainQuestion.maximum_play || '∞' }}</span>
            <span>已播放: {{ getPlayCount(mainQuestion.id) }} 次</span>
          </div>
        </div>

        <!-- 小题列表 -->
        <div
          v-for="(subQuestion, subIndex) in mainQuestion.sub_questions"
          :key="subQuestion.id"
          class="sub-question-item"
        >
          <div class="sub-question-title">
            <span class="question-number">{{ mainIndex + 1 }}.{{ subIndex + 1 }}</span>
            <span>{{ subQuestion.question_text }}</span>
          </div>

          <!-- 主观题答案输入 + AI评分 -->
          <div v-if="isSubjectiveQuestion(subQuestion)" class="subjective-answer-section">
            <el-input
              v-model="answers[subQuestion.id]"
              type="textarea"
              :rows="6"
              placeholder="请输入您的答案..."
              maxlength="2000"
              show-word-limit
              @input="onAnswerChange(subQuestion.id)"
            />

            <!-- AI评分按钮 -->
            <div class="ai-actions">
              <DuoButton
                variant="success"
                size="medium"
                :loading="aiScoring[subQuestion.id]"
                :disabled="!answers[subQuestion.id]"
                @click="requestAIScoring(subQuestion)"
              >
                {{ aiScoring[subQuestion.id] ? 'AI评分中...' : '🤖 AI智能评分' }}
              </DuoButton>
              <span v-if="!answers[subQuestion.id]" class="hint-text">
                请先输入答案
              </span>
            </div>

            <!-- AI评分反馈 -->
            <ScoringFeedback
              v-if="scoringResults[subQuestion.id]"
              :scoring-result="scoringResults[subQuestion.id]"
              class="duo-animate-slide-up"
            />
          </div>

          <!-- 其他题型（选择题、填空题等） -->
          <div v-else class="answer-input">
            <!-- 选择题 -->
            <el-radio-group
              v-if="subQuestion.question_type === 'choice'"
              v-model="answers[subQuestion.id]"
              @change="onAnswerChange(subQuestion.id)"
            >
              <el-radio
                v-for="(option, optIndex) in getChoiceOptions(subQuestion)"
                :key="optIndex"
                :label="option.value"
                class="choice-option"
              >
                {{ String.fromCharCode(65 + optIndex) }}. {{ option.text }}
              </el-radio>
            </el-radio-group>

            <!-- 填空题 -->
            <div v-else-if="subQuestion.question_type === 'blank'" class="blank-inputs">
              <div
                v-for="(blank, blankIndex) in getBlankCount(subQuestion)"
                :key="blankIndex"
                class="blank-item"
              >
                <span>空{{ blankIndex + 1 }}：</span>
                <el-input
                  v-model="answers[subQuestion.id + '_' + blankIndex]"
                  placeholder="请输入答案"
                  @input="onAnswerChange(subQuestion.id)"
                />
              </div>
            </div>

            <!-- 理解导向提示（选择/填空）：分级请求 -->
            <div v-if="canShowHint(subQuestion)" class="hint-section">
              <div class="hint-actions">
                <span class="hint-label">需要提示？</span>
                <DuoButton
                  variant="info"
                  size="small"
                  :loading="hintLoading[subQuestion.id]"
                  @click="requestHint(subQuestion, 1)"
                >
                  轻提示
                </DuoButton>
                <DuoButton
                  variant="warning"
                  size="small"
                  :loading="hintLoading[subQuestion.id]"
                  @click="requestHint(subQuestion, 2)"
                >
                  方向提示
                </DuoButton>
                <DuoButton
                  variant="success"
                  size="small"
                  :loading="hintLoading[subQuestion.id]"
                  @click="requestHint(subQuestion, 3)"
                >
                  详细解释
                </DuoButton>
              </div>
              <HintPanel
                v-if="hintResults[subQuestion.id]"
                :hint-content="hintResults[subQuestion.id].content"
                :level="hintResults[subQuestion.id].level"
                :request-time="hintResults[subQuestion.id].request_time"
              />
            </div>
          </div>
        </div>
      </DuoCard>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <DuoButton variant="secondary" size="large" @click="savePage" :loading="saving">
          💾 保存当前页
        </DuoButton>
        <DuoButton
          v-if="isLastPage"
          variant="primary"
          size="large"
          @click="handleSubmit"
          :disabled="submitting"
        >
          ✅ 提交练习
        </DuoButton>
        <DuoButton v-else variant="primary" size="large" @click="nextPage">
          下一页 →
        </DuoButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import DuoButton from '@/components/common/DuoButton.vue'
import DuoCard from '@/components/common/DuoCard.vue'
import DuoProgress from '@/components/common/DuoProgress.vue'
import DuoBadge from '@/components/common/DuoBadge.vue'
import DuoBackground from '@/components/common/DuoBackground.vue'
import ScoringFeedback from '@/components/common/ScoringFeedback.vue'
import HintPanel from '@/components/common/HintPanel.vue'
import { scoringApi } from '@/api/scoring'
import { hintsApi } from '@/api/hints'
import { playSuccessAnimation, playErrorShake } from '@/utils/duoAnimations'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(false)
const saving = ref(false)
const submitting = ref(false)
const practice = ref<any>(null)
const pages = ref<any[]>([])
const currentPageOrder = ref(0)
const pageRecord = ref<any>(null)
const mainQuestions = ref<any[]>([])
const answers = ref<Record<number | string, any>>({})
const audioRefs = ref<Record<number, HTMLAudioElement>>({})
const playCounts = ref<Record<number, number>>({})

// AI评分相关
const aiScoring = ref<Record<number, boolean>>({})
const scoringResults = ref<Record<number, any>>({})

// AI 提示相关（选择/填空）
const hintLoading = ref<Record<number, boolean>>({})
const hintResults = ref<Record<number, { content: string; level: number; request_time: string }>>({})

// 计算属性
const totalPages = computed(() => pages.value.length)
const isLastPage = computed(() => currentPageOrder.value === totalPages.value - 1)

// 判断是否为主观题
const isSubjectiveQuestion = (subQuestion: any) => {
  return subQuestion.question_type === 'comprehension' ||
         subQuestion.question_type === 'text' ||
         !subQuestion.question_type
}

// 获取题型徽章类型
const getQuestionBadgeType = (type: string) => {
  const typeMap: Record<string, any> = {
    choice: 'success',
    comprehension: 'primary',
    blank: 'warning',
    matching: 'info'
  }
  return typeMap[type] || 'secondary'
}

// 获取题型文本
const getQuestionTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    choice: '选择题',
    comprehension: '主观题',
    blank: '填空题',
    matching: '匹配题',
    correction: '改错题',
    text: '简答题'
  }
  return typeMap[type] || '未知题型'
}

// AI评分请求
const requestAIScoring = async (subQuestion: any) => {
  const studentAnswer = answers.value[subQuestion.id]
  if (!studentAnswer || !studentAnswer.trim()) {
    ElMessage.warning('请先输入答案')
    return
  }

  aiScoring.value[subQuestion.id] = true

  try {
    const response = await scoringApi.subjective({
      sub_question_id: subQuestion.id,
      student_answer: studentAnswer,
      transcript: subQuestion.main_question?.media_material?.transcript || ''
    })

    scoringResults.value[subQuestion.id] = response
    ElMessage.success('AI评分完成！')
  } catch (error: any) {
    console.error('AI评分失败:', error)
    ElMessage.error(error.message || 'AI评分失败，请稍后重试')
  } finally {
    aiScoring.value[subQuestion.id] = false
  }
}

// 格式化时间
const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 设置音频引用
const setAudioRef = (el: any, questionId: number) => {
  if (el) {
    audioRefs.value[questionId] = el
  }
}

// 获取媒体URL
const getMediaUrl = (mainQuestion: any): string => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  if (mainQuestion.media_material_url) {
    if (mainQuestion.media_material_url.startsWith('http')) {
      return mainQuestion.media_material_url
    }
    const url = mainQuestion.media_material_url.startsWith('/') ? mainQuestion.media_material_url : `/${mainQuestion.media_material_url}`
    return `${apiBaseUrl}${url}`
  }
  return ''
}

// 获取播放次数
const getPlayCount = (questionId: number) => {
  return playCounts.value[questionId] || 0
}

// 是否显示提示入口（选择题、填空题）
const canShowHint = (subQuestion: any) => {
  const t = subQuestion?.question_type
  return t === 'choice' || t === 'blank'
}

// 请求分级提示
const requestHint = async (subQuestion: any, level: 1 | 2 | 3) => {
  hintLoading.value[subQuestion.id] = true
  try {
    const mainQ = mainQuestions.value.find((mq: any) => mq.sub_questions?.some((sq: any) => sq.id === subQuestion.id))
    const transcript = (mainQ && typeof mainQ.media_material === 'object' && mainQ.media_material?.transcript) ? mainQ.media_material.transcript : ''
    const result = await hintsApi.request({
      sub_question_id: subQuestion.id,
      level,
      transcript,
      context: { page_id: pageRecord.value?.id }
    })
    hintResults.value[subQuestion.id] = {
      content: result.content,
      level: result.level,
      request_time: result.request_time
    }
    ElMessage.success('已获取提示')
  } catch (e: any) {
    ElMessage.error(e?.message || '获取提示失败')
  } finally {
    hintLoading.value[subQuestion.id] = false
  }
}

// 获取选择题选项（与后端 SubQuestionSerializer options 一致）
const getChoiceOptions = (subQuestion: any) => {
  const opts = subQuestion?.options || []
  return opts.map((o: any) => ({
    value: o.option_label || o.option_content,
    text: o.option_content || ''
  }))
}

// 获取填空题数量（无 blanks 时按答案空数或默认 1）
const getBlankCount = (subQuestion: any) => {
  const blanks = subQuestion?.blanks
  if (Array.isArray(blanks) && blanks.length > 0) return blanks.length
  const ans = subQuestion?.answer
  if (typeof ans === 'string' && ans.includes('|')) return ans.split('|').length
  return 1
}

// 答案变化处理
const onAnswerChange = (questionId: number) => {
  // 清除该题的AI评分结果
  if (scoringResults.value[questionId]) {
    delete scoringResults.value[questionId]
  }
}

// 保存页面
const savePage = async () => {
  saving.value = true
  try {
    // 实现保存逻辑
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 下一页
const nextPage = () => {
  if (currentPageOrder.value < totalPages.value - 1) {
    currentPageOrder.value++
    // 加载下一页数据
  }
}

// 提交练习
const handleSubmit = async () => {
  try {
    await ElMessageBox.confirm('确定要提交练习吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    submitting.value = true
    // 实现提交逻辑
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('提交成功！')
    router.push({ name: 'PracticeResult', params: { id: route.params.id } })
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('提交失败')
    }
  } finally {
    submitting.value = false
  }
}

// 初始化
onMounted(() => {
  // 加载练习数据
  loading.value = true
  // TODO: 实现数据加载逻辑
  setTimeout(() => {
    loading.value = false
  }, 500)
})
</script>

<style scoped lang="scss">
@use '@/styles/duolingo-design-system.scss' as *;

.practice-take-enhanced {
  min-height: 100vh;
  padding: $duo-spacing-6 $duo-spacing-4;
  position: relative;
}

.practice-container {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: $duo-spacing-6;
  position: relative;
  z-index: 1;
}

// 进度卡片
.progress-card {
  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $duo-spacing-4;

    h3 {
      font-size: $duo-font-size-2xl;
      font-weight: $duo-font-weight-bold;
      color: $duo-text-primary;
      margin: 0 0 $duo-spacing-1;
    }

    .page-info {
      font-size: $duo-font-size-sm;
      color: $duo-text-secondary;
      margin: 0;
    }
  }
}

// 题目卡片
.question-card {
  .question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: $duo-spacing-3;

    h4 {
      font-size: $duo-font-size-lg;
      font-weight: $duo-font-weight-semibold;
      color: $duo-text-primary;
      margin: 0;
      flex: 1;
    }
  }
}

// 媒体区域
.media-section {
  margin: $duo-spacing-4 0;
  padding: $duo-spacing-4;
  background: $duo-gray-300;
  border-radius: $duo-radius-lg;

  .audio-player {
    width: 100%;
    margin-bottom: $duo-spacing-2;
  }

  .play-stats {
    display: flex;
    gap: $duo-spacing-4;
    font-size: $duo-font-size-sm;
    color: $duo-text-secondary;
  }
}

// 小题
.sub-question-item {
  margin-top: $duo-spacing-5;
  padding-top: $duo-spacing-5;
  border-top: 2px solid $duo-gray-400;

  &:first-child {
    margin-top: 0;
    padding-top: 0;
    border-top: none;
  }
}

.sub-question-title {
  display: flex;
  gap: $duo-spacing-2;
  margin-bottom: $duo-spacing-3;
  font-size: $duo-font-size-base;
  font-weight: $duo-font-weight-semibold;
  color: $duo-text-primary;

  .question-number {
    color: $duo-blue-primary;
    font-weight: $duo-font-weight-bold;
  }
}

// 主观题答案区域
.subjective-answer-section {
  display: flex;
  flex-direction: column;
  gap: $duo-spacing-3;

  .ai-actions {
    display: flex;
    align-items: center;
    gap: $duo-spacing-3;

    .hint-text {
      font-size: $duo-font-size-sm;
      color: $duo-text-tertiary;
    }
  }
}

// 其他题型答案区域
.answer-input {
  .choice-option {
    display: block;
    margin-bottom: $duo-spacing-3;
    padding: $duo-spacing-3;
    border-radius: $duo-radius-base;
    transition: background $duo-duration-base;

    &:hover {
      background: $duo-gray-300;
    }
  }
}

.blank-inputs {
  display: flex;
  flex-direction: column;
  gap: $duo-spacing-3;

  .blank-item {
    display: flex;
    align-items: center;
    gap: $duo-spacing-2;

    span {
      min-width: 60px;
      font-weight: $duo-font-weight-semibold;
      color: $duo-text-secondary;
    }
  }
}

.hint-section {
  margin-top: $duo-spacing-4;
  padding-top: $duo-spacing-3;
  border-top: 1px solid $duo-gray-400;

  .hint-actions {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: $duo-spacing-2;
    margin-bottom: $duo-spacing-2;

    .hint-label {
      font-size: $duo-font-size-sm;
      color: $duo-text-secondary;
      margin-right: $duo-spacing-2;
    }
  }
}

// 操作按钮
.action-buttons {
  display: flex;
  gap: $duo-spacing-4;
  justify-content: center;
  padding: $duo-spacing-4 0;
}

@include duo-responsive(md) {
  .practice-container {
    padding: 0 $duo-spacing-6;
  }
}
</style>
