<template>
  <div class="week-task-import-container">
    <div class="week-task-import-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17,8 12,3 7,8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
          </div>
          <h2>导入周任务 - {{ materialInfo?.title }}</h2>
        </div>
        <el-button @click="goBack" type="default" class="secondary-button">返回</el-button>
      </div>

      <!-- 素材信息展示 -->
      <el-descriptions v-if="materialInfo" :column="2" border class="material-info modern-descriptions">
        <el-descriptions-item label="任务标题">{{ materialInfo.title }}</el-descriptions-item>
        <el-descriptions-item label="主题">{{ materialInfo.theme }}</el-descriptions-item>
        <el-descriptions-item label="摘要" :span="2">{{ materialInfo.abstract }}</el-descriptions-item>
        <el-descriptions-item label="关键词" :span="2">{{ materialInfo.keywords }}</el-descriptions-item>
      </el-descriptions>

      <el-divider class="modern-divider" />

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
          class="modern-upload"
        >
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div class="upload-text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="upload-tip">
              仅支持.docx格式的Word文档
            </div>
          </template>
        </el-upload>

        <div class="button-group">
          <el-button type="primary" @click="handleUploadWord" :loading="uploading" :disabled="!wordFile" class="primary-button">
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
          class="modern-form"
        >
          <el-form-item label="任务标题" prop="title">
            <el-input v-model="taskForm.title" placeholder="请输入任务标题" class="modern-input" />
          </el-form-item>

          <el-form-item label="所属班级" prop="class_id">
            <el-select v-model="taskForm.class_id" placeholder="请选择班级" style="width: 100%" class="modern-select">
              <el-option
                v-for="classItem in classes"
                :key="classItem.id"
                :label="classItem.class_name"
                :value="classItem.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="任务类型" prop="type">
            <el-select v-model="taskForm.type" placeholder="请选择任务类型" style="width: 100%" class="modern-select">
              <el-option label="作业" value="task" />
              <el-option label="练习" value="practice" />
              <el-option label="考试" value="exam" />
              <el-option label="小测" value="quiz" />
            </el-select>
          </el-form-item>

          <el-form-item label="周次" prop="week">
            <el-input-number v-model="taskForm.week" :min="1" :max="20" class="modern-input-number" />
          </el-form-item>

          <el-form-item label="排序" prop="order">
            <el-input-number v-model="taskForm.order" :min="0" :max="999" class="modern-input-number" />
          </el-form-item>

          <!-- 考试特有字段 -->
          <template v-if="taskForm.type === 'exam'">
            <el-form-item label="考试日期" prop="exam_date">
              <el-date-picker
                v-model="taskForm.exam_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                class="modern-date-picker"
              />
            </el-form-item>

            <el-form-item label="开始时间" prop="start_time">
              <el-time-picker
                v-model="taskForm.start_time"
                placeholder="选择时间"
                style="width: 100%"
                class="modern-time-picker"
              />
            </el-form-item>

            <el-form-item label="结束时间" prop="end_time">
              <el-time-picker
                v-model="taskForm.end_time"
                placeholder="选择时间"
                style="width: 100%"
                class="modern-time-picker"
              />
            </el-form-item>

            <el-form-item label="时长(分钟)" prop="duration">
              <el-input-number v-model="taskForm.duration" :min="1" :max="300" class="modern-input-number" />
            </el-form-item>
          </template>

          <el-form-item label="逾期规则">
            <el-select v-model="taskForm.overdue_rule_id" placeholder="请选择逾期规则" clearable style="width: 100%" class="modern-select">
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
        <el-divider class="modern-divider" />
        <h4>题目预览</h4>
        <div v-if="questionData && questionData.length > 0" class="question-preview">
          <el-collapse class="modern-collapse">
            <el-collapse-item
              v-for="(page, pageIdx) in questionData"
              :key="pageIdx"
              :title="`第${pageIdx + 1}页 (${page.page_content?.length || 0}道大题)`"
              class="modern-collapse-item"
            >
              <div v-for="(question, qIdx) in page.page_content" :key="qIdx" class="question-item">
                <p><strong>大题{{ qIdx + 1 }}:</strong> {{ question.question_type }}</p>
                <p>{{ question.question_text }}</p>
                <p class="sub-count">包含 {{ question.sub_questions?.length || 0 }} 道小题</p>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
        <el-empty v-else description="暂无题目数据" class="modern-empty" />

        <div class="button-group">
          <el-button @click="currentStep = 1" class="secondary-button">上一步</el-button>
          <el-button type="primary" @click="handleSaveTask" :loading="saving" class="primary-button">
            保存任务
          </el-button>
        </div>
      </div>
    </div>
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
  router.push('/teacher/dashboard')
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
.week-task-import-container {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

.week-task-import-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.week-task-import-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
}

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

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

.card-header h2 {
  margin: 0;
  color: #1A202C;
  font-size: 18px;
  font-weight: 600;
}

/* 描述列表样式 */
.modern-descriptions {
  margin-bottom: 24px;
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 10px rgba(140, 124, 240, 0.1) !important;
}

.modern-descriptions :deep(.el-descriptions__label) {
  background: #F0F2F5 !important;
  color: #4A5568 !important;
  font-weight: 500 !important;
  padding: 12px 16px !important;
}

.modern-descriptions :deep(.el-descriptions__content) {
  padding: 12px 16px !important;
  color: #4A5568 !important;
}

/* 分隔线样式 */
.modern-divider {
  margin: 24px 0 !important;
  background: #F0F2F5 !important;
}

/* 步骤内容样式 */
.step-content {
  padding: 20px 0;
}

.step-content h3 {
  margin-bottom: 16px;
  color: #1A202C;
  font-size: 16px;
  font-weight: 600;
}

.step-content h4 {
  margin-bottom: 16px;
  color: #4A5568;
  font-size: 14px;
  font-weight: 600;
}

.tip {
  color: #8B9BB4;
  margin-bottom: 24px;
  font-size: 14px;
}

/* 上传组件样式 */
.modern-upload {
  margin: 24px 0;
  border-radius: 12px !important;
  border: 2px dashed #F0F2F5 !important;
  padding: 40px 20px !important;
  transition: all 0.3s ease !important;
}

.modern-upload:hover {
  border-color: #8C7CF0 !important;
  background: rgba(140, 124, 240, 0.05) !important;
}

.upload-icon {
  font-size: 48px !important;
  color: #8C7CF0 !important;
  margin-bottom: 16px !important;
}

.upload-text {
  color: #8B9BB4 !important;
  font-size: 16px !important;
}

.upload-text em {
  color: #8C7CF0 !important;
  font-style: normal !important;
  cursor: pointer !important;
}

.upload-tip {
  font-size: 12px !important;
  color: #8B9BB4 !important;
  margin-top: 12px !important;
}

/* 表单样式 */
.modern-form {
  margin-top: 20px;
}

.modern-form .el-form-item {
  margin-bottom: 20px;
}

.modern-form .el-form-item__label {
  color: #4A5568;
  font-weight: 500;
  font-size: 14px;
}

/* 输入框样式 */
.modern-input {
  border-radius: 12px !important;
  border: 2px solid #F0F2F5 !important;
  padding: 12px 16px !important;
  font-size: 14px !important;
  transition: all 0.3s ease !important;
}

.modern-input:hover {
  border-color: #8C7CF0 !important;
}

.modern-input:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

/* 选择器样式 */
.modern-select {
  border-radius: 12px !important;
  border: 2px solid #F0F2F5 !important;
  padding: 12px 16px !important;
  font-size: 14px !important;
  transition: all 0.3s ease !important;
}

.modern-select:hover {
  border-color: #8C7CF0 !important;
}

.modern-select:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

/* 输入数字样式 */
.modern-input-number {
  border-radius: 12px !important;
  border: 2px solid #F0F2F5 !important;
  transition: all 0.3s ease !important;
}

.modern-input-number:hover {
  border-color: #8C7CF0 !important;
}

.modern-input-number:focus-within {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

/* 日期选择器样式 */
.modern-date-picker {
  border-radius: 12px !important;
  border: 2px solid #F0F2F5 !important;
  padding: 12px 16px !important;
  font-size: 14px !important;
  transition: all 0.3s ease !important;
}

.modern-date-picker:hover {
  border-color: #8C7CF0 !important;
}

.modern-date-picker:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

/* 时间选择器样式 */
.modern-time-picker {
  border-radius: 12px !important;
  border: 2px solid #F0F2F5 !important;
  padding: 12px 16px !important;
  font-size: 14px !important;
  transition: all 0.3s ease !important;
}

.modern-time-picker:hover {
  border-color: #8C7CF0 !important;
}

.modern-time-picker:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

/* 折叠面板样式 */
.modern-collapse {
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 10px rgba(140, 124, 240, 0.1) !important;
}

.modern-collapse-item {
  border-radius: 12px !important;
  overflow: hidden !important;
}

.modern-collapse :deep(.el-collapse-item__header) {
  background: #F5F7FA !important;
  color: #4A5568 !important;
  font-weight: 500 !important;
  padding: 16px 20px !important;
  border-bottom: 1px solid #F0F2F5 !important;
  transition: all 0.3s ease !important;
}

.modern-collapse :deep(.el-collapse-item__header:hover) {
  background: #E8E4FF !important;
  color: #8C7CF0 !important;
}

.modern-collapse :deep(.el-collapse-item__content) {
  padding: 20px !important;
  background: #FFFFFF !important;
}

/* 题目预览样式 */
.question-preview {
  margin-top: 20px;
}

.question-item {
  padding: 16px;
  background-color: #F5F7FA;
  border-radius: 12px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(140, 124, 240, 0.05);
}

.question-item p {
  margin: 8px 0;
  color: #4A5568;
  line-height: 1.6;
}

.sub-count {
  color: #8B9BB4;
  font-size: 12px;
  margin-top: 12px;
}

/* 按钮样式 */
.primary-button {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 12px !important;
  padding: 12px 24px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3) !important;
  transition: all 0.3s ease !important;
}

.primary-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.4) !important;
}

.secondary-button {
  background: #FFFFFF !important;
  border: 2px solid #8C7CF0 !important;
  color: #8C7CF0 !important;
  border-radius: 12px !important;
  padding: 12px 24px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.secondary-button:hover {
  background: #E8E4FF !important;
}

/* 按钮组样式 */
.button-group {
  margin-top: 32px;
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #F0F2F5;
}

/* 空状态样式 */
.modern-empty :deep(.el-empty__description) {
  color: #8B9BB4 !important;
  font-size: 14px !important;
}

/* 加载动画样式 */
:deep(.el-loading-spinner) {
  font-size: 16px !important;
  color: #8C7CF0 !important;
}

:deep(.el-loading-spinner .path) {
  stroke: #8C7CF0 !important;
}

/* 拖拽上传样式 */
:deep(.el-upload-dragger) {
  border-radius: 12px !important;
  border: 2px dashed #F0F2F5 !important;
  padding: 40px 20px !important;
  transition: all 0.3s ease !important;
}

:deep(.el-upload-dragger:hover) {
  border-color: #8C7CF0 !important;
  background: rgba(140, 124, 240, 0.05) !important;
}
</style>
