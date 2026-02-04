<template>
  <div class="student-dashboard">
      <div class="header">
        <div class="header-content">
          <div class="header-left">
            <router-link to="/dashboard" class="back-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
              </svg>
              返回
            </router-link>
            <h1>Dashboard</h1>
          </div>
          <div class="user-info">
            <span>{{ userStore.userInfo?.realName }}</span>
            <button class="change-password-button" @click="handleChangePassword">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
              修改密码
            </button>
          </div>
        </div>
      </div>

      <div class="container">
        <!-- 个人信息卡片 -->
        <div class="student-profile card">
          <div class="profile-header">
            <div class="profile-title">个人信息</div>
          </div>
          <div class="profile-info">
            <div class="info-item">
              <div class="info-label">用户名</div>
              <div class="info-value">{{ userStore.userInfo?.username }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">姓名</div>
              <div class="info-value">{{ userStore.userInfo?.realName }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">班级</div>
              <div class="info-value">{{ studentInfo.className || '-' }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">座位号</div>
              <div class="info-value">{{ studentInfo.seatNumber || '-' }}</div>
            </div>
          </div>
        </div>

        <!-- 成绩概览卡片 -->
        <div class="dashboard-section card">
          <div class="section-header">
            <div class="section-title">成绩概览</div>
          </div>
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else>
            <div v-if="practiceScores.length > 0" class="score-chart-container">
              <canvas ref="chartCanvas"></canvas>
            </div>
            <div v-else class="no-records">
              <p>暂无成绩数据</p>
            </div>
          </div>
        </div>

        <!-- 练习记录卡片 -->
        <div class="dashboard-section card">
          <div class="section-header">
            <div class="section-title">练习记录</div>
          </div>
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="practiceScores.length > 0">
            <table class="practice-records">
              <thead>
                <tr>
                  <th>练习名称</th>
                  <th>总分</th>
                  <th>开始时间</th>
                  <th>完成时间</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(score, index) in practiceScores" :key="score.id || index" :class="{ selected: selectedIndex === index }" @click="selectRow(index)">
                  <td>{{ score.practice }}</td>
                  <td><span class="score-badge">{{ score.totalScore }}</span></td>
                  <td><span class="date-time">{{ formatDate(score.startedAt) }}</span></td>
                  <td>
                    <span class="date-time">{{ score.finishedAt ? formatDate(score.finishedAt) : '-' }}</span>
                  </td>
                  <td>
                    <span :class="['practice-status', score.finishedAt ? 'status-completed' : 'status-in-progress']">
                      {{ score.finishedAt ? '已完成' : '进行中' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="no-records">
            <p>暂无练习记录</p>
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
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getStudentPracticeScores } from '@/api/practice'
import { getUserById, changePassword } from '@/api/user'
import type { PracticeScore } from '@/api/practice'

const router = useRouter()
const userStore = useUserStore()

const chartCanvas = ref<HTMLCanvasElement | null>(null)
const selectedIndex = ref<number | null>(null)
const loading = ref(false)
const studentInfo = ref({
  className: '',
  seatNumber: ''
})
const practiceScores = ref<PracticeScore[]>([])

let chartInstance: any = null

// 修改密码相关
const changePasswordDialogVisible = ref(false)
const passwordSubmitting = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
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

const selectRow = (index: number) => {
  selectedIndex.value = selectedIndex.value === index ? null : index
}

const formatDate = (date: string) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
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

      // 清空表单
      passwordForm.value = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      changePasswordDialogVisible.value = false

      // 2秒后跳转到登录页面
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

const initChart = async () => {
  if (!chartCanvas.value || practiceScores.value.length === 0) return

  try {
    // 动态导入Chart.js
    const chartModule = await import('chart.js')
    const { Chart, registerables } = chartModule
    Chart.register(...registerables)

    const ctx = chartCanvas.value!.getContext('2d')
    if (!ctx) return

    // 按日期排序
    const sortedScores = [...practiceScores.value].sort((a, b) => 
      new Date(a.startedAt).getTime() - new Date(b.startedAt).getTime()
    )

    const labels = sortedScores.map(item => item.practice)
    const scores = sortedScores.map(item => item.totalScore)

    // 如果已有图表实例，先销毁
    if (chartInstance) {
      chartInstance.destroy()
    }

    chartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: '练习分数',
          data: scores,
          backgroundColor: 'rgba(153, 182, 180, 0.2)',
          borderColor: '#99B6B4',
          borderWidth: 2,
          pointBackgroundColor: '#99B6B4',
          pointRadius: 4,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
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
    console.error('Chart.js 加载失败，图表功能不可用', error)
    // 如果Chart.js未安装，隐藏图表容器
    if (chartCanvas.value) {
      const container = chartCanvas.value.parentElement
      if (container) {
        container.style.display = 'none'
      }
    }
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

    // 初始化图表
    setTimeout(() => {
      initChart()
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
    initChart()
  }, 100)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>

<style scoped>
.student-dashboard {
  width: 100%;
}

.header {
  background-color: #FFFFFF;
  color: #1A1A1A;
  padding: 20px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
  position: relative;
  overflow: hidden;
}

.header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #99B6B4, #BACFCE, #D48982, #DFB199);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 30px;
}

.header-left {
  display: flex;
  align-items: center;
}

h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  margin-left: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.back-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  background-color: #FFFFFF;
  color: #1A1A1A;
  border: 1px solid #BACFCE;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
}

.back-button:hover {
  background-color: rgba(186, 207, 206, 0.2);
}

.back-button svg {
  margin-right: 6px;
}

.change-password-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  background-color: #D48982;
  color: #FFFFFF;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.change-password-button:hover {
  background-color: #c07770;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.change-password-button svg {
  margin-right: 6px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 30px 30px;
}

/* 统一卡片样式 */
.card {
  background-color: #FFFFFF;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
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
  background: linear-gradient(90deg, #99B6B4, #BACFCE, #D48982, #DFB199);
}

.student-profile {
  margin-bottom: 30px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.profile-title {
  font-size: 18px;
  font-weight: 600;
  color: #1A1A1A;
}

.profile-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.info-item {
  margin-bottom: 15px;
}

.info-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.info-value {
  font-size: 16px;
  font-weight: 500;
  color: #1A1A1A;
}

.dashboard-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1A1A1A;
}

.score-chart-container {
  height: 300px;
  margin-bottom: 30px;
}

.practice-records {
  width: 100%;
  border-collapse: collapse;
}

.practice-records th,
.practice-records td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.practice-records th {
  font-weight: 500;
  color: #1A1A1A;
  background-color: rgba(186, 207, 206, 0.2);
}

.practice-records tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.practice-records tr:hover {
  background-color: rgba(186, 207, 206, 0.1);
}

.practice-records tr.selected {
  background-color: #1A1A1A;
  color: #FFFFFF;
}

.practice-records tr.selected td {
  color: #FFFFFF;
}

.score-badge {
  background-color: rgba(153, 182, 180, 0.2);
  color: #1A1A1A;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 500;
  display: inline-block;
}

.practice-status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-completed {
  background-color: rgba(153, 182, 180, 0.2);
  color: #1A1A1A;
}

.status-in-progress {
  background-color: rgba(223, 177, 153, 0.2);
  color: #1A1A1A;
}

.date-time {
  color: #666;
  font-size: 14px;
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

@media (max-width: 768px) {
  .profile-info {
    grid-template-columns: 1fr;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-left {
    margin-bottom: 10px;
  }

  .user-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>

