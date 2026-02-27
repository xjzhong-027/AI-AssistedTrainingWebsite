<template>
  <div class="announcement-page">
      <div class="container card">
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
        <div class="pagination">
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
</script>

<style scoped>
.announcement-page {
  width: 100%;
  padding: 0;
}

.container {
  max-width: 1000px;
  margin: 30px auto;
  padding: 40px;
}

h1 {
  text-align: center;
  color: #1A1A1A;
  margin-bottom: 30px;
  font-size: 36px;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

h1::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #99B6B4, #D48982);
  border-radius: 2px;
}

.announcements-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.announcement-item {
  background-color: rgba(186, 207, 206, 0.1);
  padding: 18px 20px;
  border-radius: 12px;
  border: 1px solid #BACFCE;
  border-left: 4px solid #99B6B4;
  transition: all 0.3s ease;
  cursor: pointer;
}

.announcement-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-3px);
  background-color: rgba(186, 207, 206, 0.15);
  border-left-color: #D48982;
}

.announcement-item.selected {
  background-color: #1A1A1A;
  color: #FFFFFF;
  border-left-color: #D48982;
}

.announcement-item.selected * {
  color: #FFFFFF;
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
  color: inherit;
}

.announcement-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.announcement-status.read {
  background-color: rgba(153, 182, 180, 0.2);
  color: #1A1A1A;
}

.announcement-item.selected .announcement-status.read {
  background-color: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
}

.announcement-status.unread {
  background-color: rgba(212, 137, 130, 0.2);
  color: #1A1A1A;
}

.announcement-item.selected .announcement-status.unread {
  background-color: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
}

.announcement-content {
  color: #666;
  margin: 0 0 12px 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.announcement-item.selected .announcement-content {
  color: rgba(255, 255, 255, 0.8);
}

.announcement-footer {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #999;
}

.announcement-item.selected .announcement-footer {
  color: rgba(255, 255, 255, 0.7);
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

