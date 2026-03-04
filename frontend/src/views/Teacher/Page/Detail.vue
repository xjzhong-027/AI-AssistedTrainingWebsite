<template>
  <div class="page-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>页面详情</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <div v-if="page" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="页面ID">{{ page.id }}</el-descriptions-item>
          <el-descriptions-item label="页面标题">{{ page.text }}</el-descriptions-item>
          <el-descriptions-item label="序号">{{ page.order }}</el-descriptions-item>
          <el-descriptions-item label="限时（秒）">{{ page.limited_time ?? '不限' }}</el-descriptions-item>
          <el-descriptions-item label="所属任务">{{ page.unit_name }}</el-descriptions-item>
          <el-descriptions-item label="允许修改答案">
            <el-tag :type="page.can_modify ? 'success' : 'info'">{{ page.can_modify ? '是' : '否' }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="page.main_questions && page.main_questions.length > 0" style="margin-top: 24px">
          <el-divider>题目列表</el-divider>
          <el-table :data="page.main_questions" stripe>
            <el-table-column prop="id" label="题目ID" width="100" />
            <el-table-column prop="question_type" label="题型" width="120">
              <template #default="{ row }">
                {{ getQuestionTypeText(row.question_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="question_text" label="题干" min-width="200" show-overflow-tooltip />
            <el-table-column label="小题数" width="100" align="center">
              <template #default="{ row }">
                {{ row.sub_questions?.length ?? 0 }}
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else style="margin-top: 24px">
          <el-empty description="该页面暂无题目" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPageById } from '@/api/content'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const page = ref<any>(null)

const getQuestionTypeText = (type: string) => {
  const map: Record<string, string> = {
    choice: '选择题',
    matching: '连线题',
    correction: '改错题',
    comprehension: '主观题'
  }
  return map[type || ''] || type || '—'
}

const loadPage = async () => {
  const pageId = Number(route.params.id)
  if (!pageId) {
    ElMessage.error('页面ID无效')
    router.push('/teacher/exam-bank')
    return
  }
  loading.value = true
  try {
    page.value = await getPageById(pageId)
  } catch (e: any) {
    ElMessage.error(e?.message || '加载失败')
    router.push('/teacher/exam-bank')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  const unitId = page.value?.unit_id
  if (unitId) {
    router.push({ name: 'UnitDetail', params: { id: unitId } })
  } else {
    router.push('/teacher/exam-bank')
  }
}

onMounted(() => {
  loadPage()
})
</script>

<style scoped>
.page-detail {
  padding: 20px;
  background-color: #F9F8F3;
  min-height: 100vh;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.detail-content {
  padding: 20px 0;
}
</style>
