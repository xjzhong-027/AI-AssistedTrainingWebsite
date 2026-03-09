<template>
  <div class="forum-create-page">
    <div class="forum-create-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
          </div>
          <h2>发论坛</h2>
        </div>
        <div class="header-actions">
          <button @click="goBack" class="secondary-button">返回</button>
        </div>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="modern-form">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入帖子标题" class="modern-input" />
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            placeholder="请输入帖子内容"
            rows="10"
            class="modern-textarea"
          />
        </el-form-item>

        <el-form-item label="可见性">
          <el-radio-group v-model="form.isPublic" class="visibility-radio">
            <el-radio :label="true" class="radio-item">
              <div class="radio-label">
                <div class="radio-icon public-icon"></div>
                <span>公开</span>
              </div>
            </el-radio>
            <el-radio :label="false" class="radio-item">
              <div class="radio-label">
                <div class="radio-icon private-icon"></div>
                <span>私密</span>
              </div>
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="是否置顶">
          <el-switch v-model="form.isTop" class="modern-switch" />
        </el-form-item>

        <el-form-item>
          <div class="form-actions">
            <button @click="goBack" class="secondary-button">取消</button>
            <button @click="submitForm" class="primary-button" :disabled="loading">
              {{ loading ? '发布中...' : '发布' }}
            </button>
          </div>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createPost } from '@/api/forum'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = ref({
  title: '',
  content: '',
  isPublic: true,
  isTop: false
})

const rules = {
  title: [
    { required: true, message: '请输入帖子标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度应在2-100个字符之间', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入帖子内容', trigger: 'blur' },
    { min: 5, message: '内容长度至少5个字符', trigger: 'blur' }
  ]
}

const goBack = () => {
  router.push('/teacher/forum')
}

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    console.log('开始创建帖子')
    // 调用API创建帖子
    const result = await createPost({
      title: form.value.title,
      content: form.value.content,
      is_public: form.value.isPublic,
      is_top: form.value.isTop
    })
    console.log('创建帖子成功:', result)
    
    // 显示成功提示并跳转
    ElMessage.success('发布成功')
    // 立即跳转
    router.push('/teacher/forum')
  } catch (error: any) {
    console.error('创建帖子失败:', error)
    if (error !== 'cancel') {
      ElMessage.error(error.message || '发布失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forum-create-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.forum-create-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: 800px;
}

.forum-create-card::before {
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
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
  animation: float 3s ease-in-out infinite;
}

.header-icon svg {
  width: 24px;
  height: 24px;
}

.header-left h2 {
  font-size: 24px;
  font-weight: 600;
  color: #4A5568;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 表单样式 */
.modern-form {
  width: 100%;
}

.modern-input {
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  padding: 10px 16px;
  font-size: 14px;
  transition: all 0.3s ease;
  width: 100%;
}

.modern-input:hover {
  border-color: #8C7CF0;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1);
}

.modern-textarea {
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  padding: 12px 16px;
  font-size: 14px;
  transition: all 0.3s ease;
  width: 100%;
  resize: vertical;
  min-height: 200px;
}

.modern-textarea:hover {
  border-color: #8C7CF0;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1);
}

/* 可见性选择 */
.visibility-radio {
  display: flex;
  gap: 24px;
}

.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.radio-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.public-icon {
  background: linear-gradient(135deg, #48BB78, #68D391);
}

.private-icon {
  background: linear-gradient(135deg, #ED8936, #F6AD55);
}

/* 开关样式 */
.modern-switch {
  --el-switch-on-color: #8C7CF0;
  --el-switch-off-color: #E2E8F0;
}

/* 按钮样式 */
.primary-button {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
}

.primary-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.4);
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.secondary-button {
  background: #F0F2F5;
  color: #4A5568;
  border: 1px solid #E2E8F0;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.secondary-button:hover {
  background: #E2E8F0;
  transform: translateY(-2px);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

/* 动画 */
@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .forum-create-page {
    padding: 16px;
  }

  .forum-create-card {
    padding: 16px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .visibility-radio {
    flex-direction: column;
    gap: 12px;
  }

  .form-actions {
    flex-direction: column;
  }

  .primary-button, .secondary-button {
    width: 100%;
    text-align: center;
  }
}
</style>