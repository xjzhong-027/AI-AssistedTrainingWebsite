<template>
  <div class="practice-page">
    <!-- 练习统计卡片 -->
    <div class="statistics-card card">
      <!-- 返回首页按钮 -->
      <button class="back-button" @click="goToDashboard">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        返回首页
      </button>

      <div class="card-header">
        <h2 class="card-title">练习统计</h2>
        <span class="card-subtitle">本周学习概况</span>
      </div>
      <div class="statistics-grid">
        <div class="stat-item">
          <div class="stat-icon completed">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.completedCount }}</div>
            <div class="stat-label">本周完成</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon score">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.averageScore }}</div>
            <div class="stat-label">平均得分</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon time">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.studyTime }}</div>
            <div class="stat-label">学习时长</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 练习任务列表 -->
    <div class="tasks-card card">
      <div class="card-header">
        <h2 class="card-title">练习任务</h2>
        <span class="card-subtitle">当前可用练习</span>
      </div>
      <div class="filter-bar">
        <div class="filter-group">
          <label>排序：</label>
          <select v-model="sortOrder" class="filter-select">
            <option value="desc">最新创建</option>
            <option value="asc">最早创建</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      <div v-else-if="filteredPractices.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#8B9BB4" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
        <p>暂无练习任务</p>
      </div>
      <div v-else class="task-list">
        <div
          v-for="practice in paginatedPractices"
          :key="practice.id"
          class="task-item"
        >
          <div class="task-info">
            <h3 class="task-name">{{ practice.unit_name }}</h3>
            <div class="task-meta">
              <span class="task-type">{{ practice.unit_type === 'practice' ? '练习' : '考试' }}</span>
              <span class="task-id">ID: {{ practice.id }}</span>
            </div>
          </div>
          <div class="task-status">
            <span :class="['status-badge', getStatusClass(practice.status)]">
              {{ getStatusText(practice.status) }}
            </span>
          </div>
          <div class="task-action">
            <button 
              v-if="practice.status === 'completed'" 
              class="result-button"
              @click="viewPracticeResult(practice.id)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
              查看练习结果
            </button>
            <button 
              v-else 
              class="start-button"
              @click="handleStartPractice(practice.id)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              开始练习
            </button>
          </div>
        </div>
      </div>

      <div v-if="filteredPractices.length > 0" class="pagination">
        <button class="pagination-button" :disabled="currentPage === 1" @click="currentPage--">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"></polyline></svg>
          上一页
        </button>
        <div class="pagination-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</div>
        <button class="pagination-button" :disabled="currentPage === totalPages" @click="currentPage++">
          下一页
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
        </button>
      </div>
    </div>

    <!-- 练习历史记录 -->
    <div class="history-card card">
      <div class="card-header">
        <h2 class="card-title">练习历史</h2>
        <span class="card-subtitle">最近完成的练习</span>
      </div>
      <div v-if="history.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#8B9BB4" stroke-width="1.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        <p>暂无练习历史</p>
      </div>
      <div v-else class="history-list">
        <div v-for="item in history" :key="item.id" class="history-item">
          <div class="history-info">
            <h3 class="history-name">{{ item.name }}</h3>
            <p class="history-time">{{ formatDate(item.completedAt) }}</p>
          </div>
          <div class="history-score">
            <span class="score-value">{{ item.score }}</span>
            <span class="score-label">分</span>
          </div>
          <button class="detail-button" @click="viewHistoryDetail(item)">查看详情</button>
        </div>
      </div>
    </div>

    <AIWindow :show-grade-button="false" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAllPractices, startPractice as startPracticeAPI, getStudentPracticeRecords } from '@/api/practice'
import type { Unit, ExamRecord } from '@/api/practice'
import AIWindow from '@/components/common/AIWindow/index.vue'

const router = useRouter()

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const sortOrder = ref('desc')

const practiceList = ref<Unit[]>([])
const history = ref<Array<{ id: number; unitId: number; name: string; completedAt: string; score: number }>>([])
const statistics = ref({
  completedCount: 0,
  averageScore: 0,
  studyTime: '0h',
  trend: '0%'
})

const filteredPractices = computed(() => {
  const result = [...practiceList.value]
  result.sort((a, b) => {
    const idA = a.id || 0
    const idB = b.id || 0
    return sortOrder.value === 'desc' ? idB - idA : idA - idB
  })
  return result
})

const totalPages = computed(() => Math.ceil(filteredPractices.value.length / pageSize.value) || 1)

const paginatedPractices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredPractices.value.slice(start, start + pageSize.value)
})

const getStatusClass = (status: string) => {
  switch (status) {
    case 'pending': return 'pending'
    case 'in-progress': return 'in-progress'
    case 'completed': return 'completed'
    default: return 'pending'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending': return '未开始'
    case 'in-progress': return '进行中'
    case 'completed': return '已完成'
    default: return '未开始'
  }
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleStartPractice = async (unitId: number) => {
  try {
    await startPracticeAPI(unitId)
    ElMessage.success('练习已开始')
    router.push(`/practice/${unitId}/take`)
  } catch (error) {
    console.error('开始练习失败', error)
    ElMessage.error('开始练习失败，请稍后重试')
  }
}

const viewHistoryDetail = (item: { unitId: number }) => {
  router.push(`/practice/${item.unitId}/result`)
}

const viewPracticeResult = (unitId: number) => {
  router.push(`/practice/${unitId}/result`)
}

const goToDashboard = () => {
  router.push('/dashboard')
}

const loadPractices = async () => {
  loading.value = true
  try {
    const practices = await getAllPractices()
    console.log('API返回的练习数据:', practices)
    const records = await getStudentPracticeRecords()
    const completedUnitIds = new Set(records.filter((r: ExamRecord) => r.status === 'completed').map((r: ExamRecord) => r.unit_id))
    
    practiceList.value = practices.map((p: any) => ({
      ...p,
      status: completedUnitIds.has(p.id) ? 'completed' : 'pending',
      unit_name: p.unit_name || p.name || p.title || p.title_name || '未命名练习'
    }))
  } catch (error) {
    console.error('加载练习列表失败', error)
    ElMessage.error('加载练习列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const records = await getStudentPracticeRecords()
    const now = new Date()
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    const completedThisWeek = records.filter((r: ExamRecord) => {
      const t = r.submit_time ? new Date(r.submit_time) : null
      return t && t >= weekAgo
    })
    const completedRecords = records.filter((r: ExamRecord) => r.status === 'completed' && r.total_score != null)
    const averageScore = completedRecords.length > 0
      ? completedRecords.reduce((sum: number, r: ExamRecord) => sum + (parseFloat(String(r.total_score)) || 0), 0) / completedRecords.length
      : 0
    // 学习时长：本周已完成记录的总时长（开始到提交的分钟数之和）
    const studyMinutes = completedThisWeek.reduce((sum: number, r: ExamRecord) => {
      const start = r.start_time ? new Date(r.start_time).getTime() : 0
      const end = r.submit_time ? new Date(r.submit_time).getTime() : 0
      return sum + (end > start ? Math.round((end - start) / 60000) : 0)
    }, 0)
    const studyHours = Math.floor(studyMinutes / 60)
    const studyMins = studyMinutes % 60
    const studyTimeStr = studyHours > 0 ? `${studyHours}h${studyMins}min` : `${studyMins}min`
    statistics.value = {
      completedCount: completedThisWeek.length,
      averageScore: Math.round(averageScore * 10) / 10,
      studyTime: studyTimeStr,
      trend: '—'
    }
    history.value = completedRecords
      .sort((a: ExamRecord, b: ExamRecord) => (b.submit_time || '').localeCompare(a.submit_time || ''))
      .slice(0, 10)
      .map((r: ExamRecord) => ({
        id: r.id,
        unitId: r.unit_id,
        name: r.unit_name || r.name || '未命名练习',
        completedAt: r.submit_time || '',
        score: parseFloat(String(r.total_score)) || 0
      }))
  } catch (error) {
    console.error('加载统计数据失败', error)
  }
}

onMounted(() => {
  loadPractices()
  loadStatistics()
})
</script>

<style scoped>
.practice-page { 
  width: 100%; 
  min-height: 100vh;
  background: linear-gradient(180deg, #FAFBFC 0%, #F5F7FA 100%);
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 练习统计卡片 */
.statistics-card {
  width: 90%;
  margin-bottom: 32px;
}

/* 返回按钮 */
.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background-color: #FFFFFF;
  color: #8C7CF0;
  border: 2px solid #E8E4FF;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
  margin-bottom: 24px;
  align-self: flex-start;
}

.back-button:hover {
  background-color: #E8E4FF;
  border-color: #8C7CF0;
  transform: translateX(-4px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2);
}
.card {
  background-color: #FFFFFF;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  margin-bottom: 32px;
  position: relative;
  overflow: hidden;
  width: 90%;
  display: flex;
  flex-direction: column;
}
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF);
}
.card-header { margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #F0F2F5; }
.card-title { font-size: 18px; font-weight: 600; color: #1A202C; margin: 0 0 4px 0; }
.card-subtitle { font-size: 14px; color: #8B9BB4; margin: 0; }
.statistics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}
.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background-color: #FAFBFC;
  border-radius: 12px;
  transition: all 0.3s ease;
}
.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.1);
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
}
.stat-icon.completed { background: linear-gradient(135deg, #A8D5BA, #8BC4A8); }
.stat-icon.score { background: linear-gradient(135deg, #8C7CF0, #C6B9FF); }
.stat-icon.time { background: linear-gradient(135deg, #FFE082, #FFB74D); }
.stat-icon.trend { background: linear-gradient(135deg, #FFB74D, #FFB6C1); }
.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: 700; color: #1A202C; margin-bottom: 4px; }
.stat-label { font-size: 14px; color: #8B9BB4; }
.filter-bar { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.filter-group { display: flex; align-items: center; gap: 8px; }
.filter-group label { font-size: 14px; color: #4A5568; font-weight: 500; }
.filter-select {
  padding: 8px 12px;
  border: 1px solid #F0F2F5;
  border-radius: 8px;
  background-color: #FFFFFF;
  color: #4A5568;
  font-size: 14px;
  cursor: pointer;
}
.filter-select:hover, .filter-select:focus { border-color: #8C7CF0; outline: none; }
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #8B9BB4;
}
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #F0F2F5;
  border-top-color: #8C7CF0;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #8B9BB4;
}
.empty-state p { margin-top: 16px; font-size: 14px; }
.task-list { display: flex; flex-direction: column; gap: 12px; }
.task-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background-color: #FAFBFC;
  border-radius: 12px;
  border: 1px solid #F0F2F5;
  cursor: pointer;
  transition: all 0.3s ease;
}
.task-item:hover {
  background-color: #F5F7FA;
  border-color: #E8E4FF;
  transform: translateX(4px);
}
.task-info { flex: 1; }
.task-name { font-size: 16px; font-weight: 600; color: #1A202C; margin: 0 0 4px 0; }
.task-meta { display: flex; gap: 12px; font-size: 12px; color: #8B9BB4; }
.task-type {
  padding: 2px 8px;
  background-color: #E8E4FF;
  color: #8C7CF0;
  border-radius: 4px;
  font-weight: 500;
}
.status-badge { padding: 4px 12px; border-radius: 8px; font-size: 12px; font-weight: 500; }
.status-badge.pending { background-color: #FFE082; color: #FFA000; }
.status-badge.in-progress { background-color: #E8E4FF; color: #8C7CF0; }
.status-badge.completed { background-color: #A8D5BA; color: #4CAF50; }
.start-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}
.start-button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3); }

.result-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #A8D5BA, #8BC4A8);
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}
.result-button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(168, 213, 186, 0.3); }
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #F0F2F5;
}
.pagination-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: #FFFFFF;
  border: 1px solid #F0F2F5;
  border-radius: 8px;
  color: #4A5568;
  font-size: 14px;
  cursor: pointer;
}
.pagination-button:hover:not(:disabled) { background-color: #E8E4FF; border-color: #8C7CF0; color: #8C7CF0; }
.pagination-button:disabled { opacity: 0.5; cursor: not-allowed; }
.pagination-info { font-size: 14px; color: #8B9BB4; }
.history-list { display: flex; flex-direction: column; gap: 12px; }
.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background-color: #FAFBFC;
  border-radius: 12px;
  border: 1px solid #F0F2F5;
  transition: all 0.3s ease;
}
.history-item:hover { background-color: #F5F7FA; border-color: #E8E4FF; }
.history-info { flex: 1; }
.history-name { font-size: 16px; font-weight: 600; color: #1A202C; margin: 0 0 4px 0; }
.history-time { font-size: 14px; color: #8B9BB4; margin: 0; }
.history-score { display: flex; align-items: baseline; gap: 4px; }
.score-value { font-size: 24px; font-weight: 700; color: #8C7CF0; }
.score-label { font-size: 14px; color: #8B9BB4; }
.detail-button {
  padding: 8px 16px;
  background-color: transparent;
  color: #8C7CF0;
  border: 1px solid #8C7CF0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}
.detail-button:hover { background-color: #E8E4FF; }
</style>
