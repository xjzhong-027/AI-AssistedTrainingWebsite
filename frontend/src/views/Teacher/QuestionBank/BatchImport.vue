<template>
  <div class="batch-import">
    <!-- 顶部插画 -->
    <div class="illustration-header">
      <div class="illustration-content">
        <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="3" width="20" height="14" rx="2" ry="2" fill="#E8E4FF" stroke="#8C7CF0"/>
          <line x1="8" y1="21" x2="16" y2="21" stroke="#8C7CF0"/>
          <line x1="12" y1="17" x2="12" y2="21" stroke="#8C7CF0"/>
          <path d="M10 8h4" stroke="#8C7CF0"/>
          <path d="M10 10h4" stroke="#8C7CF0"/>
          <path d="M10 12h4" stroke="#8C7CF0"/>
          <path d="M10 14h4" stroke="#8C7CF0"/>
          <circle cx="6" cy="10" r="1" fill="#FFB347"/>
          <circle cx="18" cy="12" r="1" fill="#FFB347"/>
          <circle cx="6" cy="14" r="1" fill="#FFB347"/>
          <circle cx="18" cy="8" r="1" fill="#FFB347"/>
        </svg>
      </div>
    </div>

    <div class="batch-import-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7,10 12,15 17,10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </div>
          <h2>批量导入选择题</h2>
        </div>
        <el-button @click="goBack" class="secondary-button">返回</el-button>
      </div>

      <div class="import-tip">
        <p><strong>格式说明</strong>：每行一道题，使用竖线 | 分隔：</p>
        <code>题目内容|选项A|选项B|选项C|选项D|正确答案|分值</code>
        <p class="example">示例：英语中"apple"的意思是什么？|苹果|香蕉|橙子|葡萄|A|2</p>
      </div>

      <el-input
        v-model="importText"
        type="textarea"
        :rows="15"
        placeholder="请按格式输入，每行一道题..."
        class="modern-textarea"
      />

      <div class="actions">
        <el-button type="primary" @click="parseAndPreview" :loading="parsing" class="primary-button">
          解析并预览
        </el-button>
        <el-button type="success" @click="submitImport" :loading="submitting" :disabled="parsedQuestions.length === 0" class="success-button">
          确认导入 {{ parsedQuestions.length }} 道题
        </el-button>
        <el-button @click="goBack" class="secondary-button">取消</el-button>
      </div>

      <div v-if="parsedQuestions.length > 0" class="preview-section">
        <h4>解析结果（共 {{ parsedQuestions.length }} 道）</h4>
        <div v-for="(q, idx) in parsedQuestions" :key="idx" class="preview-item">
          <span class="q-num">第 {{ idx + 1 }} 题（{{ q.score }}分）</span>
          <p>{{ q.question_text }}</p>
          <p class="options">A. {{ q.option_A }} B. {{ q.option_B }} C. {{ q.option_C }} D. {{ q.option_D }}</p>
          <span class="answer">正确答案：{{ q.correct_answer }}</span>
        </div>
      </div>

      <div v-if="parseErrors.length > 0" class="error-section">
        <el-alert type="error" :title="`解析错误 ${parseErrors.length} 条`" show-icon>
          <ul>
            <li v-for="(err, i) in parseErrors" :key="i">{{ err }}</li>
          </ul>
        </el-alert>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { batchImportChoices } from '@/api/content'

const router = useRouter()
const route = useRoute()

const materialId = computed(() => Number(route.params.materialId))
const loading = ref(false)
const parsing = ref(false)
const submitting = ref(false)
const importText = ref('')
const parsedQuestions = ref<Array<{
  question_text: string
  option_A: string
  option_B: string
  option_C: string
  option_D: string
  correct_answer: string
  score: number
}>>([])
const parseErrors = ref<string[]>([])

const parseAndPreview = () => {
  const text = importText.value.trim()
  if (!text) {
    ElMessage.warning('请输入内容')
    return
  }
  parsing.value = true
  parseErrors.value = []
  const questions: typeof parsedQuestions.value = []
  const lines = text.split('\n')
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue
    const parts = line.split('|').map((p) => p.trim())
    if (parts.length !== 7) {
      parseErrors.value.push(`第 ${i + 1} 行：应为 7 个字段`)
      continue
    }
    const [qt, oa, ob, oc, od, ans, sc] = parts
    if (!qt || !oa || !ob || !oc || !od) {
      parseErrors.value.push(`第 ${i + 1} 行：题目和选项不能为空`)
      continue
    }
    const upperAns = (ans || 'A').toUpperCase()
    if (!['A', 'B', 'C', 'D'].includes(upperAns)) {
      parseErrors.value.push(`第 ${i + 1} 行：正确答案须为 A/B/C/D`)
      continue
    }
    const scoreVal = parseFloat(sc)
    if (isNaN(scoreVal) || scoreVal <= 0) {
      parseErrors.value.push(`第 ${i + 1} 行：分值须为大于 0 的数字`)
      continue
    }
    questions.push({
      question_text: qt,
      option_A: oa,
      option_B: ob,
      option_C: oc,
      option_D: od,
      correct_answer: upperAns,
      score: scoreVal
    })
  }
  parsedQuestions.value = questions
  parsing.value = false
  if (questions.length > 0) {
    ElMessage.success(`成功解析 ${questions.length} 道题`)
  }
}

const submitImport = async () => {
  if (parsedQuestions.value.length === 0) {
    ElMessage.warning('没有可导入的题目')
    return
  }
  submitting.value = true
  try {
    const res = await batchImportChoices(materialId.value, parsedQuestions.value)
    ElMessage.success(`成功导入 ${res.count} 道选择题`)
    router.push({ name: 'QuestionBank' })
  } catch (err: any) {
    ElMessage.error(err?.message || '导入失败')
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push({ name: 'QuestionBank' })
}

onMounted(() => {
  if (!materialId.value) {
    ElMessage.error('缺少素材 ID')
    router.push({ name: 'QuestionBank' })
  }
})
</script>

<style scoped>
.batch-import {
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
.batch-import-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.batch-import-card::before {
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

.success-button {
  background: linear-gradient(135deg, #67C23A, #85CE61) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 12px !important;
  padding: 10px 24px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
}

.success-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(103, 194, 58, 0.4) !important;
}

/* 输入框样式 */
.modern-textarea {
  border-radius: 12px !important;
  border: 1px solid #E2E8F0 !important;
  transition: all 0.3s ease !important;
  margin-bottom: 16px;
}

.modern-textarea:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

/* 操作按钮区域 */
.actions {
  margin-bottom: 24px;
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #F0F2F5;
}

/* 提示信息样式 */
.import-tip {
  margin-bottom: 20px;
  padding: 16px;
  background: #F8F5FF;
  border-radius: 12px;
  font-size: 14px;
  border-left: 4px solid #8C7CF0;
}

.import-tip code {
  display: block;
  margin: 12px 0;
  padding: 12px;
  background: #fff;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  overflow-x: auto;
}

.example {
  font-size: 12px;
  color: #718096;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #E2E8F0;
}

/* 预览区域样式 */
.preview-section {
  margin-top: 24px;
  padding: 20px;
  background: #F8F5FF;
  border-radius: 12px;
  max-height: 400px;
  overflow-y: auto;
  border-left: 4px solid #8C7CF0;
}

.preview-section h4 {
  margin: 0 0 16px 0;
  color: #1A202C;
  font-size: 16px;
  font-weight: 600;
}

.preview-item {
  padding: 16px;
  margin-bottom: 12px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  transition: all 0.3s ease;
}

.preview-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.1);
}

.q-num {
  font-weight: 600;
  color: #8C7CF0;
  font-size: 14px;
  display: block;
  margin-bottom: 8px;
}

.preview-item p {
  margin: 8px 0;
  color: #1A202C;
  line-height: 1.4;
}

.options {
  font-size: 13px;
  color: #4A5568;
  margin: 8px 0;
  padding: 8px 0;
  border-top: 1px dashed #E2E8F0;
  border-bottom: 1px dashed #E2E8F0;
}

.answer {
  font-size: 13px;
  color: #67C23A;
  font-weight: 600;
  display: block;
  margin-top: 8px;
}

/* 错误信息区域 */
.error-section {
  margin-top: 20px;
  padding: 16px;
  background: #FEF2F2;
  border-radius: 12px;
  border-left: 4px solid #F56C6C;
}

/* 加载状态 */
:deep(.el-loading-spinner .path) {
  stroke: #8C7CF0 !important;
}

/* 表单标签样式 */
:deep(.el-form-item__label) {
  color: #4A5568 !important;
  font-weight: 500 !important;
  font-size: 14px !important;
}
</style>
