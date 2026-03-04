<template>
  <div class="unit-create">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>新建任务包</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="120px"
        label-position="right"
      >
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择任务类型" style="width: 100%">
            <el-option label="考试" value="exam" />
            <el-option label="练习" value="practice" />
          </el-select>
        </el-form-item>

        <el-form-item label="任务标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入任务标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="所属班级" prop="class_id">
          <el-select 
            v-model="form.class_id" 
            placeholder="请选择班级" 
            clearable 
            style="width: 100%"
            :loading="loading"
            :disabled="loading"
            filterable
          >
            <el-option
              v-for="classItem in classes"
              :key="classItem.id"
              :label="classItem.class_name"
              :value="classItem.id"
            />
            <el-option v-if="classes.length === 0 && !loading" label="暂无班级数据" value="" disabled />
          </el-select>
          <div v-if="classes.length === 0 && !loading" class="form-tip" style="color: #f56c6c; margin-top: 8px">
            ⚠️ 暂无班级数据，请联系管理员创建班级
          </div>
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

        <el-form-item label="开放周次" prop="week">
          <el-input-number
            v-model="form.week"
            :min="0"
            :max="20"
            placeholder="0 表示始终开放"
            style="width: 100%"
          />
          <div class="form-tip">0=始终开放；1-20=第N周起学生可见可做</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">创建</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createUnit } from '@/api/content'
import { getAllClasses } from '@/api/user'
import { useUserStore } from '@/stores/user'
import type { Class } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const classes = ref<Class[]>([])

const form = reactive({
  type: 'exam' as 'exam' | 'practice',
  title: '',
  class_id: undefined as number | undefined,
  order: 0,
  week: 0
})

const rules: FormRules = {
  type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  class_id: [{ required: true, message: '请选择所属班级', trigger: 'change' }],
  order: [
    { type: 'number', min: 0, max: 999, message: '排序值必须在 0 到 999 之间', trigger: 'blur' }
  ]
}

// 加载班级列表
const loadClasses = async () => {
  loading.value = true
  try {
    // 如果是教师，传递 teacherId；否则获取所有班级
    const teacherId = userStore.userInfo?.id
    const data = await getAllClasses(teacherId)
    classes.value = Array.isArray(data) ? data : []
    if (classes.value.length === 0) {
      ElMessage.warning('暂无班级数据，请先创建班级')
    }
  } catch (error: any) {
    console.error('加载班级列表失败', error)
    ElMessage.error(error.message || '加载班级列表失败')
    classes.value = []
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
        const unit = await createUnit({
          class_id: form.class_id!,
          title: form.title,
          type: form.type,
          order: form.order,
          week: form.week
        })
        ElMessage.success('任务包创建成功')
        router.push({
          name: 'UnitDetail',
          params: { id: unit.id.toString() }
        })
      } catch (error: any) {
        console.error('创建任务包失败', error)
        ElMessage.error(error.message || '创建任务包失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const goBack = () => {
  router.push('/teacher/exam-bank')
}

onMounted(() => {
  loadClasses()
})
</script>

<style scoped>
.unit-create {
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


