<template>
  <div class="forum-detail-page">
    <div class="container card">
      <!-- 插画区域 -->
      <div class="illustration-header">
        <div class="illustration-chat">
          <div class="chat-bubble">
            <div class="bubble-content">
              <div class="message-dot"></div>
              <div class="message-dot"></div>
              <div class="message-dot"></div>
            </div>
            <div class="bubble-tail"></div>
          </div>
        </div>
      </div>
      
      <!-- 返回首页按钮 -->
      <button class="back-button" @click="goBack">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        返回论坛
      </button>
        <h1>帖子详情</h1>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading">加载中...</div>
        
        <!-- 帖子内容 -->
        <div v-else-if="post" class="post-content">
          <!-- 帖子信息 -->
          <div class="post-card">
            <div class="post-header">
              <h2>{{ post.title }}</h2>
              <span class="post-status" :class="post.isPublic ? 'public' : 'private'">
                {{ post.isPublic ? '公开' : '私密' }}
              </span>
            </div>
            <div class="post-meta">
              <span class="post-author">作者：{{ post.author }}</span>
              <span class="post-time">发布时间：{{ formatDate(post.createdAt) }}</span>
              <span v-if="post.updatedAt !== post.createdAt" class="post-time">更新时间：{{ formatDate(post.updatedAt) }}</span>
            </div>
            <div class="post-body">
              <div v-html="post.content" class="post-text"></div>
            </div>
            <div v-if="post && userStore.userInfo?.id === post.authorId" class="post-actions">
              <button class="action-button edit-button" @click="editPost">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                编辑
              </button>
              <button class="action-button delete-button" @click="deletePost">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
                删除
              </button>
            </div>
          </div>

          <!-- 评论区域 -->
          <div class="comments-card">
            <div class="card-header-title">
              评论 ({{ comments.length }})
            </div>

            <!-- 发表评论 -->
            <div class="comment-form">
              <el-input
                v-model="newComment"
                type="textarea"
                :rows="4"
                placeholder="请输入评论内容"
                maxlength="1000"
                show-word-limit
              ></el-input>
              <div class="comment-actions">
                <button class="submit-button" @click="submitComment" :class="{ loading: submitting }">
                  <span v-if="!submitting">发表评论</span>
                  <span v-else>发表中...</span>
                </button>
              </div>
            </div>

            <!-- 评论列表 -->
            <div class="comments-list">
              <div v-for="comment in comments" :key="comment.id" class="comment-item">
                <div class="comment-header">
                  <span class="comment-author">{{ comment.author }}</span>
                  <span class="comment-time">{{ formatDate(comment.createdAt) }}</span>
                  <div v-if="userStore.userInfo?.id === comment.authorId" class="comment-actions">
                    <button class="comment-action-button edit" @click="editComment(comment)">编辑</button>
                    <button class="comment-action-button delete" @click="deleteComment(comment.id)">删除</button>
                  </div>
                </div>
                <div class="comment-content">{{ comment.content }}</div>
              </div>
              <div v-if="comments.length === 0" class="no-comments">
                <p>暂无评论，快来发表第一条评论吧！</p>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!loading" class="empty-state">
          <p>帖子不存在</p>
        </div>
      </div>

    <!-- 编辑评论对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑评论"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-input
        v-model="editCommentContent"
        type="textarea"
        :rows="6"
        placeholder="请输入评论内容"
        maxlength="1000"
        show-word-limit
      ></el-input>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelEditComment">取消</el-button>
          <el-button type="primary" @click="saveEditedComment" :loading="editingSubmitting">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
    <AIWindow :show-grade-button="false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPostById, getPostComments, createComment, updateComment, deleteComment as deleteCommentApi, deletePost as deletePostApi } from '@/api/forum'
import { useUserStore } from '@/stores/user'
import type { Post, Comment } from '@/api/forum'
import AIWindow from '@/components/common/AIWindow/index.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const post = ref<Post | null>(null)
const comments = ref<Comment[]>([])
const newComment = ref('')

// 编辑评论相关
const editDialogVisible = ref(false)
const editingComment = ref<Comment | null>(null)
const editCommentContent = ref('')
const editingSubmitting = ref(false)

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
  router.push('/forum')
}

// 编辑帖子
const editPost = () => {
  router.push(`/forum/post/${post.value?.id}/edit`)
}

// 删除帖子
const deletePost = async () => {
  if (!post.value) return

  try {
    await ElMessageBox.confirm('确定要删除这个帖子吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deletePostApi(post.value.id)
    ElMessage.success('删除成功')
    router.push('/forum')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 提交评论
const submitComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }

  if (!post.value) return

  submitting.value = true
  try {
    await createComment(post.value.id, {
      content: newComment.value
    })
    ElMessage.success('评论发表成功')
    newComment.value = ''
    await loadComments()
    // 更新帖子的评论数
    if (post.value) {
      post.value.commentCount = comments.value.length
    }
    // 跳转到论坛页面，确保评论数更新
    router.push('/forum')
  } catch (error: any) {
    console.error('发表评论失败', error)
    ElMessage.error(error.message || '发表评论失败')
  } finally {
    submitting.value = false
  }
}

// 编辑评论
const editComment = (comment: Comment) => {
  editingComment.value = comment
  editCommentContent.value = comment.content
  editDialogVisible.value = true
}

// 保存编辑的评论
const saveEditedComment = async () => {
  if (!editCommentContent.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }

  if (!editingComment.value) return

  editingSubmitting.value = true
  try {
    await updateComment(editingComment.value.id, editCommentContent.value)
    ElMessage.success('评论更新成功')
    editDialogVisible.value = false
    await loadComments()
    // 跳转到论坛页面，确保评论数更新
    router.push('/forum')
  } catch (error: any) {
    console.error('更新评论失败', error)
    ElMessage.error(error.message || '更新评论失败')
  } finally {
    editingSubmitting.value = false
  }
}

// 取消编辑评论
const cancelEditComment = () => {
  editDialogVisible.value = false
  editingComment.value = null
  editCommentContent.value = ''
}

// 删除评论
const deleteComment = async (commentId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteCommentApi(commentId)
    ElMessage.success('删除成功')
    await loadComments()
    // 跳转到论坛页面，确保评论数更新
    router.push('/forum')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 加载帖子
const loadPost = async () => {
  const postId = Number(route.params.id)
  if (!postId) {
    ElMessage.error('帖子ID无效')
    router.push('/forum')
    return
  }

  loading.value = true
  try {
    const postData = await getPostById(postId)
    // 处理帖子数据，确保isPublic字段正确设置
    post.value = {
      ...postData,
      isPublic: postData.is_public !== false,
      author: postData.author_name || postData.author || '未知',
      authorId: postData.author_id || 0,
      createdAt: postData.created_at || postData.createdAt,
      updatedAt: postData.updated_at || postData.updatedAt,
      commentCount: postData.comment_count || 0
    }
    await loadComments()
  } catch (error: any) {
    console.error('加载帖子失败', error)
    ElMessage.error(error.message || '加载帖子失败')
    router.push('/forum')
  } finally {
    loading.value = false
  }
}

// 加载评论
const loadComments = async () => {
  if (!post.value) return

  try {
    const commentsData = await getPostComments(post.value.id)
    // 处理评论数据，确保字段名正确
    comments.value = commentsData.map((comment: any) => ({
      id: comment.id,
      content: comment.content,
      author: comment.author_name || comment.author || '未知',
      authorId: comment.author_id || 0,
      postId: comment.post_id || post.value.id,
      createdAt: comment.created_at || comment.createdAt,
      updatedAt: comment.updated_at || comment.updatedAt
    }))
  } catch (error: any) {
    console.error('加载评论失败', error)
    ElMessage.error(error.message || '加载评论失败')
  }
}

onMounted(() => {
  loadPost()
})
</script>

<style scoped>
.forum-detail-page {
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

.illustration-chat {
  position: relative;
  width: 120px;
  height: 100px;
  animation: chatFloat 4s ease-in-out infinite;
}

@keyframes chatFloat {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(5deg);
  }
}

.chat-bubble {
  position: relative;
  width: 100px;
  height: 80px;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  border-radius: 20px 20px 20px 4px;
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.3);
  overflow: hidden;
  position: relative;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bubble-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px;
}

.message-dot {
  width: 12px;
  height: 12px;
  background: white;
  border-radius: 50%;
  animation: messageBounce 1.5s ease-in-out infinite;
}

.message-dot:nth-child(1) {
  animation-delay: 0s;
}

.message-dot:nth-child(2) {
  animation-delay: 0.3s;
}

.message-dot:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes messageBounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.bubble-tail {
  position: absolute;
  bottom: 0;
  left: -10px;
  width: 0;
  height: 0;
  border-top: 10px solid transparent;
  border-right: 20px solid #8C7CF0;
  border-bottom: 10px solid transparent;
}

/* 背景装饰元素 */
.forum-detail-page::before {
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

.forum-detail-page::after {
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

.post-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

.post-card {
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

.post-card::before {
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

.post-card:hover {
  transform: translateY(-6px) scale(1.01);
  border-color: #C6B9FF;
  box-shadow: 0 12px 32px rgba(140, 124, 240, 0.2);
}

.post-card:hover::before {
  width: 8px;
  box-shadow: 0 0 15px rgba(140, 124, 240, 0.4);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.post-header h2 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #1A202C;
  flex: 1;
  margin-right: 16px;
  transition: all 0.3s ease;
}

.post-card:hover .post-header h2 {
  color: #8C7CF0;
}

.post-status {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.post-status::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s ease;
}

.post-card:hover .post-status::before {
  left: 100%;
}

.post-status.public {
  background: linear-gradient(135deg, #A8D5BA 0%, #8BC4A8 100%);
  color: #FFFFFF;
  box-shadow: 0 2px 8px rgba(168, 213, 186, 0.3);
}

.post-status.private {
  background: linear-gradient(135deg, #FFE082 0%, #FFB74D 100%);
  color: #1A202C;
  box-shadow: 0 2px 8px rgba(255, 224, 130, 0.3);
}

.post-meta {
  display: flex;
  gap: 24px;
  font-size: 14px;
  color: #8B9BB4;
  align-items: center;
  position: relative;
  z-index: 1;
  margin-bottom: 20px;
}

.post-author {
  color: inherit;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.post-time {
  color: inherit;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.post-card:hover .post-meta * {
  color: #8C7CF0;
}

.post-body {
  margin-top: 20px;
  position: relative;
  z-index: 1;
}

.post-text {
  line-height: 1.8;
  color: #4A5568;
  transition: all 0.3s ease;
}

.post-card:hover .post-text {
  color: #1A202C;
}

.post-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
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

.comments-card {
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
  padding: 24px;
  border-radius: 16px;
  border: 2px solid #F0F2F5;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.5s ease-out backwards;
  animation-delay: 0.1s;
}

.comments-card:hover {
  transform: translateY(-6px) scale(1.01);
  border-color: #C6B9FF;
  box-shadow: 0 12px 32px rgba(140, 124, 240, 0.2);
}

.card-header-title {
  font-size: 18px;
  font-weight: 600;
  color: #1A202C;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
  background: linear-gradient(135deg, #8C7CF0 0%, #6B5DD3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.comment-form {
  margin-bottom: 30px;
  position: relative;
  z-index: 1;
}

:deep(.el-textarea__inner) {
  border-radius: 12px;
  border: 2px solid #F0F2F5;
  padding: 16px;
  font-size: 14px;
  line-height: 1.6;
  transition: all 0.3s ease;
  resize: vertical;
  min-height: 120px;
}

:deep(.el-textarea__inner:focus) {
  border-color: #8C7CF0;
  box-shadow: 0 0 0 4px rgba(140, 124, 240, 0.2);
}

:deep(.el-textarea__count) {
  font-size: 12px;
  color: #8B9BB4;
  margin-top: 8px;
  text-align: right;
}

.comment-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  position: relative;
  z-index: 1;
}

.submit-button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  color: #FFFFFF;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
  position: relative;
  overflow: hidden;
}

.submit-button::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  transform: scale(0);
  transition: transform 0.6s ease;
  border-radius: 50%;
}

.submit-button:hover {
  background: linear-gradient(135deg, #6B5DD3 0%, #8C7CF0 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(140, 124, 240, 0.4);
}

.submit-button:hover::before {
  transform: scale(1);
}

.submit-button:active {
  transform: translateY(0) scale(0.95);
}

.submit-button.loading {
  opacity: 0.7;
  cursor: not-allowed;
}

.comments-list {
  margin-top: 30px;
  position: relative;
  z-index: 1;
}

.comment-item {
  padding: 20px;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #F8F9FF 0%, #FFFFFF 100%);
  border-radius: 12px;
  border: 2px solid #F0F2F5;
  transition: all 0.3s ease;
  animation: fadeInUp 0.5s ease-out backwards;
}

.comment-item:hover {
  transform: translateY(-4px);
  border-color: #E8E4FF;
  box-shadow: 0 8px 20px rgba(140, 124, 240, 0.15);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.comment-author {
  font-weight: 600;
  color: #8C7CF0;
  font-size: 14px;
}

.comment-time {
  font-size: 12px;
  color: #8B9BB4;
  margin-left: 10px;
}

.comment-actions {
  display: flex;
  gap: 8px;
  margin-top: 0;
}

.comment-action-button {
  padding: 4px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.comment-action-button.edit {
  background: linear-gradient(135deg, #E8E4FF 0%, #D8D8FF 100%);
  color: #8C7CF0;
}

.comment-action-button.edit:hover {
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  color: #FFFFFF;
}

.comment-action-button.delete {
  background: linear-gradient(135deg, #FFE0E0 0%, #FFC7C7 100%);
  color: #E53935;
}

.comment-action-button.delete:hover {
  background: linear-gradient(135deg, #E53935 0%, #FF5252 100%);
  color: #FFFFFF;
}

.comment-content {
  color: #4A5568;
  line-height: 1.6;
  font-size: 14px;
}

.no-comments {
  padding: 40px;
  text-align: center;
  background: linear-gradient(135deg, #FAFBFC 0%, #F5F7FA 100%);
  border-radius: 12px;
  border: 2px dashed #E8E4FF;
  position: relative;
  overflow: hidden;
}

.no-comments::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.05) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 3s ease-in-out infinite;
}

.no-comments p {
  font-size: 16px;
  font-weight: 600;
  color: #8B9BB4;
  margin: 0;
  position: relative;
  z-index: 1;
}

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

/* 对话框样式增强 */
:deep(.el-dialog) {
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(140, 124, 240, 0.3);
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  color: #FFFFFF;
  padding: 20px;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #FFFFFF;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  padding: 20px;
  background: #F8F9FF;
  border-top: 2px solid #E8E4FF;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  border: none;
  border-radius: 8px;
  padding: 8px 20px;
  font-weight: 600;
  transition: all 0.3s ease;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #6B5DD3 0%, #8C7CF0 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
}

:deep(.el-button) {
  border-radius: 8px;
  padding: 8px 20px;
  font-weight: 600;
  transition: all 0.3s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>





