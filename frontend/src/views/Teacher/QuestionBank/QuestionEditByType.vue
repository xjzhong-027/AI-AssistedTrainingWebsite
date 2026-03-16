<template>
  <div class="question-edit-by-type">
    <!-- 顶部插画 -->
    <div class="illustration-header">
      <div class="illustration-content">
        <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" fill="#E8E4FF" stroke="#8C7CF0"/>
          <line x1="16" y1="2" x2="16" y2="6" stroke="#8C7CF0"/>
          <line x1="8" y1="2" x2="8" y2="6" stroke="#8C7CF0"/>
          <line x1="3" y1="10" x2="21" y2="10" stroke="#8C7CF0"/>
          <path d="M9 14h6" stroke="#8C7CF0"/>
          <path d="M9 18h6" stroke="#8C7CF0"/>
          <circle cx="12" cy="14" r="1" fill="#FFB347"/>
          <circle cx="12" cy="18" r="1" fill="#FFB347"/>
        </svg>
      </div>
    </div>

    <div class="question-edit-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
          </div>
          <h2>{{ typeLabel }} - 新建</h2>
        </div>
        <el-button @click="goBack" type="default" class="secondary-button">返回</el-button>
      </div>

      <!-- 选择题表单 -->
      <el-form
        v-if="type === 'choice'"
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="140px"
        class="modern-form"
      >
        <el-form-item label="大题题干" prop="question_text">
          <el-input
            v-model="form.question_text"
            type="textarea"
            :rows="3"
            placeholder="请输入听录音/阅读后的题目说明，如：听录音选答案"
            class="modern-textarea"
          />
        </el-form-item>
        <el-form-item label="最多播放次数">
          <el-input-number v-model="form.maximum_play" :min="0" :max="99" class="modern-input-number" />
        </el-form-item>
        <el-divider class="modern-divider">小题 1</el-divider>
        <el-form-item label="小题题干" prop="sub_questions.0.question_text">
          <el-input
            v-model="form.sub_questions[0].question_text"
            type="textarea"
            :rows="2"
            placeholder="请输入小题内容"
            class="modern-textarea"
          />
        </el-form-item>
        <el-form-item label="选项" required>
          <div class="options-list">
            <div v-for="(opt, idx) in form.sub_questions[0].options" :key="idx" class="option-row">
              <span class="option-label">{{ optLabels[idx] }}.</span>
              <el-input
                v-model="opt.option_content"
                :placeholder="`选项 ${optLabels[idx]} 内容`"
                class="option-input modern-input"
              />
            </div>
          </div>
        </el-form-item>
        <el-form-item label="正确答案">
          <el-radio-group v-model="form.sub_questions[0].answer" class="modern-radio-group">
            <el-radio v-for="l in optLabels" :key="l" :label="l" class="modern-radio">{{ l }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="小题分数">
          <el-input-number v-model="form.sub_questions[0].score" :min="0" :max="100" :step="0.5" class="modern-input-number" />
        </el-form-item>
        <el-form-item class="form-actions">
          <el-button type="primary" @click="handleSubmit" :loading="submitting" class="primary-button">创建题目</el-button>
          <el-button @click="goBack" class="secondary-button">取消</el-button>
        </el-form-item>
      </el-form>

      <!-- 主观题表单（简答题、理解题、总结题） -->
      <el-form
        v-else-if="type === 'comprehension'"
        :model="formComprehension"
        :rules="rulesComprehension"
        ref="formComprehensionRef"
        label-width="140px"
        class="modern-form"
      >
        <el-form-item label="大题题干" prop="question_text">
          <el-input
            v-model="formComprehension.question_text"
            type="textarea"
            :rows="3"
            placeholder="请输入听录音/阅读后的题目说明，如：听录音后回答问题、总结主旨大意"
            class="modern-textarea"
          />
        </el-form-item>
        <el-form-item label="最多播放次数">
          <el-input-number v-model="formComprehension.maximum_play" :min="0" :max="99" class="modern-input-number" />
        </el-form-item>
        <el-divider class="modern-divider">小题 1</el-divider>
        <el-form-item label="小题题干" prop="sub_question_text">
          <el-input
            v-model="formComprehension.sub_question_text"
            type="textarea"
            :rows="3"
            placeholder="请输入问题内容，如：请总结本文主旨、请简要回答"
            class="modern-textarea"
          />
        </el-form-item>
        <el-form-item label="参考答案" prop="answer">
          <el-input
            v-model="formComprehension.answer"
            type="textarea"
            :rows="4"
            placeholder="请输入参考答案供 AI 评分参考（学生不可见）"
            class="modern-textarea"
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
    </div>

    <AIQuestionAssistant
      v-if="materialId"
      :material-id="materialId"
      :transcript="materialTranscript"
      :default-question-type="aiDefaultQuestionType"
      @questions-applied="handleQuestionsApplied"
      @fill-form="handleFillForm"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { createMaterialQuestion, getMediaMaterialById } from '@/api/content'
import AIQuestionAssistant from '@/components/common/AIQuestionWindow/index.vue'
import type { GeneratedQuestion } from '@/api/questionGeneration'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const formComprehensionRef = ref<FormInstance>()
const materialTranscript = ref('')

const formComprehension = reactive({
  question_text: '',
  maximum_play: 3,
  sub_question_text: '',
  answer: '',
  score: 5
})

const rulesComprehension: FormRules = {
  question_text: [{ required: true, message: '请输入大题题干', trigger: 'blur' }]
}

const type = computed(() => (route.params.type as string) || 'choice')
const materialId = computed(() => Number(route.params.materialId))

const aiDefaultQuestionType = computed((): 'choice' | 'fill-blank' | 'comprehension' => {
  const typeMap: Record<string, 'choice' | 'fill-blank' | 'comprehension'> = {
    'choice': 'choice',
    'fill-blank': 'fill-blank',
    'comprehension': 'comprehension'
  }
  return typeMap[type.value] || 'choice'
})

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

interface ChoiceSubQuestion {
  question_text: string
  answer: string
  score: number
  options: Array<{ option_label: string; option_content: string; is_answer: boolean }>
}

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
  ] as ChoiceSubQuestion[]
})

const rules: FormRules = {
  question_text: [{ required: true, message: '请输入大题题干', trigger: 'blur' }]
}

const addSubQuestion = () => {
  form.sub_questions.push({
    question_text: '',
    answer: 'A',
    score: 1,
    options: [
      { option_label: 'A', option_content: '', is_answer: true },
      { option_label: 'B', option_content: '', is_answer: false },
      { option_label: 'C', option_content: '', is_answer: false },
      { option_label: 'D', option_content: '', is_answer: false }
    ]
  })
}

const removeSubQuestion = (index: number) => {
  form.sub_questions.splice(index, 1)
}

const addComprehensionSubQuestion = () => {
  formComprehension.sub_questions.push({
    question_text: '',
    answer: '',
    score: 5
  })
}

const removeComprehensionSubQuestion = (index: number) => {
  formComprehension.sub_questions.splice(index, 1)
}

function buildPayload() {
  const subQuestions = form.sub_questions.map((sub) => {
    const options = (sub.options || []).map((opt, i) => ({
      option_label: optLabels[i],
      option_content: opt.option_content || '',
      is_answer: sub.answer === optLabels[i]
    }))
    return {
      question_text: sub.question_text.trim(),
      answer: sub.answer,
      score: sub.score,
      options
    }
  })
  return {
    question_type: 'choice' as const,
    question_text: form.question_text.trim(),
    maximum_play: form.maximum_play,
    sub_questions: subQuestions
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

const loadMaterial = async () => {
  if (!materialId.value) return
  try {
    const material = await getMediaMaterialById(materialId.value)
    materialTranscript.value = material.transcript || ''
  } catch (e: any) {
    console.error('加载素材失败', e)
  }
}

const handleQuestionsApplied = () => {
  ElMessage.success('AI生成的题目已添加到题库')
  router.push({ name: 'QuestionBank' })
}

const handleFillForm = (questions: GeneratedQuestion[]) => {
  if (questions.length === 0) {
    ElMessage.warning('没有可填充的题目')
    return
  }

  const firstQuestion = questions[0]
  const questionType = firstQuestion.main_question.question_type

  if (questionType === 'choice' && type.value === 'choice') {
    form.question_text = firstQuestion.main_question.question_text || ''
    form.maximum_play = firstQuestion.main_question.maximum_play || 3
    
    const allSubQuestions: ChoiceSubQuestion[] = []
    questions.forEach(q => {
      if (q.sub_questions) {
        q.sub_questions.forEach(sq => {
          allSubQuestions.push({
            question_text: sq.question_text || '',
            score: sq.score || 1,
            answer: sq.correct_answer || 'A',
            options: [
              { option_label: 'A', option_content: sq.options?.A || '', is_answer: sq.correct_answer === 'A' },
              { option_label: 'B', option_content: sq.options?.B || '', is_answer: sq.correct_answer === 'B' },
              { option_label: 'C', option_content: sq.options?.C || '', is_answer: sq.correct_answer === 'C' },
              { option_label: 'D', option_content: sq.options?.D || '', is_answer: sq.correct_answer === 'D' }
            ]
          })
        })
      }
    })
    
    form.sub_questions = allSubQuestions.length > 0 ? allSubQuestions : [createEmptyChoiceSubQuestion()]
    ElMessage.success(`已填充 ${allSubQuestions.length} 道选择题到表单`)
    
  } else if ((questionType === 'text' || questionType === 'blank' || questionType === 'fill-blank') && type.value === 'fill-blank') {
    fillBlankForm.questionText = firstQuestion.main_question.question_text?.split('\n\n')[0] || '阅读下面的短文，根据上下文填空'
    fillBlankForm.maximumPlay = firstQuestion.main_question.maximum_play || 3
    
    const fullText = firstQuestion.main_question.question_text?.split('\n\n').slice(1).join('\n\n') || ''
    fillBlankForm.fullText = fullText.replace(/_{6,}/g, '______')
    
    const allAnswers: string[] = []
    const allScores: number[] = []
    questions.forEach(q => {
      if (q.sub_questions) {
        q.sub_questions.forEach(sq => {
          if (sq.answer) {
            allAnswers.push(sq.answer)
            allScores.push(sq.score || fillBlankForm.defaultScore)
          }
        })
      }
    })
    
    blankAnswers.value = allAnswers
    blankScores.value = allScores
    
    processText()
    ElMessage.success(`已填充 ${allAnswers.length} 个填空到表单`)
    
  } else if (questionType === 'comprehension' && type.value === 'comprehension') {
    formComprehension.question_text = firstQuestion.main_question.question_text || ''
    formComprehension.maximum_play = firstQuestion.main_question.maximum_play || 3
    const firstSub = firstQuestion.sub_questions?.[0]
    if (firstSub) {
      formComprehension.sub_question_text = firstSub.question_text || ''
      formComprehension.answer = firstSub.answer || ''
      formComprehension.score = firstSub.score || 5
    }
    ElMessage.success('已填充主观题到表单')
    
  } else {
    ElMessage.warning(`当前页面不支持填充${getQuestionTypeText(questionType)}，请切换到对应题型页面`)
  }
}

const createEmptyChoiceSubQuestion = (): ChoiceSubQuestion => ({
  question_text: '',
  answer: 'A',
  score: 1,
  options: [
    { option_label: 'A', option_content: '', is_answer: true },
    { option_label: 'B', option_content: '', is_answer: false },
    { option_label: 'C', option_content: '', is_answer: false },
    { option_label: 'D', option_content: '', is_answer: false }
  ]
})

const createEmptyComprehensionSubQuestion = (): ComprehensionSubQuestion => ({
  question_text: '',
  answer: '',
  score: 5
})

const getQuestionTypeText = (t: string): string => {
  const map: Record<string, string> = {
    choice: '选择题',
    matching: '连线题',
    text: '填空题',
    blank: '填空题',
    comprehension: '主观题'
  }
  return map[t] || t
}

onMounted(() => {
  loadMaterial()
})
</script>

<style scoped>
.question-edit-by-type {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

/* 插画样式 */
.illustration-header {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  animation: fadeIn 0.8s ease-out;
}

.illustration-content {
  position: relative;
  animation: float 3s ease-in-out infinite;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

/* 卡片样式 */
.question-edit-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.question-edit-card::before {
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

/* 按钮样式 */
.primary-button {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 12px !important;
  padding: 10px 24px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
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
}

.secondary-button:hover {
  border-color: #8C7CF0 !important;
  color: #8C7CF0 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2) !important;
}

/* 表单样式 */
.modern-form {
  max-width: 720px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #F0F2F5;
}

/* 输入框样式 */
.modern-input,
.modern-textarea {
  border-radius: 12px !important;
  border: 1px solid #E2E8F0 !important;
  transition: all 0.3s ease !important;
}

.modern-input:focus,
.modern-textarea:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

.modern-input-number {
  border-radius: 12px !important;
  border: 1px solid #E2E8F0 !important;
}

/* 选项样式 */
.options-list {
  width: 100%;
}

.option-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
}

.option-label {
  width: 32px;
  flex-shrink: 0;
  font-weight: 600;
  color: #4A5568;
}

.option-row .option-input {
  flex: 1;
  max-width: 400px;
}

/* 单选框样式 */
.modern-radio-group {
  display: flex;
  gap: 20px;
}

.modern-radio {
  padding: 8px 12px !important;
  border-radius: 8px !important;
  transition: all 0.3s ease !important;
}

.modern-radio:hover {
  background: rgba(140, 124, 240, 0.1) !important;
}

/* 分割线样式 */
.modern-divider {
  margin: 24px 0 !important;
  border-color: #F0F2F5 !important;
}

/* 占位符样式 */
.placeholder-content {
  padding: 60px 40px;
  text-align: center;
  background: rgba(140, 124, 240, 0.05);
  border-radius: 16px;
  border: 2px dashed #C6B9FF;
}

.placeholder-content p {
  margin-bottom: 16px;
  color: #4A5568;
  font-size: 16px;
}

.placeholder-content .desc {
  font-size: 14px;
  color: #8B9BB4;
  margin-bottom: 24px;
}

/* 填空题样式 */
.fill-blank-form {
  max-width: 900px;
}

.fill-blank-section {
  margin-bottom: 30px;
  padding: 24px;
  background: linear-gradient(135deg, #F8F5FF, #F0ECFF);
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
}

.fill-blank-section h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #4A5568;
  font-size: 16px;
  font-weight: 600;
}

.section-title-green {
  color: #67c23a !important;
}

.text-input-section h4 {
  margin-bottom: 12px;
  color: #4A5568;
  font-size: 14px;
  font-weight: 600;
}

.text-input {
  margin-bottom: 16px;
}

.fill-blank-form .tip {
  font-size: 12px;
  color: #8B9BB4;
  margin: 0 0 16px 0;
  padding-left: 8px;
  border-left: 3px solid #C6B9FF;
}

.generated-text-preview {
  background: #FFFFFF;
  padding: 24px;
  border-radius: 12px;
  line-height: 2;
  font-size: 16px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
}

.word-item {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 0 2px;
}

.word-item:hover {
  background: rgba(140, 124, 240, 0.1);
  transform: translateY(-1px);
}

.blank-word {
  color: #8C7CF0;
  font-weight: 600;
  background: rgba(140, 124, 240, 0.1) !important;
  border: 2px solid #C6B9FF;
}

.answers-preview {
  background: #FFFFFF;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
}

.answers-preview h4 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #4A5568;
  font-size: 14px;
  font-weight: 600;
}

.answers-preview ul {
  margin: 0;
  padding-left: 20px;
}

.answers-preview li {
  margin-bottom: 12px;
  color: #4A5568;
  font-size: 14px;
}

.placeholder-box {
  background: linear-gradient(135deg, #F8F5FF, #F0ECFF);
  padding: 60px;
  border-radius: 16px;
  text-align: center;
  color: #8B9BB4;
  font-size: 16px;
  border: 2px dashed #C6B9FF;
}

.score-form {
  margin-top: 24px;
  padding: 20px;
  background: #FFFFFF;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
}

/* 加载状态 */
:deep(.el-loading-spinner .path) {
  stroke: #8C7CF0 !important;
}
</style>
