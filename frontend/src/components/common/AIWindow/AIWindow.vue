<template>
  <div
    v-if="visible"
    class="ai-window"
    :class="{ 'is-minimized': isMinimized }"
    :style="props.style"
  >
    <div class="ai-window-header" @mousedown="handleHeaderMouseDown">
      <div class="header-left">
        <span class="ai-title">AI助手</span>
        <div class="ai-icon-small">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="windowAiGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#8C7CF0;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#C6B9FF;stop-opacity:1" />
              </linearGradient>
            </defs>
            <g>
              <path d="M12 2L12 4" stroke="url(#windowAiGradient)" stroke-width="2" stroke-linecap="round"/>
              <circle cx="12" cy="1.5" r="1" fill="url(#windowAiGradient)"/>
              <rect x="6" y="5" width="12" height="10" rx="3" stroke="url(#windowAiGradient)" stroke-width="2" fill="none"/>
              <circle cx="9" cy="10" r="1.5" fill="url(#windowAiGradient)"/>
              <circle cx="15" cy="10" r="1.5" fill="url(#windowAiGradient)"/>
              <rect x="10" y="12" width="4" height="1.5" rx="0.5" fill="url(#windowAiGradient)"/>
              <path d="M8 15L8 17" stroke="url(#windowAiGradient)" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 15L12 17" stroke="url(#windowAiGradient)" stroke-width="2" stroke-linecap="round"/>
              <path d="M16 15L16 17" stroke="url(#windowAiGradient)" stroke-width="2" stroke-linecap="round"/>
              <rect x="7" y="17" width="2" height="3" rx="0.5" fill="url(#windowAiGradient)"/>
              <rect x="15" y="17" width="2" height="3" rx="0.5" fill="url(#windowAiGradient)"/>
              <path d="M4 8L2 8" stroke="url(#windowAiGradient)" stroke-width="2" stroke-linecap="round"/>
              <path d="M4 12L2 12" stroke="url(#windowAiGradient)" stroke-width="2" stroke-linecap="round"/>
              <path d="M20 8L22 8" stroke="url(#windowAiGradient)" stroke-width="2" stroke-linecap="round"/>
              <path d="M20 12L22 12" stroke="url(#windowAiGradient)" stroke-width="2" stroke-linecap="round"/>
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
      <div ref="messagesRef" class="messages-container">
        <div
          v-for="message in messages"
          :key="message.id"
          class="message-item"
          :class="`message-${message.role}`"
        >
          <div v-if="message.role === 'user'" class="message-user">
            <div class="message-content">{{ message.content }}</div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
          <div v-else-if="message.role === 'assistant'" class="message-assistant">
            <div class="message-avatar">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="avatarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#8C7CF0;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#C6B9FF;stop-opacity:1" />
                  </linearGradient>
                </defs>
                <g>
                  <path d="M12 2L12 4" stroke="url(#avatarGradient)" stroke-width="2" stroke-linecap="round"/>
                  <circle cx="12" cy="1.5" r="1" fill="url(#avatarGradient)"/>
                  <rect x="6" y="5" width="12" height="10" rx="3" stroke="url(#avatarGradient)" stroke-width="2" fill="none"/>
                  <circle cx="9" cy="10" r="1.5" fill="url(#avatarGradient)"/>
                  <circle cx="15" cy="10" r="1.5" fill="url(#avatarGradient)"/>
                  <rect x="10" y="12" width="4" height="1.5" rx="0.5" fill="url(#avatarGradient)"/>
                  <path d="M8 15L8 17" stroke="url(#avatarGradient)" stroke-width="2" stroke-linecap="round"/>
                  <path d="M12 15L12 17" stroke="url(#avatarGradient)" stroke-width="2" stroke-linecap="round"/>
                  <path d="M16 15L16 17" stroke="url(#avatarGradient)" stroke-width="2" stroke-linecap="round"/>
                  <rect x="7" y="17" width="2" height="3" rx="0.5" fill="url(#avatarGradient)"/>
                  <rect x="15" y="17" width="2" height="3" rx="0.5" fill="url(#avatarGradient)"/>
                  <path d="M4 8L2 8" stroke="url(#avatarGradient)" stroke-width="2" stroke-linecap="round"/>
                  <path d="M4 12L2 12" stroke="url(#avatarGradient)" stroke-width="2" stroke-linecap="round"/>
                  <path d="M20 8L22 8" stroke="url(#avatarGradient)" stroke-width="2" stroke-linecap="round"/>
                  <path d="M20 12L22 12" stroke="url(#avatarGradient)" stroke-width="2" stroke-linecap="round"/>
                </g>
              </svg>
            </div>
            <div class="message-wrapper">
              <div class="message-content">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
          <div v-else class="message-system">
            <div class="message-content">{{ message.content }}</div>
          </div>
          <div
            v-if="message.type === 'grade' && message.gradeData"
            class="grade-card"
          >
            <div class="grade-card-header">
              <span class="grade-question">题目 {{ message.gradeData.questionNumber || message.gradeData.sub_question_id }}</span>
              <span :class="['grade-score', getScoreClass(message.gradeData.score, message.gradeData.max_score)]">
                {{ message.gradeData.score }} / {{ message.gradeData.max_score }}
              </span>
            </div>
            <div class="grade-feedback">
              <div class="grade-feedback-title">反馈：</div>
              <div class="grade-feedback-content">{{ message.gradeData.feedback }}</div>
            </div>
            <div v-if="message.gradeData.suggestions?.length" class="grade-suggestions">
              <div class="grade-suggestions-title">建议：</div>
              <ul class="grade-suggestions-list">
                <li v-for="(suggestion, index) in message.gradeData.suggestions" :key="index">{{ suggestion }}</li>
              </ul>
            </div>
          </div>
        </div>
        <div v-if="loading" class="message-loading">
          <div class="loading-dots"><span></span><span></span><span></span></div>
        </div>
      </div>
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="输入消息..."
          :disabled="loading"
          @keydown.enter.exact.prevent="handleSendMessage"
          @keydown.enter.shift.exact="handleShiftEnter"
        />
        <div class="input-actions">
          <el-button type="primary" :loading="loading" @click="handleSendMessage">发送</el-button>
          <el-button
            v-if="showGradeButton"
            type="success"
            :loading="loading"
            @click="handleRequestGrade"
          >
            请求AI评分
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Minus, FullScreen, Close } from '@element-plus/icons-vue'
import type { Message, GradeResult, WindowState } from './types'
import { sendChatMessage } from '@/api/ai'

interface Props {
  visible: boolean
  practiceId?: number
  pageId?: number
  subQuestionId?: number
  showGradeButton?: boolean
  style?: Record<string, string>
  onGradeRequest?: () => Promise<void>
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  showGradeButton: false
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'window-state-change': [state: WindowState]
  'grade-complete': [result: GradeResult]
}>()

const messagesRef = ref<HTMLElement | null>(null)
const inputMessage = ref('')
const loading = ref(false)
const isMinimized = ref(false)

const messages = ref<Array<Message & { gradeData?: GradeResult }>>([
  { id: 1, role: 'system', content: '欢迎使用AI助手！我可以帮您解答问题、提供评分和反馈。', timestamp: new Date().toISOString() }
])

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const getScoreClass = (score: number, maxScore: number): string => {
  const p = (score / maxScore) * 100
  if (p >= 80) return 'score-high'
  if (p >= 60) return 'score-medium'
  return 'score-low'
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  })
}

const handleSendMessage = async () => {
  const content = inputMessage.value.trim()
  if (!content || loading.value) return

  const userMessage: Message = {
    id: Date.now(),
    role: 'user',
    content,
    timestamp: new Date().toISOString()
  }
  messages.value.push(userMessage)
  inputMessage.value = ''
  scrollToBottom()
  loading.value = true

  try {
    const response = await sendChatMessage({
      message: content,
      context: {
        practice_id: props.practiceId,
        page_id: props.pageId,
        sub_question_id: props.subQuestionId
      }
    })
    const aiMessage: Message = {
      id: Date.now() + 1,
      role: 'assistant',
      content: response.reply,
      timestamp: response.timestamp || new Date().toISOString()
    }
    messages.value.push(aiMessage)
    scrollToBottom()
  } catch (error: any) {
    let errorMessage = '发送消息失败，请稍后重试'
    if (error?.response?.data?.message) errorMessage = error.response.data.message
    else if (error?.message) errorMessage = error.message
    messages.value.push({
      id: Date.now() + 1,
      role: 'system',
      content: `消息发送失败：${errorMessage}`,
      timestamp: new Date().toISOString()
    })
    scrollToBottom()
  } finally {
    loading.value = false
  }
}

const handleShiftEnter = () => {}

const handleRequestGrade = async () => {
  if (loading.value) return
  if (!props.onGradeRequest) {
    ElMessage.warning('评分功能不可用')
    return
  }
  loading.value = true
  messages.value.push({
    id: Date.now(),
    role: 'system',
    content: '正在请求AI评分...',
    timestamp: new Date().toISOString()
  })
  scrollToBottom()
  try {
    await props.onGradeRequest()
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: '评分完成！详细评分结果请查看对应题目下方。',
      timestamp: new Date().toISOString()
    })
    scrollToBottom()
    ElMessage.success('AI评分完成')
  } catch (error: any) {
    const errorMessage = error?.response?.data?.message || error?.message || 'AI评分失败，请稍后重试'
    messages.value.push({
      id: Date.now() + 1,
      role: 'system',
      content: `评分失败：${errorMessage}`,
      timestamp: new Date().toISOString()
    })
    scrollToBottom()
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
  emit('window-state-change', isMinimized.value ? 'minimize' : 'open')
}

const handleClose = () => {
  emit('update:visible', false)
  emit('window-state-change', 'close')
}

const handleHeaderMouseDown = (e: MouseEvent) => {
  if ((e.target as HTMLElement).closest('button')) return
}

watch(() => props.visible, (newVal) => {
  if (newVal) scrollToBottom()
})
</script>

<style scoped>
.ai-window {
  position: fixed !important;
  width: 360px;
  height: auto;
  max-height: calc(100vh - 120px);
  min-height: 400px;
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(140, 124, 240, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 9999;
  overflow: hidden;
  animation: fadeInUp 0.3s ease-out;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.ai-window::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF);
  z-index: 1;
}
.ai-window.is-minimized {
  height: 40px !important;
  min-height: 40px !important;
  max-height: 40px !important;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.ai-window-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  padding-top: 16px;
  border-bottom: 1px solid #F0F2F5;
  background: #FFFFFF;
  cursor: default;
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 8px; }
.ai-title { font-size: 16px; font-weight: 600; color: #1A1A1A; }
.ai-icon-small { color: #8C7CF0; width: 24px; height: 24px; }
.ai-icon-small svg { width: 100%; height: 100%; animation: slowRotate 30s linear infinite; }
@keyframes slowRotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.header-right { display: flex; align-items: center; gap: 4px; }
.ai-window-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #FAFBFC;
  min-height: 0;
}
.messages-container::-webkit-scrollbar { width: 6px; }
.messages-container::-webkit-scrollbar-thumb { background: rgba(140, 124, 240, 0.3); border-radius: 3px; }
.message-item { margin-bottom: 16px; }
.message-user { display: flex; flex-direction: column; align-items: flex-end; }
.message-user .message-content {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  color: #FFFFFF;
  padding: 10px 14px;
  border-radius: 12px 12px 4px 12px;
  max-width: 70%;
  word-wrap: break-word;
}
.message-user .message-time { font-size: 12px; color: #999; margin-top: 4px; }
.message-assistant { display: flex; gap: 8px; align-items: flex-start; }
.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.3);
}
.message-avatar svg { width: 24px; height: 24px; animation: slowRotate 40s linear infinite; }
.message-wrapper { flex: 1; display: flex; flex-direction: column; }
.message-assistant .message-content {
  background: #FFFFFF;
  color: #1A1A1A;
  padding: 10px 14px;
  border-radius: 12px 12px 12px 4px;
  max-width: 80%;
  word-wrap: break-word;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.08);
  border: 1px solid #E8E4FF;
}
.message-assistant .message-time { font-size: 12px; color: #999; margin-top: 4px; }
.message-system { text-align: center; }
.message-system .message-content {
  display: inline-block;
  background: #F0F2F5;
  color: #666;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
}
.grade-card {
  margin-top: 12px;
  background: #FAFBFC;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #E8E4FF;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.08);
}
.grade-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.grade-question { font-size: 14px; color: #1A1A1A; font-weight: 500; }
.grade-score { font-size: 20px; font-weight: bold; }
.score-high { color: #4CAF50; }
.score-medium { color: #FF9800; }
.score-low { color: #F44336; }
.grade-feedback { margin-bottom: 12px; }
.grade-feedback-title { font-size: 13px; color: #666; margin-bottom: 6px; font-weight: 500; }
.grade-feedback-content { font-size: 14px; color: #1A1A1A; line-height: 1.6; }
.grade-suggestions { margin-top: 12px; padding-top: 12px; border-top: 1px solid #E8E4FF; }
.grade-suggestions-title { font-size: 13px; color: #666; margin-bottom: 8px; font-weight: 500; }
.grade-suggestions-list { margin: 0; padding-left: 20px; font-size: 14px; color: #1A1A1A; line-height: 1.8; }
.grade-suggestions-list li { margin-bottom: 4px; }
.message-loading { display: flex; align-items: center; gap: 8px; padding: 12px; }
.loading-dots { display: flex; gap: 4px; }
.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #8C7CF0;
  animation: loadingDot 1.4s infinite ease-in-out;
}
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes loadingDot {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}
.input-area {
  padding: 16px;
  background: #FFFFFF;
  border-top: 1px solid #F0F2F5;
  flex-shrink: 0;
}
:deep(.el-textarea__inner) {
  border-color: #E8E4FF;
  border-radius: 12px;
  transition: all 0.3s ease;
}
:deep(.el-textarea__inner:focus) {
  border-color: #8C7CF0;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1);
}
.input-actions { display: flex; gap: 8px; margin-top: 8px; justify-content: flex-end; }
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  border: none;
  border-radius: 10px;
  font-weight: 500;
}
:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #7B6CE0, #B5A5FF);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
}
:deep(.el-button--success) {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  border: none;
  border-radius: 10px;
  font-weight: 500;
}
@media (max-width: 768px) {
  .ai-window {
    width: 100% !important;
    height: 70vh;
    max-height: 70vh;
    bottom: 0 !important;
    top: auto !important;
    left: 0 !important;
    right: 0 !important;
    border-radius: 20px 20px 0 0;
  }
}
</style>
