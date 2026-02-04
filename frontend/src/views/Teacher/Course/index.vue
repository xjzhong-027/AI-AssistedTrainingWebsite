<template>
  <div class="course-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程管理</span>
          <div>
            <el-button @click="goHome">返回首页</el-button>
            <el-button type="primary" @click="showCreateDialog">新建课程</el-button>
          </div>
        </div>
      </template>

      <el-table :data="courseList" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="year" label="开课年份" width="120" />
        <el-table-column prop="grade" label="开课年级" width="120">
          <template #default="{ row }">
            {{ gradeLabel(row.grade) }}
          </template>
        </el-table-column>
        <el-table-column prop="semester" label="开课学期" width="120">
          <template #default="{ row }">
            {{ semesterLabel(row.semester) }}
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && courseList.length === 0" description="暂无课程，请新建" />
    </el-card>

    <el-dialog
      v-model="createDialogVisible"
      title="新建课程"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="90px">
        <el-form-item label="开课年份" prop="year">
          <el-input-number v-model="createForm.year" :min="2020" :max="2030" style="width: 100%" />
        </el-form-item>
        <el-form-item label="开课年级" prop="grade">
          <el-select v-model="createForm.grade" placeholder="请选择" style="width: 100%">
            <el-option label="大一" value="1" />
            <el-option label="大二" value="2" />
            <el-option label="大三" value="3" />
            <el-option label="大四" value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="开课学期" prop="semester">
          <el-select v-model="createForm.semester" placeholder="请选择" style="width: 100%">
            <el-option label="上学期" value="上" />
            <el-option label="下学期" value="下" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate" :loading="submitting">确定</el-button>
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
  router.push('/teacher/index')
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
