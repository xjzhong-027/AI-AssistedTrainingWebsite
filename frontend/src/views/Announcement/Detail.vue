<template>
  <div class="announcement-detail-page">
    <el-card v-loading="loading">
      <div class="card-header">
        <el-button @click="goBack">返回</el-button>
        <div v-if="announcement && userStore.isTeacher()">
          <el-button @click="editAnnouncement">编辑</el-button>
          <el-button type="danger" @click="deleteAnnouncement">删除</el-button>
        </div>
      </div>

      <div v-if="announcement" class="announcement-content">
        <el-card>
          <div class="announcement-header">
            <h2>{{ announcement.a_title }}</h2>
            <el-tag v-if="announcement.isRead" type="success">已读</el-tag>
            <el-tag v-else type="warning">未读</el-tag>
          </div>
          <div class="announcement-meta">
            <span>发布者：{{ announcement.sender_name || '系统' }}</span>
            <span>发布时间：{{ formatDate(announcement.created_at) }}</span>
            <span v-if="announcement.updated_at && announcement.updated_at !== announcement.created_at">
              更新时间：{{ formatDate(announcement.updated_at) }}
            </span>
          </div>
          <div class="announcement-body">
            <div v-html="announcement.a_content" class="announcement-text"></div>
          </div>
          <div v-if="announcement.receivers && announcement.receivers.length > 0" class="receivers">
            <div class="receivers-title">接收者：</div>
            <el-tag
              v-for="receiver in announcement.receivers"
              :key="receiver.student_id"
              style="margin-right: 10px; margin-bottom: 10px"
            >
              {{ receiver.student_name }}
            </el-tag>
          </div>
        </el-card>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <el-empty description="公告不存在"></el-empty>
      </div>
    </el-card>
    <AIWindow :show-grade-button="false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAnnouncementById, markAnnouncementAsRead, deleteAnnouncement } from '@/api/announcement'
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
    
    // 如果是学生且未读，标记为已读
    if (userStore.isStudent() && announcement.value && !announcement.value.isRead) {
      await markAnnouncementAsRead(announcementId)
      announcement.value.isRead = true
    }
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
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.announcement-content {
  margin-top: 20px;
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.announcement-header h2 {
  margin: 0;
  flex: 1;
}

.announcement-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  font-size: 14px;
  color: #909399;
}

.announcement-body {
  margin-top: 20px;
}

.announcement-text {
  line-height: 1.8;
  color: #303133;
}

.receivers {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.receivers-title {
  font-weight: 500;
  margin-bottom: 10px;
  color: #606266;
}

.empty-state {
  padding: 40px;
  text-align: center;
}
</style>





