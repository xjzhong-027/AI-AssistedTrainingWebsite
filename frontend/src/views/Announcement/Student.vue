<template>
  <div class="announcement-page">
    <div class="container card">
      <!-- 插画区域 -->
      <div class="illustration-header">
        <div class="illustration-bell">
          <div class="bell-body">
            <div class="bell-top"></div>
            <div class="bell-content">
              <div class="bell-clapper"></div>
            </div>
          </div>
          <div class="bell-shine"></div>
        </div>
      </div>
      
      <!-- 返回首页按钮 -->
      <button class="back-button" @click="goToHome">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
          <polyline points="9 22 9 12 15 12 15 22"></polyline>
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
            </div>
            <p class="announcement-content">{{ announcement.a_content }}</p>
            <div class="announcement-footer">
              <span class="announcement-time">发布时间: {{ formatDate(announcement.created_at) }}</span>
              <span class="announcement-sender">发布者: {{ announcement.teacher_name || '未知' }}</span>
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
      teacher_name: ann.teacher_name || '未知',
      teacher_id: ann.teacher_id,
      created_at: ann.created_at,
      updated_at: ann.updated_at,
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

const goBack = () => {
  router.back()
}

const goToHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.announcement-page {
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
  width: 120px;
  height: 140px;
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

.bell-body {
  position: relative;
  width: 100px;
  height: 120px;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  border-radius: 50px 50px 20px 20px;
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.3);
  overflow: hidden;
  position: relative;
  margin: 0 auto;
}

.bell-top {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #6B5BCE 0%, #8C7CF0 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bell-top::after {
  content: '';
  width: 10px;
  height: 10px;
  background: #FFD54F;
  border-radius: 50%;
}

.bell-content {
  position: absolute;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bell-clapper {
  width: 12px;
  height: 40px;
  background: linear-gradient(180deg, #FFD54F 0%, #FFB74D 100%);
  border-radius: 6px;
  animation: bellRing 2s ease-in-out infinite;
  position: relative;
}

.bell-clapper::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #FFD54F 0%, #FFB74D 100%);
  border-radius: 50%;
}

@keyframes bellRing {
  0%, 100% {
    transform: translateX(-50%) rotate(-10deg);
  }
  50% {
    transform: translateX(-50%) rotate(10deg);
  }
}

.bell-shine {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 30px;
  height: 30px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, transparent 70%);
  border-radius: 50%;
  animation: shineMove 3s ease-in-out infinite;
  z-index: 1;
}

@keyframes shineMove {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(10px, 10px);
  }
}

/* 背景装饰元素 */
.announcement-page::before {
  content: '';
  position: fixed;
  top: 12%;
  right: 8%;
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.08) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 9s ease-in-out infinite;
  z-index: 0;
}

.announcement-page::after {
  content: '';
  position: fixed;
  bottom: 18%;
  left: 10%;
  width: 90px;
  height: 90px;
  background: radial-gradient(circle, rgba(255, 224, 130, 0.08) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 11s ease-in-out infinite reverse;
  z-index: 0;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) scale(1);
  }
  50% {
    transform: translateY(-25px) scale(1.05);
  }
}

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

.container {
  width: 90%;
  padding: 32px;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  animation: slideInUp 0.6s ease-out;
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

.announcements-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.announcement-item {
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
  padding: 20px;
  border-radius: 16px;
  border: 2px solid #F0F2F5;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.5s ease-out backwards;
}

.announcement-item:nth-child(1) {
  animation-delay: 0.1s;
}

.announcement-item:nth-child(2) {
  animation-delay: 0.2s;
}

.announcement-item:nth-child(3) {
  animation-delay: 0.3s;
}

.announcement-item:nth-child(4) {
  animation-delay: 0.4s;
}

.announcement-item:nth-child(5) {
  animation-delay: 0.5s;
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

.announcement-item::before {
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

.announcement-item:hover {
  transform: translateY(-6px) scale(1.02);
  border-color: #C6B9FF;
  box-shadow: 0 12px 32px rgba(140, 124, 240, 0.2);
}

.announcement-item:hover::before {
  width: 8px;
  box-shadow: 0 0 15px rgba(140, 124, 240, 0.4);
}

.announcement-item.selected {
  background: linear-gradient(135deg, #E8E4FF 0%, #D8D8FF 100%);
  color: #8C7CF0;
  border-color: #8C7CF0;
  transform: scale(1.02);
  box-shadow: 0 12px 32px rgba(140, 124, 240, 0.25);
}

.announcement-item.selected::before {
  background: linear-gradient(180deg, #A8D5BA 0%, #8BC4A8 100%);
  width: 8px;
}

.announcement-item.selected * {
  color: #8C7CF0;
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.announcement-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: inherit;
  flex: 1;
  margin-right: 16px;
  transition: all 0.3s ease;
}

.announcement-item:hover .announcement-header h3 {
  color: #8C7CF0;
}

.announcement-status {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.announcement-status::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s ease;
}

.announcement-item:hover .announcement-status::before {
  left: 100%;
}

.announcement-status.read {
  background: linear-gradient(135deg, #A8D5BA 0%, #8BC4A8 100%);
  color: #FFFFFF;
  box-shadow: 0 2px 8px rgba(168, 213, 186, 0.3);
}

.announcement-item.selected .announcement-status.read {
  background: linear-gradient(135deg, #C6B9FF 0%, #8C7CF0 100%);
  color: #FFFFFF;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.4);
}

.announcement-status.unread {
  background: linear-gradient(135deg, #FFE082 0%, #FFB74D 100%);
  color: #1A202C;
  box-shadow: 0 2px 8px rgba(255, 224, 130, 0.3);
}

.announcement-item.selected .announcement-status.unread {
  background: linear-gradient(135deg, #FFE082 0%, #FFB74D 100%);
  color: #1A202C;
  box-shadow: 0 2px 8px rgba(255, 224, 130, 0.4);
}

.announcement-content {
  color: #4A5568;
  margin: 0 0 16px 0;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.announcement-item:hover .announcement-content {
  color: #1A202C;
}

.announcement-item.selected .announcement-content {
  color: #8C7CF0;
}

.announcement-footer {
  display: flex;
  gap: 24px;
  font-size: 14px;
  color: #8B9BB4;
  align-items: center;
  position: relative;
  z-index: 1;
}

.announcement-item.selected .announcement-footer {
  color: #8C7CF0;
}

.announcement-time,
.announcement-sender {
  color: inherit;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.announcement-item:hover .announcement-time,
.announcement-item:hover .announcement-sender {
  color: #8C7CF0;
}

.no-announcements {
  text-align: center;
  padding: 80px 40px;
  background: linear-gradient(135deg, #FAFBFC 0%, #F5F7FA 100%);
  border-radius: 20px;
  border: 3px dashed #E8E4FF;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.6s ease-out;
}

.no-announcements::before {
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

.no-announcements p {
  font-size: 18px;
  font-weight: 600;
  color: #8B9BB4;
  margin: 0;
  position: relative;
  z-index: 1;
}

.pagination {
  margin-top: 32px;
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 2px solid #F0F2F5;
  position: relative;
}

/* 分页样式增强 */
:deep(.el-pagination) {
  --el-pagination-button-bg-color: #FFFFFF;
  --el-pagination-button-color: #4A5568;
  --el-pagination-hover-color: #8C7CF0;
  --el-pagination-bg-color: #FFFFFF;
  --el-pagination-border-radius: 12px;
  font-weight: 600;
}

:deep(.el-pagination.is-background .el-pager li) {
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid #F0F2F5;
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
}

:deep(.el-pagination.is-background .el-pager li:hover) {
  background: linear-gradient(135deg, #E8E4FF 0%, #D8D8FF 100%);
  border-color: #C6B9FF;
  color: #8C7CF0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2);
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  border-color: #8C7CF0;
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
  transform: scale(1.05);
}

:deep(.el-pagination button) {
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid #F0F2F5;
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
}

:deep(.el-pagination button:hover) {
  background: linear-gradient(135deg, #E8E4FF 0%, #D8D8FF 100%);
  border-color: #C6B9FF;
  color: #8C7CF0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2);
}

:deep(.el-pagination button:disabled) {
  background: #F5F7FA;
  color: #8B9BB4;
  border-color: #F0F2F5;
}

:deep(.el-pagination__sizes .el-select .el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid #F0F2F5;
  transition: all 0.3s ease;
}

:deep(.el-pagination__sizes .el-select .el-input__wrapper:hover) {
  border-color: #C6B9FF;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.15);
}

:deep(.el-pagination__sizes .el-select .el-input__wrapper.is-focus) {
  border-color: #8C7CF0;
  box-shadow: 0 0 0 4px rgba(140, 124, 240, 0.2);
}

:deep(.el-pagination__jump .el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid #F0F2F5;
  transition: all 0.3s ease;
}

:deep(.el-pagination__jump .el-input__wrapper:hover) {
  border-color: #C6B9FF;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.15);
}

:deep(.el-pagination__jump .el-input__wrapper.is-focus) {
  border-color: #8C7CF0;
  box-shadow: 0 0 0 4px rgba(140, 124, 240, 0.2);
}
</style>

