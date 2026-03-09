<template>
  <div class="announcement-detail-page">
    <!-- 背景装饰元素 -->
    <div class="background-decoration"></div>
    
    <div class="container card">
      <!-- 插画区域 -->
      <div class="illustration-header">
        <div class="illustration-bell">
          <div class="bell-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
          </div>
        </div>
      </div>
      
      <!-- 返回按钮 -->
      <button class="back-button" @click="goBack">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        {{ userStore.isTeacher() ? '返回公告管理' : '返回公告栏' }}
      </button>
      
      <h1>公告详情</h1>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading">加载中...</div>
      
      <!-- 公告内容 -->
      <div v-else-if="announcement" class="announcement-content">
        <!-- 公告卡片 -->
        <div class="announcement-card">
          <div class="announcement-header">
            <h2>{{ announcement.a_title }}</h2>
          </div>
          <div class="announcement-meta">
            <span class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              发布者：{{ announcement.teacher_name || '未知' }}
            </span>
            <span class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              发布时间：{{ formatDate(announcement.created_at) }}
            </span>
            <span v-if="announcement.updated_at && announcement.updated_at !== announcement.created_at" class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
              </svg>
              更新时间：{{ formatDate(announcement.updated_at) }}
            </span>
          </div>
          <div class="announcement-body">
            <div v-html="announcement.a_content" class="announcement-text"></div>
          </div>
          <div v-if="announcement.receivers && announcement.receivers.length > 0" class="receivers">
            <div class="receivers-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              接收者
            </div>
            <div class="receivers-list">
              <div 
                v-for="receiver in announcement.receivers" 
                :key="receiver.student_id" 
                class="receiver-tag"
              >
                {{ receiver.student_name }}
              </div>
            </div>
          </div>
          <div v-if="announcement && userStore.isTeacher()" class="announcement-actions">
            <button class="action-button edit-button" @click="editAnnouncement">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              编辑
            </button>
            <button class="action-button delete-button" @click="deleteAnnouncement">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
              删除
            </button>
          </div>
        </div>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <p>公告不存在</p>
      </div>
    </div>
    <AIWindow :show-grade-button="false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAnnouncementById, deleteAnnouncement } from '@/api/announcement'
import AIWindow from '@/components/common/AIWindow/index.vue'
import { useUserStore } from '@/stores/user'
import type { Announcement } from '@/api/announcement'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const announcement = ref<Announcement | null>(null)

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
  router.push('/announcements')
}

// 编辑公告
const editAnnouncement = () => {
  router.push(`/announcements/${announcement.value?.id}/edit`)
}

// 删除公告
const deleteAnnouncement = async () => {
  if (!announcement.value) return

  try {
    await ElMessageBox.confirm('确定要删除这个公告吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteAnnouncement(announcement.value.id)
    ElMessage.success('删除成功')
    router.push('/announcements')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 加载公告
const loadAnnouncement = async () => {
  const announcementId = Number(route.params.id)
  if (!announcementId) {
    ElMessage.error('公告ID无效')
    router.push('/announcements')
    return
  }

  loading.value = true
  try {
    announcement.value = await getAnnouncementById(announcementId)
  } catch (error: any) {
    console.error('加载公告失败', error)
    ElMessage.error(error.message || '加载公告失败')
    router.push('/announcements')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAnnouncement()
})
</script>

<style scoped>
.announcement-detail-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #FAFBFC 0%, #F5F3FF 100%);
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow-x: hidden;
}

/* 背景装饰元素 */
.announcement-detail-page::before {
  content: '';
  position: fixed;
  top: 15%;
  right: 10%;
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.08) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 8s ease-in-out infinite;
  z-index: 0;
}

.announcement-detail-page::after {
  content: '';
  position: fixed;
  bottom: 15%;
  left: 8%;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(168, 213, 186, 0.08) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 10s ease-in-out infinite reverse;
  z-index: 0;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) scale(1);
  }
  50% {
    transform: translateY(-30px) scale(1.05);
  }
}

/* 插画区域 */
.illustration-header {
  position: absolute;
  top: 20px;
  right: 30px;
  z-index: 2;
  animation: slideInRight 0.8s ease-out;
}

@keyframes slideInRight {
  0% {
    opacity: 0;
    transform: translateX(100px) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

.illustration-bell {
  position: relative;
  width: 80px;
  height: 80px;
  animation: bellFloat 4s ease-in-out infinite;
}

@keyframes bellFloat {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(5deg);
  }
}

.bell-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.3);
  color: white;
  animation: bellPulse 2s ease-in-out infinite;
}

@keyframes bellPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 8px 24px rgba(140, 124, 240, 0.3);
  }
  50% {
    transform: scale(1.1);
    box-shadow: 0 12px 32px rgba(140, 124, 240, 0.4);
  }
}

/* 容器 */
.container {
  width: 90%;
  padding: 32px;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  animation: slideInUp 0.6s ease-out;
  position: relative;
  z-index: 1;
}

@keyframes slideInUp {
  0% {
    opacity: 0;
    transform: translateY(40px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 卡片 */
.card {
  background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FF 100%);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(140, 124, 240, 0.15);
  position: relative;
  overflow: hidden;
  width: 90%;
  display: flex;
  flex-direction: column;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF, #A8D5BA, #FFE082);
  background-size: 300% 100%;
  animation: gradientMove 8s linear infinite;
}

@keyframes gradientMove {
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

/* 卡片装饰圆点 */
.card::after {
  content: '';
  position: absolute;
  top: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

/* 返回按钮 */
.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FF 100%);
  color: #8C7CF0;
  border: 2px solid #E8E4FF;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.15);
  margin-bottom: 24px;
  align-self: flex-start;
  position: relative;
  overflow: hidden;
}

.back-button::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.2) 0%, transparent 70%);
  transform: scale(0);
  transition: transform 0.6s ease;
  border-radius: 50%;
}

.back-button:hover {
  background: linear-gradient(135deg, #E8E4FF 0%, #D8D8FF 100%);
  border-color: #8C7CF0;
  transform: translateX(-6px) translateY(-2px);
  box-shadow: 0 8px 20px rgba(140, 124, 240, 0.25);
}

.back-button:hover::before {
  transform: scale(1);
}

.back-button:active {
  transform: translateX(-6px) translateY(0) scale(0.95);
}

/* 标题 */
h1 {
  text-align: center;
  color: #1A202C;
  margin-bottom: 32px;
  font-size: 32px;
  font-weight: 700;
  position: relative;
  z-index: 1;
  background: linear-gradient(135deg, #8C7CF0 0%, #6B5DD3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: titleGlow 3s ease-in-out infinite;
}

@keyframes titleGlow {
  0%, 100% {
    filter: drop-shadow(0 0 0 rgba(140, 124, 240, 0));
  }
  50% {
    filter: drop-shadow(0 0 8px rgba(140, 124, 240, 0.3));
  }
}

/* 加载状态 */
.loading {
  text-align: center;
  padding: 40px;
  font-size: 16px;
  font-weight: 600;
  color: #8B9BB4;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

/* 公告内容 */
.announcement-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

/* 公告卡片 */
.announcement-card {
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
  padding: 24px;
  border-radius: 16px;
  border: 2px solid #F0F2F5;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.5s ease-out backwards;
}

@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.announcement-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 5px;
  height: 100%;
  background: linear-gradient(180deg, #8C7CF0 0%, #C6B9FF 50%, #A8D5BA 100%);
  border-radius: 5px 0 0 5px;
  transition: all 0.3s ease;
}

.announcement-card:hover {
  transform: translateY(-6px) scale(1.01);
  border-color: #C6B9FF;
  box-shadow: 0 12px 32px rgba(140, 124, 240, 0.2);
}

.announcement-card:hover::before {
  width: 8px;
  box-shadow: 0 0 15px rgba(140, 124, 240, 0.4);
}

/* 公告头部 */
.announcement-header {
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.announcement-header h2 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #1A202C;
  transition: all 0.3s ease;
  line-height: 1.3;
}

.announcement-card:hover .announcement-header h2 {
  color: #8C7CF0;
}

/* 公告元信息 */
.announcement-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  font-size: 14px;
  color: #8B9BB4;
  align-items: center;
  position: relative;
  z-index: 1;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #F0F2F5;
}

.meta-item {
  color: inherit;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  padding: 6px 12px;
  border-radius: 12px;
  background: rgba(140, 124, 240, 0.05);
}

.announcement-card:hover .meta-item {
  color: #8C7CF0;
  background: rgba(140, 124, 240, 0.1);
}

/* 公告正文 */
.announcement-body {
  margin-top: 20px;
  position: relative;
  z-index: 1;
}

.announcement-text {
  line-height: 1.8;
  color: #4A5568;
  transition: all 0.3s ease;
  padding: 20px;
  background: rgba(248, 249, 255, 0.5);
  border-radius: 12px;
  border: 1px solid #E8E4FF;
}

.announcement-card:hover .announcement-text {
  color: #1A202C;
  background: rgba(248, 249, 255, 0.8);
}

/* 接收者 */
.receivers {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 2px solid #F0F2F5;
  position: relative;
  z-index: 1;
}

.receivers-title {
  font-weight: 600;
  margin-bottom: 16px;
  color: #1A202C;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
}

.receivers-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.receiver-tag {
  padding: 8px 16px;
  background: linear-gradient(135deg, #E8E4FF 0%, #D8D8FF 100%);
  color: #8C7CF0;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 1px solid #C6B9FF;
}

.receiver-tag:hover {
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  color: #FFFFFF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
}

/* 公告操作 */
.announcement-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 2px solid #F0F2F5;
  position: relative;
  z-index: 1;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.edit-button {
  background: linear-gradient(135deg, #E8E4FF 0%, #D8D8FF 100%);
  color: #8C7CF0;
  border-color: #C6B9FF;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.15);
}

.edit-button:hover {
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  color: #FFFFFF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
}

.delete-button {
  background: linear-gradient(135deg, #FFE0E0 0%, #FFC7C7 100%);
  color: #E53935;
  border-color: #FFC7C7;
  box-shadow: 0 2px 8px rgba(229, 57, 53, 0.15);
}

.delete-button:hover {
  background: linear-gradient(135deg, #E53935 0%, #FF5252 100%);
  color: #FFFFFF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(229, 57, 53, 0.3);
}

/* 空状态 */
.empty-state {
  padding: 80px 40px;
  background: linear-gradient(135deg, #FAFBFC 0%, #F5F7FA 100%);
  border-radius: 20px;
  border: 3px dashed #E8E4FF;
  position: relative;
  overflow: hidden;
  text-align: center;
  animation: fadeInUp 0.6s ease-out;
}

.empty-state::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.05) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 3s ease-in-out infinite;
}

.empty-state p {
  font-size: 18px;
  font-weight: 600;
  color: #8B9BB4;
  margin: 0;
  position: relative;
  z-index: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .announcement-detail-page {
    padding: 16px;
  }
  
  .container {
    width: 95%;
    padding: 24px;
  }
  
  .card {
    width: 100%;
  }
  
  h1 {
    font-size: 24px;
  }
  
  .announcement-header h2 {
    font-size: 20px;
  }
  
  .announcement-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .meta-item {
    width: 100%;
    justify-content: flex-start;
  }
  
  .announcement-actions {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
    justify-content: center;
  }
  
  .receivers-list {
    justify-content: center;
  }
}
</style>





