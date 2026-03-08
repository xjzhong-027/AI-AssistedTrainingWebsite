<template>
  <div class="student-dashboard">
    <div class="container">
      <!-- 学习行为评估大卡片 -->
      <div class="assessment-main-card card">
        <!-- 返回首页按钮 -->
        <button class="back-button" @click="goToDashboard">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回首页
        </button>

        <div class="section-header">
          <div class="section-title">学习行为评估</div>
        </div>
        
        <!-- 四宫格布局 -->
        <div class="four-grid">
          <!-- 左上：综合评分 -->
          <div class="grid-item">
            <div class="grid-title">综合评分</div>
            <div class="score-content">
              <div class="score-circle" :style="{ background: `conic-gradient(#99B6B4 ${overallScore}%, #E8E8E8 0%)` }">
                <div class="score-value">{{ overallScore }}</div>
                <div class="score-max">/ 100</div>
              </div>
              <div class="score-info">
                <div class="score-title">综合学习行为评分</div>
                <div class="score-rating">{{ scoreRating }}</div>
                <div class="score-description">综合评分综合了您的课堂成绩、参与度、学习时长和AI使用。</div>
              </div>
            </div>
          </div>
          
          <!-- 右上：学习趋势 -->
          <div class="grid-item">
            <div class="grid-title highlight">学习趋势</div>
            <div class="trend-chart-container">
              <canvas ref="trendChart"></canvas>
            </div>
          </div>
          
          <!-- 左下：行为指标分析 -->
          <div class="grid-item">
            <div class="grid-title">行为指标分析</div>
            <div class="metrics-content">
              <div class="radar-chart-container">
                <canvas ref="radarChart"></canvas>
              </div>
              <div class="metrics-list">
                <div class="metric-row">
                  <span class="metric-name">正确率</span>
                  <span class="metric-value">{{ metrics.accuracy }}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">提示使用率</span>
                  <span class="metric-value">{{ metrics.hintUsage }}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">有效学习时长</span>
                  <span class="metric-value">{{ metrics.studyTime }}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">练习完成率</span>
                  <span class="metric-value">{{ metrics.completionRate }}%</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">参与度</span>
                  <span class="metric-value">{{ metrics.participation }}%</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 右下：练习行为记录 -->
          <div class="grid-item">
            <div class="grid-title">练习行为记录</div>
            <div class="records-content">
              <div v-if="loading" class="loading">加载中...</div>
              <div v-else-if="practiceRecords.length === 0" class="no-records">暂无练习记录</div>
              <table v-else class="practice-records">
                <thead>
                  <tr>
                    <th>练习名称</th>
                    <th>正确率</th>
                    <th>提示使用</th>
                    <th>时长</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(record, index) in practiceRecords" :key="index">
                    <td>{{ record.name }}</td>
                    <td>{{ record.accuracy }}</td>
                    <td>{{ record.hints }}</td>
                    <td>{{ record.duration }}</td>
                  </tr>
                </tbody>
              </table>
              <div class="week-selector">
                <button class="week-button" @click="prevWeek">&lt;</button>
                <span class="week-label">week {{ currentWeek }}</span>
                <button class="week-button" @click="nextWeek">&gt;</button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="changePasswordDialogVisible"
      title="修改密码"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="passwordForm" :rules="passwordFormRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入旧密码" show-password></el-input>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelChangePassword">取消</el-button>
          <el-button type="primary" @click="savePassword" :loading="passwordSubmitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
    <AIWindow :show-grade-button="false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getStudentPracticeScores, getStudentPracticeRecords } from '@/api/practice'
import AIWindow from '@/components/common/AIWindow/index.vue'
import { getUserById, changePassword } from '@/api/user'
import type { PracticeScore, ExamRecord } from '@/api/practice'

const router = useRouter()
const userStore = useUserStore()

const trendChart = ref<HTMLCanvasElement | null>(null)
const radarChart = ref<HTMLCanvasElement | null>(null)
const selectedIndex = ref<number | null>(null)
const loading = ref(false)
const currentWeek = ref(2)
const studentInfo = ref({
  className: '',
  seatNumber: ''
})
const practiceScores = ref<PracticeScore[]>([])
const practiceRecordsRaw = ref<ExamRecord[]>([])

// 行为指标数据
const metrics = ref({
  accuracy: 0,
  hintUsage: 0,
  studyTime: 0,
  completionRate: 0,
  participation: 0
})

let trendChartInstance: any = null
let radarChartInstance: any = null

// 修改密码相关
const changePasswordDialogVisible = ref(false)
const passwordSubmitting = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 计算综合评分
const overallScore = computed(() => {
  if (practiceScores.value.length === 0) return 0
  const totalScore = practiceScores.value.reduce((sum, item) => sum + (item.totalScore || 0), 0)
  return Math.round(totalScore / practiceScores.value.length)
})

// 计算评分等级
const scoreRating = computed(() => {
  const score = overallScore.value
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '需努力'
})

// 计算练习行为记录
const practiceRecords = computed(() => {
  return practiceRecordsRaw.value.slice(0, 3).map(record => {
    const startTime = new Date(record.start_time)
    const submitTime = record.submit_time ? new Date(record.submit_time) : null
    const duration = submitTime 
      ? Math.round((submitTime.getTime() - startTime.getTime()) / 60000)
      : 0
    
    return {
      name: record.unit_name || `练习 ${record.unit_id}`,
      accuracy: record.total_score ? `${record.total_score}%` : '-',
      hints: '0', // 后端暂无此字段，默认显示0
      duration: duration > 0 ? `${duration}分钟` : '-'
    }
  })
})

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== passwordForm.value.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordFormRules: FormRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const goToDashboard = () => {
  router.push('/dashboard')
}

const prevWeek = () => {
  if (currentWeek.value > 1) {
    currentWeek.value--
  }
}

const nextWeek = () => {
  if (currentWeek.value < 5) {
    currentWeek.value++
  }
}

const handleChangePassword = () => {
  changePasswordDialogVisible.value = true
}

const cancelChangePassword = () => {
  changePasswordDialogVisible.value = false
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
}

const savePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return

    passwordSubmitting.value = true
    try {
      await changePassword(passwordForm.value.oldPassword, passwordForm.value.newPassword)
      ElMessage.success('密码修改成功，请重新登录')

      passwordForm.value = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      changePasswordDialogVisible.value = false

      setTimeout(() => {
        userStore.logout()
        router.push('/login')
      }, 2000)
    } catch (error: any) {
      console.error('修改密码失败', error)
      ElMessage.error(error.message || '修改密码失败')
    } finally {
      passwordSubmitting.value = false
    }
  })
}

// 计算行为指标
const calculateMetrics = () => {
  const records = practiceRecordsRaw.value
  if (records.length === 0) {
    metrics.value = {
      accuracy: 0,
      hintUsage: 0,
      studyTime: 0,
      completionRate: 0,
      participation: 0
    }
    return
  }

  // 正确率：基于平均分数
  const completedRecords = records.filter(r => r.status === 'completed')
  const avgScore = completedRecords.length > 0
    ? completedRecords.reduce((sum, r) => sum + (r.total_score || 0), 0) / completedRecords.length
    : 0
  
  // 练习完成率
  const completionRate = records.length > 0
    ? Math.round((completedRecords.length / records.length) * 100)
    : 0

  // 有效学习时长（分钟）
  const totalStudyTime = completedRecords.reduce((sum, r) => {
    if (r.start_time && r.submit_time) {
      const start = new Date(r.start_time)
      const end = new Date(r.submit_time)
      return sum + Math.round((end.getTime() - start.getTime()) / 60000)
    }
    return sum
  }, 0)

  metrics.value = {
    accuracy: Math.round(avgScore),
    hintUsage: Math.round(avgScore * 0.8), // 模拟数据
    studyTime: totalStudyTime,
    completionRate: completionRate,
    participation: Math.min(100, completionRate + 10) // 模拟数据
  }
}

const initTrendChart = async () => {
  if (!trendChart.value) return

  try {
    const chartModule = await import('chart.js')
    const { Chart, registerables } = chartModule
    Chart.register(...registerables)

    const ctx = trendChart.value!.getContext('2d')
    if (!ctx) return

    // 使用真实数据，如果没有则使用默认数据
    let labels: string[] = []
    let scores: number[] = []
    
    if (practiceScores.value.length > 0) {
      const sortedScores = [...practiceScores.value].sort((a, b) => 
        new Date(a.startedAt).getTime() - new Date(b.startedAt).getTime()
      )
      labels = sortedScores.map((_, index) => `练习${index + 1}`)
      scores = sortedScores.map(item => item.totalScore)
    } else {
      labels = ['week 1', 'week 2', 'week 3', 'week 4', 'week 5']
      scores = [70, 72, 75, 80, 85]
    }

    if (trendChartInstance) {
      trendChartInstance.destroy()
    }

    trendChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: '学习趋势',
          data: scores,
          backgroundColor: 'rgba(153, 182, 180, 0.15)',
          borderColor: '#99B6B4',
          borderWidth: 2,
          pointBackgroundColor: '#99B6B4',
          pointRadius: 4,
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            min: 0,
            max: 100,
            ticks: {
              stepSize: 20,
              font: { size: 11 }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            ticks: {
              font: { size: 11 }
            },
            grid: {
              display: false
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            titleColor: '#333',
            bodyColor: '#666',
            borderColor: '#ddd',
            borderWidth: 1,
            padding: 10,
            displayColors: false
          }
        }
      }
    })
  } catch (error) {
    console.error('Chart.js 加载失败', error)
  }
}

const initRadarChart = async () => {
  if (!radarChart.value) return

  try {
    const chartModule = await import('chart.js')
    const { Chart, registerables } = chartModule
    Chart.register(...registerables)

    const ctx = radarChart.value!.getContext('2d')
    if (!ctx) return

    // 使用真实指标数据
    const dataValues = [
      metrics.value.accuracy,
      metrics.value.hintUsage,
      Math.min(100, metrics.value.studyTime),
      metrics.value.completionRate,
      metrics.value.participation
    ]

    if (radarChartInstance) {
      radarChartInstance.destroy()
    }

    radarChartInstance = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: ['正确率', '提示使用率', '有效学习时长', '练习完成率', '参与度'],
        datasets: [{
          label: '行为指标',
          data: dataValues,
          backgroundColor: 'rgba(153, 182, 180, 0.3)',
          borderColor: '#99B6B4',
          borderWidth: 2,
          pointBackgroundColor: '#99B6B4',
          pointBorderColor: '#fff',
          pointRadius: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            beginAtZero: true,
            max: 100,
            min: 0,
            ticks: {
              display: false,
              stepSize: 20
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.1)'
            },
            pointLabels: {
              display: false
            }
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    })
  } catch (error) {
    console.error('Chart.js 加载失败', error)
  }
}

const loadStudentData = async () => {
  if (!userStore.userInfo?.id) return

  loading.value = true
  try {
    // 加载学生信息
    const user = await getUserById(userStore.userInfo.id, userStore.userInfo?.role)
    studentInfo.value = {
      className: (user as any).class_name || (user as any).className || '-',
      seatNumber: (user as any).seat_number || (user as any).seatNumber || '-'
    }

    // 加载练习成绩
    const scores = await getStudentPracticeScores(userStore.userInfo.id)
    practiceScores.value = scores

    // 加载练习记录
    const records = await getStudentPracticeRecords(userStore.userInfo.id)
    practiceRecordsRaw.value = records

    // 计算行为指标
    calculateMetrics()

    setTimeout(() => {
      initTrendChart()
      initRadarChart()
    }, 100)
  } catch (error) {
    console.error('加载学生数据失败', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadStudentData()
  setTimeout(() => {
    initTrendChart()
    initRadarChart()
  }, 100)
})

onUnmounted(() => {
  if (trendChartInstance) {
    trendChartInstance.destroy()
  }
  if (radarChartInstance) {
    radarChartInstance.destroy()
  }
})
</script>

<style scoped>
.student-dashboard {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #FAFBFC 0%, #F5F7FA 100%);
  padding: 30px 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 30px;
  width: 90%;
}

/* 统一卡片样式 */
.card {
  background-color: #FFFFFF;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  position: relative;
  overflow: hidden;
  margin-bottom: 30px;
  animation: fadeInUp 0.5s ease-out;
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

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF);
}

/* 学习行为评估大卡片 */
.assessment-main-card {
  position: relative;
  width: 100%;
}

.back-button {
  position: absolute;
  top: 24px;
  right: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  background-color: #FFFFFF;
  color: #8C7CF0;
  border: 2px solid #E8E4FF;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
  z-index: 10;
}

.back-button:hover {
  background-color: #E8E4FF;
  border-color: #8C7CF0;
  transform: translateX(-4px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2);
}

.back-button svg {
  margin-right: 8px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #F0F2F5;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #1A202C;
}

/* 四宫格布局 */
.four-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 24px;
}

.grid-item {
  background-color: #F8F9FF;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.grid-title {
  font-size: 16px;
  font-weight: 600;
  color: #1A202C;
  margin-bottom: 16px;
}

.grid-title.highlight {
  color: #8C7CF0;
  background-color: #E8E4FF;
  display: inline-block;
  padding: 4px 12px;
  border-radius: 8px;
  width: fit-content;
}

/* 综合评分 */
.score-content {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  flex-shrink: 0;
}

.score-circle::before {
  content: '';
  position: absolute;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #FFFFFF;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
  color: #1A202C;
  position: relative;
  z-index: 1;
}

.score-max {
  font-size: 12px;
  color: #666;
  position: relative;
  z-index: 1;
}

.score-info {
  flex: 1;
}

.score-title {
  font-size: 14px;
  font-weight: 600;
  color: #1A202C;
  margin-bottom: 4px;
}

.score-rating {
  font-size: 13px;
  font-weight: 500;
  color: #99B6B4;
  margin-bottom: 8px;
}

.score-description {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

/* 学习趋势 */
.trend-chart-container {
  flex: 1;
  min-height: 150px;
}

/* 行为指标分析 */
.metrics-content {
  display: flex;
  gap: 20px;
  flex: 1;
}

.radar-chart-container {
  flex: 1;
  min-height: 150px;
  max-width: 150px;
}

.metrics-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #E8E4FF;
}

.metric-row:last-child {
  border-bottom: none;
}

.metric-name {
  font-size: 13px;
  color: #666;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #8C7CF0;
}

/* 练习行为记录 */
.records-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.practice-records {
  width: 100%;
  border-collapse: collapse;
  flex: 1;
}

.practice-records th,
.practice-records td {
  padding: 10px 8px;
  text-align: left;
  font-size: 13px;
}

.practice-records th {
  font-weight: 600;
  color: #1A202C;
  border-bottom: 1px solid #E8E4FF;
}

.practice-records td {
  color: #666;
  border-bottom: 1px solid #F0F2F5;
}

.practice-records tr:last-child td {
  border-bottom: none;
}

.week-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #E8E4FF;
}

.week-button {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid #E8E4FF;
  background-color: #FFFFFF;
  color: #8C7CF0;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.week-button:hover {
  background-color: #E8E4FF;
  border-color: #8C7CF0;
}

.week-label {
  font-size: 14px;
  font-weight: 600;
  color: #1A202C;
}

.loading {
  text-align: center;
  padding: 30px;
  color: #666;
}

.no-records {
  text-align: center;
  padding: 30px;
  color: #666;
}

@media (max-width: 1024px) {
  .four-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }
  
  .score-content {
    flex-direction: column;
    text-align: center;
  }
  
  .metrics-content {
    flex-direction: column;
  }
  
  .radar-chart-container {
    max-width: 100%;
    height: 200px;
  }
}

@media (max-width: 768px) {
  .container {
    width: 95%;
    padding: 0 15px;
  }
  
  .back-button {
    position: relative;
    top: auto;
    right: auto;
    margin-bottom: 16px;
    align-self: flex-start;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .card {
    padding: 16px;
  }
  
  .grid-item {
    padding: 16px;
  }
  
  .practice-records th,
  .practice-records td {
    padding: 8px 4px;
    font-size: 12px;
  }
}
</style>
