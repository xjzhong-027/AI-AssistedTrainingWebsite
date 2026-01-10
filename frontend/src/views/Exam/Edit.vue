<template>
  <div class="exam-edit">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>编辑考试</span>
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
        <el-form-item label="考试标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入考试标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="考试描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入考试描述（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="开始时间" prop="startTime">
          <el-date-picker
            v-model="form.startTime"
            type="datetime"
            placeholder="选择开始时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="结束时间" prop="endTime">
          <el-date-picker
            v-model="form.endTime"
            type="datetime"
            placeholder="选择结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="考试时长" prop="duration">
          <el-input-number
            v-model="form.duration"
            :min="1"
            :max="600"
            placeholder="请输入考试时长（分钟）"
            style="width: 100%"
          />
          <div class="form-tip">单位：分钟（1-600分钟）</div>
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
import { getExamById, updateExam } from '@/api/exam'
import type { ExamUpdateDTO } from '@/types/exam'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const form = reactive<ExamUpdateDTO & { startTime?: string; endTime?: string }>({
  title: '',
  description: '',
  startTime: '',
  endTime: '',
  duration: 60
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入考试标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  startTime: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  endTime: [
    { required: true, message: '请选择结束时间', trigger: 'change' },
    {
      validator: (rule, value, callback) => {
        if (form.startTime && value && new Date(value) <= new Date(form.startTime)) {
          callback(new Error('结束时间必须晚于开始时间'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  duration: [
    { required: true, message: '请输入考试时长', trigger: 'blur' },
    { type: 'number', min: 1, max: 600, message: '时长必须在 1 到 600 分钟之间', trigger: 'blur' }
  ]
}

// 加载考试数据
const loadExam = async () => {
  const id = Number(route.params.id)
  if (!id) {
    ElMessage.error('考试ID无效')
    router.push('/exams')
    return
  }

  loading.value = true
  try {
    const exam = await getExamById(id)
    form.title = exam.title
    form.description = exam.description || ''
    form.startTime = exam.startTime
    form.endTime = exam.endTime
    form.duration = exam.duration
  } catch (error) {
    console.error('加载考试失败', error)
  } finally {
    loading.value = false
  }
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const id = Number(route.params.id)
        const examData: ExamUpdateDTO = {
          title: form.title,
          description: form.description,
          startTime: new Date(form.startTime!).toISOString(),
          endTime: new Date(form.endTime!).toISOString(),
          duration: form.duration
        }

        await updateExam(id, examData)
        ElMessage.success('更新成功')
        router.push(`/exams/${id}`)
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
  loadExam()
})
</script>

<style scoped>
.exam-edit {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
