<template>
  <div class="material-create">
    <div class="material-create-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7,10 12,15 17,10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </div>
          <h2>新建媒体素材</h2>
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
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入素材标题" maxlength="200" show-word-limit class="modern-input" />
        </el-form-item>

        <el-form-item label="主题" prop="theme">
          <el-input v-model="form.theme" placeholder="选填，如：日常对话、新闻" class="modern-input" />
        </el-form-item>

        <el-form-item label="摘要" prop="abstract">
          <el-input v-model="form.abstract" type="textarea" :rows="2" placeholder="选填" class="modern-textarea" />
        </el-form-item>

        <el-form-item label="关键词" prop="keywords">
          <el-input v-model="form.keywords" placeholder="选填，逗号分隔" class="modern-input" />
        </el-form-item>

        <el-form-item label="听力/视频原文" prop="transcript">
          <el-input
            v-model="form.transcript"
            type="textarea"
            :rows="6"
            placeholder="选填。填写后 AI 提示可结合材料给出具体词汇与逻辑提示"
            class="modern-textarea"
          />
          <div class="ai-actions">
            <el-button
              type="success"
              :loading="transcribing"
              @click="handleTranscribe"
              class="success-button"
            >
              语音识别（提取 Transcript）
            </el-button>
            <el-button
              type="primary"
              :loading="analyzing"
              :disabled="!form.transcript?.trim()"
              @click="handleAnalyze"
              class="primary-button"
            >
              AI 智能分析素材
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="媒体文件" prop="media_url">
          <el-upload
            :auto-upload="true"
            :show-file-list="true"
            :limit="1"
            accept="audio/*,video/*,.mp3,.mp4,.wav,.m4a,.webm"
            :http-request="handleUploadMedia"
            :on-remove="() => { form.media_url = '' }"
            :on-exceed="() => ElMessage.warning('仅支持一个媒体文件，请先移除已选文件')"
            class="modern-upload"
          >
            <el-button type="primary" :loading="uploadingMedia" class="primary-button">选取音频/视频文件</el-button>
          </el-upload>
          <div v-if="form.media_url" class="upload-tip">已上传，保存后将使用此文件</div>
        </el-form-item>

        <el-form-item label="图片" prop="image_url">
          <el-upload
            :auto-upload="true"
            :show-file-list="true"
            :limit="1"
            accept="image/*,.jpg,.jpeg,.png,.gif,.webp"
            :http-request="handleUploadImage"
            :on-remove="() => { form.image_url = '' }"
            :on-exceed="() => ElMessage.warning('仅支持一张图片，请先移除已选文件')"
            class="modern-upload"
          >
            <el-button :loading="uploadingImage" class="secondary-button">选取图片文件</el-button>
          </el-upload>
          <div v-if="form.image_url" class="upload-tip">已上传，保存后将使用此图片</div>
        </el-form-item>

        <el-form-item class="form-actions">
          <el-button type="primary" @click="handleSubmit" :loading="submitting" class="primary-button">创建</el-button>
          <el-button @click="goBack" class="secondary-button">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import { createMediaMaterial, uploadMediaFile, uploadMaterialImage, transcribeMedia, analyzeMaterial } from '@/api/content'

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const uploadingMedia = ref(false)
const uploadingImage = ref(false)
const transcribing = ref(false)
const analyzing = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  title: '',
  theme: '',
  abstract: '',
  keywords: '',
  transcript: '',
  media_url: '',
  image_url: ''
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入素材标题', trigger: 'blur' }]
}

const handleUploadMedia = async (options: UploadRequestOptions) => {
  uploadingMedia.value = true
  try {
    const res = await uploadMediaFile(options.file)
    form.media_url = res.media_url || ''
    options.onSuccess?.(res as any)
  } catch (e: any) {
    options.onError?.(e)
    ElMessage.error(e?.message || '媒体文件上传失败')
  } finally {
    uploadingMedia.value = false
  }
}

const handleTranscribe = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'audio/*,video/*,.mp3,.mp4,.wav,.m4a,.webm'
  input.onchange = async (e: Event) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (!file) return
    transcribing.value = true
    try {
      const res = await transcribeMedia(file)
      form.transcript = res.transcript || ''
      form.media_url = res.media_url || ''
      ElMessage.success('语音识别完成')
    } catch (err: any) {
      ElMessage.error(err?.message || '语音识别失败')
    } finally {
      transcribing.value = false
    }
  }
  input.click()
}

const handleAnalyze = async () => {
  const t = form.transcript?.trim()
  if (!t) {
    ElMessage.warning('请先填写 transcript 或使用语音识别')
    return
  }
  analyzing.value = true
  try {
    const res = await analyzeMaterial(t)
    if (res.title) form.title = res.title
    if (res.theme) form.theme = res.theme
    if (res.abstract) form.abstract = res.abstract
    if (res.keywords) form.keywords = res.keywords
    ElMessage.success('AI 分析完成')
  } catch (err: any) {
    ElMessage.error(err?.message || 'AI 分析失败')
  } finally {
    analyzing.value = false
  }
}

const handleUploadImage = async (options: UploadRequestOptions) => {
  uploadingImage.value = true
  try {
    const res = await uploadMaterialImage(options.file)
    form.image_url = res.image_url || ''
    options.onSuccess?.(res as any)
  } catch (e: any) {
    options.onError?.(e)
    ElMessage.error(e?.message || '图片上传失败')
  } finally {
    uploadingImage.value = false
  }
}

const goBack = () => {
  router.push({ name: 'QuestionBank' })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await createMediaMaterial({
        title: form.title.trim(),
        theme: form.theme?.trim() || '',
        abstract: form.abstract?.trim() || '',
        keywords: form.keywords?.trim() || '',
        transcript: form.transcript?.trim() || '',
        media_url: form.media_url?.trim() || '',
        image_url: form.image_url?.trim() || ''
      })
      ElMessage.success('媒体素材创建成功')
      router.push({ name: 'QuestionBank' })
    } catch (error: any) {
      ElMessage.error(error?.message || '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {})
</script>

<style scoped>
.material-create {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

/* 插画样式 */
.illustration-header {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  animation: fadeIn 0.8s ease-out;
}

.illustration-content {
  position: relative;
  animation: float 3s ease-in-out infinite;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

/* 卡片样式 */
.material-create-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.material-create-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
}

/* 头部样式 */
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

.card-header h2 {
  margin: 0;
  color: #1A202C;
  font-size: 18px;
  font-weight: 600;
}

/* 按钮样式 */
.primary-button {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 12px !important;
  padding: 10px 24px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
}

.primary-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.4) !important;
}

.secondary-button {
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  color: #4A5568 !important;
  border-radius: 12px !important;
  padding: 10px 24px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.secondary-button:hover {
  border-color: #8C7CF0 !important;
  color: #8C7CF0 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2) !important;
}

.success-button {
  background: linear-gradient(135deg, #67C23A, #85CE61) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 12px !important;
  padding: 10px 24px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
}

.success-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(103, 194, 58, 0.4) !important;
}

/* 表单样式 */
.modern-form {
  max-width: 800px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #F0F2F5;
  justify-content: flex-end;
}

/* 输入框样式 */
.modern-input,
.modern-textarea {
  border-radius: 12px !important;
  border: 1px solid #E2E8F0 !important;
  transition: all 0.3s ease !important;
}

.modern-input:focus,
.modern-textarea:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

/* 上传样式 */
.modern-upload {
  margin-bottom: 12px;
}

.upload-tip {
  font-size: 12px;
  color: #67C23A;
  margin-top: 8px;
  padding-left: 8px;
  border-left: 3px solid #67C23A;
}

/* AI操作按钮 */
.ai-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #F0F2F5;
}

/* 加载状态 */
:deep(.el-loading-spinner .path) {
  stroke: #8C7CF0 !important;
}

/* 表单标签样式 */
:deep(.el-form-item__label) {
  color: #4A5568 !important;
  font-weight: 500 !important;
  font-size: 14px !important;
}

/* 上传文件列表样式 */
:deep(.el-upload-list__item) {
  border-radius: 8px !important;
  border: 1px solid #E2E8F0 !important;
  background: #F8F5FF !important;
}

:deep(.el-upload-list__item-name) {
  color: #4A5568 !important;
}

:deep(.el-upload-list__item-status-label) {
  color: #8C7CF0 !important;
}
</style>
