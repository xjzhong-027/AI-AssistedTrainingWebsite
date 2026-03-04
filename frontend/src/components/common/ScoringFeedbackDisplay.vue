<template>
  <div class="scoring-feedback-display">
    <div class="score-overview">
      <div class="total-score">
        <div class="score-value">{{ Math.round(feedback.total_score ?? 0) }}</div>
        <div class="score-label">总分</div>
      </div>
      <div class="dimension-scores">
        <div class="dimension-item">
          <div class="dimension-label">内容准确性</div>
          <el-progress :percentage="feedback.content_accuracy ?? 0" :color="getScoreColor(feedback.content_accuracy ?? 0)" :stroke-width="10" />
        </div>
        <div class="dimension-item">
          <div class="dimension-label">语言表达</div>
          <el-progress :percentage="feedback.language_expression ?? 0" :color="getScoreColor(feedback.language_expression ?? 0)" :stroke-width="10" />
        </div>
        <div class="dimension-item">
          <div class="dimension-label">完整性</div>
          <el-progress :percentage="feedback.completeness ?? 0" :color="getScoreColor(feedback.completeness ?? 0)" :stroke-width="10" />
        </div>
        <div class="dimension-item">
          <div class="dimension-label">逻辑连贯性</div>
          <el-progress :percentage="feedback.logical_coherence ?? 0" :color="getScoreColor(feedback.logical_coherence ?? 0)" :stroke-width="10" />
        </div>
      </div>
    </div>

    <div v-if="feedback.feedback" class="feedback-section">
      <h4><el-icon><ChatLineRound /></el-icon> 整体反馈</h4>
      <p>{{ feedback.feedback }}</p>
    </div>

    <div v-if="feedback.suggestions && feedback.suggestions.length > 0" class="feedback-section">
      <h4><el-icon><EditPen /></el-icon> 改进建议</h4>
      <ul>
        <li v-for="(suggestion, index) in feedback.suggestions" :key="index">
          {{ suggestion }}
        </li>
      </ul>
    </div>

    <div v-if="feedback.grammar_errors && feedback.grammar_errors.length > 0" class="feedback-section">
      <h4><el-icon><Document /></el-icon> 语法错误</h4>
      <div v-for="(error, index) in feedback.grammar_errors" :key="index" class="error-item">
        <div class="error-location">{{ error.location }}</div>
        <div class="error-content">
          <span class="error-type">{{ error.error }}</span>
          <span class="arrow">→</span>
          <span class="error-correction">{{ error.correction }}</span>
        </div>
      </div>
    </div>

    <div v-if="feedback.vocabulary_suggestions && feedback.vocabulary_suggestions.length > 0" class="feedback-section">
      <h4><el-icon><Reading /></el-icon> 词汇提升</h4>
      <div v-for="(vocab, index) in feedback.vocabulary_suggestions" :key="index" class="vocab-item">
        <div class="vocab-change">
          <span class="vocab-original">{{ vocab.word }}</span>
          <el-icon><Right /></el-icon>
          <span class="vocab-better">{{ vocab.better }}</span>
        </div>
        <div class="vocab-reason">{{ vocab.reason }}</div>
      </div>
    </div>

    <div v-if="feedback.score_time" class="score-time">
      <el-icon><Clock /></el-icon>
      <span>评分时间: {{ formatScoreTime(feedback.score_time) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ChatLineRound, EditPen, Document, Reading, Right, Clock } from '@element-plus/icons-vue'

interface Props {
  feedback: {
    id?: number
    content_accuracy?: number
    language_expression?: number
    completeness?: number
    logical_coherence?: number
    total_score?: number
    feedback?: string
    suggestions?: string[]
    grammar_errors?: Array<{ error: string; correction: string; location: string }>
    vocabulary_suggestions?: Array<{ word: string; better: string; reason: string }>
    score_time?: string
  }
}

const props = defineProps<Props>()

const getScoreColor = (score: number) => {
  if (score >= 80) return '#58cc02'
  if (score >= 60) return '#ffc800'
  return '#ff4b4b'
}

const formatScoreTime = (time: string): string => {
  if (!time) return '-'
  return time
}
</script>

<style scoped>
.scoring-feedback-display {
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
}

.score-overview {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e5e5e5;
}

.total-score {
  flex-shrink: 0;
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #58cc02 0%, #4caf50 100%);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(88, 204, 2, 0.3);
  min-width: 100px;
}

.score-value {
  font-size: 42px;
  font-weight: 800;
  color: #ffffff;
  line-height: 1;
  margin-bottom: 4px;
}

.score-label {
  font-size: 14px;
  font-weight: 700;
  color: #ffffff;
  opacity: 0.9;
}

.dimension-scores {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
}

.dimension-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dimension-label {
  width: 90px;
  font-size: 13px;
  font-weight: 600;
  color: #4b4b4b;
  flex-shrink: 0;
}

.feedback-section {
  margin-bottom: 20px;
}

.feedback-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 700;
  color: #1cb0f6;
}

.feedback-section p {
  margin: 0;
  line-height: 1.7;
  color: #4b4b4b;
  padding: 12px;
  background: #f7f7f7;
  border-radius: 8px;
  border-left: 4px solid #1cb0f6;
  font-size: 14px;
}

.feedback-section ul {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.feedback-section li {
  position: relative;
  padding: 10px 12px 10px 36px;
  margin-bottom: 8px;
  background: #f7f7f7;
  border-radius: 8px;
  line-height: 1.6;
  color: #4b4b4b;
  font-size: 14px;
}

.feedback-section li::before {
  content: '💡';
  position: absolute;
  left: 12px;
  font-size: 16px;
}

.error-item {
  padding: 12px;
  margin-bottom: 8px;
  background: #fff4f4;
  border-radius: 8px;
  border-left: 4px solid #ff4b4b;
}

.error-location {
  font-size: 12px;
  color: #777;
  margin-bottom: 6px;
  font-weight: 600;
}

.error-content {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.error-type {
  color: #ff4b4b;
  font-weight: 600;
}

.arrow {
  color: #777;
  font-weight: 600;
}

.error-correction {
  color: #58cc02;
  font-weight: 600;
}

.vocab-item {
  padding: 12px;
  margin-bottom: 8px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #1cb0f6;
}

.vocab-change {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 14px;
}

.vocab-original {
  color: #777;
  text-decoration: line-through;
  font-weight: 600;
}

.vocab-better {
  color: #1cb0f6;
  font-weight: 700;
}

.vocab-reason {
  font-size: 12px;
  color: #4b4b4b;
  font-weight: 500;
}

.score-time {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-top: 12px;
  border-top: 2px solid #e5e5e5;
  font-size: 12px;
  color: #777;
  font-weight: 600;
}
</style>
