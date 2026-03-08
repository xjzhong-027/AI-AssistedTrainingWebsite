<template>
  <div class="question-edit-by-type">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>{{ typeLabel }} - 新建</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <!-- 选择题表单 -->
      <el-form
        v-if="type === 'choice'"
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="140px"
        class="edit-form"
      >
        <el-form-item label="大题题干" prop="question_text">
          <el-input
            v-model="form.question_text"
            type="textarea"
            :rows="3"
            placeholder="请输入听录音/阅读后的题目说明，如：听录音选答案"
          />
        </el-form-item>
        <el-form-item label="最多播放次数">
          <el-input-number v-model="form.maximum_play" :min="0" :max="99" />
        </el-form-item>
        <el-divider>小题 1</el-divider>
        <el-form-item label="小题题干" prop="sub_questions.0.question_text">
          <el-input
            v-model="form.sub_questions[0].question_text"
            type="textarea"
            :rows="2"
            placeholder="请输入小题内容"
          />
        </el-form-item>
        <el-form-item label="选项" required>
          <div class="options-list">
            <div v-for="(opt, idx) in form.sub_questions[0].options" :key="idx" class="option-row">
              <span class="option-label">{{ optLabels[idx] }}.</span>
              <el-input
                v-model="opt.option_content"
                :placeholder="`选项 ${optLabels[idx]} 内容`"
                class="option-input"
              />
            </div>
          </div>
        </el-form-item>
        <el-form-item label="正确答案">
          <el-radio-group v-model="form.sub_questions[0].answer">
            <el-radio v-for="l in optLabels" :key="l" :label="l">{{ l }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="小题分数">
          <el-input-number v-model="form.sub_questions[0].score" :min="0" :max="100" :step="0.5" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">创建题目</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>

      <!-- 主观题表单（简答题、理解题、总结题） -->
      <el-form
        v-else-if="type === 'comprehension'"
        :model="formComprehension"
        :rules="rulesComprehension"
        ref="formComprehensionRef"
        label-width="140px"
        class="edit-form"
      >
        <el-form-item label="大题题干" prop="question_text">
          <el-input
            v-model="formComprehension.question_text"
            type="textarea"
            :rows="3"
            placeholder="请输入听录音/阅读后的题目说明，如：听录音后回答问题、总结主旨大意"
          />
        </el-form-item>
        <el-form-item label="最多播放次数">
          <el-input-number v-model="formComprehension.maximum_play" :min="0" :max="99" />
        </el-form-item>
        <el-divider>小题 1</el-divider>
        <el-form-item label="小题题干" prop="sub_question_text">
          <el-input
            v-model="formComprehension.sub_question_text"
            type="textarea"
            :rows="3"
            placeholder="请输入问题内容，如：请总结本文主旨、请简要回答"
          />
        </el-form-item>
        <el-form-item label="参考答案" prop="answer">
          <el-input
            v-model="formComprehension.answer"
            type="textarea"
            :rows="4"
            placeholder="请输入参考答案供 AI 评分参考（学生不可见）"
          />
        </el-form-item>
        <el-form-item label="小题分数">
          <el-input-number v-model="formComprehension.score" :min="0" :max="100" :step="0.5" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmitComprehension" :loading="submitting">创建题目</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>

      <!-- 填空题表单 -->
      <div v-else-if="type === 'fill-blank'" class="fill-blank-form">
        <div class="fill-blank-section">
          <h3>填空题设置</h3>
          <div class="text-input-section">
            <h4>请输入完整文本：</h4>
            <el-input
              v-model="fillBlankForm.fullText"
              type="textarea"
              :rows="12"
              placeholder="请输入一段完整的文本，然后双击需要删除的单词生成填空..."
              class="text-input"
              @input="processText"
            />
            <p class="tip">提示：双击文本中的单词将其标记为填空，再次双击标记的填空将恢复为原单词</p>
          </div>
        </div>
        <div class="fill-blank-section">
          <h3 class="section-title-green">生成的填空题：</h3>
          <div class="generated-text-preview" v-if="processedWords.length > 0">
            <span
              v-for="(word, index) in processedWords"
              :key="index"
              :class="['word-item', { 'blank-word': word.isBlank }]"
              @dblclick="toggleBlank(index)"
            >
              {{ word.isBlank ? '______' : word.content }}
            </span>
          </div>
          <div v-else class="placeholder-box">双击上方文本中的单词生成填空</div>
        </div>
        <div class="fill-blank-section">
          <h3 class="section-title-green">填空题答案：</h3>
          <div class="answers-preview" v-if="blankAnswers.length > 0">
            <ul>
              <li v-for="(answer, index) in blankAnswers" :key="index">
                <strong>填空 {{ index + 1 }}:</strong> {{ answer }} ({{ blankScores[index] || 1 }}分)
              </li>
            </ul>
          </div>
          <div v-else class="placeholder-box">生成填空后，答案将自动显示在这里</div>
        </div>
        <div class="fill-blank-section">
          <el-form label-width="140px" class="score-form">
            <el-form-item label="每个填空的分值：">
              <el-input-number v-model="fillBlankForm.defaultScore" :min="0.5" :max="100" :step="0.5" />
            </el-form-item>
            <el-form-item label="大题题干：">
              <el-input
                v-model="fillBlankForm.questionText"
                type="textarea"
                :rows="2"
                placeholder="请输入大题题干，如：阅读下面的短文，根据上下文填空"
              />
            </el-form-item>
            <el-form-item label="最多播放次数：">
              <el-input-number v-model="fillBlankForm.maximumPlay" :min="0" :max="99" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSubmitFillBlank" :loading="submitting">创建题目</el-button>
              <el-button @click="goBack">取消</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
      <!-- 连线题、改错题：暂保留占位，可后续扩展 -->
      <div v-else class="placeholder-content">
        <p><strong>{{ typeLabel }}</strong> 新建功能已支持选择题、主观题和填空题，请先使用对应题型添加题目。</p>
        <p class="desc">连线题、改错题的表单与 API 已就绪，如需在页面上直接新建可后续扩展。</p>
        <el-button type="primary" @click="goBack">返回题库</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createMaterialQuestion } from '@/api/content'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const formComprehensionRef = ref<FormInstance>()

const formComprehension = reactive({
  question_text: '',
  maximum_play: 3,
  sub_question_text: '',
  answer: '',
  score: 5
})

const rulesComprehension: FormRules = {
  question_text: [{ required: true, message: '请输入大题题干', trigger: 'blur' }],
  sub_question_text: [{ required: true, message: '请输入小题题干', trigger: 'blur' }],
  answer: [{ required: true, message: '请输入参考答案', trigger: 'blur' }]
}

const type = computed(() => (route.params.type as string) || 'choice')
const materialId = computed(() => Number(route.params.materialId))

const typeLabel = computed(() => {
  const map: Record<string, string> = {
    choice: '选择题',
    matching: '连线题',
    correction: '改错题',
    'fill-blank': '填空题',
    comprehension: '主观题'
  }
  return map[type.value] || type.value
})

const optLabels = ['A', 'B', 'C', 'D']

const form = reactive({
  question_text: '',
  maximum_play: 3,
  sub_questions: [
    {
      question_text: '',
      answer: 'A',
      score: 1,
      options: [
        { option_label: 'A', option_content: '', is_answer: true },
        { option_label: 'B', option_content: '', is_answer: false },
        { option_label: 'C', option_content: '', is_answer: false },
        { option_label: 'D', option_content: '', is_answer: false }
      ]
    }
  ]
})

const rules: FormRules = {
  question_text: [{ required: true, message: '请输入大题题干', trigger: 'blur' }],
  'sub_questions.0.question_text': [{ required: true, message: '请输入小题题干', trigger: 'blur' }]
}

function buildPayload() {
  const sub = form.sub_questions[0]
  const options = (sub.options || []).map((opt, i) => ({
    option_label: optLabels[i],
    option_content: opt.option_content || '',
    is_answer: sub.answer === optLabels[i]
  }))
  return {
    question_type: 'choice' as const,
    question_text: form.question_text.trim(),
    maximum_play: form.maximum_play,
    sub_questions: [
      {
        question_text: sub.question_text.trim(),
        answer: sub.answer,
        score: sub.score,
        options
      }
    ]
  }
}

const handleSubmit = async () => {
  if (!formRef.value || type.value !== 'choice') return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    if (!materialId.value) {
      ElMessage.error('素材 ID 无效')
      return
    }
    const hasContent = form.sub_questions[0].options?.some(o => (o.option_content || '').trim())
    if (!hasContent) {
      ElMessage.warning('请至少填写一个选项内容')
      return
    }
    submitting.value = true
    try {
      await createMaterialQuestion(materialId.value, buildPayload())
      ElMessage.success('题目创建成功')
      router.push({ name: 'QuestionBank' })
    } catch (e: any) {
      ElMessage.error(e?.message || '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleSubmitComprehension = async () => {
  if (!formComprehensionRef.value || type.value !== 'comprehension') return
  await formComprehensionRef.value.validate(async (valid) => {
    if (!valid) return
    if (!materialId.value) {
      ElMessage.error('素材 ID 无效')
      return
    }
    submitting.value = true
    try {
      await createMaterialQuestion(materialId.value, {
        question_type: 'comprehension',
        question_text: formComprehension.question_text.trim(),
        maximum_play: formComprehension.maximum_play,
        sub_questions: [
          {
            question_text: formComprehension.sub_question_text.trim(),
            answer: formComprehension.answer.trim(),
            score: formComprehension.score
          }
        ]
      })
      ElMessage.success('题目创建成功')
      router.push({ name: 'QuestionBank' })
    } catch (e: any) {
      ElMessage.error(e?.message || '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

const goBack = () => {
  router.push({ name: 'QuestionBank' })
}

// 填空题
interface WordItem {
  content: string
  isBlank: boolean
}

const fillBlankForm = reactive({
  fullText: '',
  questionText: '阅读下面的短文，根据上下文填空',
  defaultScore: 1,
  maximumPlay: 3
})

const processedWords = ref<WordItem[]>([])
const blankAnswers = ref<string[]>([])
const blankScores = ref<number[]>([])

const processText = () => {
  if (!fillBlankForm.fullText) {
    processedWords.value = []
    return
  }
  const words = fillBlankForm.fullText.split(/(\s+)/)
  const newWords: WordItem[] = []
  const oldBlanks = new Map<number, boolean>()
  processedWords.value.forEach((word, index) => {
    if (word.isBlank) oldBlanks.set(index, true)
  })
  words.forEach((word, index) => {
    if (word.trim()) {
      newWords.push({ content: word, isBlank: oldBlanks.has(index) || false })
    } else if (word) {
      newWords.push({ content: word, isBlank: false })
    }
  })
  processedWords.value = newWords
  updateAnswers()
}

const toggleBlank = (index: number) => {
  processedWords.value[index].isBlank = !processedWords.value[index].isBlank
  updateAnswers()
}

const updateAnswers = () => {
  blankAnswers.value = []
  blankScores.value = []
  processedWords.value.forEach((word) => {
    if (word.isBlank) {
      blankAnswers.value.push(word.content.trim())
      blankScores.value.push(fillBlankForm.defaultScore)
    }
  })
}

const handleSubmitFillBlank = async () => {
  if (!fillBlankForm.fullText) {
    ElMessage.warning('请输入完整文本')
    return
  }
  if (blankAnswers.value.length === 0) {
    ElMessage.warning('请至少标记一个填空')
    return
  }
  if (!materialId.value) {
    ElMessage.error('素材 ID 无效')
    return
  }
  submitting.value = true
  try {
    const questionText = fillBlankForm.questionText || '阅读下面的短文，根据上下文填空'
    const subQuestions = blankAnswers.value.map((answer, index) => ({
      question_text: `填空 ${index + 1}`,
      answer: answer,
      score: blankScores.value[index] || fillBlankForm.defaultScore
    }))
    const processedText = processedWords.value
      .map((word) => (word.isBlank ? '______' : word.content))
      .join('')
    await createMaterialQuestion(materialId.value, {
      question_type: 'text',
      question_text: `${questionText}\n\n${processedText}`,
      maximum_play: fillBlankForm.maximumPlay,
      sub_questions: subQuestions
    })
    ElMessage.success('题目创建成功')
    router.push({ name: 'QuestionBank' })
  } catch (e: any) {
    ElMessage.error(e?.message || '创建失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.question-edit-by-type {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.edit-form {
  max-width: 720px;
}
.options-list {
  width: 100%;
}
.option-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
}
.option-label {
  width: 28px;
  flex-shrink: 0;
  font-weight: 500;
}
.option-row .option-input {
  flex: 1;
  max-width: 400px;
}
.placeholder-content {
  padding: 40px 20px;
  text-align: center;
}
.placeholder-content p {
  margin-bottom: 16px;
  color: #606266;
}
.placeholder-content .desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 24px;
}

.fill-blank-form {
  max-width: 900px;
}
.fill-blank-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}
.fill-blank-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
}
.section-title-green {
  color: #67c23a !important;
}
.text-input-section h4 {
  margin-bottom: 10px;
  color: #606266;
}
.text-input {
  margin-bottom: 10px;
}
.fill-blank-form .tip {
  font-size: 12px;
  color: #909399;
  margin: 0;
}
.generated-text-preview {
  background-color: #f0f9ff;
  padding: 20px;
  border-radius: 6px;
  line-height: 2;
  font-size: 16px;
  border: 1px solid #d9ecff;
}
.word-item {
  display: inline-block;
  padding: 2px 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}
.word-item:hover {
  background-color: #e6f7ff;
}
.blank-word {
  color: #409eff;
  font-weight: 600;
  background-color: #ecf5ff !important;
}
.answers-preview {
  background-color: #f0f9ff;
  padding: 20px;
  border-radius: 6px;
  border: 1px solid #d9ecff;
}
.answers-preview ul {
  margin: 0;
  padding-left: 20px;
}
.answers-preview li {
  margin-bottom: 10px;
  color: #303133;
}
.placeholder-box {
  background-color: #f0f9ff;
  padding: 40px;
  border-radius: 6px;
  text-align: center;
  color: #909399;
  font-size: 16px;
  border: 1px solid #d9ecff;
}
.score-form {
  margin-top: 20px;
}
</style>
