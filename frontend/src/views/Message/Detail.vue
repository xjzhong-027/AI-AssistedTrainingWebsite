<template>
  <div class="message-detail-page">
    <el-card v-loading="loading">
      <div class="card-header">
        <el-button @click="goBack">返回</el-button>
        <div>
          <el-button type="danger" @click="deleteMessage">删除</el-button>
        </div>
      </div>

      <div v-if="message" class="message-content">
        <el-card>
          <div class="message-header">
            <h2>{{ message.title }}</h2>
            <el-tag v-if="message.isRead" type="success">已读</el-tag>
            <el-tag v-else type="warning">未读</el-tag>
          </div>
          <div class="message-meta">
            <span>发送者：{{ message.sender }}</span>
            <span>发送时间：{{ formatDate(message.createdAt) }}</span>
            <span v-if="message.readAt">阅读时间：{{ formatDate(message.readAt) }}</span>
          </div>
          <div class="message-body">
            <div v-html="message.content" class="message-text"></div>
          </div>
        </el-card>
      </div>

      <div v-else-if="!loading" class="empty-state">
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

const route = useRoute()
const router = useRouter()

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
  router.push('/messages')
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
    router.push('/messages')
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
    router.push('/messages')
    return
  }

  loading.value = true
  try {
    message.value = await getMessageById(messageId)
    
    // 如果未读，标记为已读
    if (message.value && !message.value.isRead) {
      await markMessageAsRead(messageId)
      message.value.isRead = true
      message.value.readAt = new Date().toISOString()
    }
  } catch (error: any) {
    console.error('加载消息失败', error)
    ElMessage.error(error.message || '加载消息失败')
    router.push('/messages')
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
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.message-content {
  margin-top: 20px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.message-header h2 {
  margin: 0;
  flex: 1;
}

.message-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  font-size: 14px;
  color: #909399;
}

.message-body {
  margin-top: 20px;
}

.message-text {
  line-height: 1.8;
  color: #303133;
}

.empty-state {
  padding: 40px;
  text-align: center;
}
</style>





