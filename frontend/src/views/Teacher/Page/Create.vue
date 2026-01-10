<template>
  <div class="create-paper-page">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>组卷</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <div v-if="material" class="material-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="媒体素材ID">{{ material.id }}</el-descriptions-item>
          <el-descriptions-item label="标题">{{ material.title }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="120px"
        label-position="right"
        style="margin-top: 20px"
      >
        <el-form-item label="选择任务包" prop="unit_id">
          <el-select
            v-model="form.unit_id"
            placeholder="请选择任务包或创建新任务包"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="unit in units"
              :key="unit.id"
              :label="`${unit.title || unit.name || unit.unit_name} (${unit.type === 'exam' ? '考试' : '练习'})`"
              :value="unit.id"
            />
          </el-select>
          <div class="form-tip">
            <el-button link type="primary" @click="showCreateUnitDialog = true">创建新任务包</el-button>
          </div>
        </el-form-item>

        <el-form-item label="页面标题" prop="text">
          <el-input v-model="form.text" placeholder="请输入页面标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="页面顺序" prop="order">
          <el-input-number
            v-model="form.order"
            :min="1"
            :max="999"
            placeholder="请输入页面顺序"
            style="width: 100%"
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
          />
        </el-form-item>

        <el-form-item label="允许修改答案">
          <el-switch v-model="form.can_modify" />
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

        <el-form-item style="margin-top: 30px">
          <el-button type="primary" @click="handleSubmit" :loading="submitting">创建页面</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

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

onMounted(() => {
  loadMaterial()
  loadQuestions()
  loadUnits()
  loadClasses()
})
</script>

<style scoped>
.create-paper-page {
  padding: 20px;
  background-color: #F9F8F3;
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.material-info {
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.questions-list {
  max-height: 600px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #fff;
}

.question-card {
  margin-bottom: 15px;
  transition: all 0.3s ease;
}

.question-card.selected {
  border-color: #99B6B4;
  box-shadow: 0 2px 12px rgba(153, 182, 180, 0.2);
}

.question-header {
  display: flex;
  align-items: center;
  gap: 15px;
}

.question-type {
  padding: 4px 12px;
  background-color: #99B6B4;
  color: #fff;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.question-id {
  color: #909399;
  font-size: 12px;
  margin-left: auto;
}

.question-content {
  padding: 10px 0;
}

.question-text {
  line-height: 1.8;
  color: #303133;
}

.sub-questions {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #e4e7ed;
}

.sub-questions-title {
  font-size: 12px;
  color: #909399;
}
</style>


