<template>
  <div class="course-page">
    <div class="course-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
              <path d="M6 12v5c3 3 9 3 12 0v-5"></path>
            </svg>
          </div>
          <h2>课程管理</h2>
        </div>
        <div class="header-actions">
          <button @click="goHome" class="secondary-button">返回首页</button>
          <button @click="showCreateDialog" class="primary-button">新建课程</button>
        </div>
      </div>

      <!-- 课程列表 -->
      <div class="table-section">
        <el-table :data="courseList" v-loading="loading" class="modern-table">
          <el-table-column prop="id" label="#" width="80" />
          <el-table-column prop="year" label="开课年份" width="120" />
          <el-table-column prop="grade" label="开课年级" width="120">
            <template #default="{ row }">
              <el-tag type="primary" class="modern-tag">{{ gradeLabel(row.grade) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="semester" label="开课学期" width="120">
            <template #default="{ row }">
              <el-tag type="success" class="modern-tag">{{ semesterLabel(row.semester) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <!-- 空状态 -->
        <el-empty v-if="!loading && courseList.length === 0" description="暂无课程" class="modern-empty">
          <el-button type="primary" @click="showCreateDialog" class="primary-button">新建课程</el-button>
        </el-empty>
      </div>
    </div>

    <el-dialog
      v-model="createDialogVisible"
      title="新建课程"
      width="400px"
      :close-on-click-modal="false"
      custom-class="modern-dialog"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="90px" class="modern-form">
        <el-form-item label="开课年份" prop="year">
          <el-input-number v-model="createForm.year" :min="2020" :max="2030" style="width: 100%" class="modern-input-number" />
        </el-form-item>
        <el-form-item label="开课年级" prop="grade">
          <el-select v-model="createForm.grade" placeholder="请选择" style="width: 100%" class="modern-select">
            <el-option label="大一" value="1" />
            <el-option label="大二" value="2" />
            <el-option label="大三" value="3" />
            <el-option label="大四" value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="开课学期" prop="semester">
          <el-select v-model="createForm.semester" placeholder="请选择" style="width: 100%" class="modern-select">
            <el-option label="上学期" value="上" />
            <el-option label="下学期" value="下" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false" class="secondary-button">取消</el-button>
        <el-button type="primary" @click="submitCreate" :loading="submitting" class="primary-button">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { getCourseList, createCourse, type Course } from '@/api/user'

const router = useRouter()
const loading = ref(false)
const courseList = ref<Course[]>([])
const createDialogVisible = ref(false)
const submitting = ref(false)
const createFormRef = ref<FormInstance>()

const createForm = reactive({
  year: new Date().getFullYear(),
  grade: '1',
  semester: '上'
})

const createRules: FormRules = {
  year: [{ required: true, message: '请选择开课年份', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择开课年级', trigger: 'change' }],
  semester: [{ required: true, message: '请选择开课学期', trigger: 'change' }]
}

const gradeLabel = (grade: string) => {
  const map: Record<string, string> = { '1': '大一', '2': '大二', '3': '大三', '4': '大四' }
  return map[grade] || grade
}

const semesterLabel = (semester: string) => {
  const map: Record<string, string> = { '上': '上学期', '下': '下学期' }
  return map[semester] || semester
}

const goHome = () => {
  router.push('/teacher/dashboard')
}

const showCreateDialog = () => {
  createForm.year = new Date().getFullYear()
  createForm.grade = '1'
  createForm.semester = '上'
  createDialogVisible.value = true
}

const loadList = async () => {
  loading.value = true
  try {
    courseList.value = await getCourseList()
  } catch (e: any) {
    ElMessage.error(e.message || '加载课程列表失败')
  } finally {
    loading.value = false
  }
}

const submitCreate = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await createCourse({
        year: createForm.year,
        grade: createForm.grade,
        semester: createForm.semester
      })
      ElMessage.success('创建成功')
      createDialogVisible.value = false
      await loadList()
    } catch (e: any) {
      ElMessage.error(e.message || '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
.course-page {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

/* 卡片样式 */
.course-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: none;
}

.course-card::before {
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

.header-actions {
  display: flex;
  gap: 12px;
}

/* 按钮样式 */
.primary-button {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 12px !important;
  padding: 10px 24px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
  cursor: pointer !important;
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
  cursor: pointer !important;
}

.secondary-button:hover {
  border-color: #8C7CF0 !important;
  color: #8C7CF0 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2) !important;
}

/* 表格区域 */
.table-section {
  margin-bottom: 24px;
}

.modern-table {
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1) !important;
}

:deep(.el-table th) {
  background: #F0F2F5 !important;
  color: #4A5568 !important;
  font-weight: 600 !important;
  font-size: 14px !important;
}

:deep(.el-table tr:hover > td) {
  background: #F8F5FF !important;
}

:deep(.el-table__row:nth-child(even)) {
  background: #FAFAFA !important;
}

/* 标签样式 */
.modern-tag {
  border-radius: 8px !important;
  padding: 4px 12px !important;
  font-size: 12px !important;
  font-weight: 600 !important;
}

/* 空状态 */
.modern-empty {
  padding: 60px 0 !important;
  margin-top: 24px;
}

/* 对话框样式 */
.modern-dialog {
  border-radius: 20px !important;
  overflow: hidden !important;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #F8F5FF, #FFFFFF) !important;
  padding: 20px 24px !important;
  border-bottom: 1px solid #F0F2F5 !important;
}

:deep(.el-dialog__title) {
  color: #1A202C !important;
  font-weight: 600 !important;
  font-size: 16px !important;
}

:deep(.el-dialog__body) {
  padding: 24px !important;
}

:deep(.el-dialog__footer) {
  padding: 16px 24px !important;
  border-top: 1px solid #F0F2F5 !important;
}

/* 表单样式 */
.modern-form {
  width: 100%;
}

:deep(.el-form-item__label) {
  color: #4A5568 !important;
  font-weight: 500 !important;
}

.modern-select {
  border-radius: 12px !important;
  border: 1px solid #E2E8F0 !important;
  transition: all 0.3s ease !important;
}

.modern-select:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

.modern-input-number {
  border-radius: 12px !important;
  border: 1px solid #E2E8F0 !important;
  transition: all 0.3s ease !important;
}

.modern-input-number:focus-within {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

/* 动画效果 */
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

/* 加载状态 */
:deep(.el-loading-spinner .path) {
  stroke: #8C7CF0 !important;
}
</style>