<template>
  <div class="material-create">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>新建媒体素材</span>
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
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入素材标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="主题" prop="theme">
          <el-input v-model="form.theme" placeholder="选填，如：日常对话、新闻" />
        </el-form-item>

        <el-form-item label="摘要" prop="abstract">
          <el-input v-model="form.abstract" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>

        <el-form-item label="关键词" prop="keywords">
          <el-input v-model="form.keywords" placeholder="选填，逗号分隔" />
        </el-form-item>

        <el-form-item label="听力/视频原文" prop="transcript">
          <el-input
            v-model="form.transcript"
            type="textarea"
            :rows="6"
            placeholder="选填。填写后 AI 提示可结合材料给出具体词汇与逻辑提示"
          />
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
          >
            <el-button type="primary" :loading="uploadingMedia">选取音频/视频文件</el-button>
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
          >
            <el-button :loading="uploadingImage">选取图片文件</el-button>
          </el-upload>
          <div v-if="form.image_url" class="upload-tip">已上传，保存后将使用此图片</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">创建</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import { createMediaMaterial, uploadMediaFile, uploadMaterialImage } from '@/api/content'

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const uploadingMedia = ref(false)
const uploadingImage = ref(false)
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
  padding: 20px;
  background-color: #f9f8f3;
  min-height: 100vh;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.upload-tip {
  font-size: 12px;
  color: #67c23a;
  margin-top: 6px;
}
</style>
