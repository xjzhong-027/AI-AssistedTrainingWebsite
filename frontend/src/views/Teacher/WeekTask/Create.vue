<template>
  <div class="week-task-create">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>新建周任务包</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="120px"
        label-position="right"
      >
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入任务标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="主题" prop="theme">
          <el-input v-model="form.theme" placeholder="请输入主题" maxlength="50" />
        </el-form-item>

        <el-form-item label="摘要" prop="abstract">
          <el-input
            v-model="form.abstract"
            type="textarea"
            :rows="3"
            placeholder="请输入摘要"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="关键词" prop="keywords">
          <el-input
            v-model="form.keywords"
            placeholder="请输入关键词，多个关键词用逗号分隔"
          />
        </el-form-item>

        <el-form-item label="文本内容" prop="transcript">
          <el-input
            v-model="form.transcript"
            type="textarea"
            :rows="5"
            placeholder="请输入文本内容"
            maxlength="5000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="媒体文件" prop="media_file">
          <el-upload
            ref="mediaUploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleMediaChange"
            :on-remove="handleMediaRemove"
            accept="audio/*,video/*"
          >
            <el-button type="primary">选择音频/视频文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持音频和视频文件</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item label="图片文件">
          <el-upload
            ref="imageUploadRef"
            :auto-upload="false"
            :limit="10"
            :on-change="handleImageChange"
            :on-remove="handleImageRemove"
            accept="image/*"
            multiple
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
            <template #tip>
              <div class="el-upload__tip">最多上传10张图片</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">创建并导入题目</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const mediaUploadRef = ref()
const imageUploadRef = ref()

const form = reactive({
  title: '',
  theme: '',
  abstract: '',
  keywords: '',
  transcript: ''
})

const mediaFile = ref<File | null>(null)
const imageFiles = ref<File[]>([])

const rules: FormRules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  media_file: [{ required: true, message: '请上传媒体文件', trigger: 'change' }]
}

const goBack = () => {
  router.back()
}

const handleMediaChange = (file: UploadFile) => {
  if (file.raw) {
    mediaFile.value = file.raw
  }
}

const handleMediaRemove = () => {
  mediaFile.value = null
}

const handleImageChange = (file: UploadFile) => {
  if (file.raw) {
    imageFiles.value.push(file.raw)
  }
}

const handleImageRemove = (file: UploadFile) => {
  const index = imageFiles.value.findIndex(f => f.name === file.name)
  if (index > -1) {
    imageFiles.value.splice(index, 1)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    if (!mediaFile.value) {
      ElMessage.error('请上传媒体文件')
      return
    }

    submitting.value = true
    try {
      const formData = new FormData()
      formData.append('title', form.title)
      formData.append('theme', form.theme)
      formData.append('abstract', form.abstract)
      formData.append('keywords', form.keywords)
      formData.append('transcript', form.transcript)
      formData.append('media_file', mediaFile.value)

      imageFiles.value.forEach((file) => {
        formData.append('image_file', file)
      })

      const response = await request.post('/content/week-task-packages/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      ElMessage.success('任务包创建成功')

      // 跳转到导入页面
      if (response.id) {
        router.push(`/teacher/week-task/import/${response.id}`)
      } else {
        router.push('/teacher/week-task')
      }
    } catch (error: any) {
      ElMessage.error(error.message || '创建失败')
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.week-task-create {
  padding: 20px;
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
