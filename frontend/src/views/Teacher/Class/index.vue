<template>
  <div class="class-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班级管理</span>
          <div>
            <el-button @click="goHome">返回首页</el-button>
            <el-button type="primary" @click="openCreate">新建班级</el-button>
          </div>
        </div>
      </template>

      <el-table :data="classList" v-loading="loading" style="width: 100%">
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
            <el-button size="small" @click="openStudents(row)">查看学生</el-button>
            <el-button size="small" type="primary" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && classList.length === 0" description="暂无班级，请新建" />
    </el-card>

    <!-- 新建/编辑 弹窗 -->
    <el-dialog
      v-model="formVisible"
      :title="formMode === 'create' ? '新建班级' : '编辑班级'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="90px">
        <el-form-item label="班级名称" prop="class_name">
          <el-input v-model="form.class_name" placeholder="请输入班级名称" />
        </el-form-item>
        <el-form-item label="课程" prop="course">
          <el-select v-model="form.course" placeholder="请选择课程" style="width: 100%">
            <el-option
              v-for="c in courses"
              :key="c.id"
              :label="`${c.year}-${gradeLabel(c.grade)}-${semesterLabel(c.semester)}`"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="授课教师" prop="teacher">
          <el-select v-model="form.teacher" placeholder="请选择教师" style="width: 100%">
            <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开课日期" prop="start_date">
          <el-input v-model="form.start_date" placeholder="如 2024-09-01" />
        </el-form-item>
        <el-form-item label="周几" prop="week">
          <el-select v-model="form.week" placeholder="请选择" style="width: 100%">
            <el-option v-for="w in weekOptions" :key="w.value" :label="w.label" :value="w.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课时间" prop="start_time">
          <el-input v-model="form.start_time" placeholder="如 08:00" />
        </el-form-item>
        <el-form-item label="下课时间" prop="end_time">
          <el-input v-model="form.end_time" placeholder="如 10:00" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看学生 弹窗 -->
    <el-dialog v-model="studentsVisible" title="班级学生" width="560px">
      <el-table :data="studentList" v-loading="studentsLoading" size="small">
        <el-table-column prop="username" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="seat_number" label="座位号" width="80" />
      </el-table>
      <el-empty v-if="!studentsLoading && studentList.length === 0" description="暂无学生" />
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

const goHome = () => router.push('/teacher/index')

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
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header > div {
  display: flex;
  gap: 10px;
}
</style>
