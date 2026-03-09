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
            <span class="label">{{ canModifyAnyPage ? '本次得分' : '本次得分（提交后不可修改答案）' }}</span>
            <div class="total-score-actions">
              <span class="total-score">{{ result.score != null ? result.score : 0 }} 分</span>
              <el-button v-if="canModifyAnyPage" type="primary" size="small" @click="goModify">修改答案</el-button>
            </div>
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
              <el-table-column v-if="hasAnyAiFeedback" label="AI反馈" width="100" align="center">
                <template #default="{ row }">
                  <span v-if="row.ai_feedback" class="has-feedback">有</span>
                  <span v-else>—</span>
                </template>
              </el-table-column>
            </el-table>
            <!-- AI反馈详情（有反馈的题目展示） -->
            <div v-for="(ans, aIdx) in (pageRecord.answers || [])" :key="aIdx" v-show="ans.ai_feedback" class="ai-feedback-block">
              <div class="ai-feedback-question">第 {{ aIdx + 1 }} 题 · {{ ans.sub_question_text || '题目' }}</div>
              <ScoringFeedbackDisplay v-if="ans.ai_feedback" :feedback="ans.ai_feedback" />
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getExamResult } from '@/api/exam'
import AIWindow from '@/components/common/AIWindow/index.vue'
import ScoringFeedbackDisplay from '@/components/common/ScoringFeedbackDisplay.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const result = ref<any>(null)

// 是否有任意页面允许修改答案
const canModifyAnyPage = computed(() => {
  const records = result.value?.page_records || []
  return records.some((p: any) => p.can_modify)
})

// 是否有任意答案包含AI反馈
const hasAnyAiFeedback = computed(() => {
  const records = result.value?.page_records || []
  return records.some((p: any) => (p.answers || []).some((a: any) => a.ai_feedback))
})

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

// 查看页面详情（跳转到答题页指定页面查看）
const viewPageDetail = (pageRecord: any) => {
  const practiceId = Number(route.params.id)
  if (practiceId && pageRecord.page_order !== undefined) {
    router.push({
      name: 'PracticeTake',
      params: { id: practiceId },
      query: { page: String(pageRecord.page_order + 1), viewMode: 'result' }
    })
  } else {
    ElMessage.warning('无法查看页面详情')
  }
}

// 返回
const goBack = () => {
  router.push('/practice/list')
}

// 修改答案（跳转到 Take 页面，带 mode=modify）
const goModify = () => {
  const practiceId = Number(route.params.id)
  if (practiceId) {
    router.push({ path: `/practice/${practiceId}/take`, query: { mode: 'modify' } })
  }
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
  padding: 24px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

/* 卡片样式 - Modern Soft-Neo UI */
:deep(.el-card) {
  background-color: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.5s ease-out;
  border: none;
  margin-bottom: 24px;
}

:deep(.el-card)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  z-index: 1;
}

:deep(.el-card__body) {
  padding: 32px;
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
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #F0F2F5;
}

.card-header h2 {
  margin: 0;
  color: #1A202C;
  font-size: 20px;
  font-weight: 600;
}

.result-content {
  margin-top: 24px;
}

.summary-card {
  margin-bottom: 24px;
}

.summary-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.summary-item .label {
  font-weight: 600;
  color: #8B9BB4;
  min-width: 80px;
  font-size: 13px;
}

.summary-item .value {
  color: #4A5568;
  font-size: 14px;
  flex: 1;
}

.summary-item .value.score {
  font-size: 32px;
  font-weight: 700;
  color: #8C7CF0;
  text-shadow: 0 2px 4px rgba(140, 124, 240, 0.2);
}

.score-summary-card .total-score-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  padding: 16px;
  background: #F8F9FA;
  border-radius: 12px;
}

.score-summary-card .total-score-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.score-summary-card .total-score {
  font-weight: 700;
  font-size: 28px;
  color: #8C7CF0;
  text-shadow: 0 2px 4px rgba(140, 124, 240, 0.2);
}

.has-feedback {
  color: #8C7CF0;
  font-weight: 600;
}

.ai-feedback-block {
  margin-top: 16px;
  padding: 16px;
  background: #E8E4FF;
  border-radius: 12px;
  border: 1px solid #C6B9FF;
  box-shadow: 0 2px 10px rgba(140, 124, 240, 0.1);
}

.ai-feedback-question {
  font-weight: 600;
  color: #8C7CF0;
  margin-bottom: 12px;
  font-size: 14px;
}

.pages-card,
.answers-card {
  margin-top: 24px;
}

.page-answers-block {
  margin-bottom: 28px;
}

.page-answers-block:last-child {
  margin-bottom: 0;
}

.page-title {
  font-weight: 600;
  color: #8C7CF0;
  margin-bottom: 16px;
  font-size: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #E8E4FF;
}

.answers-table {
  margin-bottom: 0;
  border-radius: 12px;
  overflow: hidden;
}

.score-ok {
  color: #A8D5BA;
  font-weight: 600;
}

.score-zero {
  color: #8B9BB4;
}

.card-header-title {
  font-weight: 600;
  font-size: 16px;
  color: #1A202C;
}

.score-highlight {
  font-weight: 700;
  color: #8C7CF0;
  font-size: 16px;
}

/* 表格样式优化 - Modern Soft-Neo UI */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #F0F2F5;
}

:deep(.el-table thead) {
  background: linear-gradient(135deg, #FAFBFC, #F0F2F5);
}

:deep(.el-table thead th) {
  background: transparent;
  color: #4A5568;
  font-weight: 600;
  font-size: 13px;
  padding: 12px 8px;
  border-bottom: 1px solid #F0F2F5;
}

:deep(.el-table tbody tr) {
  transition: all 0.3s ease;
}

:deep(.el-table tbody tr:hover) {
  background-color: rgba(140, 124, 240, 0.05);
}

:deep(.el-table td) {
  color: #4A5568;
  font-size: 13px;
  padding: 12px 8px;
  border-bottom: 1px solid #F0F2F5;
}

/* 按钮样式 - Modern Soft-Neo UI */
:deep(.el-button) {
  border-radius: 10px;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 13px;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  border: none;
  color: white;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #7A6BD0, #B5A8EE);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
}

:deep(.el-button--default) {
  background: #FFFFFF;
  border: 1px solid #F0F2F5;
  color: #4A5568;
}

:deep(.el-button--default:hover) {
  background: #E8E4FF;
  border-color: #C6B9FF;
  color: #8C7CF0;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.2);
}

.empty-state {
  padding: 60px;
  text-align: center;
}

:deep(.el-empty__description) {
  color: #8B9BB4;
  font-size: 14px;
}

/* 标签样式 - Modern Soft-Neo UI */
:deep(.el-tag) {
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
}

:deep(.el-tag--success) {
  background: #E8F5E9;
  border-color: #A8D5BA;
  color: #4A7C59;
}

:deep(.el-tag--warning) {
  background: #FFF8E1;
  border-color: #FFE082;
  color: #8B6914;
}

:deep(.el-tag--info) {
  background: #E8E4FF;
  border-color: #C6B9FF;
  color: #8C7CF0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .practice-result-page {
    padding: 16px;
  }
  
  :deep(.el-card__body) {
    padding: 20px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .summary-info {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .score-summary-card .total-score-row {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .total-score-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>



