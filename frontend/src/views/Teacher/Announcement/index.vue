<template>
  <div class="announcement-page">
    <div class="announcement-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          </div>
          <h2>公告管理</h2>
        </div>
        <div class="header-actions">
          <button @click="goHome" class="secondary-button">返回首页</button>
          <button @click="createAnnouncement" class="primary-button">发布公告</button>
        </div>
      </div>

      <!-- 公告列表 -->
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      <div v-else-if="announcements.length === 0" class="no-announcements">
        <div class="empty-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <h3>暂无公告</h3>
        <p>还没有发布任何公告，开始创建第一个公告吧！</p>
        <button @click="createAnnouncement" class="primary-button">发布公告</button>
      </div>
      <div v-else class="announcements-list">
        <div
          v-for="announcement in announcements"
          :key="announcement.id"
          class="announcement-item"
        >
          <div class="announcement-header">
            <h3>{{ announcement.a_title }}</h3>
            <div class="announcement-badges">
              <el-tag type="info" size="small">发布于: {{ formatDate(announcement.created_at) }}</el-tag>
            </div>
          </div>
          <p class="announcement-content">{{ announcement.a_content }}</p>
          <div class="announcement-footer">
            <div class="announcement-meta">
              <span class="announcement-sender">发布者: {{ announcement.sender_name || '未知' }}</span>
              <span v-if="announcement.receivers" class="announcement-receivers">
                接收者: {{ announcement.receivers.length }} 人
              </span>
            </div>
          </div>
          <div class="announcement-actions">
            <el-button size="small" @click="viewAnnouncement(announcement.id)" class="link-button">查看详情</el-button>
            <el-button size="small" @click="editAnnouncement(announcement.id)" class="secondary-button small">编辑</el-button>
            <el-button size="small" @click="handleDeleteAnnouncement(announcement.id)" class="danger-button small">删除</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTeacherAnnouncements, deleteAnnouncement } from '@/api/announcement'
import type { Announcement } from '@/api/announcement'

const router = useRouter()

const loading = ref(false)
const announcements = ref<Announcement[]>([])

const goHome = () => {
  router.push('/teacher/dashboard')
}

const createAnnouncement = () => {
  router.push('/teacher/announcements/create')
}

const viewAnnouncement = (id: number) => {
  router.push(`/announcements/${id}`)
}

const editAnnouncement = (id: number) => {
  router.push(`/teacher/announcements/edit/${id}`)
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

const handleDeleteAnnouncement = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个公告吗？删除后无法恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteAnnouncement(id)
    ElMessage.success('删除成功')
    await loadAnnouncements()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const loadAnnouncements = async () => {
  loading.value = true
  try {
    const data = await getTeacherAnnouncements()
    announcements.value = data
  } catch (error) {
    console.error('加载公告列表失败', error)
    ElMessage.error('加载公告列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAnnouncements()
})
</script>

<style scoped>
.announcement-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.announcement-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: 1200px;
}

.announcement-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #F0F2F5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
  animation: float 3s ease-in-out infinite;
}

.header-icon svg {
  width: 24px;
  height: 24px;
}

.header-left h2 {
  font-size: 24px;
  font-weight: 600;
  color: #4A5568;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 按钮样式 */
.primary-button {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
}

.primary-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.4);
}

.secondary-button {
  background: #F0F2F5;
  color: #4A5568;
  border: 1px solid #E2E8F0;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.secondary-button:hover {
  background: #E2E8F0;
  transform: translateY(-2px);
}

.secondary-button.small {
  padding: 6px 12px;
  font-size: 12px;
}

.danger-button {
  background: #FED7D7;
  color: #E53E3E;
  border: 1px solid #F56565;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.danger-button:hover {
  background: #F56565;
  color: white;
  transform: translateY(-2px);
}

.danger-button.small {
  padding: 6px 12px;
  font-size: 12px;
}

.link-button {
  color: #8C7CF0;
  background: transparent;
  border: none;
  padding: 6px 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
}

.link-button:hover {
  background: rgba(140, 124, 240, 0.1);
  transform: translateY(-1px);
}

/* 公告列表 */
.announcements-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.announcement-item {
  background: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
  padding: 20px;
  transition: all 0.3s ease;
  border: 1px solid #F0F2F5;
}

.announcement-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.15);
  border-color: #E2E8F0;
}

.announcement-header {
  margin-bottom: 12px;
}

.announcement-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #4A5568;
  margin: 0 0 8px 0;
}

.announcement-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.announcement-content {
  color: #718096;
  margin: 0 0 16px 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 14px;
}

.announcement-footer {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #F0F2F5;
}

.announcement-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #A0AEC0;
  flex-wrap: wrap;
}

.announcement-sender, .announcement-receivers {
  display: flex;
  align-items: center;
}

.announcement-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

/* 加载和空状态 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #718096;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #F0F2F5;
  border-top: 3px solid #8C7CF0;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.no-announcements {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: #718096;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(140, 124, 240, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8C7CF0;
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}

.no-announcements h3 {
  font-size: 18px;
  font-weight: 600;
  color: #4A5568;
  margin: 0 0 8px 0;
}

.no-announcements p {
  margin: 0 0 24px 0;
  font-size: 14px;
}

/* 动画 */
@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0px);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .announcement-page {
    padding: 16px;
  }

  .announcement-card {
    padding: 16px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    justify-content: space-between;
  }

  .announcement-actions {
    justify-content: flex-start;
  }

  .announcement-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>