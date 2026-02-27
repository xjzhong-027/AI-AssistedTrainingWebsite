<template>
  <div class="forum-detail-page">
    <el-card v-loading="loading">
      <div class="card-header">
        <el-button @click="goBack">返回</el-button>
        <div v-if="post && userStore.userInfo?.id === post.authorId">
          <el-button @click="editPost">编辑</el-button>
          <el-button type="danger" @click="deletePost">删除</el-button>
        </div>
      </div>

      <div v-if="post" class="post-content">
        <!-- 帖子信息 -->
        <el-card class="post-card">
          <div class="post-header">
            <h2>{{ post.title }}</h2>
            <el-tag :type="post.isPublic ? 'success' : 'warning'">
              {{ post.isPublic ? '公开' : '私密' }}
            </el-tag>
          </div>
          <div class="post-meta">
            <span>作者：{{ post.author }}</span>
            <span>发布时间：{{ formatDate(post.createdAt) }}</span>
            <span v-if="post.updatedAt !== post.createdAt">更新时间：{{ formatDate(post.updatedAt) }}</span>
          </div>
          <div class="post-body">
            <div v-html="post.content" class="post-text"></div>
          </div>
        </el-card>

        <!-- 评论区域 -->
        <el-card class="comments-card">
          <template #header>
            <div class="card-header-title">
              评论 ({{ comments.length }})
            </div>
          </template>

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
              <el-button type="primary" @click="submitComment" :loading="submitting">发表评论</el-button>
            </div>
          </div>

          <!-- 评论列表 -->
          <div class="comments-list">
            <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <div class="comment-header">
                <span class="comment-author">{{ comment.author }}</span>
                <span class="comment-time">{{ formatDate(comment.createdAt) }}</span>
                <div v-if="userStore.userInfo?.id === comment.authorId" class="comment-actions">
                  <el-button size="small" text @click="editComment(comment)">编辑</el-button>
                  <el-button size="small" text type="danger" @click="deleteComment(comment.id)">删除</el-button>
                </div>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
            </div>
            <div v-if="comments.length === 0" class="no-comments">
              <el-empty description="暂无评论"></el-empty>
            </div>
          </div>
        </el-card>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <el-empty description="帖子不存在"></el-empty>
      </div>
    </el-card>

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
    post.value = await getPostById(postId)
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
    comments.value = await getPostComments(post.value.id)
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
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.post-content {
  margin-top: 20px;
}

.post-card {
  margin-bottom: 20px;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.post-header h2 {
  margin: 0;
  flex: 1;
}

.post-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  font-size: 14px;
  color: #909399;
}

.post-body {
  margin-top: 20px;
}

.post-text {
  line-height: 1.8;
  color: #303133;
}

.comments-card {
  margin-top: 20px;
}

.card-header-title {
  font-weight: 500;
  font-size: 16px;
}

.comment-form {
  margin-bottom: 30px;
}

.comment-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.comments-list {
  margin-top: 20px;
}

.comment-item {
  padding: 15px;
  margin-bottom: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment-author {
  font-weight: 500;
  color: #409eff;
}

.comment-time {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}

.comment-content {
  color: #606266;
  line-height: 1.6;
}

.no-comments {
  padding: 40px;
  text-align: center;
}

.empty-state {
  padding: 40px;
  text-align: center;
}
</style>





