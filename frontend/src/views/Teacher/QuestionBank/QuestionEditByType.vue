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

      <!-- 连线题/改错题：暂保留占位，可后续扩展 -->
      <div v-else class="placeholder-content">
        <p><strong>{{ typeLabel }}</strong> 新建功能已支持选择题，请先使用「选择题」添加题目。</p>
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

const type = computed(() => (route.params.type as string) || 'choice')
const materialId = computed(() => Number(route.params.materialId))

const typeLabel = computed(() => {
  const map: Record<string, string> = {
    choice: '选择题',
    matching: '连线题',
    correction: '改错题'
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

const goBack = () => {
  router.push({ name: 'QuestionBank' })
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
</style>
