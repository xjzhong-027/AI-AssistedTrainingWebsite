<template>
  <div class="question-edit-by-type">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ typeLabel }} - 编辑</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>
      <div class="placeholder-content">
        <p>
          <strong>{{ typeLabel }}</strong> 编辑功能需后端提供题目创建/更新 API 后对接。
        </p>
        <p class="desc">
          当前可通过「周任务」导入 Word 文档解析题目，或在「组卷」时从媒体素材中选择已有题目。
        </p>
        <el-button type="primary" @click="goBack">返回题库</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const type = computed(() => (route.params.type as string) || 'choice')

const typeLabel = computed(() => {
  const map: Record<string, string> = {
    choice: '选择题',
    matching: '连线题',
    correction: '改错题'
  }
  return map[type.value] || type.value
})

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
