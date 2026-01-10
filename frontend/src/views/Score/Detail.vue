<template>
  <div class="score-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>成绩详情</span>
          <div>
            <el-button
              v-if="userStore.isTeacher() && score && (!score.isGraded || score.manualScore === null)"
              type="warning"
              @click="gradeScore"
            >
              批改
            </el-button>
            <el-button @click="goBack">返回</el-button>
          </div>
        </div>
      </template>

      <div v-if="score" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="成绩ID">{{ score.id }}</el-descriptions-item>
          <el-descriptions-item label="考试记录ID">{{ score.examRecordId }}</el-descriptions-item>
          <el-descriptions-item label="总分">
            <span style="font-size: 20px; font-weight: bold; color: #409eff">{{ score.totalScore }}</span>
            分
          </el-descriptions-item>
          <el-descriptions-item label="已评分">
            <el-tag :type="score.isGraded ? 'success' : 'warning'">
              {{ score.isGraded ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="自动评分（客观题）">{{ score.autoScore }} 分</el-descriptions-item>
          <el-descriptions-item label="手动评分（主观题）">
            {{ score.manualScore ?? '未评分' }} 分
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getScoreById } from '@/api/score'
import { useUserStore } from '@/stores/user'
import type { Score } from '@/types/score'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const score = ref<Score | null>(null)

const loadScore = async () => {
  const id = Number(route.params.id)
  if (!id) {
    router.push('/scores')
    return
  }

  loading.value = true
  try {
    score.value = await getScoreById(id)
  } catch (error) {
    console.error('加载成绩详情失败', error)
  } finally {
    loading.value = false
  }
}

const gradeScore = () => {
  if (score.value) {
    router.push(`/scores/grade/${score.value.examRecordId}`)
  }
}

const goBack = () => {
  router.push('/scores')
}

onMounted(() => {
  loadScore()
})
</script>

<style scoped>
.score-detail {
  padding: 20px;
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
