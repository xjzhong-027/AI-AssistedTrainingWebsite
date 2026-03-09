<template>
  <div class="week-task-create-container">
    <div class="week-task-create-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
          </div>
          <h2>新建周任务包</h2>
        </div>
        <el-button @click="goBack" type="default" class="secondary-button">返回</el-button>
      </div>

      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="120px"
        label-position="right"
        class="modern-form"
      >
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入任务标题" maxlength="200" show-word-limit class="modern-input" />
        </el-form-item>

        <el-form-item label="主题" prop="theme">
          <el-input v-model="form.theme" placeholder="请输入主题" maxlength="50" class="modern-input" />
        </el-form-item>

        <el-form-item label="摘要" prop="abstract">
          <el-input
            v-model="form.abstract"
            type="textarea"
            :rows="3"
            placeholder="请输入摘要"
            maxlength="500"
            show-word-limit
            class="modern-input"
          />
        </el-form-item>

        <el-form-item label="关键词" prop="keywords">
          <el-input
            v-model="form.keywords"
            placeholder="请输入关键词，多个关键词用逗号分隔"
            class="modern-input"
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
            class="modern-input"
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
            class="modern-upload"
          >
            <el-button type="primary" class="primary-button">选择音频/视频文件</el-button>
            <template #tip>
              <div class="upload-tip">支持音频和视频文件</div>
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
            class="modern-upload"
          >
            <el-icon class="upload-icon"><Plus /></el-icon>
            <template #tip>
              <div class="upload-tip">最多上传10张图片</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item class="form-actions">
          <el-button type="primary" @click="handleSubmit" :loading="submitting" class="primary-button">创建并导入题目</el-button>
          <el-button @click="goBack" class="secondary-button">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
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
  router.push('/teacher/dashboard')
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
.week-task-create-container {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

.week-task-create-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.week-task-create-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #F0F2F5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

.card-header h2 {
  margin: 0;
  color: #1A202C;
  font-size: 18px;
  font-weight: 600;
}

/* 表单样式 */
.modern-form {
  margin-top: 20px;
}

.modern-form .el-form-item {
  margin-bottom: 20px;
}

.modern-form .el-form-item__label {
  color: #4A5568;
  font-weight: 500;
  font-size: 14px;
}

/* 输入框样式 */
.modern-input {
  border-radius: 12px !important;
  border: 2px solid #F0F2F5 !important;
  padding: 12px 16px !important;
  font-size: 14px !important;
  transition: all 0.3s ease !important;
}

.modern-input:hover {
  border-color: #8C7CF0 !important;
}

.modern-input:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

/* 上传组件样式 */
.modern-upload {
  margin-top: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #8B9BB4;
  margin-top: 8px;
}

.upload-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F5F7FA;
  border-radius: 12px;
  color: #8C7CF0;
  font-size: 24px;
  transition: all 0.3s ease;
}

.upload-icon:hover {
  background: #E8E4FF;
  transform: scale(1.05);
}

/* 按钮样式 */
.primary-button {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 12px !important;
  padding: 12px 24px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3) !important;
  transition: all 0.3s ease !important;
}

.primary-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.4) !important;
}

.secondary-button {
  background: #FFFFFF !important;
  border: 2px solid #8C7CF0 !important;
  color: #8C7CF0 !important;
  border-radius: 12px !important;
  padding: 12px 24px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.secondary-button:hover {
  background: #E8E4FF !important;
}

/* 表单操作区 */
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #F0F2F5;
}

/* 加载动画样式 */
:deep(.el-loading-spinner) {
  font-size: 16px !important;
  color: #8C7CF0 !important;
}

:deep(.el-loading-spinner .path) {
  stroke: #8C7CF0 !important;
}

/* 图片上传卡片 */
:deep(.el-upload-list__item) {
  border-radius: 12px !important;
  border: 2px dashed #F0F2F5 !important;
}

:deep(.el-upload-list__item:hover) {
  border-color: #8C7CF0 !important;
}

:deep(.el-upload-list__item .el-upload-list__item-actions) {
  background: rgba(0, 0, 0, 0.6) !important;
  border-radius: 0 0 12px 12px !important;
}
</style>
