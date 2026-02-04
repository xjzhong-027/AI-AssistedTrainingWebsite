<template>
  <div class="week-task-import">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>导入周任务 - {{ materialInfo?.title }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <!-- 素材信息展示 -->
      <el-descriptions v-if="materialInfo" :column="2" border class="material-info">
        <el-descriptions-item label="任务标题">{{ materialInfo.title }}</el-descriptions-item>
        <el-descriptions-item label="主题">{{ materialInfo.theme }}</el-descriptions-item>
        <el-descriptions-item label="摘要" :span="2">{{ materialInfo.abstract }}</el-descriptions-item>
        <el-descriptions-item label="关键词" :span="2">{{ materialInfo.keywords }}</el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <!-- 步骤1: 上传Word文档 -->
      <div v-if="currentStep === 1" class="step-content">
        <h3>步骤1: 上传Word文档</h3>
        <p class="tip">请上传包含题目的Word文档（仅支持.docx格式）</p>

        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          accept=".docx"
          drag
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              仅支持.docx格式的Word文档
            </div>
          </template>
        </el-upload>

        <div class="button-group">
          <el-button type="primary" @click="handleUploadWord" :loading="uploading" :disabled="!wordFile">
            解析文档
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 预览和配置 -->
      <div v-if="currentStep === 2" class="step-content">
        <h3>步骤2: 配置任务信息</h3>

        <el-form
          :model="taskForm"
          :rules="taskRules"
          ref="taskFormRef"
          label-width="120px"
        >
          <el-form-item label="任务标题" prop="title">
            <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
          </el-form-item>

          <el-form-item label="所属班级" prop="class_id">
            <el-select v-model="taskForm.class_id" placeholder="请选择班级" style="width: 100%">
              <el-option
                v-for="classItem in classes"
                :key="classItem.id"
                :label="classItem.class_name"
                :value="classItem.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="任务类型" prop="type">
            <el-select v-model="taskForm.type" placeholder="请选择任务类型" style="width: 100%">
              <el-option label="作业" value="task" />
              <el-option label="练习" value="practice" />
              <el-option label="考试" value="exam" />
              <el-option label="小测" value="quiz" />
            </el-select>
          </el-form-item>

          <el-form-item label="周次" prop="week">
            <el-input-number v-model="taskForm.week" :min="1" :max="20" />
          </el-form-item>

          <el-form-item label="排序" prop="order">
            <el-input-number v-model="taskForm.order" :min="0" :max="999" />
          </el-form-item>

          <!-- 考试特有字段 -->
          <template v-if="taskForm.type === 'exam'">
            <el-form-item label="考试日期" prop="exam_date">
              <el-date-picker
                v-model="taskForm.exam_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="开始时间" prop="start_time">
              <el-time-picker
                v-model="taskForm.start_time"
                placeholder="选择时间"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="结束时间" prop="end_time">
              <el-time-picker
                v-model="taskForm.end_time"
                placeholder="选择时间"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="时长(分钟)" prop="duration">
              <el-input-number v-model="taskForm.duration" :min="1" :max="300" />
            </el-form-item>
          </template>

          <el-form-item label="逾期规则">
            <el-select v-model="taskForm.overdue_rule_id" placeholder="请选择逾期规则" clearable style="width: 100%">
              <el-option
                v-for="rule in overdueRules"
                :key="rule.id"
                :label="rule.name"
                :value="rule.id"
              />
            </el-select>
          </el-form-item>
        </el-form>

        <!-- 题目预览 -->
        <el-divider />
        <h4>题目预览</h4>
        <div v-if="questionData && questionData.length > 0" class="question-preview">
          <el-collapse>
            <el-collapse-item
              v-for="(page, pageIdx) in questionData"
              :key="pageIdx"
              :title="`第${pageIdx + 1}页 (${page.page_content?.length || 0}道大题)`"
            >
              <div v-for="(question, qIdx) in page.page_content" :key="qIdx" class="question-item">
                <p><strong>大题{{ qIdx + 1 }}:</strong> {{ question.question_type }}</p>
                <p>{{ question.question_text }}</p>
                <p class="sub-count">包含 {{ question.sub_questions?.length || 0 }} 道小题</p>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
        <el-empty v-else description="暂无题目数据" />

        <div class="button-group">
          <el-button @click="currentStep = 1">上一步</el-button>
          <el-button type="primary" @click="handleSaveTask" :loading="saving">
            保存任务
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import { getMediaMaterialById } from '@/api/content'
import { getAllClasses } from '@/api/user'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const uploading = ref(false)
const saving = ref(false)
const currentStep = ref(1)
const uploadRef = ref()
const taskFormRef = ref<FormInstance>()

const materialId = ref(Number(route.params.id))
const materialInfo = ref<any>(null)
const wordFile = ref<File | null>(null)
const questionData = ref<any[]>([])
const classes = ref<any[]>([])
const overdueRules = ref<any[]>([])

const taskForm = reactive({
  title: '',
  class_id: undefined as number | undefined,
  type: 'task' as string,
  week: 1,
  order: 0,
  exam_date: null as Date | null,
  start_time: null as Date | null,
  end_time: null as Date | null,
  duration: 60,
  overdue_rule_id: undefined as number | undefined
})

const taskRules: FormRules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  class_id: [{ required: true, message: '请选择班级', trigger: 'change' }],
  type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  week: [{ required: true, message: '请输入周次', trigger: 'blur' }]
}

const goBack = () => {
  router.back()
}

const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    wordFile.value = file.raw
  }
}

const handleFileRemove = () => {
  wordFile.value = null
}

const handleUploadWord = async () => {
  if (!wordFile.value) {
    ElMessage.error('请选择Word文档')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('word_file', wordFile.value)
    formData.append('material_id', materialId.value.toString())

    const response = await request.post('/content/week-task-import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    questionData.value = response.question_data || []
    taskForm.title = materialInfo.value?.title || ''
    currentStep.value = 2
    ElMessage.success('文档解析成功')
  } catch (error: any) {
    ElMessage.error(error.message || '文档解析失败')
  } finally {
    uploading.value = false
  }
}

const handleSaveTask = async () => {
  if (!taskFormRef.value) return

  await taskFormRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      const data = {
        ...taskForm,
        material_id: materialId.value,
        question_data: questionData.value,
        exam_date: taskForm.exam_date ? taskForm.exam_date.toISOString().split('T')[0] : null,
        start_time: taskForm.start_time ? taskForm.start_time.toTimeString().split(' ')[0] : null,
        end_time: taskForm.end_time ? taskForm.end_time.toTimeString().split(' ')[0] : null
      }

      await request.post('/content/week-task-save/', data)

      ElMessage.success('任务保存成功')
      router.push('/teacher/week-task')
    } catch (error: any) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const loadMaterialInfo = async () => {
  loading.value = true
  try {
    materialInfo.value = await getMediaMaterialById(materialId.value)
  } catch (error: any) {
    ElMessage.error(error.message || '加载素材信息失败')
  } finally {
    loading.value = false
  }
}

const loadClasses = async () => {
  try {
    classes.value = await getAllClasses()
  } catch (error: any) {
    ElMessage.error(error.message || '加载班级列表失败')
  }
}

const loadOverdueRules = async () => {
  try {
    const response = await request.get('/query/overdue-rules/')
    overdueRules.value = response
  } catch (error: any) {
    console.error('加载逾期规则失败:', error)
  }
}

onMounted(() => {
  loadMaterialInfo()
  loadClasses()
  loadOverdueRules()
})
</script>

<style scoped>
.week-task-import {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.material-info {
  margin-bottom: 20px;
}

.step-content {
  padding: 20px 0;
}

.step-content h3 {
  margin-bottom: 15px;
  color: #333;
}

.tip {
  color: #909399;
  margin-bottom: 20px;
}

.button-group {
  margin-top: 30px;
  text-align: center;
}

.question-preview {
  margin-top: 15px;
}

.question-item {
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 10px;
}

.question-item p {
  margin: 5px 0;
}

.sub-count {
  color: #909399;
  font-size: 12px;
}
</style>
