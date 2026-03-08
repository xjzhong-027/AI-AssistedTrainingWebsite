<template>
  <div class="exam-page">
    <div class="exam-content">
      <!-- 考试中心卡片（合并标题和统计） -->
      <div class="exam-center-card">
        <!-- 返回首页按钮 -->
        <button class="back-button" @click="goToDashboard">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回首页
        </button>
        
        <div class="card-header">
          <div class="header-content">
            <h1 class="page-title">考试中心</h1>
            <p class="page-subtitle">管理你的考试安排，查看历史成绩</p>
          </div>
          <div class="header-illustration">
            <div class="cute-character">
              <!-- 头部 -->
              <div class="character-head">
                <!-- 头发 -->
                <div class="hair-back"></div>
                <div class="hair-front">
                  <div class="bang bang-1"></div>
                  <div class="bang bang-2"></div>
                  <div class="bang bang-3"></div>
                </div>
                <!-- 脸部 -->
                <div class="character-face">
                  <!-- 眼睛 -->
                  <div class="character-eyes">
                    <div class="character-eye left">
                      <div class="eye-pupil"></div>
                      <div class="eye-shine"></div>
                    </div>
                    <div class="character-eye right">
                      <div class="eye-pupil"></div>
                      <div class="eye-shine"></div>
                    </div>
                  </div>
                  <!-- 眉毛 -->
                  <div class="eyebrow left"></div>
                  <div class="eyebrow right"></div>
                  <!-- 腮红 -->
                  <div class="character-blush left"></div>
                  <div class="character-blush right"></div>
                  <!-- 嘴巴 -->
                  <div class="character-mouth">
                    <div class="mouth-smile"></div>
                  </div>
                </div>
              </div>
              <!-- 身体 -->
              <div class="character-body">
                <div class="character-torso">
                  <div class="shirt">
                    <div class="shirt-collar"></div>
                    <div class="shirt-logo">EXAM</div>
                  </div>
                </div>
                <!-- 手臂 -->
                <div class="arm left">
                  <div class="hand-holding">
                    <div class="book">
                      <div class="book-cover"></div>
                      <div class="book-pages"></div>
                    </div>
                  </div>
                </div>
                <div class="arm right">
                  <div class="hand-peace">
                    <div class="finger f1"></div>
                    <div class="finger f2"></div>
                  </div>
                </div>
              </div>
              <!-- 装饰元素 -->
              <div class="character-decorations">
                <div class="exam-paper">📄</div>
                <div class="pencil">✏️</div>
                <div class="star s1">⭐</div>
                <div class="star s2">✨</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 统计概览 -->
        <div class="stats-overview">
          <div class="stat-card">
            <div class="stat-icon upcoming">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ upcomingCount }}</div>
              <div class="stat-label">待考考试</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon completed">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ completedCount }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon average">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ averageScore }}</div>
              <div class="stat-label">平均分</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 即将到来的考试 -->
      <div class="exam-section">
        <div class="section-header">
          <div class="section-title-wrapper">
            <div class="section-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            </div>
            <h2 class="section-title">即将到来的考试</h2>
          </div>
          <span class="section-count">{{ upcomingExams.length }} 个考试</span>
        </div>

        <div v-if="upcomingExams.length > 0" class="exam-cards">
          <div v-for="exam in upcomingExams" :key="exam.id" class="exam-card">
            <div class="card-decoration"></div>
            <div class="exam-card-content">
              <div class="exam-info">
                <h3 class="exam-title">{{ exam.title }}</h3>
                <p class="exam-description">{{ exam.description || '暂无描述' }}</p>
                <div class="exam-meta">
                  <div class="meta-item">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                      <line x1="16" y1="2" x2="16" y2="6"></line>
                      <line x1="8" y1="2" x2="8" y2="6"></line>
                      <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    <span>{{ formatDateTime(exam.startTime) }}</span>
                  </div>
                  <div class="meta-item">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    <span>{{ exam.duration }} 分钟</span>
                  </div>
                </div>
                <div v-if="isUrgent(exam.startTime)" class="urgent-badge">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                    <line x1="12" y1="9" x2="12" y2="13"></line>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                  </svg>
                  即将开始
                </div>
              </div>
              <div class="exam-actions">
                <button 
                  v-if="canTakeExam(exam)" 
                  class="btn-primary"
                  @click="takeExam(exam.id)"
                >
                  进入考试
                </button>
                <button 
                  v-else
                  class="btn-secondary"
                  @click="viewDetail(exam.id)"
                >
                  查看详情
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">📚</div>
          <p class="empty-text">暂无即将到来的考试</p>
          <p class="empty-subtext">好好休息，为下次考试做准备吧！</p>
        </div>
      </div>

      <!-- 历史考试成绩 -->
      <div class="exam-section">
        <div class="section-header">
          <div class="section-title-wrapper">
            <div class="section-icon history">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="1 4 1 10 7 10"></polyline>
                <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
              </svg>
            </div>
            <h2 class="section-title">历史考试成绩</h2>
          </div>
        </div>

        <div v-if="completedExams.length > 0" class="history-table-wrapper">
          <table class="history-table">
            <thead>
              <tr>
                <th>考试名称</th>
                <th>考试时间</th>
                <th>得分</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="exam in completedExams" :key="exam.id">
                <td>
                  <div class="exam-name-cell">
                    <div class="exam-name">{{ exam.title }}</div>
                    <div class="exam-desc">{{ exam.description || '暂无描述' }}</div>
                  </div>
                </td>
                <td>{{ formatDateTime(exam.endTime || exam.startTime) }}</td>
                <td>
                  <div class="score-cell">
                    <span class="score-value" :class="getScoreClass(exam.score)">{{ exam.score || '-' }}</span>
                    <span v-if="exam.score" class="score-total">/ 100</span>
                  </div>
                </td>
                <td>
                  <span class="status-badge" :class="getScoreStatusClass(exam.score)">
                    {{ getScoreStatusText(exam.score) }}
                  </span>
                </td>
                <td>
                  <button class="btn-text" @click="viewDetail(exam.id)">查看详情</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">📝</div>
          <p class="empty-text">暂无历史考试记录</p>
          <p class="empty-subtext">完成考试后，成绩会显示在这里</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getAllExams } from '@/api/exam'
import { formatDateTime } from '@/utils/format'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const examList = ref<any[]>([])

// 统计数据
const upcomingCount = computed(() => upcomingExams.value.length)
const completedCount = computed(() => completedExams.value.length)
const averageScore = computed(() => {
  const completed = completedExams.value.filter(e => e.score != null)
  if (completed.length === 0) return '-'
  const total = completed.reduce((sum, e) => sum + (e.score || 0), 0)
  return Math.round(total / completed.length)
})

// 即将到来的考试
const upcomingExams = computed(() => {
  return examList.value.filter(exam => {
    const status = exam.status || ''
    return status === 'NOT_STARTED' || status === 'IN_PROGRESS'
  })
})

// 已完成的考试
const completedExams = computed(() => {
  return examList.value.filter(exam => {
    const status = exam.status || ''
    return status === 'ENDED' || status === 'completed' || exam.score != null
  })
})

// 加载考试列表
const loadExams = async () => {
  loading.value = true
  try {
    const studentId = userStore.userInfo?.id
    const exams = await getAllExams(studentId, 'exam')
    
    examList.value = exams.map((exam: any) => ({
      id: exam.id,
      title: exam.unit_name || exam.title || '未命名考试',
      description: exam.description || '',
      startTime: exam.start_time || exam.startTime || '',
      endTime: exam.submit_time || exam.endTime || '',
      duration: exam.duration || 0,
      status: exam.status || 'NOT_STARTED',
      score: exam.total_score || exam.score || null
    }))
  } catch (error) {
    console.error('加载考试列表失败', error)
    ElMessage.error('加载考试列表失败')
  } finally {
    loading.value = false
  }
}

// 判断考试是否紧急（24小时内）
const isUrgent = (startTime: string) => {
  if (!startTime) return false
  const start = new Date(startTime).getTime()
  const now = Date.now()
  const diff = start - now
  return diff > 0 && diff < 24 * 60 * 60 * 1000
}

// 判断是否可以参加考试
const canTakeExam = (exam: any) => {
  return exam.status === 'IN_PROGRESS'
}

// 获取分数样式类
const getScoreClass = (score: number | null) => {
  if (score == null) return ''
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 60) return 'pass'
  return 'fail'
}

// 获取分数状态样式类
const getScoreStatusClass = (score: number | null) => {
  if (score == null) return 'status-pending'
  if (score >= 90) return 'status-excellent'
  if (score >= 80) return 'status-good'
  if (score >= 60) return 'status-pass'
  return 'status-fail'
}

// 获取分数状态文本
const getScoreStatusText = (score: number | null) => {
  if (score == null) return '待评分'
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 60) return '及格'
  return '不及格'
}

// 查看详情
const viewDetail = (id: number) => {
  router.push(`/exams/${id}`)
}

// 参加考试
const takeExam = (id: number) => {
  router.push(`/exams/${id}/take`)
}

// 返回首页
const goToDashboard = () => {
  router.push('/dashboard')
}

onMounted(() => {
  loadExams()
})
</script>

<style scoped>
.exam-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FAFBFC 0%, #F5F7FA 100%);
  padding: 24px 32px;
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

/* 页面内容 */
.exam-content {
  max-width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 考试中心卡片 */
.exam-center-card {
  background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FF 100%);
  border-radius: 24px;
  padding: 40px 50px;
  margin-bottom: 32px;
  box-shadow: 0 8px 32px rgba(140, 124, 240, 0.12);
  position: relative;
  overflow: hidden;
  width: 90%;
  display: flex;
  flex-direction: column;
}

.exam-center-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF, #A8D5BA);
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
  gap: 40px;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  color: #1A202C;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #8C7CF0 0%, #6B5DD3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 16px;
  color: #8B9BB4;
  margin: 0;
}

/* 可爱卡通人物 */
.header-illustration {
  width: 150px;
  height: 150px;
  position: relative;
  flex-shrink: 0;
}

.cute-character {
  width: 100%;
  height: 100%;
  position: relative;
  animation: character-bounce 2.5s ease-in-out infinite;
}

@keyframes character-bounce {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(1deg);
  }
}

/* 头部 */
.character-head {
  width: 90px;
  height: 85px;
  background: linear-gradient(180deg, #FFE4C4 0%, #FFDAB9 100%);
  border-radius: 50% 50% 45% 45%;
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  box-shadow: 0 8px 20px rgba(255, 218, 185, 0.3),
              inset 0 -8px 15px rgba(255, 182, 193, 0.2);
  z-index: 10;
}

/* 头发 - 后面 */
.hair-back {
  position: absolute;
  width: 100px;
  height: 60px;
  background: linear-gradient(180deg, #5D4E37 0%, #4A3F2F 100%);
  border-radius: 50% 50% 30% 30%;
  top: 5px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 8;
}

/* 头发 - 前面刘海 */
.hair-front {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 30px;
  z-index: 12;
}

.bang {
  position: absolute;
  background: linear-gradient(180deg, #5D4E37 0%, #4A3F2F 100%);
  border-radius: 0 0 50% 50%;
}

.bang-1 {
  width: 30px;
  height: 25px;
  left: 5px;
  top: 0;
  transform: rotate(-10deg);
}

.bang-2 {
  width: 35px;
  height: 28px;
  left: 50%;
  transform: translateX(-50%);
  top: -2px;
}

.bang-3 {
  width: 30px;
  height: 25px;
  right: 5px;
  top: 0;
  transform: rotate(10deg);
}

/* 脸部 */
.character-face {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -45%);
  width: 70px;
  height: 50px;
}

/* 眉毛 */
.eyebrow {
  position: absolute;
  width: 15px;
  height: 2px;
  background: #5D4E37;
  border-radius: 1px;
  top: 8px;
}

.eyebrow.left {
  left: 10px;
  transform: rotate(-5deg);
}

.eyebrow.right {
  right: 10px;
  transform: rotate(5deg);
}

/* 眼睛 */
.character-eyes {
  display: flex;
  justify-content: space-between;
  width: 45px;
  margin: 15px auto 0;
}

.character-eye {
  width: 16px;
  height: 19px;
  background: #FFFFFF;
  border-radius: 50%;
  position: relative;
  border: 1px solid #E8E4FF;
  animation: character-blink 4s ease-in-out infinite;
}

.eye-pupil {
  position: absolute;
  width: 9px;
  height: 11px;
  background: linear-gradient(180deg, #8C7CF0 0%, #6B5DD3 100%);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.eye-shine {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #FFFFFF;
  border-radius: 50%;
  top: 4px;
  right: 2px;
}

@keyframes character-blink {
  0%, 92%, 100% {
    transform: scaleY(1);
  }
  96% {
    transform: scaleY(0.1);
  }
}

/* 腮红 */
.character-blush {
  position: absolute;
  width: 14px;
  height: 9px;
  background: linear-gradient(180deg, rgba(255, 182, 193, 0.7) 0%, rgba(255, 160, 180, 0.5) 100%);
  border-radius: 50%;
  top: 28px;
}

.character-blush.left {
  left: 4px;
}

.character-blush.right {
  right: 4px;
}

/* 嘴巴 */
.character-mouth {
  position: absolute;
  bottom: 5px;
  left: 50%;
  transform: translateX(-50%);
  width: 18px;
  height: 9px;
}

.mouth-smile {
  width: 100%;
  height: 100%;
  border: 1.5px solid #FF6B9D;
  border-top: none;
  border-radius: 0 0 20px 20px;
  background: transparent;
}

/* 身体 */
.character-body {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 70px;
  height: 50px;
  z-index: 5;
}

.character-torso {
  width: 70px;
  height: 50px;
  background: linear-gradient(180deg, #8C7CF0 0%, #6B5DD3 100%);
  border-radius: 35px 35px 25px 25px;
  position: relative;
}

.shirt {
  position: relative;
  width: 100%;
  height: 100%;
}

.shirt-collar {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 12px;
  background: #FFFFFF;
  border-radius: 0 0 15px 15px;
}

.shirt-logo {
  position: absolute;
  top: 22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 9px;
  font-weight: 700;
  color: #FFFFFF;
  background: linear-gradient(135deg, #FFE082 0%, #FFB74D 100%);
  padding: 2px 6px;
  border-radius: 8px;
  letter-spacing: 1px;
}

/* 手臂 */
.arm {
  position: absolute;
  width: 18px;
  height: 45px;
  background: linear-gradient(180deg, #8C7CF0 0%, #6B5DD3 100%);
  border-radius: 9px;
  top: 15px;
  z-index: 8;
}

.arm.left {
  left: -5px;
  transform: rotate(-20deg);
  transform-origin: top center;
}

.arm.right {
  right: -5px;
  transform: rotate(20deg);
  transform-origin: top center;
}

/* 左手拿书 */
.hand-holding {
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 25px;
  height: 20px;
}

.book {
  position: absolute;
  width: 22px;
  height: 17px;
  bottom: 0;
}

.book-cover {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #A8D5BA 0%, #8BC4A8 100%);
  border-radius: 2px;
  box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}

.book-pages {
  position: absolute;
  width: 17px;
  height: 15px;
  background: #FFFFFF;
  right: 0;
  top: 1px;
  border-radius: 0 2px 2px 0;
}

/* 右手比耶 */
.hand-peace {
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 1.5px;
}

.finger {
  width: 5px;
  height: 12px;
  background: linear-gradient(180deg, #FFE4C4 0%, #FFDAB9 100%);
  border-radius: 2.5px;
}

.finger.f1 {
  transform: rotate(-10deg);
}

.finger.f2 {
  transform: rotate(10deg);
  height: 14px;
}

/* 装饰元素 */
.character-decorations {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.exam-paper {
  position: absolute;
  font-size: 32px;
  top: 25px;
  right: 10px;
  animation: float 2s ease-in-out infinite;
}

.pencil {
  position: absolute;
  font-size: 28px;
  bottom: 25px;
  left: 10px;
  animation: float 2s ease-in-out infinite 0.5s;
}

.star {
  position: absolute;
  font-size: 16px;
  animation: float 2.5s ease-in-out infinite;
}

.star.s1 {
  top: 15px;
  left: 20px;
  animation-delay: 0.3s;
}

.star.s2 {
  bottom: 15px;
  right: 20px;
  font-size: 14px;
  animation-delay: 0.8s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* 统计概览 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 2px solid #F0F2F5;
  transition: all 0.3s ease;
  position: relative;
  backdrop-filter: blur(10px);
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: #E8E4FF;
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.15);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  flex-shrink: 0;
}

.stat-icon.upcoming {
  background: linear-gradient(135deg, #FFB74D 0%, #FFA726 100%);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #A8D5BA 0%, #8BC4A8 100%);
}

.stat-icon.average {
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1A202C;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 14px;
  color: #8B9BB4;
  font-weight: 500;
}

/* 考试区块 */
.exam-section {
  background: #FFFFFF;
  border-radius: 24px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.12);
  position: relative;
  overflow: hidden;
  width: 90%;
}

.exam-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF, #A8D5BA);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
}

.section-icon.history {
  background: linear-gradient(135deg, #A8D5BA 0%, #8BC4A8 100%);
}

.section-title {
  font-size: 22px;
  font-weight: 700;
  color: #1A202C;
  margin: 0;
}

.section-count {
  font-size: 14px;
  color: #8B9BB4;
  font-weight: 500;
  padding: 6px 14px;
  background: #F5F7FA;
  border-radius: 20px;
}

/* 考试卡片 */
.exam-cards {
  display: grid;
  gap: 20px;
}

.exam-card {
  background: linear-gradient(135deg, #FAFBFC 0%, #FFFFFF 100%);
  border-radius: 16px;
  padding: 24px;
  border: 2px solid #F0F2F5;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.exam-card:hover {
  border-color: #E8E4FF;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.15);
}

.card-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #8C7CF0 0%, #C6B9FF 100%);
}

.exam-card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.exam-info {
  flex: 1;
}

.exam-title {
  font-size: 18px;
  font-weight: 600;
  color: #1A202C;
  margin: 0 0 8px 0;
}

.exam-description {
  font-size: 14px;
  color: #8B9BB4;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.exam-meta {
  display: flex;
  gap: 24px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #4A5568;
}

.meta-item svg {
  color: #8C7CF0;
}

.urgent-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #FFB74D 0%, #FFA726 100%);
  color: #FFFFFF;
  font-size: 12px;
  font-weight: 600;
  border-radius: 20px;
}

.exam-actions {
  flex-shrink: 0;
}

/* 按钮样式 */
.btn-primary {
  padding: 12px 28px;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  color: #FFFFFF;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.4);
}

.btn-secondary {
  padding: 12px 28px;
  background: #FFFFFF;
  color: #8C7CF0;
  border: 2px solid #E8E4FF;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #E8E4FF;
  border-color: #8C7CF0;
}

.btn-text {
  padding: 8px 16px;
  background: transparent;
  color: #8C7CF0;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-text:hover {
  background: rgba(140, 124, 240, 0.1);
}

/* 历史成绩表格 */
.history-table-wrapper {
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.history-table th {
  background: #F5F7FA;
  padding: 16px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #4A5568;
  border-bottom: 2px solid #E8E4FF;
}

.history-table th:first-child {
  border-radius: 12px 0 0 0;
}

.history-table th:last-child {
  border-radius: 0 12px 0 0;
}

.history-table td {
  padding: 20px 16px;
  border-bottom: 1px solid #F0F2F5;
  font-size: 14px;
  color: #4A5568;
}

.history-table tr:hover td {
  background: #FAFBFC;
}

.exam-name-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.exam-name {
  font-weight: 600;
  color: #1A202C;
}

.exam-desc {
  font-size: 12px;
  color: #8B9BB4;
}

.score-cell {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.score-value {
  font-size: 20px;
  font-weight: 700;
}

.score-value.excellent {
  color: #A8D5BA;
}

.score-value.good {
  color: #8C7CF0;
}

.score-value.pass {
  color: #FFB74D;
}

.score-value.fail {
  color: #FF6B6B;
}

.score-total {
  font-size: 14px;
  color: #8B9BB4;
}

/* 状态标签 */
.status-badge {
  display: inline-flex;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-excellent {
  background: rgba(168, 213, 186, 0.2);
  color: #5A9A6E;
}

.status-good {
  background: rgba(140, 124, 240, 0.2);
  color: #6B5DD3;
}

.status-pass {
  background: rgba(255, 183, 77, 0.2);
  color: #E69500;
}

.status-fail {
  background: rgba(255, 107, 107, 0.2);
  color: #E53E3E;
}

.status-pending {
  background: #F0F2F5;
  color: #8B9BB4;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
  font-weight: 600;
  color: #1A202C;
  margin: 0 0 8px 0;
}

.empty-subtext {
  font-size: 14px;
  color: #8B9BB4;
  margin: 0;
}

/* 响应式 */
@media (max-width: 1024px) {
  .card-header {
    flex-direction: column;
    text-align: center;
    gap: 30px;
  }
  
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .exam-card-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .exam-actions {
    width: 100%;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .exam-page {
    padding: 16px;
  }
  
  .exam-center-card {
    padding: 30px 24px;
  }
  
  .header-illustration {
    width: 120px;
    height: 120px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .exam-meta {
    flex-direction: column;
    gap: 8px;
  }
  
  .history-table {
    font-size: 12px;
  }
  
  .history-table th,
  .history-table td {
    padding: 12px 8px;
  }
}
</style>
练习任务状态显示错误