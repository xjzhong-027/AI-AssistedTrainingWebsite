<template>
  <div class="create-paper-page">
    <div class="create-paper-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7,10 12,15 17,10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </div>
          <h2>组卷</h2>
        </div>
        <el-button @click="goBack" class="secondary-button">返回</el-button>
      </div>

      <div v-if="material" class="material-info">
        <el-descriptions :column="2" border class="modern-descriptions">
          <el-descriptions-item label="媒体素材ID">{{ material.id }}</el-descriptions-item>
          <el-descriptions-item label="标题">{{ material.title }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="140px"
        label-position="right"
        class="modern-form"
      >
        <el-form-item label="选择任务包" prop="unit_id">
          <el-select
            v-model="form.unit_id"
            placeholder="请选择任务包或创建新任务包"
            filterable
            style="width: 100%"
            class="modern-select"
          >
            <el-option
              v-for="unit in units"
              :key="unit.id"
              :label="`${unit.title || unit.name || unit.unit_name} (${unit.type === 'exam' ? '考试' : '练习'})`"
              :value="unit.id"
            />
          </el-select>
          <div class="form-tip">
            <el-button link type="primary" @click="showCreateUnitDialog = true" class="link-button">创建新任务包</el-button>
          </div>
        </el-form-item>

        <el-form-item label="页面标题" prop="text">
          <el-input v-model="form.text" placeholder="请输入页面标题" maxlength="200" show-word-limit class="modern-input" />
        </el-form-item>

        <el-form-item label="页面顺序" prop="order">
          <el-input-number
            v-model="form.order"
            :min="1"
            :max="999"
            placeholder="请输入页面顺序"
            style="width: 100%"
            class="modern-input-number"
          />
          <div class="form-tip">数字越小越靠前</div>
        </el-form-item>

        <el-form-item label="限时（分钟）" prop="limited_time">
          <el-input-number
            v-model="form.limited_time"
            :min="0"
            :max="600"
            placeholder="请输入限时（0表示不限时）"
            style="width: 100%"
            class="modern-input-number"
          />
        </el-form-item>

        <el-form-item label="允许修改答案">
          <el-switch v-model="form.can_modify" class="modern-switch" />
        </el-form-item>

        <el-divider>选择题目</el-divider>

        <div v-if="questionsLoading" style="text-align: center; padding: 20px">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span style="margin-left: 10px">加载题目中...</span>
        </div>

        <div v-else-if="questions.length === 0" style="text-align: center; padding: 20px; color: #909399">
          该媒体素材暂无题目
        </div>

        <div v-else class="questions-list">
          <el-checkbox-group v-model="selectedQuestionIds">
            <el-card
              v-for="question in questions"
              :key="question.id"
              class="question-card"
              :class="{ selected: selectedQuestionIds.includes(question.id) }"
            >
              <template #header>
                <div class="question-header">
                  <el-checkbox :label="question.id" />
                  <span class="question-type">{{ getQuestionTypeText(question.question_type) }}</span>
                  <span class="question-id">题目ID: {{ question.id }}</span>
                </div>
              </template>
              <div class="question-content">
                <div class="question-text" v-html="question.question_text"></div>
                <div v-if="question.sub_questions && question.sub_questions.length > 0" class="sub-questions">
                  <div class="sub-questions-title">包含 {{ question.sub_questions.length }} 道小题</div>
                </div>
              </div>
            </el-card>
          </el-checkbox-group>
        </div>

        <el-form-item class="form-actions">
          <el-button type="primary" @click="handleSubmit" :loading="submitting" class="primary-button">创建页面</el-button>
          <el-button @click="goBack" class="secondary-button">取消</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 创建任务包对话框 -->
    <el-dialog
      v-model="showCreateUnitDialog"
      title="创建新任务包"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="unitForm"
        :rules="unitRules"
        ref="unitFormRef"
        label-width="120px"
      >
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="unitForm.type" placeholder="请选择任务类型" style="width: 100%">
            <el-option label="考试" value="exam" />
            <el-option label="练习" value="practice" />
          </el-select>
        </el-form-item>

        <el-form-item label="任务标题" prop="title">
          <el-input v-model="unitForm.title" placeholder="请输入任务标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="所属班级" prop="class_id">
          <el-select v-model="unitForm.class_id" placeholder="请选择班级" clearable style="width: 100%">
            <el-option
              v-for="classItem in classes"
              :key="classItem.id"
              :label="classItem.class_name"
              :value="classItem.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="排序" prop="order">
          <el-input-number
            v-model="unitForm.order"
            :min="0"
            :max="999"
            placeholder="请输入排序值"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateUnitDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateUnit" :loading="creatingUnit">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { getMediaMaterialById, getMaterialQuestions, createPaperPage, getAllUnits, createUnit } from '@/api/content'
import { getAllClasses } from '@/api/user'
import { useUserStore } from '@/stores/user'
import type { MediaMaterial } from '@/api/content'
import type { Class } from '@/api/user'
import type { Unit } from '@/api/content'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const questionsLoading = ref(false)
const submitting = ref(false)
const creatingUnit = ref(false)
const formRef = ref<FormInstance>()
const unitFormRef = ref<FormInstance>()

const material = ref<MediaMaterial | null>(null)
const questions = ref<any[]>([])
const units = ref<Unit[]>([])
const classes = ref<Class[]>([])
const selectedQuestionIds = ref<number[]>([])
const showCreateUnitDialog = ref(false)

const form = reactive({
  unit_id: undefined as number | undefined,
  text: '',
  order: 1,
  limited_time: 0,
  can_modify: true
})

const unitForm = reactive({
  type: 'exam' as 'exam' | 'practice',
  title: '',
  class_id: undefined as number | undefined,
  order: 0
})

const rules: FormRules = {
  unit_id: [{ required: true, message: '请选择任务包', trigger: 'change' }],
  text: [{ required: true, message: '请输入页面标题', trigger: 'blur' }],
  order: [{ required: true, message: '请输入页面顺序', trigger: 'blur' }]
}

const unitRules: FormRules = {
  type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  class_id: [{ required: true, message: '请选择所属班级', trigger: 'change' }]
}

// 获取题目类型文本
const getQuestionTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    choice: '选择题',
    matching: '连线题',
    correction: '改错题',
    comprehension: '主观题',
    text: '纯文本',
    blank: '填空题'
  }
  return typeMap[type] || type
}

// 加载媒体素材信息
const loadMaterial = async () => {
  const materialId = Number(route.params.materialId)
  if (!materialId) {
    ElMessage.error('媒体素材ID无效')
    router.push('/teacher/question-bank')
    return
  }

  loading.value = true
  try {
    material.value = await getMediaMaterialById(materialId)
  } catch (error: any) {
    console.error('加载媒体素材失败', error)
    ElMessage.error(error.message || '加载媒体素材失败')
  } finally {
    loading.value = false
  }
}

// 加载题目列表
const loadQuestions = async () => {
  const materialId = Number(route.params.materialId)
  if (!materialId) return

  questionsLoading.value = true
  try {
    questions.value = await getMaterialQuestions(materialId)
  } catch (error: any) {
    console.error('加载题目列表失败', error)
    ElMessage.error(error.message || '加载题目列表失败')
  } finally {
    questionsLoading.value = false
  }
}

// 加载任务包列表
const loadUnits = async () => {
  try {
    units.value = await getAllUnits()
  } catch (error) {
    console.error('加载任务包列表失败', error)
  }
}

// 加载班级列表
const loadClasses = async () => {
  try {
    const teacherId = userStore.userInfo?.id
    classes.value = await getAllClasses(teacherId)
  } catch (error) {
    console.error('加载班级列表失败', error)
  }
}

// 创建任务包
const handleCreateUnit = async () => {
  if (!unitFormRef.value) return

  await unitFormRef.value.validate(async (valid) => {
    if (valid) {
      creatingUnit.value = true
      try {
        const newUnit = await createUnit({
          class_id: unitForm.class_id!,
          title: unitForm.title,
          type: unitForm.type,
          order: unitForm.order
        })
        ElMessage.success('任务包创建成功')
        form.unit_id = newUnit.id
        showCreateUnitDialog.value = false
        // 重新加载任务包列表
        await loadUnits()
        // 重置表单
        unitForm.type = 'exam'
        unitForm.title = ''
        unitForm.class_id = undefined
        unitForm.order = 0
      } catch (error: any) {
        console.error('创建任务包失败', error)
        ElMessage.error(error.message || '创建任务包失败')
      } finally {
        creatingUnit.value = false
      }
    }
  })
}

// 提交创建页面
const handleSubmit = async () => {
  if (!formRef.value) return

  if (selectedQuestionIds.value.length === 0) {
    ElMessage.warning('请至少选择一道题目')
    return
  }

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await createPaperPage({
          unit_id: form.unit_id!,
          text: form.text,
          order: form.order,
          limited_time: form.limited_time,
          can_modify: form.can_modify,
          main_question_ids: selectedQuestionIds.value
        })
        ElMessage.success('页面创建成功')
        router.push({
          name: 'UnitDetail',
          params: { id: form.unit_id!.toString() }
        })
      } catch (error: any) {
        console.error('创建页面失败', error)
        ElMessage.error(error.message || '创建页面失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const goBack = () => {
  router.push('/teacher/question-bank')
}

onMounted(async () => {
  loadMaterial()
  loadQuestions()
  await loadUnits()
  loadClasses()
  // 从任务包详情「添加页面」进入时，预选当前任务包
  const unitIdFromQuery = route.query.unit_id
  if (unitIdFromQuery) {
    const id = Number(unitIdFromQuery)
    if (id && units.value.some((u) => u.id === id)) {
      form.unit_id = id
    }
  }
})
</script>

<style scoped>
.create-paper-page {
  padding: 20px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

/* 卡片样式 */
.create-paper-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: none;
}

.create-paper-card::before {
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

.link-button {
  color: #8C7CF0 !important;
  font-weight: 500 !important;
}

.link-button:hover {
  color: #6A5AE0 !important;
}

/* 表单样式 */
.modern-form {
  width: 100%;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 30px;
  padding-top: 16px;
  border-top: 1px solid #F0F2F5;
  justify-content: flex-end;
}

/* 输入框样式 */
.modern-input,
.modern-select {
  border-radius: 12px !important;
  border: 1px solid #E2E8F0 !important;
  transition: all 0.3s ease !important;
}

.modern-input:focus,
.modern-select:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

.modern-input-number {
  border-radius: 12px !important;
  border: 1px solid #E2E8F0 !important;
}

.modern-switch {
  --el-switch-on-color: #8C7CF0 !important;
  --el-switch-off-color: #E2E8F0 !important;
}

/* 描述信息样式 */
.modern-descriptions {
  border-radius: 12px !important;
  overflow: hidden !important;
  margin-bottom: 24px !important;
}

.modern-descriptions th {
  background: #F0F2F5 !important;
  color: #4A5568 !important;
  font-weight: 600 !important;
}

.modern-descriptions td {
  color: #4A5568 !important;
}

/* 提示信息样式 */
.form-tip {
  font-size: 12px;
  color: #718096;
  margin-top: 4px;
  padding-left: 8px;
  border-left: 3px solid #C6B9FF;
}

/* 题目列表样式 */
.questions-list {
  max-height: 600px;
  overflow-y: auto;
  padding: 20px;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  background-color: #F8F5FF;
  margin: 20px 0;
  width: 100%;
}

.question-card {
  margin-bottom: 16px;
  border-radius: 12px !important;
  border: 1px solid #E2E8F0 !important;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1) !important;
}

.question-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.2) !important;
  border-color: #8C7CF0 !important;
}

.question-card.selected {
  border-color: #8C7CF0 !important;
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.2) !important;
  background: #F0ECFF !important;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px !important;
  border-bottom: 1px solid #F0F2F5 !important;
}

.question-type {
  padding: 4px 12px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  color: #fff;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.question-id {
  color: #718096;
  font-size: 12px;
  margin-left: auto;
}

.question-content {
  padding: 16px;
}

.question-text {
  line-height: 1.6;
  color: #1A202C;
  margin-bottom: 12px;
}

.sub-questions {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #E2E8F0;
}

.sub-questions-title {
  font-size: 13px;
  color: #718096;
  font-weight: 500;
}

/* 动画效果 */
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
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

/* 对话框样式 */
:deep(.el-dialog) {
  border-radius: 16px !important;
  overflow: hidden !important;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF) !important;
  color: #FFFFFF !important;
  padding: 20px 24px !important;
  margin: 0 !important;
}

:deep(.el-dialog__title) {
  color: #FFFFFF !important;
  font-size: 16px !important;
  font-weight: 600 !important;
}

:deep(.el-dialog__body) {
  padding: 24px !important;
}
</style>


