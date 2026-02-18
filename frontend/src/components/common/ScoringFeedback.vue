<template>
  <div class="scoring-feedback duolingo-style">
    <div v-if="loading" class="loading">
      <el-icon class="is-loading"><loading /></el-icon>
      <span>AI正在评分...</span>
    </div>

    <div v-else-if="error" class="error">
      <el-icon><warning /></el-icon>
      <span>{{ error }}</span>
    </div>

    <div v-else-if="scoringResult" class="feedback-content">
      <div class="score-overview">
        <div class="total-score">
          <div class="score-value">{{ Math.round(scoringResult.total_score) }}</div>
          <div class="score-label">总分</div>
        </div>
        <div class="dimension-scores">
          <div class="dimension-item">
            <div class="dimension-label">内容准确性</div>
            <el-progress :percentage="scoringResult.content_accuracy" :color="getScoreColor(scoringResult.content_accuracy)" :stroke-width="12" />
          </div>
          <div class="dimension-item">
            <div class="dimension-label">语言表达</div>
            <el-progress :percentage="scoringResult.language_expression" :color="getScoreColor(scoringResult.language_expression)" :stroke-width="12" />
          </div>
          <div class="dimension-item">
            <div class="dimension-label">完整性</div>
            <el-progress :percentage="scoringResult.completeness" :color="getScoreColor(scoringResult.completeness)" :stroke-width="12" />
          </div>
          <div class="dimension-item">
            <div class="dimension-label">逻辑连贯性</div>
            <el-progress :percentage="scoringResult.logical_coherence" :color="getScoreColor(scoringResult.logical_coherence)" :stroke-width="12" />
          </div>
        </div>
      </div>

      <div v-if="scoringResult.feedback" class="feedback-section">
        <h4><el-icon><chat-line-round /></el-icon> 整体反馈</h4>
        <p>{{ scoringResult.feedback }}</p>
      </div>

      <div v-if="scoringResult.suggestions && scoringResult.suggestions.length > 0" class="feedback-section">
        <h4><el-icon><edit-pen /></el-icon> 改进建议</h4>
        <ul>
          <li v-for="(suggestion, index) in scoringResult.suggestions" :key="index">
            {{ suggestion }}
          </li>
        </ul>
      </div>

      <div v-if="scoringResult.grammar_errors && scoringResult.grammar_errors.length > 0" class="feedback-section">
        <h4><el-icon><document /></el-icon> 语法错误</h4>
        <div v-for="(error, index) in scoringResult.grammar_errors" :key="index" class="error-item">
          <div class="error-location">{{ error.location }}</div>
          <div class="error-content">
            <span class="error-type">{{ error.error }}</span>
            <span class="arrow">→</span>
            <span class="error-correction">{{ error.correction }}</span>
          </div>
        </div>
      </div>

      <div v-if="scoringResult.vocabulary_suggestions && scoringResult.vocabulary_suggestions.length > 0" class="feedback-section">
        <h4><el-icon><reading /></el-icon> 词汇提升</h4>
        <div v-for="(vocab, index) in scoringResult.vocabulary_suggestions" :key="index" class="vocab-item">
          <div class="vocab-change">
            <span class="vocab-original">{{ vocab.word }}</span>
            <el-icon><right /></el-icon>
            <span class="vocab-better">{{ vocab.better }}</span>
          </div>
          <div class="vocab-reason">{{ vocab.reason }}</div>
        </div>
      </div>

      <div class="score-time">
        <el-icon><clock /></el-icon>
        <span>评分时间: {{ scoringResult.score_time }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Warning, ChatLineRound, EditPen, Document, Reading, Right, Clock } from '@element-plus/icons-vue'
import { scoringApi, type AIScoringResponse } from '@/api/scoring'

interface Props {
  subQuestionId: number
  studentAnswer: string
  transcript?: string
  autoScore?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoScore: false
})

const emit = defineEmits<{
  scored: [result: AIScoringResponse]
  error: [error: string]
}>()

const loading = ref(false)
const error = ref('')
const scoringResult = ref<AIScoringResponse | null>(null)

const getScoreColor = (score: number) => {
  if (score >= 80) return '#58cc02'  // Duolingo green
  if (score >= 60) return '#ffc800'  // Duolingo yellow
  return '#ff4b4b'  // Duolingo red
}

const score = async () => {
  if (!props.studentAnswer || !props.studentAnswer.trim()) {
    ElMessage.warning('请先填写答案')
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await scoringApi.subjective({
      sub_question_id: props.subQuestionId,
      student_answer: props.studentAnswer,
      transcript: props.transcript
    })

    scoringResult.value = response
    emit('scored', response)
    ElMessage.success('AI评分完成')
  } catch (err: any) {
    console.error('评分错误详情:', err)
    error.value = err.response?.data?.message || err.message || '评分失败，请稍后重试'
    emit('error', error.value)
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const reset = () => {
  scoringResult.value = null
  error.value = ''
}

defineExpose({
  score,
  reset
})

if (props.autoScore && props.studentAnswer) {
  score()
}
</script>

<style scoped>
/* Duolingo风格样式 */
.scoring-feedback.duolingo-style {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  margin-top: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 2px solid #e5e5e5;
}

.loading,
.error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 48px 20px;
  font-size: 18px;
  font-weight: 600;
  color: #4b4b4b;
}

.error {
  color: #ff4b4b;
}

.feedback-content {
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.score-overview {
  display: flex;
  gap: 32px;
  margin-bottom: 28px;
  padding-bottom: 28px;
  border-bottom: 2px solid #e5e5e5;
}

.total-score {
  flex-shrink: 0;
  text-align: center;
  padding: 28px;
  background: linear-gradient(135deg, #58cc02 0%, #4caf50 100%);
  border-radius: 20px;
  box-shadow: 0 6px 20px rgba(88, 204, 2, 0.3);
  min-width: 140px;
}

.score-value {
  font-size: 56px;
  font-weight: 800;
  color: #ffffff;
  line-height: 1;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.score-label {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  opacity: 0.9;
}

.dimension-scores {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 18px;
}

.dimension-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.dimension-label {
  width: 110px;
  font-size: 15px;
  font-weight: 700;
  color: #4b4b4b;
  flex-shrink: 0;
}

.feedback-section {
  margin-bottom: 28px;
}

.feedback-section h4 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 800;
  color: #1cb0f6;
}

.feedback-section p {
  margin: 0;
  line-height: 1.8;
  color: #4b4b4b;
  padding: 18px;
  background: #f7f7f7;
  border-radius: 12px;
  border-left: 5px solid #1cb0f6;
  font-size: 15px;
}

.feedback-section ul {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.feedback-section li {
  position: relative;
  padding: 14px 18px 14px 48px;
  margin-bottom: 12px;
  background: #f7f7f7;
  border-radius: 12px;
  line-height: 1.7;
  color: #4b4b4b;
  font-size: 15px;
  font-weight: 500;
}

.feedback-section li::before {
  content: '💡';
  position: absolute;
  left: 16px;
  font-size: 20px;
}

.error-item {
  padding: 18px;
  margin-bottom: 12px;
  background: #fff4f4;
  border-radius: 12px;
  border-left: 5px solid #ff4b4b;
}

.error-location {
  font-size: 13px;
  color: #777;
  margin-bottom: 8px;
  font-weight: 600;
}

.error-content {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
}

.error-type {
  color: #ff4b4b;
  font-weight: 700;
}

.arrow {
  color: #777;
  font-weight: 700;
}

.error-correction {
  color: #58cc02;
  font-weight: 700;
}

.vocab-item {
  padding: 18px;
  margin-bottom: 12px;
  background: #f0f9ff;
  border-radius: 12px;
  border-left: 5px solid #1cb0f6;
}

.vocab-change {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 15px;
}

.vocab-original {
  color: #777;
  text-decoration: line-through;
  font-weight: 600;
}

.vocab-better {
  color: #1cb0f6;
  font-weight: 800;
}

.vocab-reason {
  font-size: 13px;
  color: #4b4b4b;
  margin-top: 6px;
  font-weight: 500;
}

.score-time {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 18px;
  border-top: 2px solid #e5e5e5;
  font-size: 13px;
  color: #777;
  font-weight: 600;
}
</style>
