<template>
  <div class="message-page">
    <div class="container card">
      <div class="illustration-bg">
        <div class="illustration-circle circle-1"></div>
        <div class="illustration-circle circle-2"></div>
        <div class="illustration-star star-1"></div>
        <div class="illustration-star star-2"></div>
        <div class="illustration-star star-3"></div>
      </div>

      <div class="illustration-header">
        <div class="illustration-email">
          <div class="email-body">
            <div class="email-top"></div>
            <div class="email-content">
              <div class="email-line line-1"></div>
              <div class="email-line line-2"></div>
              <div class="email-line line-3"></div>
            </div>
          </div>
          <div class="email-flag"></div>
          <div class="email-shine"></div>
        </div>
      </div>

      <button class="back-button" @click="goBack">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        返回
      </button>
        <h1 class="title">消息箱</h1>
        <div class="action-center">
          <button class="send-button" @click="goToSendMessage">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
            发送消息
          </button>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading">加载中...</div>
        
        <!-- 消息列表 -->
        <div v-else class="messages-list">
          <div
            v-for="(message, index) in messages"
            :key="message.id"
            class="message-item"
            :class="{ selected: selectedIndex === index }"
            @click="selectMessage(index, message.id)"
          >
            <div class="message-header">
              <h3>{{ message.content.substring(0, 20) }}{{ message.content.length > 20 ? '...' : '' }}</h3>
            </div>
            <p class="message-content">{{ message.content }}</p>
            <div class="message-footer">
              <span class="message-time">时间: {{ formatDate(message.createdAt) }}</span>
              <span class="message-sender">发送者: {{ message.sender }}</span>
            </div>
          </div>
        </div>

        <div v-if="messages.length === 0" class="no-messages">
          <p>暂无消息</p>
        </div>

        <!-- 分页 -->
        <div v-if="messages.length > 0" class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadMessages"
            @current-change="loadMessages"
          />
        </div>
        <AIWindow :show-grade-button="false" />
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAllMessages } from '@/api/message'
import AIWindow from '@/components/common/AIWindow/index.vue'
import type { Message } from '@/api/message'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const selectedIndex = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const messages = ref<Message[]>([])

const selectMessage = (index: number, id: number) => {
  selectedIndex.value = selectedIndex.value === index ? null : index
  if (userStore.isTeacher()) {
    router.push(`/announce/messages/${id}`)
  } else {
    router.push(`/messages/${id}`)
  }
}

const formatDate = (date: string) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadMessages = async () => {
  loading.value = true
  try {
    const data = await getAllMessages()
    messages.value = data.map((msg: any) => ({
      id: msg.id,
      title: msg.title || msg.a_title || '无标题',
      content: msg.content || msg.a_content || '',
      sender: msg.sender_name || msg.sender || '未知',
      senderId: msg.sender_id || 0,
      receiverId: msg.receiver_id || 0,
      createdAt: msg.created_at || msg.createdAt,
      isRead: msg.is_read || false,
      readAt: msg.read_at
    }))
    total.value = messages.value.length
  } catch (error) {
    console.error('加载消息列表失败', error)
    ElMessage.error('加载消息列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadMessages()
})

const goBack = () => {
  router.back()
}

const goToSendMessage = () => {
  if (userStore.isTeacher()) {
    router.push('/announce/messages/send')
  } else {
    router.push('/messages/send')
  }
}
</script>

<style scoped>
.message-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #FAFBFC 0%, #F5F3FF 100%);
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.illustration-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.illustration-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
}

.circle-1 {
  top: 10%;
  right: 8%;
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.15) 0%, transparent 70%);
  animation: float 10s ease-in-out infinite;
}

.circle-2 {
  bottom: 15%;
  left: 5%;
  width: 140px;
  height: 140px;
  background: radial-gradient(circle, rgba(255, 193, 7, 0.12) 0%, transparent 70%);
  animation: float 12s ease-in-out infinite 2s;
}

.illustration-star {
  position: absolute;
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #FFD54F 0%, #FF9800 100%);
  border-radius: 50%;
  opacity: 0.8;
  animation: twinkle 3s ease-in-out infinite;
}

.star-1 {
  top: 20%;
  left: 15%;
  animation-delay: 0s;
}

.star-2 {
  top: 35%;
  right: 12%;
  animation-delay: 1s;
}

.star-3 {
  bottom: 30%;
  right: 20%;
  animation-delay: 2s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) scale(1);
  }
  50% {
    transform: translateY(-40px) scale(1.08);
  }
}

@keyframes twinkle {
  0%, 100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.illustration-header {
  position: fixed;
  top: 20px;
  right: 5%;
  z-index: 2;
  animation: characterFloat 6s ease-in-out infinite;
}

@keyframes characterFloat {
  0%, 100% {
    transform: translateY(0px) rotate(-2deg);
  }
  50% {
    transform: translateY(-15px) rotate(2deg);
  }
}

.illustration-email {
  position: relative;
  width: 140px;
  height: 120px;
  animation: emailFloat 4s ease-in-out infinite;
}

@keyframes emailFloat {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(2deg);
  }
}

.email-body {
  position: relative;
  width: 140px;
  height: 100px;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  border-radius: 12px 12px 8px 8px;
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.3);
  overflow: hidden;
}

.email-top {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 30px;
  background: linear-gradient(135deg, #6B5BCE 0%, #8C7CF0 100%);
  clip-path: polygon(0 0, 50% 100%, 100% 0);
  animation: emailTopMove 3s ease-in-out infinite;
}

@keyframes emailTopMove {
  0%, 100% {
    height: 30px;
  }
  50% {
    height: 35px;
  }
}

.email-content {
  position: absolute;
  top: 40px;
  left: 20px;
  right: 20px;
  height: 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.email-line {
  height: 4px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 2px;
  animation: linePulse 2s ease-in-out infinite;
}

.line-1 {
  width: 80%;
  animation-delay: 0s;
}

.line-2 {
  width: 100%;
  animation-delay: 0.5s;
}

.line-3 {
  width: 60%;
  animation-delay: 1s;
}

@keyframes linePulse {
  0%, 100% {
    opacity: 0.7;
    transform: scaleX(1);
  }
  50% {
    opacity: 1;
    transform: scaleX(1.05);
  }
}

.email-flag {
  position: absolute;
  top: -10px;
  right: 15px;
  width: 0;
  height: 0;
  border-left: 15px solid transparent;
  border-right: 15px solid transparent;
  border-bottom: 25px solid #FFD54F;
  animation: flagWave 1s ease-in-out infinite;
}

@keyframes flagWave {
  0%, 100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(15deg);
  }
}

.email-shine {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 40px;
  height: 40px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, transparent 70%);
  border-radius: 50%;
  animation: shineMove 3s ease-in-out infinite;
}

@keyframes shineMove {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(10px, 10px);
  }
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #FFFFFF 0%, #F5F3FF 100%);
  color: #8C7CF0;
  border: 2px solid #E8E4FF;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
  margin-bottom: 24px;
  align-self: flex-start;
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.back-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s ease, height 0.4s ease;
}

.back-button:hover::before {
  width: 200px;
  height: 200px;
}

.back-button:hover {
  background: linear-gradient(135deg, #E8E4FF 0%, #D4C8FF 100%);
  border-color: #8C7CF0;
  transform: translateX(-6px) translateY(-2px);
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.25);
}

.back-button:active {
  transform: translateX(-4px) translateY(0px) scale(0.95);
}

.action-center {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  width: 100%;
}

.send-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #8C7CF0 0%, #6B5BCE 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.4);
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.send-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s ease, height 0.4s ease;
}

.send-button:hover::before {
  width: 200px;
  height: 200px;
}

.send-button:hover {
  background: linear-gradient(135deg, #9E8CFF 0%, #8C7CF0 100%);
  transform: translateY(-4px);
  box-shadow: 0 10px 24px rgba(140, 124, 240, 0.5);
}

.send-button:active {
  transform: translateY(0px) scale(0.95);
}

.container {
  width: 90%;
  padding: 32px;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.card {
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  position: relative;
  overflow: hidden;
  width: 90%;
  display: flex;
  flex-direction: column;
  animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF, #A8D5BA, #FFD54F);
  background-size: 300% 100%;
  animation: gradientFlow 8s ease infinite;
}

@keyframes gradientFlow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.title {
  text-align: center;
  color: #1A202C;
  margin-bottom: 32px;
  font-size: 32px;
  font-weight: 700;
  position: relative;
  z-index: 1;
  background: linear-gradient(135deg, #8C7CF0 0%, #6B5BCE 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: titleGlow 3s ease-in-out infinite;
}

@keyframes titleGlow {
  0%, 100% {
    filter: drop-shadow(0 0 2px rgba(140, 124, 240, 0.3));
  }
  50% {
    filter: drop-shadow(0 0 8px rgba(140, 124, 240, 0.6));
  }
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-item {
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
  padding: 20px;
  border-radius: 16px;
  border: 1px solid #F0F2F5;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.5s ease-out backwards;
}

.message-item:nth-child(1) {
  animation-delay: 0.1s;
}

.message-item:nth-child(2) {
  animation-delay: 0.2s;
}

.message-item:nth-child(3) {
  animation-delay: 0.3s;
}

.message-item:nth-child(4) {
  animation-delay: 0.4s;
}

.message-item:nth-child(5) {
  animation-delay: 0.5s;
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

.message-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #8C7CF0, #C6B9FF);
  border-radius: 4px 0 0 4px;
  transition: all 0.3s ease;
}

.message-item:hover {
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.2);
  transform: translateY(-6px) scale(1.02);
  border-color: #C6B9FF;
}

.message-item:hover::before {
  width: 6px;
  box-shadow: 0 0 12px rgba(140, 124, 240, 0.5);
}



.message-item.selected {
  background: linear-gradient(135deg, #E8E4FF 0%, #F5F3FF 100%);
  color: #8C7CF0;
  border-color: #8C7CF0;
}

.message-item.selected::before {
  background: linear-gradient(180deg, #A8D5BA, #81C784);
  width: 6px;
}

.message-item.selected * {
  color: #8C7CF0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.message-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #1A202C;
}

.message-item.selected .message-header h3 {
  color: #8C7CF0;
}

.message-status {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}



.message-content {
  color: #4A5568;
  margin: 0 0 12px 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.message-item.selected .message-content {
  color: #8C7CF0;
}

.message-footer {
  display: flex;
  gap: 24px;
  font-size: 14px;
  color: #8B9BB4;
}

.message-item.selected .message-footer {
  color: #8C7CF0;
}

.message-time,
.message-sender {
  color: inherit;
  transition: color 0.3s ease;
}

.message-item:hover .message-time,
.message-item:hover .message-sender {
  color: #8C7CF0;
}

.no-messages {
  text-align: center;
  padding: 80px 40px;
  color: #8B9BB4;
  position: relative;
}

.no-messages::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.5;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.8;
  }
}

.pagination {
  margin-top: 32px;
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #F0F2F5;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background: linear-gradient(135deg, #8C7CF0 0%, #A8D5BA 100%);
  color: #FFFFFF;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
}

:deep(.el-pagination.is-background .el-pager li) {
  border-radius: 8px;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
  border: 1px solid #F0F2F5;
}

:deep(.el-pagination.is-background .el-pager li:hover:not(.disabled)) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2);
  border-color: #C6B9FF;
}

:deep(.el-pagination__sizes .el-input .el-input__inner) {
  border-color: #F0F2F5;
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-pagination__sizes .el-input .el-input__inner:hover) {
  border-color: #8C7CF0;
  box-shadow: 0 0 8px rgba(140, 124, 240, 0.2);
}

:deep(.el-pagination button:hover:not(:disabled)) {
  color: #8C7CF0;
  transform: translateY(-2px);
}

:deep(.el-pagination button:not(:disabled)) {
  border-radius: 8px;
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
  border: 1px solid #F0F2F5;
  transition: all 0.3s ease;
}

:deep(.el-pagination button:not(:disabled):hover) {
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2);
  border-color: #C6B9FF;
}
</style>

