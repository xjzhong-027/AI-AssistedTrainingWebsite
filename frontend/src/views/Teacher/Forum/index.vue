<template>
  <div class="forum">
    <div class="header">
      <h2>论坛管理</h2>
    </div>
    <div class="content">
      <div class="filter-section">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索帖子"
          style="width: 300px"
          clearable
          @keyup.enter="loadPosts"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" style="margin-left: 10px" @click="loadPosts">搜索</el-button>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
      <div v-else class="posts-list">
        <div
          v-for="(post, index) in posts"
          :key="post.id"
          class="post-card card"
        >
          <div class="post-header">
            <h3>{{ post.title }}</h3>
            <div class="post-badges">
              <el-tag v-if="post.isTop" type="danger" size="small">置顶</el-tag>
              <el-tag :type="post.isPublic ? 'success' : 'warning'" size="small">
                {{ post.isPublic ? '公开' : '私密' }}
              </el-tag>
            </div>
          </div>
          <p class="post-content">{{ post.content }}</p>
          <div class="post-footer">
            <span class="post-author">作者: {{ post.author }}</span>
            <span class="post-time">{{ formatDate(post.createdAt) }}</span>
            <span class="post-comments">评论: {{ post.commentCount || 0 }}</span>
          </div>
          <div class="post-actions">
            <el-button size="small" @click="viewPost(post.id)">查看详情</el-button>
            <el-button size="small" type="warning" @click="toggleTop(post)">
              {{ post.isTop ? '取消置顶' : '置顶' }}
            </el-button>
            <el-button size="small" type="danger" @click="handleDeletePost(post.id)">删除</el-button>
          </div>
        </div>
      </div>

      <div v-if="!loading && posts.length === 0" class="no-posts">
        <p>暂无帖子</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getAllPosts, deletePost, togglePostTop } from '@/api/forum'
import type { Post } from '@/api/forum'

const router = useRouter()

const loading = ref(false)
const searchKeyword = ref('')
const posts = ref<Post[]>([])

const viewPost = (id: number) => {
  router.push(`/forum/post/${id}`)
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

const toggleTop = async (post: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要${post.isTop ? '取消置顶' : '置顶'}这个帖子吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await togglePostTop(post.id)
    ElMessage.success(`${post.isTop ? '取消置顶' : '置顶'}成功`)
    await loadPosts()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('操作失败', error)
      ElMessage.error(error.message || '操作失败')
    }
  }
}

const handleDeletePost = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个帖子吗？删除后无法恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deletePost(id)
    ElMessage.success('删除成功')
    await loadPosts()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const loadPosts = async () => {
  loading.value = true
  try {
    const params = searchKeyword.value ? { search: searchKeyword.value } : {}
    const data = await getAllPosts(params)
    posts.value = data.map((post: any) => ({
      id: post.id,
      title: post.title,
      content: post.content,
      author: post.author_name || post.author || '未知',
      authorId: post.author_id || 0,
      createdAt: post.created_at || post.createdAt,
      updatedAt: post.updated_at || post.updatedAt,
      isPublic: post.is_public !== false,
      isTop: post.is_top || false,
      commentCount: post.comment_count || 0
    }))
  } catch (error) {
    console.error('加载帖子列表失败', error)
    ElMessage.error('加载帖子列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.forum {
  padding: 20px;
  background-color: #F9F8F3;
  min-height: calc(100vh - 60px);
}

.header {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header h2 {
  margin: 0;
  color: #1A1A1A;
  font-size: 24px;
  font-weight: 600;
}

.content {
  max-width: 1000px;
  margin: 0 auto;
}

.filter-section {
  margin-bottom: 30px;
  display: flex;
  align-items: center;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-card {
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 20px;
  background-color: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.post-card.selected {
  background-color: #1A1A1A;
  color: #FFFFFF;
}

.post-card.selected * {
  color: #FFFFFF;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.post-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: inherit;
}

.post-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.post-status.public {
  background-color: rgba(153, 182, 180, 0.2);
  color: #1A1A1A;
}

.post-card.selected .post-status.public {
  background-color: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
}

.post-status.private {
  background-color: rgba(223, 177, 153, 0.2);
  color: #1A1A1A;
}

.post-card.selected .post-status.private {
  background-color: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
}

.post-content {
  color: #666;
  margin: 0 0 12px 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-card.selected .post-content {
  color: rgba(255, 255, 255, 0.8);
}

.post-footer {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #999;
}

.post-card.selected .post-footer {
  color: rgba(255, 255, 255, 0.7);
}

.post-author,
.post-time,
.post-comments {
  color: inherit;
}

.no-posts {
  text-align: center;
  padding: 40px;
  color: #666;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>

