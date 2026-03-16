<template>
  <div v-if="visible" class="ai-question-window" :class="{ 'is-minimized': isMinimized }">
    <div class="ai-window-header">
      <div class="header-left">
        <span class="ai-title">AI出题助手</span>
        <div class="ai-icon-small">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="questionGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#8C7CF0;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#C6B9FF;stop-opacity:1" />
              </linearGradient>
            </defs>
            <g>
              <path d="M12 2L12 4" stroke="url(#questionGradient)" stroke-width="2" stroke-linecap="round" />
              <circle cx="12" cy="1.5" r="1" fill="url(#questionGradient)" />
              <rect
                x="6"
                y="5"
                width="12"
                height="10"
                rx="3"
                stroke="url(#questionGradient)"
                stroke-width="2"
                fill="none"
              />
              <circle cx="9" cy="10" r="1.5" fill="url(#questionGradient)" />
              <circle cx="15" cy="10" r="1.5" fill="url(#questionGradient)" />
              <rect x="10" y="12" width="4" height="1.5" rx="0.5" fill="url(#questionGradient)" />
              <path d="M8 15L8 17" stroke="url(#questionGradient)" stroke-width="2" stroke-linecap="round" />
              <path d="M12 15L12 17" stroke="url(#questionGradient)" stroke-width="2" stroke-linecap="round" />
              <path d="M16 15L16 17" stroke="url(#questionGradient)" stroke-width="2" stroke-linecap="round" />
            </g>
          </svg>
        </div>
      </div>
      <div class="header-right">
        <el-button text circle size="small" @click="toggleMinimize">
          <el-icon><Minus v-if="!isMinimized" /><FullScreen v-else /></el-icon>
        </el-button>
        <el-button text circle size="small" @click="handleClose">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>

    <div v-if="!isMinimized" class="ai-window-content">
      <div v-if="!isGenerating && generatedQuestions.length === 0" class="config-section">
        <div class="config-title">出题配置</div>

        <el-form :model="config" label-width="80px" size="small" class="config-form">
          <el-form-item label="题目类型">
            <el-select
              v-model="config.question_type"
              style="width: 100%"
              @change="handleQuestionTypeChange"
              append-to-body
            >
              <el-option label="选择题" value="choice" />
              <el-option label="填空题" value="fill-blank" />
              <el-option label="主观题" value="comprehension" />
            </el-select>
          </el-form-item>

          <el-form-item v-if="config.question_type === 'fill-blank'" label="考察方向">
            <el-radio-group v-model="config.fill_blank_type" style="width: 100%">
              <el-radio value="transcript">听力原文考察</el-radio>
              <el-radio value="summary">主旨大意考察</el-radio>
            </el-radio-group>
            <div class="fill-blank-hint">
              <span v-if="config.fill_blank_type === 'transcript'" class="hint-text">
                基于听力原文进行挖空，考察学生对原文细节的理解
              </span>
              <span v-else class="hint-text">
                生成文章主旨大意摘要，考察学生对文章整体理解
              </span>
            </div>
          </el-form-item>

          <el-form-item label="难度等级">
            <el-select
              v-model="config.difficulty"
              placeholder="请选择难度"
              style="width: 100%"
              append-to-body
            >
              <el-option label="简单" value="easy" />
              <el-option label="中等" value="medium" />
              <el-option label="困难" value="hard" />
            </el-select>
          </el-form-item>

          <el-form-item label="题目数量">
            <el-input-number v-model="config.count" :min="1" :max="10" style="width: 100%" />
          </el-form-item>

          <el-form-item label="考察重点">
            <div class="focus-points-config">
              <div
                v-for="direction in assessmentDirections"
                :key="direction.value"
                class="focus-point-item"
                :class="{ active: config.focus_points.includes(direction.value) }"
              >
                <div class="focus-point-row" @click="toggleFocusPoint(direction.value)">
                  <el-checkbox
                    :model-value="config.focus_points.includes(direction.value)"
                    @change="toggleFocusPoint(direction.value)"
                  />
                  <span class="focus-point-label">{{ direction.label }}</span>
                </div>
              </div>
            </div>
            <div class="focus-hint">
              <span class="hint-text">
                勾选考察方向，不选则按权重自动分配
              </span>
            </div>
          </el-form-item>

          <el-form-item label="其他要求">
            <el-input
              v-model="config.additional_requirements"
              type="textarea"
              :rows="2"
              placeholder="输入其他出题要求..."
            />
          </el-form-item>
        </el-form>

        <el-button
          type="primary"
          :loading="isGenerating"
          @click="handleGenerate"
          class="generate-button"
        >
          <el-icon><MagicStick /></el-icon>
          开始生成题目
        </el-button>
      </div>

      <div v-if="isGenerating" class="generating-section">
        <div class="generating-animation">
          <div class="loading-dots"><span></span><span></span><span></span></div>
        </div>
        <div class="generating-text">{{ generatingMessage }}</div>
        <div class="generating-tip">AI正在根据听力原文生成题目，请稍候...</div>
      </div>

      <div v-if="!isGenerating && generatedQuestions.length > 0" class="chat-only-section">
        <div class="section-header">
          <span class="section-title">已生成 {{ generatedQuestions.length }} 道题目</span>
          <div class="header-actions">
            <el-button size="small" @click="resetGeneration" text type="primary">重新生成</el-button>
          </div>
        </div>

        <div class="chat-section-full">
          <div class="chat-messages" ref="chatMessagesRef">
            <div
              v-for="(msg, index) in chatMessages"
              :key="index"
              class="chat-message"
              :class="msg.role"
            >
              <div class="message-content">{{ msg.content }}</div>
            </div>
            <div v-if="isChatting" class="chat-loading">
              <div class="loading-dots"><span></span><span></span><span></span></div>
            </div>
          </div>
          <div class="chat-input-wrapper">
            <el-input
              v-model="chatInput"
              placeholder="输入修订指令，如：把第一题改得更难一些..."
              @keydown.enter.exact.prevent="handleChat"
              :disabled="isChatting"
              class="chat-input-field"
            />
            <el-button
              type="primary"
              :loading="isChatting"
              @click="handleChat"
              :disabled="!chatInput.trim()"
              class="send-button"
            >
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>

        <div class="actions-section">
          <el-button type="primary" @click="handleFillForm" :disabled="generatedQuestions.length === 0">
            <el-icon><RefreshRight /></el-icon>
            重新填充
          </el-button>
          <el-button
            type="success"
            :loading="isApplying"
            @click="handleApply"
            :disabled="generatedQuestions.length === 0"
          >
            <el-icon><Upload /></el-icon>
            保存到题库
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Minus, FullScreen, Close, MagicStick, RefreshRight, Upload, Promotion } from '@element-plus/icons-vue'
import { questionGenerationApi, type GeneratedQuestion } from '@/api/questionGeneration'

interface Props {
  visible: boolean
  materialId: number
  transcript?: string
  defaultQuestionType?: 'choice' | 'fill-blank' | 'comprehension'
}

const props = withDefaults(defineProps<Props>(), {
  defaultQuestionType: 'choice'
})
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'questions-applied': [questions: GeneratedQuestion[]]
  'fill-form': [questions: GeneratedQuestion[]]
}>()

const isMinimized = ref(false)
const isGenerating = ref(false)
const isChatting = ref(false)
const isApplying = ref(false)
const generatedQuestions = ref<GeneratedQuestion[]>([])
const chatInput = ref('')
const chatMessages = ref<Array<{ role: string; content: string }>>([])
const conversationHistory = ref<Array<{ role: string; content: string }>>([])
const chatMessagesRef = ref<HTMLElement | null>(null)
const generatingMessage = ref('正在初始化...')
const pollTimer = ref<number | null>(null)

const config = reactive({
  question_type: (props.defaultQuestionType || 'choice') as 'choice' | 'matching' | 'fill-blank' | 'comprehension',
  fill_blank_type: 'transcript' as 'transcript' | 'summary',
  difficulty: 'medium' as 'easy' | 'medium' | 'hard',
  count: 3,
  focus_points: [] as string[],
  additional_requirements: ''
})

const assessmentDirections = [
  { value: 'main_idea', label: '主旨大意概括', weight: 6 },
  { value: 'cause_effect', label: '因果关系理解', weight: 5 },
  { value: 'purpose_attitude', label: '目的与态度推断', weight: 4 },
  { value: 'inference', label: '推理与结论', weight: 3 },
  { value: 'vocabulary_context', label: '词汇语境含义', weight: 2 },
  { value: 'factual_detail', label: '事实细节捕捉', weight: 1 }
]

const toggleFocusPoint = (key: string) => {
  const index = config.focus_points.indexOf(key)
  if (index > -1) {
    config.focus_points.splice(index, 1)
  } else {
    config.focus_points.push(key)
  }
}

const handleQuestionTypeChange = () => {
  if (config.question_type === 'fill-blank') {
    config.fill_blank_type = 'transcript'
  }
}

const scrollToBottom = (el: HTMLElement | null) => {
  nextTick(() => {
    if (el) el.scrollTop = el.scrollHeight
  })
}

const stopPolling = () => {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

const handleGenerate = async () => {
  if (!props.materialId) {
    ElMessage.warning('缺少素材ID')
    return
  }

  if (!props.transcript) {
    ElMessage.warning('该素材没有听力原文，无法生成题目')
    return
  }

  let finalQuestionType = config.question_type
  if (config.question_type === 'fill-blank') {
    finalQuestionType =
      config.fill_blank_type === 'transcript' ? 'fill-blank-transcript' : 'fill-blank-summary'
  }

  isGenerating.value = true
  generatingMessage.value = '正在提交任务...'

  try {
    const response = await questionGenerationApi.generate({
      material_id: props.materialId,
      question_type: finalQuestionType,
      difficulty: config.difficulty,
      count: config.count,
      focus_points: config.focus_points,
      additional_requirements: config.additional_requirements
    })

    const taskId = response.task_id
    generatingMessage.value = '正在生成题目...'

    let polls = 0
    const maxPolls = 150

    const poll = async () => {
      try {
        const status = await questionGenerationApi.getStatus(taskId)

        generatingMessage.value = status.message || '正在处理...'

        if (status.status === 'completed') {
          stopPolling()
          isGenerating.value = false
          generatedQuestions.value = status.questions

          if (status.conversation_history) {
            conversationHistory.value = status.conversation_history
          }

          chatMessages.value = [
            {
              role: 'assistant',
              content: `已为您生成 ${status.questions.length} 道题目，已自动填充到左侧表单。您可以继续对话修订。`
            }
          ]

          emit('fill-form', status.questions)
          ElMessage.success(`已生成 ${status.questions.length} 道题目并填充到表单`)
          return
        }

        if (status.status === 'failed') {
          stopPolling()
          isGenerating.value = false

          let errorMsg = status.message || '题目生成失败'
          if (status.suggestions && status.suggestions.length > 0) {
            errorMsg += '\n建议：' + status.suggestions.join('；')
          }

          ElMessage.error(errorMsg)
          chatMessages.value = [{ role: 'system', content: errorMsg }]
          return
        }

        polls++
        if (polls >= maxPolls) {
          stopPolling()
          isGenerating.value = false
          ElMessage.error('题目生成超时，请稍后重试')
        }
      } catch (error: any) {
        console.error('轮询失败:', error)
        polls++
        if (polls >= maxPolls) {
          stopPolling()
          isGenerating.value = false
          ElMessage.error('查询状态失败')
        }
      }
    }

    pollTimer.value = window.setInterval(poll, 2000)
    await poll()
  } catch (error: any) {
    isGenerating.value = false
    ElMessage.error(error.message || '题目生成失败')
  }
}

const handleChat = async () => {
  const message = chatInput.value.trim()
  if (!message || isChatting.value) return

  chatMessages.value.push({ role: 'user', content: message })
  chatInput.value = ''
  scrollToBottom(chatMessagesRef.value)

  isChatting.value = true
  try {
    const response = await questionGenerationApi.chat({
      material_id: props.materialId,
      message,
      current_questions: generatedQuestions.value,
      conversation_history: conversationHistory.value
    })

    generatedQuestions.value = response.questions
    conversationHistory.value = response.conversation_history

    chatMessages.value.push({
      role: 'assistant',
      content: '题目已根据您的要求进行修订，已自动更新左侧表单。'
    })
    scrollToBottom(chatMessagesRef.value)

    emit('fill-form', response.questions)
    ElMessage.success('修订成功，表单已更新')
  } catch (error: any) {
    chatMessages.value.push({
      role: 'assistant',
      content: `修订失败：${error.message || '请重试'}`
    })
    scrollToBottom(chatMessagesRef.value)
  } finally {
    isChatting.value = false
  }
}

const handleFillForm = () => {
  if (generatedQuestions.value.length === 0) {
    ElMessage.warning('没有可填充的题目')
    return
  }

  emit('fill-form', generatedQuestions.value)
  chatMessages.value.push({
    role: 'assistant',
    content: `已将 ${generatedQuestions.value.length} 道题目重新填充到左侧表单。`
  })
  ElMessage.success('题目已重新填充到表单')
}

const handleApply = async () => {
  if (generatedQuestions.value.length === 0) {
    ElMessage.warning('没有可应用的题目')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要将 ${generatedQuestions.value.length} 道题目添加到题库吗？`,
      '确认保存',
      { type: 'info' }
    )

    isApplying.value = true
    const response = await questionGenerationApi.apply({
      material_id: props.materialId,
      questions: generatedQuestions.value
    })

    ElMessage.success(`已成功添加 ${response.total_count} 道题目到题库`)
    emit('questions-applied', generatedQuestions.value)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '应用失败')
    }
  } finally {
    isApplying.value = false
  }
}

const resetGeneration = () => {
  generatedQuestions.value = []
  chatMessages.value = []
  conversationHistory.value = []
}

const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
}

const handleClose = () => {
  stopPolling()
  emit('update:visible', false)
}

watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      resetGeneration()
    } else {
      stopPolling()
    }
  }
)
</script>

<style scoped>
.ai-question-window {
  position: fixed !important;
  width: 380px;
  max-height: calc(100vh - 100px);
  min-height: 450px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(140, 124, 240, 0.2);
  display: flex;
  flex-direction: column;
  z-index: 9999;
  overflow: visible;
  right: 20px;
  bottom: 80px;
  animation: fadeInUp 0.3s ease-out;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.ai-question-window::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8c7cf0, #c6b9ff);
  z-index: 1;
}

.ai-question-window.is-minimized {
  height: 40px !important;
  min-height: 40px !important;
  max-height: 40px !important;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ai-window-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  padding-top: 16px;
  border-bottom: 1px solid #f0f2f5;
  background: #ffffff;
  cursor: default;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.ai-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}
.ai-icon-small {
  color: #8c7cf0;
  width: 24px;
  height: 24px;
}
.ai-icon-small svg {
  width: 100%;
  height: 100%;
  animation: slowRotate 30s linear infinite;
}

@keyframes slowRotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.ai-window-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: visible;
  min-height: 0;
}

.config-section {
  padding: 16px;
  border-bottom: 1px solid #f0f2f5;
  overflow: visible;
}

.config-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 12px;
}

.config-form {
  margin-bottom: 12px;
}

.fill-blank-hint {
  margin-top: 8px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #f0ecff, #f8f6ff);
  border-radius: 8px;
  border-left: 3px solid #8c7cf0;
}

.hint-text {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

.focus-hint {
  margin-top: 8px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
  border-radius: 8px;
  border-left: 3px solid #67c23a;
}

.focus-points-config {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 280px;
  overflow-y: auto;
  padding-right: 4px;
}

.focus-point-item {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px 12px;
  background: #fafbfc;
  transition: all 0.3s ease;
}

.focus-point-item:hover {
  border-color: #c6b9ff;
  background: #f8f5ff;
}

.focus-point-item.active {
  border-color: #8c7cf0;
  background: linear-gradient(135deg, #f8f5ff, #f0ecff);
}

.focus-point-row {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.focus-point-label {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.generate-button {
  width: 100%;
  background: linear-gradient(135deg, #8c7cf0, #c6b9ff) !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
}

.generating-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.generating-animation {
  margin-bottom: 20px;
}

.loading-dots {
  display: flex;
  gap: 6px;
}
.loading-dots span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8c7cf0, #c6b9ff);
  animation: loadingDot 1.4s infinite ease-in-out;
}
.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}
.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loadingDot {
  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

.generating-text {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.generating-tip {
  font-size: 13px;
  color: #666;
}

.chat-only-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafbfc;
  border-bottom: 1px solid #f0f2f5;
  flex-shrink: 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.chat-section-full {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fafbfc;
}

.chat-message {
  margin-bottom: 12px;
}

.chat-message.user .message-content {
  background: linear-gradient(135deg, #8c7cf0, #c6b9ff);
  color: #ffffff;
  padding: 10px 14px;
  border-radius: 14px 14px 4px 14px;
  display: inline-block;
  font-size: 13px;
  line-height: 1.5;
  max-width: 85%;
  float: right;
  clear: both;
}

.chat-message.assistant .message-content {
  background: #ffffff;
  color: #333333;
  padding: 10px 14px;
  border-radius: 14px 14px 14px 4px;
  display: inline-block;
  font-size: 13px;
  line-height: 1.5;
  max-width: 85%;
  float: left;
  clear: both;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.chat-message.system .message-content {
  background: #fff3e0;
  color: #e65100;
  padding: 10px 14px;
  border-radius: 8px;
  display: inline-block;
  font-size: 13px;
  line-height: 1.5;
  max-width: 85%;
  float: left;
  clear: both;
}

.chat-loading {
  display: flex;
  justify-content: center;
  padding: 10px;
  clear: both;
}

.chat-loading .loading-dots span {
  width: 8px;
  height: 8px;
}

.chat-input-wrapper {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #ffffff;
  border-top: 1px solid #f0f2f5;
  flex-shrink: 0;
}

.chat-input-field {
  flex: 1;
}

.chat-input-field :global(.el-input__wrapper) {
  border-radius: 20px !important;
  padding: 4px 12px;
}

.send-button {
  border-radius: 20px !important;
  padding: 8px 16px !important;
  background: linear-gradient(135deg, #8c7cf0, #c6b9ff) !important;
  border: none !important;
  font-weight: 600 !important;
}

.send-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
}

.actions-section {
  padding: 12px 16px;
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-shrink: 0;
  background: #ffffff;
  border-top: 1px solid #f0f2f5;
}

.actions-section :global(.el-button--primary) {
  background: linear-gradient(135deg, #8c7cf0, #c6b9ff) !important;
  border: none !important;
}

.actions-section :global(.el-button--success) {
  background: linear-gradient(135deg, #67c23a, #95d475) !important;
  border: none !important;
}

:global(.el-form-item) {
  margin-bottom: 12px;
}

:global(.el-form-item__label) {
  font-size: 13px;
  color: #666666;
}

:global(.el-select .el-input__wrapper),
:global(.el-input__wrapper),
:global(.el-textarea__inner) {
  border-radius: 8px !important;
}

:global(.el-input-number) {
  width: 100%;
}
</style>

<style>
.ai-select-dropdown,
.el-select__popper {
  z-index: 10000 !important;
}
.el-popper {
  z-index: 10000 !important;
}
</style>

