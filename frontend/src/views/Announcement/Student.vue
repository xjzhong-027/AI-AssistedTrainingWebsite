<template>
  <div class="announcement-page">
    <div class="container card">
      <!-- 返回首页按钮 -->
      <button class="back-button" @click="goToDashboard">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        返回首页
      </button>
        <h1>公告栏</h1>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading">加载中...</div>
        
        <!-- 公告列表 -->
        <div v-else class="announcements-list">
          <div
            v-for="(announcement, index) in announcements"
            :key="announcement.id"
            class="announcement-item"
            :class="{ selected: selectedIndex === index }"
            @click="selectAnnouncement(index, announcement.id)"
          >
            <div class="announcement-header">
              <h3>{{ announcement.a_title }}</h3>
              <span class="announcement-status" :class="announcement.isRead ? 'read' : 'unread'">
                {{ announcement.isRead ? '已读' : '未读' }}
              </span>
            </div>
            <p class="announcement-content">{{ announcement.a_content }}</p>
            <div class="announcement-footer">
              <span class="announcement-time">发布时间: {{ formatDate(announcement.created_at) }}</span>
              <span class="announcement-sender">发布者: {{ announcement.sender_name }}</span>
            </div>
          </div>
        </div>

        <div v-if="announcements.length === 0" class="no-announcements">
          <p>暂无公告</p>
        </div>

        <!-- 分页 -->
        <div v-if="announcements.length > 0" class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadAnnouncements"
            @current-change="loadAnnouncements"
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
import { getStudentAnnouncements } from '@/api/announcement'
import AIWindow from '@/components/common/AIWindow/index.vue'
import { useUserStore } from '@/stores/user'
import type { Announcement } from '@/api/announcement'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const selectedIndex = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const announcements = ref<Announcement[]>([])

const selectAnnouncement = (index: number, id: number) => {
  selectedIndex.value = selectedIndex.value === index ? null : index
  router.push(`/announcements/${id}`)
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

const loadAnnouncements = async () => {
  loading.value = true
  try {
    const studentId = userStore.userInfo?.id
    const data = await getStudentAnnouncements(studentId)
    announcements.value = data.map((ann: any) => ({
      id: ann.id,
      a_title: ann.a_title,
      a_content: ann.a_content,
      sender_name: ann.sender_name || '未知',
      sender_id: ann.sender_id,
      created_at: ann.created_at,
      updated_at: ann.updated_at,
      isRead: ann.is_read || false,
      receivers: ann.receivers || []
    }))
    total.value = announcements.value.length
  } catch (error) {
    console.error('加载公告列表失败', error)
    ElMessage.error('加载公告列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAnnouncements()
})

const goToDashboard = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.announcement-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #FAFBFC 0%, #F5F7FA 100%);
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background-color: #FFFFFF;
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
}

.back-button:hover {
  background-color: #E8E4FF;
  border-color: #8C7CF0;
  transform: translateX(-4px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2);
}

.container {
  width: 90%;
  padding: 32px;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
}

.card {
  background-color: #FFFFFF;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  position: relative;
  overflow: hidden;
  width: 90%;
  display: flex;
  flex-direction: column;
}

.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF);
}

h1 {
  text-align: center;
  color: #1A202C;
  margin-bottom: 32px;
  font-size: 28px;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

.no-announcements {
  text-align: center;
  padding: 60px 20px;
  color: #8B9BB4;
}

.pagination {
  margin-top: 32px;
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #F0F2F5;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background-color: #8C7CF0;
  color: #FFFFFF;
}

:deep(.el-pagination__sizes .el-input .el-input__inner) {
  border-color: #F0F2F5;
  border-radius: 8px;
}

:deep(.el-pagination__sizes .el-input .el-input__inner:hover) {
  border-color: #8C7CF0;
}

:deep(.el-pagination button:hover:not(:disabled)) {
  color: #8C7CF0;
}

.announcements-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.announcement-item {
  background-color: #FAFBFC;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #F0F2F5;
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 12px;
}

.announcement-item:hover {
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.12);
  transform: translateY(-3px);
  background-color: #F5F7FA;
  border-color: #E8E4FF;
}

.announcement-item.selected {
  background-color: #E8E4FF;
  color: #8C7CF0;
  border-color: #8C7CF0;
}

.announcement-item.selected * {
  color: #8C7CF0;
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.announcement-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #1A202C;
}

.announcement-item.selected .announcement-header h3 {
  color: #8C7CF0;
}

.announcement-status {
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}

.announcement-status.read {
  background-color: #E8F5E9;
  color: #4CAF50;
}

.announcement-item.selected .announcement-status.read {
  background-color: rgba(140, 124, 240, 0.2);
  color: #8C7CF0;
}

.announcement-status.unread {
  background-color: #FFF3E0;
  color: #FF9800;
}

.announcement-item.selected .announcement-status.unread {
  background-color: rgba(140, 124, 240, 0.2);
  color: #8C7CF0;
}

.announcement-content {
  color: #4A5568;
  margin: 0 0 12px 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.announcement-item.selected .announcement-content {
  color: #8C7CF0;
}

.announcement-footer {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #8B9BB4;
}

.announcement-item.selected .announcement-footer {
  color: #8C7CF0;
}

.announcement-time,
.announcement-sender {
  color: inherit;
}

.no-announcements {
  text-align: center;
  padding: 40px;
  color: #666;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background-color: #1A1A1A;
  color: #FFFFFF;
}
</style>

