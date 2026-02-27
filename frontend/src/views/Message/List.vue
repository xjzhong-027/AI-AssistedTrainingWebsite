<template>
  <div class="message-page">
      <div class="container card">
        <h1>消息箱</h1>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading">加载中...</div>
        
        <!-- 消息列表 -->
        <div v-else class="messages-list">
          <div
            v-for="(message, index) in messages"
            :key="message.id"
            class="message-item"
            :class="{ selected: selectedIndex === index, unread: !message.isRead }"
            @click="selectMessage(index, message.id)"
          >
            <div class="message-header">
              <h3>{{ message.title }}</h3>
              <span class="message-status" :class="message.isRead ? 'read' : 'unread'">
                {{ message.isRead ? '已读' : '未读' }}
              </span>
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
        <div class="pagination">
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

const router = useRouter()

const loading = ref(false)
const selectedIndex = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const messages = ref<Message[]>([])

const selectMessage = (index: number, id: number) => {
  selectedIndex.value = selectedIndex.value === index ? null : index
  router.push(`/messages/${id}`)
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
</script>

<style scoped>
.message-page {
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

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-item {
  background-color: rgba(186, 207, 206, 0.1);
  padding: 18px 20px;
  border-radius: 12px;
  border: 1px solid #BACFCE;
  border-left: 4px solid #99B6B4;
  transition: all 0.3s ease;
  cursor: pointer;
}

.message-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-3px);
  background-color: rgba(186, 207, 206, 0.15);
  border-left-color: #D48982;
}

.message-item.unread {
  border-left-color: #D48982;
  background-color: rgba(212, 137, 130, 0.1);
}

.message-item.selected {
  background-color: #1A1A1A;
  color: #FFFFFF;
  border-left-color: #D48982;
}

.message-item.selected * {
  color: #FFFFFF;
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
  color: inherit;
}

.message-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.message-status.read {
  background-color: rgba(153, 182, 180, 0.2);
  color: #1A1A1A;
}

.message-item.selected .message-status.read {
  background-color: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
}

.message-status.unread {
  background-color: rgba(212, 137, 130, 0.2);
  color: #1A1A1A;
}

.message-item.selected .message-status.unread {
  background-color: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
}

.message-content {
  color: #666;
  margin: 0 0 12px 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.message-item.selected .message-content {
  color: rgba(255, 255, 255, 0.8);
}

.message-footer {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #999;
}

.message-item.selected .message-footer {
  color: rgba(255, 255, 255, 0.7);
}

.message-time,
.message-sender {
  color: inherit;
}

.no-messages {
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

