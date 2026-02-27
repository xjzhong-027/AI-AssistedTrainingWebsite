<template>
  <div class="forum-page">
      <div class="container card">
        <h1>论坛</h1>
        
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
</script>

<style scoped>
.forum-page {
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
</style>

