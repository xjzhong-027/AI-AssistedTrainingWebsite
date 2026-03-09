<template>
  <div class="announcement-create-page">
    <div class="announcement-create-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          </div>
          <h2>发布公告</h2>
        </div>
        <div class="header-actions">
          <button @click="goBack" class="secondary-button">返回</button>
        </div>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="modern-form">
        <el-form-item label="标题" prop="a_title">
          <el-input v-model="form.a_title" placeholder="请输入公告标题" class="modern-input" />
        </el-form-item>

        <el-form-item label="内容" prop="a_content">
          <el-input
            v-model="form.a_content"
            type="textarea"
            placeholder="请输入公告内容"
            rows="10"
            class="modern-textarea"
          />
        </el-form-item>

        <el-form-item label="接收学生">
          <el-checkbox v-model="selectAll" @change="handleSelectAll">全选</el-checkbox>
          <div class="student-list">
            <el-checkbox-group v-model="form.receiver_student_ids">
              <el-checkbox
                v-for="student in students"
                :key="student.id"
                :label="student.id"
                class="student-checkbox"
              >
                {{ student.name }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createAnnouncement } from '@/api/announcement'
import { getStudents } from '@/api/student'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const selectAll = ref(false)

const students = ref<any[]>([])

const form = ref({
  a_title: '',
  a_content: '',
  receiver_student_ids: []
})

const rules = {
  a_title: [
    { required: true, message: '请输入公告标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度应在2-100个字符之间', trigger: 'blur' }
  ],
  a_content: [
    { required: true, message: '请输入公告内容', trigger: 'blur' },
    { min: 5, message: '内容长度至少5个字符', trigger: 'blur' }
  ],
  receiver_student_ids: [
    { required: true, message: '请选择至少一个接收学生', trigger: 'change' }
  ]
}

const goBack = () => {
  router.push('/teacher/announcements')
}

const handleSelectAll = () => {
  if (selectAll.value) {
    form.value.receiver_student_ids = students.value.map(student => student.id)
  } else {
    form.value.receiver_student_ids = []
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    await createAnnouncement({
      a_title: form.value.a_title,
      a_content: form.value.a_content,
      receiver_student_ids: form.value.receiver_student_ids
    })
    
    ElMessage.success('发布成功')
    router.push('/teacher/announcements')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '发布失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

const loadStudents = async () => {
  try {
    const data = await getStudents()
    students.value = data
  } catch (error) {
    console.error('加载学生列表失败', error)
    ElMessage.error('加载学生列表失败，请稍后重试')
  }
}

onMounted(() => {
  loadStudents()
})
</script>

<style scoped>
.announcement-create-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.announcement-create-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: 800px;
}

.announcement-create-card::before {
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

/* 学生列表 */
.student-list {
  margin-top: 16px;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.student-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
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
  .announcement-create-page {
    padding: 16px;
  }

  .announcement-create-card {
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

  .student-list {
    grid-template-columns: 1fr;
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