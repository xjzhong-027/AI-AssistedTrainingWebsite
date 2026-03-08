<template>
  <div class="forum-page">
    <div class="forum-content">
      <div class="forum-card card">
        <!-- 返回首页按钮 -->
        <button class="back-button" @click="goToDashboard">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回首页
        </button>
        
        <div class="forum-header">
          <h1 class="forum-title">论坛</h1>
          <p class="forum-subtitle">参与讨论，分享学习心得</p>
        </div>
        
        <!-- 搜索和筛选 -->
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
          <el-button
            :type="showMyPosts ? 'warning' : 'default'"
            style="margin-left: 10px"
            @click="toggleMyPosts"
          >
            {{ showMyPosts ? '显示全部' : '我的帖子' }}
          </el-button>
          <el-button type="success" style="margin-left: 10px" @click="showPostForm = true">发布帖子</el-button>
        </div>

        <!-- 帖子列表 -->
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else class="posts-list">
          <div
            v-for="(post, index) in posts"
            :key="post.id"
            class="post-card card"
            :class="{ selected: selectedIndex === index }"
            @click="selectPost(index, post.id)"
          >
            <div class="post-header">
              <h3>{{ post.title }}</h3>
              <span class="post-status" :class="post.isPublic ? 'public' : 'private'">
                {{ post.isPublic ? '公开' : '私密' }}
              </span>
            </div>
            <p class="post-content">{{ post.content }}</p>
            <div class="post-footer">
              <span class="post-author">作者: {{ post.author }}</span>
              <span class="post-time">{{ formatDate(post.createdAt) }}</span>
              <span class="post-comments">评论: {{ post.commentCount || 0 }}</span>
            </div>
          </div>
        </div>

        <div v-if="!loading && posts.length === 0" class="no-posts">
          <p>暂无帖子</p>
        </div>

        <!-- 发布帖子对话框 -->
        <el-dialog v-model="showPostForm" title="发布新帖子" width="600px">
          <el-form :model="newPost" label-width="80px">
            <el-form-item label="标题">
              <el-input v-model="newPost.title" placeholder="请输入帖子标题" />
            </el-form-item>
            <el-form-item label="内容">
              <el-input
                v-model="newPost.content"
                type="textarea"
                :rows="6"
                placeholder="请输入帖子内容"
              />
            </el-form-item>
            <el-form-item label="公开性">
              <el-radio-group v-model="newPost.isPublic">
                <el-radio :label="true">公开</el-radio>
                <el-radio :label="false">私密</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showPostForm = false">取消</el-button>
            <el-button type="primary" @click="submitPost">发布</el-button>
          </template>
        </el-dialog>
        <AIWindow :show-grade-button="false" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getAllPosts, createPost } from '@/api/forum'
import type { Post } from '@/api/forum'
import { useUserStore } from '@/stores/user'
import AIWindow from '@/components/common/AIWindow/index.vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const searchKeyword = ref('')
const selectedIndex = ref<number | null>(null)
const showPostForm = ref(false)
const showMyPosts = ref(false)
const posts = ref<Post[]>([])

const newPost = ref({
  title: '',
  content: '',
  isPublic: true
})

const selectPost = (index: number, id: number) => {
  selectedIndex.value = selectedIndex.value === index ? null : index
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

const toggleMyPosts = () => {
  showMyPosts.value = !showMyPosts.value
  loadPosts()
}

const loadPosts = async () => {
  loading.value = true
  try {
    const params: any = {}

    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }

    if (showMyPosts.value && userStore.userInfo?.id) {
      params.author = userStore.userInfo.id
    }
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
      commentCount: post.comment_count || 0
    }))
  } catch (error) {
    console.error('加载帖子列表失败', error)
    ElMessage.error('加载帖子列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const submitPost = async () => {
  if (!newPost.value.title || !newPost.value.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }

  try {
    await createPost({
      title: newPost.value.title,
      content: newPost.value.content,
      isPublic: newPost.value.isPublic
    })
    ElMessage.success('帖子发布成功')
    showPostForm.value = false
    newPost.value = { title: '', content: '', isPublic: true }
    loadPosts()
  } catch (error) {
    console.error('发布帖子失败', error)
    ElMessage.error('发布帖子失败，请稍后重试')
  }
}

onMounted(() => {
  loadPosts()
})

const goToDashboard = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.forum-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FAFBFC 0%, #F5F7FA 100%);
  padding: 24px 32px;
}

/* 页面内容 */
.forum-content {
  max-width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 论坛卡片 */
.forum-card {
  background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FF 100%);
  border-radius: 24px;
  padding: 40px 50px;
  margin-bottom: 32px;
  box-shadow: 0 8px 32px rgba(140, 124, 240, 0.12);
  position: relative;
  overflow: hidden;
  width: 90%;
  display: flex;
  flex-direction: column;
}

.forum-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF, #A8D5BA);
}

/* 返回按钮 */
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

/* 论坛标题 */
.forum-header {
  margin-bottom: 32px;
  text-align: center;
}

.forum-title {
  font-size: 36px;
  font-weight: 700;
  color: #1A202C;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #8C7CF0 0%, #6B5DD3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.forum-subtitle {
  font-size: 16px;
  color: #8B9BB4;
  margin: 0;
}

/* 搜索和筛选 */
.filter-section {
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* 帖子列表 */
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

/* 帖子卡片 */
.post-card {
  background: linear-gradient(135deg, #FAFBFC 0%, #FFFFFF 100%);
  border-radius: 16px;
  padding: 24px;
  border: 2px solid #F0F2F5;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.post-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #8C7CF0 0%, #C6B9FF 100%);
  border-radius: 4px 0 0 4px;
}

.post-card:hover {
  transform: translateY(-4px);
  border-color: #E8E4FF;
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.15);
}

.post-card.selected {
  background: linear-gradient(135deg, #1A202C 0%, #2D3748 100%);
  color: #FFFFFF;
  border-color: #4A5568;
}

.post-card.selected::before {
  background: linear-gradient(180deg, #A8D5BA 0%, #8BC4A8 100%);
}

.post-card.selected * {
  color: #FFFFFF;
}

/* 帖子头部 */
.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.post-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: inherit;
  flex: 1;
  margin-right: 16px;
}

/* 帖子状态 */
.post-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.post-status.public {
  background: linear-gradient(135deg, #A8D5BA 0%, #8BC4A8 100%);
  color: #FFFFFF;
}

.post-card.selected .post-status.public {
  background: linear-gradient(135deg, #C6B9FF 0%, #8C7CF0 100%);
  color: #FFFFFF;
}

.post-status.private {
  background: linear-gradient(135deg, #FFB74D 0%, #FFA726 100%);
  color: #FFFFFF;
}

.post-card.selected .post-status.private {
  background: linear-gradient(135deg, #FFE082 0%, #FFB74D 100%);
  color: #1A202C;
}

/* 帖子内容 */
.post-content {
  color: #4A5568;
  margin: 0 0 16px 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-card.selected .post-content {
  color: rgba(255, 255, 255, 0.8);
}

/* 帖子底部 */
.post-footer {
  display: flex;
  gap: 24px;
  font-size: 14px;
  color: #8B9BB4;
  align-items: center;
}

.post-card.selected .post-footer {
  color: rgba(255, 255, 255, 0.7);
}

.post-author,
.post-time,
.post-comments {
  color: inherit;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 无帖子状态 */
.no-posts {
  text-align: center;
  padding: 60px 20px;
  background: linear-gradient(135deg, #FAFBFC 0%, #F5F7FA 100%);
  border-radius: 16px;
  border: 2px dashed #E8E4FF;
}

.no-posts p {
  font-size: 18px;
  font-weight: 600;
  color: #8B9BB4;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .forum-page {
    padding: 16px;
  }
  
  .forum-card {
    width: 95%;
    padding: 30px 24px;
  }
  
  .forum-title {
    font-size: 28px;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-section .el-input {
    width: 100% !important;
  }
  
  .filter-section .el-button {
    margin-left: 0 !important;
    width: 100%;
  }
  
  .post-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .post-status {
    align-self: flex-start;
  }
  
  .post-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>

