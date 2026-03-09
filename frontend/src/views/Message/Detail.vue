<template>
  <div class="message-detail-page">
    <div class="illustration-bg">
      <div class="illustration-circle circle-1"></div>
      <div class="illustration-circle circle-2"></div>
      <div class="illustration-star star-1"></div>
      <div class="illustration-star star-2"></div>
      <div class="illustration-star star-3"></div>
      <div class="illustration-cloud cloud-1"></div>
      <div class="illustration-cloud cloud-2"></div>
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

    <el-card v-loading="loading" class="main-card">
      <div class="card-header">
        <el-button class="back-btn" @click="goBack">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回
        </el-button>
        <div>
          <el-button type="danger" class="delete-btn" @click="deleteMessage">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
            删除
          </el-button>
        </div>
      </div>

      <div v-if="message" class="message-content">
        <el-card class="message-card">
          <div class="message-header">
            <h2 class="message-title">{{ message.content.substring(0, 30) }}{{ message.content.length > 30 ? '...' : '' }}</h2>
          </div>
          <div class="message-meta">
            <span class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              发送者：{{ message.sender }}
            </span>
            <span class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              发送时间：{{ formatDate(message.createdAt) }}
            </span>

          </div>
          <div class="message-body">
            <div v-html="message.content" class="message-text"></div>
          </div>
        </el-card>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <div class="empty-illustration">
          <div class="empty-envelope"></div>
          <div class="empty-question"></div>
        </div>
        <el-empty description="消息不存在"></el-empty>
      </div>
    </el-card>
    <AIWindow :show-grade-button="false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMessageById, markMessageAsRead, deleteMessage } from '@/api/message'
import AIWindow from '@/components/common/AIWindow/index.vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const message = ref<any>(null)

// 格式化日期
const formatDate = (dateStr: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 返回
const goBack = () => {
  if (userStore.isTeacher()) {
    router.push('/announce/messages')
  } else {
    router.push('/messages')
  }
}

// 删除消息
const deleteMessage = async () => {
  if (!message.value) return

  try {
    await ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteMessage(message.value.id)
    ElMessage.success('删除成功')
    if (userStore.isTeacher()) {
      router.push('/announce/messages')
    } else {
      router.push('/messages')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 加载消息
const loadMessage = async () => {
  const messageId = Number(route.params.id)
  if (!messageId) {
    ElMessage.error('消息ID无效')
    if (userStore.isTeacher()) {
      router.push('/announce/messages')
    } else {
      router.push('/messages')
    }
    return
  }

  loading.value = true
  try {
    message.value = await getMessageById(messageId)
    
    // 暂时移除标记为已读的功能，因为后端API不支持
    // if (message.value && !message.value.isRead) {
    //   await markMessageAsRead(messageId)
    //   message.value.isRead = true
    //   message.value.readAt = new Date().toISOString()
    // }
  } catch (error: any) {
    console.error('加载消息失败', error)
    // 处理404错误，显示资源不存在的提示
    if (error.response && error.response.status === 404) {
      ElMessage.error('消息不存在或您无权访问')
    } else {
      ElMessage.error(error.message || '加载消息失败')
    }
    if (userStore.isTeacher()) {
      router.push('/announce/messages')
    } else {
      router.push('/messages')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadMessage()
})
</script>

<style scoped>
.message-detail-page {
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(180deg, #FAFBFC 0%, #F5F3FF 100%);
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
  top: 15%;
  right: 10%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.12) 0%, transparent 70%);
  animation: float 12s ease-in-out infinite;
}

.circle-2 {
  bottom: 20%;
  left: 8%;
  width: 160px;
  height: 160px;
  background: radial-gradient(circle, rgba(255, 193, 7, 0.1) 0%, transparent 70%);
  animation: float 14s ease-in-out infinite 3s;
}

.illustration-star {
  position: absolute;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #FFD54F 0%, #FF9800 100%);
  border-radius: 50%;
  opacity: 0.8;
  animation: twinkle 3s ease-in-out infinite;
}

.star-1 {
  top: 25%;
  left: 20%;
  animation-delay: 0s;
}

.star-2 {
  top: 40%;
  right: 15%;
  animation-delay: 1.5s;
}

.star-3 {
  bottom: 35%;
  right: 25%;
  animation-delay: 3s;
}

.illustration-cloud {
  position: absolute;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(240, 240, 255, 0.6) 100%);
  border-radius: 50px;
  opacity: 0.5;
  animation: cloudFloat 20s ease-in-out infinite;
}

.cloud-1 {
  top: 10%;
  left: 5%;
  width: 120px;
  height: 60px;
}

.cloud-2 {
  top: 60%;
  right: 8%;
  width: 100px;
  height: 50px;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) scale(1);
  }
  50% {
    transform: translateY(-50px) scale(1.1);
  }
}

@keyframes twinkle {
  0%, 100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1.3);
  }
}

@keyframes cloudFloat {
  0%, 100% {
    transform: translateX(0px);
  }
  50% {
    transform: translateX(30px);
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
    transform: translateY(-20px) rotate(2deg);
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

.main-card {
  max-width: 900px;
  margin: 0 auto;
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(140, 124, 240, 0.2);
  position: relative;
  z-index: 1;
  animation: slideInUp 0.6s ease-out;
  border: none;
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

.main-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF, #A8D5BA, #FFD54F);
  background-size: 300% 100%;
  animation: gradientFlow 8s ease infinite;
  border-radius: 20px 20px 0 0;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: linear-gradient(135deg, #FFFFFF 0%, #F5F3FF 100%);
  color: #8C7CF0;
  border: 2px solid #E8E4FF;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
}

.back-btn:hover {
  background: linear-gradient(135deg, #E8E4FF 0%, #D4C8FF 100%);
  border-color: #8C7CF0;
  transform: translateX(-4px) translateY(-2px);
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.25);
}

.back-btn:active {
  transform: translateX(-2px) translateY(0px) scale(0.95);
}

.delete-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: linear-gradient(135deg, #FFE4E1 0%, #FFD4D4 100%);
  color: #FF6B6B;
  border: 2px solid #FFB8B8;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.15);
}

.delete-btn:hover {
  background: linear-gradient(135deg, #FFD4D4 0%, #FFB8B8 100%);
  border-color: #FF6B6B;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 107, 107, 0.25);
}

.delete-btn:active {
  transform: translateY(0px) scale(0.95);
}

.message-content {
  margin-top: 20px;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.message-card {
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.1);
  border: 1px solid #F0F2F5;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #F0F2F5;
}

.message-title {
  margin: 0;
  flex: 1;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #8C7CF0 0%, #6B5BCE 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}



.message-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 24px;
  font-size: 14px;
  color: #8B9BB4;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #F8F9FA 0%, #F0F2F5 100%);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.meta-item:hover {
  background: linear-gradient(135deg, #E8E4FF 0%, #F5F3FF 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.15);
}

.meta-item svg {
  color: #8C7CF0;
  transition: all 0.3s ease;
}

.meta-item:hover svg {
  color: #6B5BCE;
  transform: scale(1.1);
}

.message-body {
  margin-top: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #F8F9FA 0%, #FFFFFF 100%);
  border-radius: 12px;
  border: 1px solid #F0F2F5;
}

.message-text {
  line-height: 1.8;
  color: #303133;
  font-size: 15px;
}

.empty-state {
  padding: 60px 40px;
  text-align: center;
  position: relative;
}

.empty-illustration {
  position: relative;
  width: 120px;
  height: 100px;
  margin: 0 auto 30px;
}

.empty-envelope {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 60px;
  background: linear-gradient(135deg, #E0E0E0 0%, #BDBDBD 100%);
  border-radius: 8px;
  animation: emptyFloat 3s ease-in-out infinite;
}

.empty-envelope::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 50%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.3) 100%);
  border-radius: 8px 8px 0 0;
}

.empty-question {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #FFD54F 0%, #FF9800 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: #FFFFFF;
  animation: questionBounce 2s ease-in-out infinite;
}

@keyframes emptyFloat {
  0%, 100% {
    transform: translateX(-50%) translateY(0px);
  }
  50% {
    transform: translateX(-50%) translateY(-10px);
  }
}

@keyframes questionBounce {
  0%, 100% {
    transform: translateY(0px) scale(1);
  }
  50% {
    transform: translateY(-8px) scale(1.1);
  }
}

:deep(.el-card__body) {
  padding: 24px;
}

:deep(.el-empty__description p) {
  color: #8B9BB4;
  font-size: 15px;
}
</style>





