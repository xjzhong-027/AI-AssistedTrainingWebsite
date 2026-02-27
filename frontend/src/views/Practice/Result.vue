<template>
  <div class="practice-result-page">
    <el-card v-loading="loading">
      <div class="card-header">
        <h2>练习结果</h2>
        <el-button @click="goBack">返回</el-button>
      </div>

      <div v-if="result" class="result-content">
        <!-- 总体信息 -->
        <el-card class="summary-card">
          <div class="summary-info">
            <div class="summary-item">
              <span class="label">练习名称：</span>
              <span class="value">{{ result.unit_name }}</span>
            </div>
            <div class="summary-item">
              <span class="label">总分：</span>
              <span class="value score">{{ result.score || 0 }} 分</span>
            </div>
            <div class="summary-item">
              <span class="label">开始时间：</span>
              <span class="value">{{ formatDate(result.started_at) }}</span>
            </div>
            <div class="summary-item">
              <span class="label">提交时间：</span>
              <span class="value">{{ formatDate(result.finished_at) }}</span>
            </div>
            <div class="summary-item">
              <span class="label">状态：</span>
              <el-tag :type="result.submitted ? 'success' : 'warning'">
                {{ result.submitted ? '已提交' : '未提交' }}
              </el-tag>
            </div>
          </div>
        </el-card>

        <!-- 总分（提交后显示） -->
        <el-card v-if="result.submitted" class="score-summary-card">
          <div class="total-score-row">
            <span class="label">本次得分（提交后不可修改答案）</span>
            <span class="total-score">{{ result.score != null ? result.score : 0 }} 分</span>
          </div>
        </el-card>

        <!-- 各页面得分与答题详情 -->
        <el-card v-if="result.page_records && result.page_records.length > 0" class="pages-card">
          <template #header>
            <div class="card-header-title">各页面得分</div>
          </template>
          <el-table :data="result.page_records" border>
            <el-table-column prop="page_order" label="页面顺序" width="120" align="center" />
            <el-table-column prop="page_title" label="页面标题" />
            <el-table-column prop="page_score" label="得分" width="100" align="center">
              <template #default="{ row }">
                <span :class="{ 'score-highlight': row.is_graded }">
                  {{ row.is_graded ? (row.page_score ?? 0) : '待批改' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="is_graded" label="批改状态" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="row.is_graded ? 'success' : 'warning'">
                  {{ row.is_graded ? '已批改' : '待批改' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="submitted" label="提交状态" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="row.submitted ? 'success' : 'info'">
                  {{ row.submitted ? '已提交' : '未提交' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="viewPageDetail(row)">查看答题详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 各题得分与答案（已提交时展示，只读） -->
        <el-card v-if="result.submitted && result.page_records && result.page_records.length > 0" class="answers-card">
          <template #header>
            <div class="card-header-title">各题得分与答案（仅查看，不可修改）</div>
          </template>
          <div v-for="(pageRecord, pIdx) in result.page_records" :key="pageRecord.id" class="page-answers-block">
            <div class="page-title">第 {{ (pageRecord.page_order ?? pIdx) + 1 }} 页 · {{ pageRecord.page_title || '未命名' }}</div>
            <el-table :data="pageRecord.answers || []" border size="small" class="answers-table">
              <el-table-column label="题号" width="80" align="center">
                <template #default="{ row, $index }">{{ $index + 1 }}</template>
              </el-table-column>
              <el-table-column prop="sub_question_text" label="题目" min-width="200" show-overflow-tooltip />
              <el-table-column prop="text" label="你的答案" width="140" show-overflow-tooltip />
              <el-table-column prop="correct_answer" label="正确答案" width="140" show-overflow-tooltip />
              <el-table-column prop="score" label="得分" width="80" align="center">
                <template #default="{ row }">
                  <span :class="{ 'score-ok': row.score != null && Number(row.score) > 0, 'score-zero': row.score != null && Number(row.score) === 0 }">
                    {{ row.score != null ? row.score : '—' }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>

        <!-- 反馈信息 -->
        <el-card v-if="result.page_records && result.page_records.some((p: any) => p.feedback)" class="feedback-card">
          <template #header>
            <div class="card-header-title">教师反馈</div>
          </template>
          <div v-for="(pageRecord, index) in result.page_records" :key="index">
            <div v-if="pageRecord.feedback" class="feedback-item">
              <div class="feedback-page">第 {{ pageRecord.page_order + 1 }} 页</div>
              <div class="feedback-content">{{ pageRecord.feedback }}</div>
            </div>
          </div>
        </el-card>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <el-empty description="暂无结果数据"></el-empty>
      </div>
    </el-card>
    <AIWindow :show-grade-button="false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getExamResult } from '@/api/exam'
import AIWindow from '@/components/common/AIWindow/index.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const result = ref<any>(null)

// 格式化日期
const formatDate = (dateStr: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 查看页面详情
const viewPageDetail = (pageRecord: any) => {
  // 跳转到页面详情，显示题目和答案
  const practiceId = Number(route.params.id)
  if (practiceId && pageRecord.page_order !== undefined) {
    // 跳转到详情页面，传递practiceId和pageOrder
    router.push({
      name: 'PracticeDetail',
      params: { id: practiceId },
      query: { 
        page: pageRecord.page_order + 1,
        viewMode: 'result',
        pageRecordId: pageRecord.id
      }
    })
  } else {
    ElMessage.warning('无法查看页面详情')
  }
}

// 返回
const goBack = () => {
  router.push('/practice/list')
}

// 加载结果
const loadResult = async () => {
  const practiceId = Number(route.params.id)
  if (!practiceId) {
    ElMessage.error('练习ID无效')
    router.push('/practice/list')
    return
  }

  loading.value = true
  try {
    // 使用考试结果API（练习和考试使用相同的API）
    result.value = await getExamResult(practiceId)
  } catch (error: any) {
    console.error('加载结果失败', error)
    ElMessage.error(error.message || '加载结果失败')
    router.push('/practice/list')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadResult()
})
</script>

<style scoped>
.practice-result-page {
  padding: 20px;
  background-color: #F9F8F3;
  min-height: 100vh;
}

/* 卡片样式 - 符合UI设计规范 */
:deep(.el-card) {
  background-color: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.5s ease-out;
}

:deep(.el-card)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #99B6B4, #BACFCE, #D48982, #DFB199);
  z-index: 1;
}

:deep(.el-card__body) {
  padding: 30px;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h2 {
  margin: 0;
  color: #1A1A1A;
  font-size: 24px;
  font-weight: 500;
}

.result-content {
  margin-top: 20px;
}

.summary-card {
  margin-bottom: 20px;
}

.summary-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.summary-item {
  display: flex;
  align-items: center;
}

.summary-item .label {
  font-weight: 500;
  color: #606266;
  margin-right: 10px;
}

.summary-item .value {
  color: #1A1A1A;
}

.summary-item .value.score {
  font-size: 28px;
  font-weight: bold;
  color: #99B6B4;
}

.score-summary-card .total-score-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 18px;
}
.score-summary-card .total-score {
  font-weight: bold;
  font-size: 24px;
  color: #99B6B4;
}

.pages-card,
.feedback-card,
.answers-card {
  margin-top: 20px;
}

.page-answers-block {
  margin-bottom: 24px;
}
.page-answers-block:last-child {
  margin-bottom: 0;
}
.page-title {
  font-weight: 500;
  color: #99B6B4;
  margin-bottom: 12px;
  font-size: 16px;
}
.answers-table {
  margin-bottom: 0;
}
.score-ok {
  color: #67c23a;
  font-weight: 500;
}
.score-zero {
  color: #909399;
}

.card-header-title {
  font-weight: 500;
  font-size: 18px;
  color: #1A1A1A;
}

.score-highlight {
  font-weight: bold;
  color: #99B6B4;
  font-size: 16px;
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table thead) {
  background-color: rgba(186, 207, 206, 0.2);
}

:deep(.el-table tbody tr:hover) {
  background-color: rgba(186, 207, 206, 0.1);
}

:deep(.el-button) {
  border-radius: 6px;
  transition: all 0.3s ease;
}

:deep(.el-button--default) {
  background-color: #99B6B4;
  border-color: #99B6B4;
  color: #FFFFFF;
}

:deep(.el-button--default:hover) {
  background-color: #7A9E9C;
  border-color: #7A9E9C;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.feedback-item {
  margin-bottom: 20px;
  padding: 20px;
  background: #F9F8F3;
  border-radius: 12px;
  border: 1px solid rgba(186, 207, 206, 0.2);
}

.feedback-page {
  font-weight: 500;
  margin-bottom: 10px;
  color: #99B6B4;
  font-size: 16px;
}

.feedback-content {
  color: #606266;
  line-height: 1.8;
  font-size: 15px;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

/* 标签样式 */
:deep(.el-tag) {
  border-radius: 6px;
}
</style>



