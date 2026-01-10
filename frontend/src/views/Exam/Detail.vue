<template>
  <div class="exam-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>考试详情</span>
          <div>
            <el-button @click="goBack">返回</el-button>
            <el-button
              v-if="userStore.isTeacher() && exam?.creatorId === userStore.userInfo?.id"
              type="primary"
              @click="editExam"
            >
              编辑
            </el-button>
            <el-button
              v-if="userStore.isStudent() && exam?.status === 'IN_PROGRESS'"
              type="success"
              @click="takeExam"
            >
              参加考试
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="exam" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="考试ID">{{ exam.id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(exam.status)">{{ getStatusText(exam.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="考试标题" :span="2">{{ exam.title }}</el-descriptions-item>
          <el-descriptions-item label="考试描述" :span="2">
            {{ exam.description || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDateTime(exam.startTime) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ formatDateTime(exam.endTime) }}
          </el-descriptions-item>
          <el-descriptions-item label="考试时长">{{ exam.duration }} 分钟</el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(exam.createdAt) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 题目列表 -->
        <div v-if="userStore.isTeacher()" style="margin-top: 30px">
          <el-divider>题目列表</el-divider>
          <el-button type="primary" @click="goCreateQuestion">
            <el-icon><Plus /></el-icon>
            添加题目
          </el-button>
          <el-table :data="questions" style="width: 100%; margin-top: 20px" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="type" label="类型" width="120">
              <template #default="{ row }">
                {{ getQuestionTypeText(row.type) }}
              </template>
            </el-table-column>
            <el-table-column prop="content" label="题目内容" min-width="200" show-overflow-tooltip />
            <el-table-column prop="score" label="分值" width="80" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewQuestion(row.id)">查看</el-button>
                <el-button link type="warning" @click="editQuestion(row.id)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getExamById } from '@/api/exam'
import { getQuestionsByExamId } from '@/api/question'
import { formatDateTime } from '@/utils/format'
import type { Exam } from '@/types/exam'
import type { Question } from '@/types/question'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const exam = ref<Exam | null>(null)
const questions = ref<Question[]>([])

// 加载考试详情
const loadExam = async () => {
  const id = Number(route.params.id)
  if (!id) {
    ElMessage.error('考试ID无效')
    router.push('/exams')
    return
  }

  loading.value = true
  try {
    exam.value = await getExamById(id)
    if (userStore.isTeacher()) {
      questions.value = await getQuestionsByExamId(id)
    }
  } catch (error) {
    console.error('加载考试详情失败', error)
  } finally {
    loading.value = false
  }
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    NOT_STARTED: '未开始',
    IN_PROGRESS: '进行中',
    ENDED: '已结束'
  }
  return statusMap[status] || status
}

const getStatusType = (status: string): string => {
  const typeMap: Record<string, string> = {
    NOT_STARTED: 'info',
    IN_PROGRESS: 'success',
    ENDED: 'warning'
  }
  return typeMap[status] || ''
}

const getQuestionTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    SINGLE_CHOICE: '单选题',
    MULTIPLE_CHOICE: '多选题',
    TRUE_FALSE: '判断题',
    SHORT_ANSWER: '简答题'
  }
  return typeMap[type] || type
}

const goBack = () => {
  router.push('/exams')
}

const editExam = () => {
  router.push(`/exams/${exam.value?.id}/edit`)
}

const takeExam = () => {
  router.push(`/exams/${exam.value?.id}/take`)
}

const goCreateQuestion = () => {
  router.push(`/questions/create?examId=${exam.value?.id}`)
}

const viewQuestion = (id: number) => {
  router.push(`/questions/${id}`)
}

const editQuestion = (id: number) => {
  router.push(`/questions/${id}/edit`)
}

onMounted(() => {
  loadExam()
})
</script>

<style scoped>
.exam-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-content {
  padding: 20px 0;
}
</style>
