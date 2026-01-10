<template>
  <div class="question-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>题目详情</span>
          <div>
            <el-button @click="goBack">返回</el-button>
            <el-button type="primary" @click="editQuestion">编辑</el-button>
          </div>
        </div>
      </template>

      <div v-if="question" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="题目ID">{{ question.id }}</el-descriptions-item>
          <el-descriptions-item label="考试ID">{{ question.examId }}</el-descriptions-item>
          <el-descriptions-item label="题目类型">
            <el-tag>{{ getQuestionTypeText(question.type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="分值">{{ question.score }} 分</el-descriptions-item>
          <el-descriptions-item label="题目内容" :span="2">
            <div style="white-space: pre-wrap">{{ question.content }}</div>
          </el-descriptions-item>
          <el-descriptions-item v-if="question.options" label="选项" :span="2">
            <div v-if="parsedOptions">
              <div v-for="(option, index) in parsedOptions" :key="index" style="margin-bottom: 8px">
                <strong>{{ String.fromCharCode(65 + index) }}.</strong> {{ option }}
              </div>
            </div>
          </el-descriptions-item>
          <el-descriptions-item v-if="question.correctAnswer" label="正确答案" :span="2">
            <el-tag type="success">{{ question.correctAnswer }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getQuestionById } from '@/api/question'
import type { Question } from '@/types/question'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const question = ref<Question | null>(null)

const parsedOptions = computed(() => {
  if (!question.value?.options) return null
  try {
    return JSON.parse(question.value.options)
  } catch {
    return null
  }
})

const getQuestionTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    SINGLE_CHOICE: '单选题',
    MULTIPLE_CHOICE: '多选题',
    TRUE_FALSE: '判断题',
    SHORT_ANSWER: '简答题'
  }
  return typeMap[type] || type
}

const loadQuestion = async () => {
  const id = Number(route.params.id)
  if (!id) {
    router.push('/questions')
    return
  }

  loading.value = true
  try {
    question.value = await getQuestionById(id)
  } catch (error) {
    console.error('加载题目详情失败', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/questions')
}

const editQuestion = () => {
  router.push(`/questions/${question.value?.id}/edit`)
}

onMounted(() => {
  loadQuestion()
})
</script>

<style scoped>
.question-detail {
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
