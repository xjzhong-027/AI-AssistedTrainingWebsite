<template>
  <div class="forum-edit-page">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>编辑帖子</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="100px"
        label-position="top"
      >
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="请输入帖子标题"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="15"
            placeholder="请输入帖子内容"
            maxlength="5000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="公开性" prop="isPublic">
          <el-radio-group v-model="form.isPublic">
            <el-radio :label="true">公开</el-radio>
            <el-radio :label="false">私密</el-radio>
          </el-radio-group>
          <div class="form-tip">
            公开帖子所有人可见，私密帖子仅自己和教师可见
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            保存修改
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getPostById, updatePost } from '@/api/forum'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const postId = ref(Number(route.params.id))

const form = reactive({
  title: '',
  content: '',
  isPublic: true
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入帖子标题', trigger: 'blur' },
    { min: 1, max: 100, message: '标题长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入帖子内容', trigger: 'blur' },
    { min: 1, max: 5000, message: '内容长度在 1 到 5000 个字符', trigger: 'blur' }
  ]
}

const goBack = () => {
  router.back()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await updatePost(postId.value, {
        title: form.title,
        content: form.content,
        is_public: form.isPublic
      })

      ElMessage.success('帖子更新成功')
      router.push(`/forum/post/${postId.value}`)
    } catch (error: any) {
      ElMessage.error(error.message || '更新失败')
    } finally {
      submitting.value = false
    }
  })
}

const loadPost = async () => {
  loading.value = true
  try {
    const post = await getPostById(postId.value)

    // 检查权限：只有作者可以编辑
    if (post.authorId !== userStore.userInfo?.id) {
      ElMessage.error('您没有权限编辑此帖子')
      router.push(`/forum/post/${postId.value}`)
      return
    }

    form.title = post.title
    form.content = post.content
    form.isPublic = post.isPublic
  } catch (error: any) {
    ElMessage.error(error.message || '加载帖子失败')
    router.push('/forum')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPost()
})
</script>

<style scoped>
.forum-edit-page {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
