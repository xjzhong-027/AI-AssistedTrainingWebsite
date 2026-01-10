<template>
  <div class="question-edit">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>编辑题目</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        v-if="form"
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="120px"
        label-position="right"
      >
        <el-form-item label="题目类型">
          <el-tag>{{ getQuestionTypeText(questionType) }}</el-tag>
          <div class="form-tip">题目类型不可修改</div>
        </el-form-item>

        <el-form-item label="题目内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            placeholder="请输入题目内容"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- 选项编辑 -->
        <el-form-item
          v-if="questionType !== 'SHORT_ANSWER'"
          label="选项"
          prop="options"
        >
          <div v-for="(option, index) in options" :key="index" class="option-item">
            <el-input
              v-model="options[index]"
              :placeholder="`选项 ${String.fromCharCode(65 + index)}`"
              style="width: calc(100% - 100px); margin-right: 10px"
            />
            <el-button
              v-if="options.length > 2 && questionType !== 'TRUE_FALSE'"
              type="danger"
              :icon="Delete"
              @click="removeOption(index)"
            />
          </div>
          <el-button
            v-if="questionType !== 'TRUE_FALSE' && options.length < 10"
            type="primary"
            :icon="Plus"
            @click="addOption"
            style="margin-top: 10px"
          >
            添加选项
          </el-button>
        </el-form-item>

        <!-- 正确答案 -->
        <el-form-item
          v-if="questionType !== 'SHORT_ANSWER'"
          label="正确答案"
          prop="correctAnswer"
        >
          <el-radio-group
            v-if="questionType === 'SINGLE_CHOICE' || questionType === 'TRUE_FALSE'"
            v-model="form.correctAnswer"
          >
            <el-radio
              v-for="(option, index) in options"
              :key="index"
              :label="String.fromCharCode(65 + index)"
            >
              {{ String.fromCharCode(65 + index) }}. {{ option }}
            </el-radio>
          </el-radio-group>
          <el-checkbox-group v-if="questionType === 'MULTIPLE_CHOICE'" v-model="correctAnswers">
            <el-checkbox
              v-for="(option, index) in options"
              :key="index"
              :label="String.fromCharCode(65 + index)"
            >
              {{ String.fromCharCode(65 + index) }}. {{ option }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="分值" prop="score">
          <el-input-number
            v-model="form.score"
            :min="1"
            :max="100"
            placeholder="请输入分值"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { getQuestionById, updateQuestion } from '@/api/question'
import type { QuestionUpdateDTO } from '@/types/question'
import type { Question } from '@/types/question'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const question = ref<Question | null>(null)
const questionType = ref<string>('')
const options = ref<string[]>([])
const correctAnswers = ref<string[]>([])

const form = reactive<QuestionUpdateDTO & { content?: string }>({
  content: '',
  options: '',
  correctAnswer: '',
  score: 10
})

const rules: FormRules = {
  content: [
    { required: true, message: '请输入题目内容', trigger: 'blur' },
    { min: 1, max: 1000, message: '内容长度在 1 到 1000 个字符', trigger: 'blur' }
  ],
  score: [
    { required: true, message: '请输入分值', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: '分值必须在 1 到 100 之间', trigger: 'blur' }
  ]
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

const addOption = () => {
  if (options.value.length < 10) {
    options.value.push('')
  }
}

const removeOption = (index: number) => {
  if (options.value.length > 2 && questionType.value !== 'TRUE_FALSE') {
    options.value.splice(index, 1)
  }
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
    if (question.value) {
      questionType.value = question.value.type
      form.content = question.value.content
      form.score = question.value.score

      if (question.value.options) {
        try {
          options.value = JSON.parse(question.value.options)
        } catch {
          options.value = []
        }
      }

      if (question.value.correctAnswer) {
        if (questionType.value === 'MULTIPLE_CHOICE') {
          correctAnswers.value = question.value.correctAnswer.split(',')
        } else {
          form.correctAnswer = question.value.correctAnswer
        }
      }
    }
  } catch (error) {
    console.error('加载题目失败', error)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  // 验证选项
  if (questionType.value !== 'SHORT_ANSWER') {
    const validOptions = options.value.filter((opt) => opt.trim() !== '')
    if (validOptions.length < 2) {
      ElMessage.warning('至少需要2个有效选项')
      return
    }
    form.options = JSON.stringify(validOptions)
  }

  // 处理多选题答案
  if (questionType.value === 'MULTIPLE_CHOICE') {
    if (correctAnswers.value.length === 0) {
      ElMessage.warning('请选择正确答案')
      return
    }
    form.correctAnswer = correctAnswers.value.join(',')
  }

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const id = Number(route.params.id)
        await updateQuestion(id, form)
        ElMessage.success('更新成功')
        router.push(`/questions/${id}`)
      } catch (error) {
        console.error('更新失败', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadQuestion()
})
</script>

<style scoped>
.question-edit {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.option-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
