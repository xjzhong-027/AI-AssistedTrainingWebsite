<template>
  <div class="question-type-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>添加题目 - 选择题型</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>
      <p class="tip">请选择要添加的题目类型：</p>
      <div class="type-options">
        <el-card class="type-card" shadow="hover" @click="goEdit('choice')">
          <span class="type-label">选择题</span>
          <p class="type-desc">单选题、多选题等</p>
        </el-card>
        <el-card class="type-card" shadow="hover" @click="goEdit('matching')">
          <span class="type-label">连线题</span>
          <p class="type-desc">左右项配对</p>
        </el-card>
        <el-card class="type-card" shadow="hover" @click="goEdit('correction')">
          <span class="type-label">改错题</span>
          <p class="type-desc">改错、填空等</p>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const goBack = () => {
  router.push({ name: 'QuestionBank' })
}

const goEdit = (type: string) => {
  router.push({
    name: 'QuestionEditByType',
    params: { materialId: route.params.materialId, type }
  })
}
</script>

<style scoped>
.question-type-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tip {
  margin-bottom: 20px;
  color: #606266;
}

.type-options {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.type-card {
  flex: 1;
  min-width: 160px;
  cursor: pointer;
}

.type-card:hover {
  border-color: var(--el-color-primary);
}

.type-label {
  font-size: 18px;
  font-weight: 600;
}

.type-desc {
  margin: 8px 0 0;
  font-size: 12px;
  color: #909399;
}
</style>
