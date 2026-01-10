<template>
  <div class="unit-edit">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>编辑任务</span>
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
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择任务类型" disabled>
            <el-option label="考试" value="exam" />
            <el-option label="练习" value="practice" />
          </el-select>
          <div class="form-tip">任务类型创建后不可修改</div>
        </el-form-item>

        <el-form-item label="任务标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入任务标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="所属班级" prop="class_id">
          <el-select v-model="form.class_id" placeholder="请选择班级" clearable>
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
          />
          <div class="form-tip">数字越小越靠前</div>
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
}>({
  type: 'exam',
  title: '',
  class_id: undefined,
  order: 0
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
          order: form.order
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
  padding: 20px;
  background-color: #F9F8F3;
  min-height: 100vh;
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

