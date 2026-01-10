<template>
  <Layout>
    <div class="learning-record-page">
      <el-card>
        <template #header>
          <div class="card-header">
            <h3>学习记录管理</h3>
            <el-button @click="goBack">返回</el-button>
          </div>
        </template>

        <!-- 查询表单 -->
        <el-form :model="queryForm" :inline="true" class="query-form">
          <el-form-item label="班级" v-if="userStore.userInfo?.role === 'TEACHER'">
            <el-select v-model="queryForm.class_id" placeholder="请选择班级" clearable style="width: 200px">
              <el-option
                v-for="cls in classList"
                :key="cls.id"
                :label="cls.class_name"
                :value="cls.id"
              ></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="学生" v-if="userStore.userInfo?.role === 'TEACHER'">
            <el-select v-model="queryForm.student_id" placeholder="请选择学生" clearable style="width: 200px">
              <el-option
                v-for="student in studentList"
                :key="student.id"
                :label="student.student_name"
                :value="student.id"
              ></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="queryForm.unit_type" placeholder="请选择类型" clearable style="width: 150px">
              <el-option label="考试" value="exam"></el-option>
              <el-option label="练习" value="practice"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleQuery" :loading="loading">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 学习记录表格 -->
        <el-table :data="recordList" v-loading="loading" stripe border style="margin-top: 20px">
          <el-table-column prop="student_name" label="学生姓名" width="120"></el-table-column>
          <el-table-column prop="unit_name" label="任务名称" min-width="200"></el-table-column>
          <el-table-column prop="unit_type" label="类型" width="80">
            <template #default="{ row }">
              <el-tag :type="row.unit_type === 'exam' ? 'danger' : 'success'">
                {{ row.unit_type === 'exam' ? '考试' : '练习' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="成绩" width="120">
            <template #default="{ row }">
              <span :style="{ color: getScoreColor(row.score, row.total_score) }">
                {{ row.score }} / {{ row.total_score }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="completion_time" label="完成时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.completion_time) }}
            </template>
          </el-table-column>
        </el-table>

        <!-- 空状态 -->
        <el-empty v-if="!loading && recordList.length === 0" description="暂无学习记录"></el-empty>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout/index.vue'
import { queryLearningRecords } from '@/api/query'
import { getAllClasses, getStudentsByClass } from '@/api/user'
import { formatDateTime } from '@/utils/format'
import { useUserStore } from '@/stores/user'
import type { LearningRecord } from '@/types/query'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const recordList = ref<LearningRecord[]>([])
const classList = ref<any[]>([])
const studentList = ref<any[]>([])

const queryForm = ref({
  student_id: undefined as number | undefined,
  class_id: undefined as number | undefined,
  unit_type: undefined as 'exam' | 'practice' | undefined
})

// 获取班级列表
const loadClasses = async () => {
  try {
    classList.value = await getAllClasses()
  } catch (error: any) {
    console.error('加载班级列表失败', error)
    ElMessage.error(error.message || '加载班级列表失败')
  }
}

// 获取学生列表
const loadStudents = async (classId: number) => {
  try {
    studentList.value = await getStudentsByClass(classId)
  } catch (error: any) {
    console.error('加载学生列表失败', error)
    ElMessage.error(error.message || '加载学生列表失败')
  }
}

// 监听班级变化，加载学生列表
watch(
  () => queryForm.value.class_id,
  (newClassId) => {
    if (newClassId) {
      loadStudents(newClassId)
      queryForm.value.student_id = undefined
    } else {
      studentList.value = []
      queryForm.value.student_id = undefined
    }
  }
)

// 查询学习记录
const handleQuery = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (queryForm.value.student_id) params.student_id = queryForm.value.student_id
    if (queryForm.value.class_id) params.class_id = queryForm.value.class_id
    if (queryForm.value.unit_type) params.unit_type = queryForm.value.unit_type

    recordList.value = await queryLearningRecords(params)
    if (recordList.value.length === 0) {
      ElMessage.info('暂无学习记录')
    }
  } catch (error: any) {
    console.error('查询学习记录失败', error)
    ElMessage.error(error.message || '查询学习记录失败')
  } finally {
    loading.value = false
  }
}

// 重置查询
const handleReset = () => {
  queryForm.value = {
    student_id: undefined,
    class_id: undefined,
    unit_type: undefined
  }
  recordList.value = []
}

// 获取成绩颜色
const getScoreColor = (score: number, totalScore: number): string => {
  const percentage = (score / totalScore) * 100
  if (percentage >= 90) return '#67c23a' // 绿色
  if (percentage >= 70) return '#409eff' // 蓝色
  if (percentage >= 60) return '#e6a23c' // 橙色
  return '#f56c6c' // 红色
}

const goBack = () => {
  router.back()
}

onMounted(async () => {
  if (userStore.userInfo?.role === 'TEACHER') {
    await loadClasses()
  }
  // 默认查询当前用户的学习记录
  handleQuery()
})
</script>

<style scoped>
.learning-record-page {
  padding: 20px;
  background-color: #F9F8F3;
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.query-form {
  margin-top: 10px;
}

:deep(.el-card) {
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}
</style>
