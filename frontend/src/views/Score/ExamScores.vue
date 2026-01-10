<template>
  <div class="exam-scores">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>考试成绩统计 - {{ exam?.title }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <div v-if="statistics" class="statistics-content">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="参考人数" :value="statistics.totalCount || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="平均分" :value="statistics.averageScore || 0" :precision="2" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="最高分" :value="statistics.maxScore || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="最低分" :value="statistics.minScore || 0" />
          </el-col>
        </el-row>

        <el-divider>成绩列表</el-divider>

        <el-table :data="scoreList" style="width: 100%" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="examRecordId" label="考试记录ID" width="120" />
          <el-table-column prop="totalScore" label="总分" width="100" />
          <el-table-column prop="autoScore" label="自动评分" width="100" />
          <el-table-column prop="manualScore" label="手动评分" width="100">
            <template #default="{ row }">
              {{ row.manualScore ?? '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="isGraded" label="已评分" width="100">
            <template #default="{ row }">
              <el-tag :type="row.isGraded ? 'success' : 'warning'">
                {{ row.isGraded ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="250">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewDetail(row.id)">查看详情</el-button>
              <el-button
                v-if="!row.isGraded || row.manualScore === null"
                link
                type="warning"
                @click="gradeScore(row.examRecordId)"
              >
                批改
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getExamById } from '@/api/exam'
import { getScoresByExamId, getScoreStatistics } from '@/api/score'
import type { Exam } from '@/types/exam'
import type { Score } from '@/types/score'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const exam = ref<Exam | null>(null)
const scoreList = ref<Score[]>([])
const statistics = ref<any>(null)

const loadData = async () => {
  const examId = Number(route.params.id)
  if (!examId) {
    router.push('/exams')
    return
  }

  loading.value = true
  try {
    exam.value = await getExamById(examId)
    scoreList.value = await getScoresByExamId(examId)
    statistics.value = await getScoreStatistics(examId)
  } catch (error) {
    console.error('加载数据失败', error)
  } finally {
    loading.value = false
  }
}

const viewDetail = (id: number) => {
  router.push(`/scores/${id}`)
}

const gradeScore = (examRecordId: number) => {
  router.push(`/scores/grade/${examRecordId}`)
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.exam-scores {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statistics-content {
  padding: 20px 0;
}
</style>
