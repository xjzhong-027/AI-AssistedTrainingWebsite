<template>
  <div class="batch-import">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>批量导入选择题</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

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
        class="import-textarea"
      />

      <div class="actions">
        <el-button type="primary" @click="parseAndPreview" :loading="parsing">
          解析并预览
        </el-button>
        <el-button type="success" @click="submitImport" :loading="submitting" :disabled="parsedQuestions.length === 0">
          确认导入 {{ parsedQuestions.length }} 道题
        </el-button>
        <el-button @click="goBack">取消</el-button>
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
    </el-card>
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
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.import-tip {
  margin-bottom: 16px;
  padding: 12px;
  background: #f0f9ff;
  border-radius: 6px;
  font-size: 14px;
}
.import-tip code {
  display: block;
  margin: 8px 0;
  padding: 8px;
  background: #fff;
  border: 1px solid #d9ecff;
  border-radius: 4px;
}
.example {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}
.import-textarea {
  margin-bottom: 16px;
}
.actions {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}
.preview-section {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 6px;
  max-height: 400px;
  overflow-y: auto;
}
.preview-item {
  padding: 10px;
  margin-bottom: 10px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}
.q-num {
  font-weight: 600;
  color: #409eff;
}
.options {
  font-size: 13px;
  color: #606266;
  margin: 6px 0;
}
.answer {
  font-size: 12px;
  color: #67c23a;
  font-weight: 600;
}
.error-section {
  margin-top: 16px;
}
</style>
