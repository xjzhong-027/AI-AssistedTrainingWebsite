<template>
  <div class="unit-edit">
    <div class="unit-edit-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
          </div>
          <h2>编辑任务</h2>
        </div>
        <el-button @click="goBack" class="secondary-button">返回</el-button>
      </div>

      <el-form
        v-if="form"
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="140px"
        label-position="right"
        class="modern-form"
      >
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择任务类型" disabled class="modern-select">
            <el-option label="考试" value="exam" />
            <el-option label="练习" value="practice" />
          </el-select>
          <div class="form-tip">任务类型创建后不可修改</div>
        </el-form-item>

        <el-form-item label="任务标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入任务标题" maxlength="200" show-word-limit class="modern-input" />
        </el-form-item>

        <el-form-item label="所属班级" prop="class_id">
          <el-select v-model="form.class_id" placeholder="请选择班级" clearable class="modern-select">
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
            v-model="form.order"
            :min="0"
            :max="999"
            placeholder="请输入排序值"
            style="width: 100%"
            class="modern-input-number"
          />
          <div class="form-tip">数字越小越靠前</div>
        </el-form-item>

        <el-form-item label="开放周次" prop="week">
          <el-input-number
            v-model="form.week"
            :min="0"
            :max="20"
            placeholder="0 表示始终开放"
            style="width: 100%"
            class="modern-input-number"
          />
          <div class="form-tip">0=始终开放；1-20=第N周起学生可见可做</div>
        </el-form-item>

        <el-form-item class="form-actions">
          <el-button type="primary" @click="handleSubmit" :loading="submitting" class="primary-button">保存</el-button>
          <el-button @click="goBack" class="secondary-button">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getUnitById, updateUnit } from '@/api/content'
import type { Unit } from '@/api/content'
import { getAllClasses } from '@/api/user'
import type { Class } from '@/api/user'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const classes = ref<Class[]>([])

const form = reactive<{
  type: 'exam' | 'practice'
  title: string
  class_id?: number
  order?: number
  week?: number
}>({
  type: 'exam',
  title: '',
  class_id: undefined,
  order: 0,
  week: 0
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  order: [
    { type: 'number', min: 0, max: 999, message: '排序值必须在 0 到 999 之间', trigger: 'blur' }
  ]
}

// 加载单元数据
const loadUnit = async () => {
  const id = Number(route.params.id)
  if (!id) {
    ElMessage.error('任务ID无效')
    router.push('/teacher/exam-bank')
    return
  }

  loading.value = true
  try {
    const unitData = await getUnitById(id)
    // 兼容处理
    form.type = unitData.type || unitData.unit_type || 'exam'
    form.title = unitData.title || unitData.name || unitData.unit_name || ''
    form.class_id = unitData.class_id
    form.order = unitData.order || 0
    form.week = unitData.week ?? 0
  } catch (error: any) {
    console.error('加载任务失败', error)
    ElMessage.error(error.message || '加载任务失败')
  } finally {
    loading.value = false
  }
}

// 加载班级列表
const loadClasses = async () => {
  try {
    classes.value = await getAllClasses()
  } catch (error) {
    console.error('加载班级列表失败', error)
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
        await updateUnit(id, {
          title: form.title,
          class_id: form.class_id,
          order: form.order,
          week: form.week
        })
        ElMessage.success('更新成功')
        router.push(`/teacher/units/${id}`)
      } catch (error: any) {
        console.error('更新失败', error)
        ElMessage.error(error.message || '更新失败')
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
  loadUnit()
  loadClasses()
})
</script>

<style scoped>
.unit-edit {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

/* 卡片样式 */
.unit-edit-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: none;
}

.unit-edit-card::before {
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

/* 提示信息样式 */
.form-tip {
  font-size: 12px;
  color: #718096;
  margin-top: 4px;
  padding-left: 8px;
  border-left: 3px solid #C6B9FF;
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
</style>

