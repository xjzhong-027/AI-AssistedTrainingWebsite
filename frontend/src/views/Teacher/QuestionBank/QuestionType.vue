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
        <el-card class="type-card batch-card" shadow="hover" @click="goBatchImport">
          <span class="type-label">批量导入选择题</span>
          <p class="type-desc">按格式批量导入多道选择题</p>
        </el-card>
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
        <el-card class="type-card" shadow="hover" @click="goEdit('fill-blank')">
          <span class="type-label">填空题</span>
          <p class="type-desc">输入文本后双击单词生成填空</p>
        </el-card>
        <el-card class="type-card" shadow="hover" @click="goEdit('comprehension')">
          <span class="type-label">主观题</span>
          <p class="type-desc">简答题、理解题、总结题（主旨题）</p>
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

const goBatchImport = () => {
  router.push({
    name: 'BatchImport',
    params: { materialId: route.params.materialId }
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
