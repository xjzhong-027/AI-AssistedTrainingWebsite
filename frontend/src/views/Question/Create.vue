<template>
  <div class="question-create">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>创建题目</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" label-position="right">
        <el-form-item label="所属考试" prop="examId">
          <el-select v-model="form.examId" placeholder="请选择考试" style="width: 100%">
            <el-option
              v-for="exam in examList"
              :key="exam.id"
              :label="exam.title"
              :value="exam.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="题目类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择题目类型" style="width: 100%">
            <el-option label="单选题" value="SINGLE_CHOICE" />
            <el-option label="多选题" value="MULTIPLE_CHOICE" />
            <el-option label="判断题" value="TRUE_FALSE" />
            <el-option label="简答题" value="SHORT_ANSWER" />
          </el-select>
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

        <!-- 选项（单选、多选、判断题） -->
        <el-form-item
          v-if="form.type === 'SINGLE_CHOICE' || form.type === 'MULTIPLE_CHOICE' || form.type === 'TRUE_FALSE'"
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
              v-if="options.length > 2"
              type="danger"
              :icon="Delete"
              @click="removeOption(index)"
            />
          </div>
          <el-button
            v-if="form.type !== 'TRUE_FALSE' && options.length < 10"
            type="primary"
            :icon="Plus"
            @click="addOption"
            style="margin-top: 10px"
          >
            添加选项
          </el-button>
          <div class="form-tip">
            {{ form.type === 'TRUE_FALSE' ? '判断题固定为"正确"和"错误"两个选项' : '至少需要2个选项，最多10个选项' }}
          </div>
        </el-form-item>

        <!-- 正确答案 -->
        <el-form-item
          v-if="form.type !== 'SHORT_ANSWER'"
          label="正确答案"
          prop="correctAnswer"
        >
          <el-radio-group v-if="form.type === 'SINGLE_CHOICE' || form.type === 'TRUE_FALSE'" v-model="form.correctAnswer">
            <el-radio
              v-for="(option, index) in options"
              :key="index"
              :label="String.fromCharCode(65 + index)"
            >
              {{ String.fromCharCode(65 + index) }}. {{ option }}
            </el-radio>
          </el-radio-group>
          <el-checkbox-group v-if="form.type === 'MULTIPLE_CHOICE'" v-model="correctAnswers">
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
          <el-button type="primary" @click="handleSubmit" :loading="loading">创建题目</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { createQuestion } from '@/api/question'
import { getExamsByCreatorId } from '@/api/exam'
import { useUserStore } from '@/stores/user'
import type { QuestionCreateDTO } from '@/types/question'
import type { Exam } from '@/types/exam'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const formRef = ref<FormInstance>()
const examList = ref<Exam[]>([])
const options = ref<string[]>(['', ''])
const correctAnswers = ref<string[]>([])

const form = reactive<QuestionCreateDTO>({
  examId: 0,
  type: 'SINGLE_CHOICE',
  content: '',
  options: '',
  correctAnswer: '',
  score: 10
})

const rules: FormRules = {
  examId: [{ required: true, message: '请选择所属考试', trigger: 'change' }],
  type: [{ required: true, message: '请选择题目类型', trigger: 'change' }],
  content: [
    { required: true, message: '请输入题目内容', trigger: 'blur' },
    { min: 1, max: 1000, message: '内容长度在 1 到 1000 个字符', trigger: 'blur' }
  ],
  correctAnswer: [{ required: true, message: '请选择正确答案', trigger: 'change' }],
  score: [
    { required: true, message: '请输入分值', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: '分值必须在 1 到 100 之间', trigger: 'blur' }
  ]
}

// 监听题目类型变化
watch(
  () => form.type,
  (newType) => {
    if (newType === 'TRUE_FALSE') {
      options.value = ['正确', '错误']
    } else if (newType === 'SINGLE_CHOICE' || newType === 'MULTIPLE_CHOICE') {
      if (options.value.length === 2 && options.value[0] === '正确') {
        options.value = ['', '']
      }
    }
    form.correctAnswer = ''
    correctAnswers.value = []
  }
)

// 添加选项
const addOption = () => {
  if (options.value.length < 10) {
    options.value.push('')
  }
}

// 删除选项
const removeOption = (index: number) => {
  if (options.value.length > 2) {
    options.value.splice(index, 1)
  }
}

// 加载考试列表
const loadExams = async () => {
  if (userStore.isTeacher() && userStore.userInfo?.id) {
    try {
      examList.value = await getExamsByCreatorId(userStore.userInfo.id)
      // 如果URL中有examId参数，自动选择
      const examId = route.query.examId
      if (examId) {
        form.examId = Number(examId)
      }
    } catch (error) {
      console.error('加载考试列表失败', error)
    }
  }
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return

  // 验证选项
  if (form.type !== 'SHORT_ANSWER') {
    const validOptions = options.value.filter((opt) => opt.trim() !== '')
    if (validOptions.length < 2) {
      ElMessage.warning('至少需要2个有效选项')
      return
    }
    form.options = JSON.stringify(validOptions)
  }

  // 处理多选题答案
  if (form.type === 'MULTIPLE_CHOICE') {
    if (correctAnswers.value.length === 0) {
      ElMessage.warning('请选择正确答案')
      return
    }
    form.correctAnswer = correctAnswers.value.join(',')
  }

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await createQuestion(form)
        ElMessage.success('创建题目成功')
        router.push('/questions')
      } catch (error) {
        console.error('创建题目失败', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleReset = () => {
  if (!formRef.value) return
  formRef.value.resetFields()
  options.value = ['', '']
  correctAnswers.value = []
  form.score = 10
}

const goBack = () => {
  router.push('/questions')
}

onMounted(() => {
  loadExams()
})
</script>

<style scoped>
.question-create {
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
