<template>
  <div class="question-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>题目列表</span>
          <el-button type="primary" @click="goCreate">
            <el-icon><Plus /></el-icon>
            创建题目
          </el-button>
        </div>
      </template>

      <!-- 筛选区域 -->
      <div class="filter-area">
        <el-select
          v-model="filterExamId"
          placeholder="选择考试"
          style="width: 200px"
          clearable
          @change="loadQuestions"
        >
          <el-option
            v-for="exam in examList"
            :key="exam.id"
            :label="exam.title"
            :value="exam.id"
          />
        </el-select>
        <el-select
          v-model="filterType"
          placeholder="选择类型"
          style="width: 150px; margin-left: 10px"
          clearable
          @change="loadQuestions"
        >
          <el-option label="单选题" value="SINGLE_CHOICE" />
          <el-option label="多选题" value="MULTIPLE_CHOICE" />
          <el-option label="判断题" value="TRUE_FALSE" />
          <el-option label="简答题" value="SHORT_ANSWER" />
        </el-select>
        <el-button type="primary" style="margin-left: 10px" @click="loadQuestions">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetFilter">重置</el-button>
      </div>

      <!-- 表格 -->
      <el-table
        v-loading="loading"
        :data="questionList"
        style="width: 100%; margin-top: 20px"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="examId" label="考试ID" width="100" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getQuestionTypeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="题目内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="score" label="分值" width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row.id)">查看</el-button>
            <el-button link type="warning" @click="editQuestion(row.id)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && questionList.length === 0" description="暂无题目数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { getAllQuestions, getQuestionsByExamId, deleteQuestion } from '@/api/question'
import { getExamsByCreatorId } from '@/api/exam'
import { useUserStore } from '@/stores/user'
import type { Question } from '@/types/question'
import type { Exam } from '@/types/exam'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const questionList = ref<Question[]>([])
const examList = ref<Exam[]>([])
const filterExamId = ref<number | null>(null)
const filterType = ref<string>('')

// 加载题目列表
const loadQuestions = async () => {
  loading.value = true
  try {
    let questions: Question[] = []

    if (filterExamId.value) {
      questions = await getQuestionsByExamId(filterExamId.value)
      if (filterType.value) {
        questions = questions.filter((q) => q.type === filterType.value)
      }
    } else {
      questions = await getAllQuestions()
      if (filterType.value) {
        questions = questions.filter((q) => q.type === filterType.value)
      }
    }

    questionList.value = questions
  } catch (error) {
    console.error('加载题目列表失败', error)
  } finally {
    loading.value = false
  }
}

// 加载考试列表
const loadExams = async () => {
  if (userStore.isTeacher() && userStore.userInfo?.id) {
    try {
      examList.value = await getExamsByCreatorId(userStore.userInfo.id)
    } catch (error) {
      console.error('加载考试列表失败', error)
    }
  }
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

const resetFilter = () => {
  filterExamId.value = null
  filterType.value = ''
  loadQuestions()
}

const goCreate = () => {
  router.push('/questions/create')
}

const viewDetail = (id: number) => {
  router.push(`/questions/${id}`)
}

const editQuestion = (id: number) => {
  router.push(`/questions/${id}/edit`)
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个题目吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteQuestion(id)
    ElMessage.success('删除成功')
    loadQuestions()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败', error)
    }
  }
}

onMounted(() => {
  loadExams()
  loadQuestions()
})
</script>

<style scoped>
.question-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-area {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
</style>
