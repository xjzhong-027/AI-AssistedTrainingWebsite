<template>
  <div class="class-page">
    <div class="class-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
          </div>
          <h2>班级管理</h2>
        </div>
        <div class="header-actions">
          <button @click="goHome" class="secondary-button">返回首页</button>
          <button @click="openCreate" class="primary-button">新建班级</button>
        </div>
      </div>

      <!-- 班级列表 -->
      <div class="table-section">
        <el-table :data="classList" v-loading="loading" class="modern-table">
          <el-table-column prop="class_name" label="班级名称" min-width="140" />
          <el-table-column prop="course_name" label="课程" width="140" />
          <el-table-column prop="teacher_name" label="授课教师" width="100" />
          <el-table-column prop="start_date" label="开课日期" width="110" />
          <el-table-column prop="week" label="周几" width="80">
            <template #default="{ row }">{{ weekLabel(row.week) }}</template>
          </el-table-column>
          <el-table-column prop="start_time" label="上课时间" width="100" />
          <el-table-column prop="end_time" label="下课时间" width="100" />
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="openStudents(row)" class="link-button">查看学生</el-button>
              <el-button size="small" @click="openEdit(row)" class="link-button">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 空状态 -->
        <el-empty v-if="!loading && classList.length === 0" description="暂无班级" class="modern-empty">
          <el-button type="primary" @click="openCreate" class="primary-button">新建班级</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 新建/编辑 弹窗 -->
    <el-dialog
      v-model="formVisible"
      :title="formMode === 'create' ? '新建班级' : '编辑班级'"
      width="500px"
      :close-on-click-modal="false"
      custom-class="modern-dialog"
    >
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="90px" class="modern-form">
        <el-form-item label="班级名称" prop="class_name">
          <el-input v-model="form.class_name" placeholder="请输入班级名称" class="modern-input" />
        </el-form-item>
        <el-form-item label="课程" prop="course">
          <el-select v-model="form.course" placeholder="请选择课程" style="width: 100%" class="modern-select">
            <el-option
              v-for="c in courses"
              :key="c.id"
              :label="`${c.year}-${gradeLabel(c.grade)}-${semesterLabel(c.semester)}`"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="授课教师" prop="teacher">
          <el-select v-model="form.teacher" placeholder="请选择教师" style="width: 100%" class="modern-select">
            <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开课日期" prop="start_date">
          <el-input v-model="form.start_date" placeholder="如 2024-09-01" class="modern-input" />
        </el-form-item>
        <el-form-item label="周几" prop="week">
          <el-select v-model="form.week" placeholder="请选择" style="width: 100%" class="modern-select">
            <el-option v-for="w in weekOptions" :key="w.value" :label="w.label" :value="w.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课时间" prop="start_time">
          <el-input v-model="form.start_time" placeholder="如 08:00" class="modern-input" />
        </el-form-item>
        <el-form-item label="下课时间" prop="end_time">
          <el-input v-model="form.end_time" placeholder="如 10:00" class="modern-input" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false" class="secondary-button">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting" class="primary-button">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看学生 弹窗 -->
    <el-dialog v-model="studentsVisible" title="班级学生" width="560px" custom-class="modern-dialog">
      <el-table :data="studentList" v-loading="studentsLoading" size="small" class="modern-table">
        <el-table-column prop="username" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="seat_number" label="座位号" width="80" />
      </el-table>
      <el-empty v-if="!studentsLoading && studentList.length === 0" description="暂无学生" class="modern-empty" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  getCourseList,
  getTeacherList,
  getAllClasses,
  getClassById,
  getClassStudents,
  createClass,
  updateClass,
  type Course,
  type TeacherBrief,
  type Class,
  type User
} from '@/api/user'

const router = useRouter()
const loading = ref(false)
const classList = ref<Class[]>([])
const courses = ref<Course[]>([])
const teachers = ref<TeacherBrief[]>([])
const formVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const formRef = ref<FormInstance>()
const editingId = ref<number | null>(null)

const form = reactive({
  class_name: '',
  course: null as number | null,
  teacher: null as number | null,
  start_date: '',
  week: 1,
  start_time: '',
  end_time: ''
})

const formRules: FormRules = {
  class_name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  course: [{ required: true, message: '请选择课程', trigger: 'change' }],
  teacher: [{ required: true, message: '请选择教师', trigger: 'change' }],
  week: [{ required: true, message: '请选择周几', trigger: 'change' }],
  start_time: [{ required: true, message: '请输入上课时间', trigger: 'blur' }],
  end_time: [{ required: true, message: '请输入下课时间', trigger: 'blur' }]
}

const weekOptions = [
  { value: 1, label: '周一' },
  { value: 2, label: '周二' },
  { value: 3, label: '周三' },
  { value: 4, label: '周四' },
  { value: 5, label: '周五' },
  { value: 6, label: '周六' },
  { value: 7, label: '周日' }
]

const weekLabel = (w: number) => weekOptions.find((o) => o.value === w)?.label ?? w
const gradeLabel = (g: string) => ({ '1': '大一', '2': '大二', '3': '大三', '4': '大四' }[g] || g)
const semesterLabel = (s: string) => ({ '上': '上学期', '下': '下学期' }[s] || s)

const studentList = ref<User[]>([])
const studentsVisible = ref(false)
const studentsLoading = ref(false)

const goHome = () => router.push('/teacher/dashboard')

const loadList = async () => {
  loading.value = true
  try {
    classList.value = await getAllClasses()
  } catch (e: any) {
    ElMessage.error(e.message || '加载班级列表失败')
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [c, t] = await Promise.all([getCourseList(), getTeacherList()])
    courses.value = c
    teachers.value = t
  } catch (e: any) {
    ElMessage.error(e.message || '加载选项失败')
  }
}

const openCreate = () => {
  formMode.value = 'create'
  editingId.value = null
  form.class_name = ''
  form.course = null
  form.teacher = null
  form.start_date = ''
  form.week = 1
  form.start_time = ''
  form.end_time = ''
  formVisible.value = true
}

const openEdit = async (row: Class) => {
  formMode.value = 'edit'
  editingId.value = row.id
  try {
    const detail = await getClassById(row.id)
    form.class_name = detail.class_name ?? ''
    form.course = detail.course_id ?? null
    form.teacher = detail.teacher_id ?? null
    form.start_date = detail.start_date ?? ''
    form.week = detail.week ?? 1
    form.start_time = detail.start_time ?? ''
    form.end_time = detail.end_time ?? ''
  } catch (e: any) {
    ElMessage.error(e.message || '加载班级详情失败')
    return
  }
  formVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    if (form.course == null || form.teacher == null) {
      ElMessage.warning('请选择课程和教师')
      return
    }
    submitting.value = true
    try {
      const payload = {
        class_name: form.class_name,
        course: form.course,
        teacher: form.teacher,
        start_date: form.start_date || undefined,
        week: form.week,
        start_time: form.start_time,
        end_time: form.end_time
      }
      if (formMode.value === 'create') {
        await createClass(payload)
        ElMessage.success('创建成功')
      } else if (editingId.value != null) {
        await updateClass(editingId.value, payload)
        ElMessage.success('更新成功')
      }
      formVisible.value = false
      await loadList()
    } catch (e: any) {
      ElMessage.error(e.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const openStudents = async (row: Class) => {
  studentsVisible.value = true
  studentList.value = []
  studentsLoading.value = true
  try {
    studentList.value = await getClassStudents(row.id)
  } catch (e: any) {
    ElMessage.error(e.message || '加载学生列表失败')
  } finally {
    studentsLoading.value = false
  }
}

onMounted(() => {
  loadList()
  loadOptions()
})
</script>

<style scoped>
.class-page {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

/* 卡片样式 */
.class-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: none;
}

.class-card::before {
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

/* 链接按钮 */
.link-button {
  color: #8C7CF0 !important;
  font-weight: 500 !important;
}

.link-button:hover {
  color: #6A5AE0 !important;
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

.modern-input {
  border-radius: 12px !important;
  border: 1px solid #E2E8F0 !important;
  transition: all 0.3s ease !important;
}

.modern-input:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
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