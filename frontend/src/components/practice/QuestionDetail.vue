<template>
  <div class="question-detail">
    <div class="question-header">
      <h5>{{ question.question_text }}</h5>
      <el-tag>{{ getQuestionTypeText(question.question_type) }}</el-tag>
    </div>
    
    <div v-if="question.options && question.options.length > 0" class="options">
      <div 
        v-for="(option, index) in question.options" 
        :key="index"
        class="option-item"
        :class="{
          'user-answer': isUserAnswer(option),
          'correct-answer': isCorrectAnswer(option)
        }"
      >
        {{ String.fromCharCode(65 + index) }}. {{ option }}
      </div>
    </div>
    
    <div v-else-if="question.question_type === 'choice'" class="options">
      <div class="option-item">
        没有选项数据
      </div>
    </div>
    
    <div class="answers">
      <div class="answer-item">
        <span class="label">你的答案：</span>
        <span class="content">{{ userAnswer }}</span>
      </div>
      <div class="answer-item">
        <span class="label">正确答案：</span>
        <span class="content correct">{{ correctAnswer }}</span>
      </div>
    </div>
    
    <!-- 答案出处 -->
    <div v-if="answerSource" class="answer-source">
      <span class="label">答案出处：</span>
      <span class="content">{{ answerSource }}</span>
    </div>
    
    <div class="score">
      得分：<el-tag :type="score >= 60 ? 'success' : 'danger'">{{ score }}</el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  question: {
    type: Object,
    required: true
  },
  userAnswer: {
    type: String,
    required: true
  },
  correctAnswer: {
    type: String,
    required: true
  },
  score: {
    type: Number,
    required: true
  },
  transcript: {
    type: String,
    default: ''
  }
})

const getQuestionTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    choice: '选择题',
    matching: '匹配题',
    blank: '填空题',
    correction: '改错题',
    comprehension: '理解题',
    text: '文本题'
  }
  return typeMap[type] || type
}

const isUserAnswer = (option: string): boolean => {
  return option === props.userAnswer
}

const isCorrectAnswer = (option: string): boolean => {
  return option === props.correctAnswer
}

// 计算答案出处
const answerSource = computed(() => {
  if (!props.transcript) return ''
  
  const correctAnswer = props.correctAnswer
  if (!correctAnswer) return ''
  
  const transcript = props.transcript
  
  // 对于主观题，提取关键词并在听力文本中查找
  if (props.question.question_type === 'comprehension') {
    // 从正确答案中提取关键词
    const keywords = extractKeywords(correctAnswer)
    
    // 在听力文本中查找包含关键词的句子
    const sentences = transcript.split(/[.!?]+/)
    const relevantSentences = []
    
    for (const sentence of sentences) {
      const sentenceLower = sentence.toLowerCase()
      const hasKeyword = keywords.some(keyword => sentenceLower.includes(keyword.toLowerCase()))
      if (hasKeyword) {
        relevantSentences.push(sentence.trim())
        if (relevantSentences.length >= 2) break // 最多取2个相关句子
      }
    }
    
    if (relevantSentences.length > 0) {
      return relevantSentences.join(' ')
    }
  } else {
    // 对于客观题，直接查找答案
    const transcriptLower = transcript.toLowerCase()
    const answerLower = correctAnswer.toLowerCase()
    
    if (transcriptLower.includes(answerLower)) {
      // 提取包含答案的句子
      const sentences = transcript.split(/[.!?]+/)
      for (const sentence of sentences) {
        if (sentence.toLowerCase().includes(answerLower)) {
          return sentence.trim()
        }
      }
    }
  }
  
  return '听力文本中相关内容'
})

// 提取关键词
const extractKeywords = (text: string): string[] => {
  // 移除标点符号
  const cleanText = text.replace(/[.,!?'";:()]/g, ' ')
  // 分割成单词
  const words = cleanText.split(/\s+/)
  // 过滤掉常见的停用词
  const stopWords = new Set([
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'from', 'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
  ])
  // 提取长度大于3的单词作为关键词
  return words
    .filter(word => word.length > 3 && !stopWords.has(word.toLowerCase()))
    .slice(0, 5) // 最多取5个关键词
}
</script>

<style scoped>
.question-detail {
  background: rgba(255, 255, 255, 0.95);
  padding: 32px;
  border-radius: 24px;
  border: 1px solid rgba(198, 185, 255, 0.2);
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(140, 124, 240, 0.08);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.question-detail:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(140, 124, 240, 0.15);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(198, 185, 255, 0.15);
}

.question-header h5 {
  margin: 0;
  flex: 1;
  color: #5A5A7E;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.6;
  letter-spacing: -0.2px;
}

.question-header :deep(.el-tag) {
  background: linear-gradient(135deg, #E8E4FF 0%, #F0EFFF 100%);
  border: 1px solid rgba(198, 185, 255, 0.4);
  color: #8C7CF0;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
}

.comprehension-tips {
  margin-bottom: 24px;
}

.comprehension-tips :deep(.el-alert) {
  background: linear-gradient(135deg, #F8F7FF 0%, #F0EFFF 100%);
  border: 1px solid rgba(198, 185, 255, 0.3);
  border-radius: 16px;
  padding: 20px;
}

.comprehension-tips :deep(.el-alert__title) {
  color: #8C7CF0;
  font-weight: 700;
  font-size: 15px;
  margin-bottom: 12px;
}

.comprehension-tips :deep(.el-alert__description) {
  color: #5A5A7E;
  font-size: 14px;
  line-height: 1.7;
}

.comprehension-tips ul {
  margin: 0;
  padding-left: 20px;
}

.comprehension-tips li {
  color: #5A5A7E;
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 8px;
}

.options {
  margin-bottom: 24px;
}

.option-item {
  padding: 16px 20px;
  margin-bottom: 12px;
  border-radius: 16px;
  border: 2px solid rgba(198, 185, 255, 0.15);
  font-size: 14px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  color: #5A5A7E;
}

.option-item:hover {
  background: linear-gradient(135deg, #F8F7FF 0%, #F0EFFF 100%);
  border-color: rgba(198, 185, 255, 0.4);
}

.option-item.user-answer {
  background: linear-gradient(135deg, #FFF3CD 0%, #FFE8A1 100%);
  border-color: #FFC107;
  color: #856404;
  box-shadow: 0 4px 16px rgba(255, 193, 7, 0.2);
}

.option-item.correct-answer {
  background: linear-gradient(135deg, #D4F1D9 0%, #C3E6CB 100%);
  border-color: #28A745;
  color: #155724;
  box-shadow: 0 4px 16px rgba(40, 167, 69, 0.2);
}

.answers {
  margin-bottom: 20px;
  padding: 24px;
  background: linear-gradient(135deg, #F8F7FF 0%, #F0EFFF 100%);
  border-radius: 20px;
  border: 1px solid rgba(198, 185, 255, 0.2);
}

.answer-item {
  display: flex;
  margin-bottom: 16px;
  font-size: 14px;
  align-items: flex-start;
}

.answer-item:last-child {
  margin-bottom: 0;
}

.answer-item .label {
  min-width: 100px;
  font-weight: 700;
  color: #8C7CF0;
  font-size: 14px;
  padding-top: 2px;
}

.answer-item .content {
  flex: 1;
  color: #5A5A7E;
  line-height: 1.7;
  font-weight: 500;
}

.answer-item .content.correct {
  color: #28A745;
  font-weight: 600;
  line-height: 1.7;
}

.answer-source {
  display: flex;
  margin-bottom: 20px;
  font-size: 14px;
  padding: 20px;
  background: linear-gradient(135deg, #FFF3CD 0%, #FFE8A1 100%);
  border-radius: 20px;
  border: 1px solid rgba(255, 193, 7, 0.3);
  align-items: flex-start;
}

.answer-source .label {
  min-width: 100px;
  font-weight: 700;
  color: #856404;
  font-size: 14px;
  padding-top: 2px;
}

.answer-source .content {
  flex: 1;
  color: #856404;
  font-style: italic;
  line-height: 1.7;
  font-weight: 500;
}

.score {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 2px solid rgba(198, 185, 255, 0.15);
  font-size: 15px;
  font-weight: 700;
  color: #5A5A7E;
  display: flex;
  align-items: center;
  gap: 12px;
}

.score :deep(.el-tag) {
  padding: 10px 20px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.15);
}

.score :deep(.el-tag--success) {
  background: linear-gradient(135deg, #D4F1D9 0%, #C3E6CB 100%);
  border-color: #28A745;
  color: #155724;
}

.score :deep(.el-tag--danger) {
  background: linear-gradient(135deg, #F8D7DA 0%, #F5C6CB 100%);
  border-color: #DC3545;
  color: #721C24;
}
</style>

