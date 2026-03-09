<template>
  <div class="teacher-dashboard">
    <div class="dashboard-content">
      <div class="welcome-card card">
        <div class="welcome-illustration">
          <div class="teacher-character">
            <div class="teacher-body">
              <div class="teacher-head">
                <div class="hair-back"></div>
                <div class="hair-front">
                  <div class="bang bang-1"></div>
                  <div class="bang bang-2"></div>
                  <div class="bang bang-3"></div>
                </div>
                <div class="teacher-face">
                  <div class="teacher-eyes">
                    <div class="teacher-eye left">
                      <div class="eye-pupil"></div>
                      <div class="eye-shine"></div>
                    </div>
                    <div class="teacher-eye right">
                      <div class="eye-pupil"></div>
                      <div class="eye-shine"></div>
                    </div>
                  </div>
                  <div class="eyebrow left"></div>
                  <div class="eyebrow right"></div>
                  <div class="teacher-glasses">
                    <div class="glasses-frame left"></div>
                    <div class="glasses-bridge"></div>
                    <div class="glasses-frame right"></div>
                  </div>
                  <div class="teacher-blush left"></div>
                  <div class="teacher-blush right"></div>
                  <div class="teacher-mouth">
                    <div class="mouth-smile"></div>
                  </div>
                </div>
              </div>
              <div class="teacher-torso">
                <div class="shirt">
                  <div class="shirt-collar"></div>
                  <div class="shirt-tie"></div>
                </div>
              </div>
              <div class="arm left">
                <div class="hand-holding">
                  <div class="pointer">
                    <div class="pointer-stick"></div>
                    <div class="pointer-tip"></div>
                  </div>
                </div>
              </div>
              <div class="arm right">
                <div class="hand-wave">
                  <div class="finger f1"></div>
                  <div class="finger f2"></div>
                  <div class="finger f3"></div>
                </div>
              </div>
              <div class="leg left"></div>
              <div class="leg right"></div>
              <div class="shoe left"></div>
              <div class="shoe right"></div>
            </div>
            <div class="teacher-decorations">
              <div class="book b1">📚</div>
              <div class="book b2">📖</div>
              <div class="star s1">⭐</div>
              <div class="star s2">✨</div>
              <div class="speech-bubble">
                <span>Good morning!</span>
              </div>
            </div>
          </div>
        </div>
        <div class="welcome-content">
          <h1 class="welcome-title">欢迎回来, {{ userStore.userInfo?.realName || '老师' }}!</h1>
          <p class="welcome-subtitle">准备好开始今天的教学工作了吗？</p>
          <div class="welcome-stats">
            <div class="stat-item">
              <div class="stat-icon students">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ studentCount }}</div>
                <div class="stat-label">学生总数</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon courses">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                </svg>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ courseCount }}</div>
                <div class="stat-label">课程总数</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon assignments">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14,2 14,8 20,8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10,9 9,9 8,9"></polyline>
                </svg>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ assignmentCompletionRate }}%</div>
                <div class="stat-label">作业完成率</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="overview-section">
        <div class="overview-card card">
          <div class="card-icon exam">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <div class="card-content">
            <h3 class="card-title">考试通过率</h3>
            <p class="card-description">平均通过率 {{ examPassRate }}%</p>
            <div class="card-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: examPassRate + '%' }"></div>
              </div>
              <span class="progress-text">{{ examPassRate }}%</span>
            </div>
          </div>
        </div>
        <div class="overview-card card">
          <div class="card-icon tasks">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 20h9"></path>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
          </div>
          <div class="card-content">
            <h3 class="card-title">待批改任务</h3>
            <p class="card-description">还有 {{ pendingGrading }} 个任务待批改</p>
            <div class="card-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (100 - pendingGrading * 10) + '%' }"></div>
              </div>
              <span class="progress-text">{{ 100 - pendingGrading * 10 }}%</span>
            </div>
          </div>
        </div>
        <div class="overview-card card">
          <div class="card-icon messages">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <div class="card-content">
            <h3 class="card-title">新消息</h3>
            <p class="card-description">收到 {{ newMessages }} 条新消息</p>
            <div class="card-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: Math.min(100, newMessages * 10) + '%' }"></div>
              </div>
              <span class="progress-text">{{ Math.min(100, newMessages * 10) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <div class="bottom-section">
        <div class="activity-section">
          <div class="section-header">
            <h2>最近活动</h2>
          </div>
          <div class="activity-list">
            <div v-for="(activity, index) in recentActivities" :key="index" class="activity-item">
              <div class="activity-icon" :class="activity.type">
                <svg v-if="activity.type === 'assignment'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14,2 14,8 20,8"></polyline>
                </svg>
                <svg v-else-if="activity.type === 'exam'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                </svg>
                <svg v-else-if="activity.type === 'message'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
              </div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-time">{{ activity.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <AIWindow :show-grade-button="false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import AIWindow from '@/components/common/AIWindow/index.vue'
import { getAllClasses, getClassStudents } from '@/api/user'

const userStore = useUserStore()

const studentCount = ref(0)
const courseCount = ref(0)
const assignmentCompletionRate = ref(0)
const examPassRate = ref(0)
const pendingGrading = ref(0)
const newMessages = ref(0)

const recentActivities = ref([])

onMounted(async () => {
  await loadDashboardData()
  console.log('教师端首页已加载')
})

const loadDashboardData = async () => {
  try {
    const teacherId = userStore.userInfo?.id
    if (!teacherId) return

    // 获取教师的班级列表
    const classes = await getAllClasses(teacherId)
    
    // 课程总数就是班级数量（假设每个班级对应一门课程）
    courseCount.value = classes.length
    
    // 获取所有班级的学生
    let totalStudents = 0
    for (const cls of classes) {
      try {
        const students = await getClassStudents(cls.id)
        totalStudents += students.length
      } catch (error) {
        console.error(`获取班级 ${cls.id} 的学生列表失败`, error)
      }
    }
    
    // 学生总数
    studentCount.value = totalStudents
    
    // 其他数据暂时设为 0，因为没有对应的 API 接口
    assignmentCompletionRate.value = 0
    examPassRate.value = 0
    pendingGrading.value = 0
    newMessages.value = 0
    
    // 最近活动暂时为空数组
    recentActivities.value = []
    
  } catch (error) {
    console.error('加载仪表盘数据失败', error)
  }
}
</script>

<style scoped>
.teacher-dashboard {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #FAFBFC 0%, #F5F7FA 100%);
  padding: 0;
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px;
}

.card {
  background-color: #FFFFFF;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(140, 124, 240, 0.12);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF, #A8D5BA);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(140, 124, 240, 0.18);
}

.welcome-card {
  display: flex;
  align-items: center;
  gap: 60px;
  padding: 60px;
  margin-bottom: 40px;
  background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FF 100%);
}

.welcome-illustration {
  flex-shrink: 0;
  width: 400px;
  height: 400px;
  position: relative;
}

.teacher-character {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.teacher-body {
  width: 300px;
  height: 380px;
  position: relative;
  animation: teacher-bounce 2.5s ease-in-out infinite;
}

@keyframes teacher-bounce {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-12px) rotate(1deg);
  }
}

.teacher-head {
  width: 180px;
  height: 170px;
  background: linear-gradient(180deg, #FFE4C4 0%, #FFDAB9 100%);
  border-radius: 50% 50% 45% 45%;
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  box-shadow: 0 10px 30px rgba(255, 218, 185, 0.4),
              inset 0 -10px 20px rgba(255, 182, 193, 0.2);
  z-index: 10;
}

.hair-back {
  position: absolute;
  width: 200px;
  height: 120px;
  background: linear-gradient(180deg, #2C1810 0%, #1A0F0A 100%);
  border-radius: 50% 50% 30% 30%;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 8;
}

.hair-front {
  position: absolute;
  top: 5px;
  left: 50%;
  transform: translateX(-50%);
  width: 160px;
  height: 60px;
  z-index: 12;
}

.bang {
  position: absolute;
  background: linear-gradient(180deg, #2C1810 0%, #1A0F0A 100%);
  border-radius: 0 0 50% 50%;
}

.bang-1 {
  width: 60px;
  height: 50px;
  left: 10px;
  top: 0;
  transform: rotate(-10deg);
}

.bang-2 {
  width: 70px;
  height: 55px;
  left: 50%;
  transform: translateX(-50%);
  top: -5px;
}

.bang-3 {
  width: 60px;
  height: 50px;
  right: 10px;
  top: 0;
  transform: rotate(10deg);
}

.teacher-face {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -45%);
  width: 140px;
  height: 100px;
}

.eyebrow {
  position: absolute;
  width: 30px;
  height: 4px;
  background: #2C1810;
  border-radius: 2px;
  top: 15px;
}

.eyebrow.left {
  left: 20px;
  transform: rotate(-5deg);
}

.eyebrow.right {
  right: 20px;
  transform: rotate(5deg);
}

.teacher-eyes {
  display: flex;
  justify-content: space-between;
  width: 90px;
  margin: 30px auto 0;
}

.teacher-eye {
  width: 32px;
  height: 38px;
  background: #FFFFFF;
  border-radius: 50%;
  position: relative;
  border: 2px solid #E8E4FF;
  animation: teacher-blink 4s ease-in-out infinite;
}

.eye-pupil {
  position: absolute;
  width: 18px;
  height: 22px;
  background: linear-gradient(180deg, #8C7CF0 0%, #6B5DD3 100%);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.eye-shine {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #FFFFFF;
  border-radius: 50%;
  top: 8px;
  right: 5px;
}

@keyframes teacher-blink {
  0%, 92%, 100% {
    transform: scaleY(1);
  }
  96% {
    transform: scaleY(0.1);
  }
}

.teacher-glasses {
  position: absolute;
  top: 25px;
  left: 50%;
  transform: translateX(-50%);
  width: 110px;
  height: 50px;
  z-index: 15;
}

.glasses-frame {
  position: absolute;
  width: 40px;
  height: 40px;
  border: 3px solid #2C1810;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  top: 5px;
}

.glasses-frame.left {
  left: 0;
}

.glasses-frame.right {
  right: 0;
}

.glasses-bridge {
  position: absolute;
  width: 20px;
  height: 3px;
  background: #2C1810;
  top: 25px;
  left: 50%;
  transform: translateX(-50%);
}

.teacher-blush {
  position: absolute;
  width: 28px;
  height: 18px;
  background: linear-gradient(180deg, rgba(255, 182, 193, 0.7) 0%, rgba(255, 160, 180, 0.5) 100%);
  border-radius: 50%;
  top: 55px;
}

.teacher-blush.left {
  left: 8px;
}

.teacher-blush.right {
  right: 8px;
}

.teacher-mouth {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 35px;
  height: 18px;
}

.mouth-smile {
  width: 100%;
  height: 100%;
  border: 3px solid #FF6B9D;
  border-top: none;
  border-radius: 0 0 35px 35px;
  background: transparent;
}

.teacher-torso {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  width: 140px;
  height: 130px;
  background: linear-gradient(180deg, #2C3E50 0%, #1A252F 100%);
  border-radius: 40px 40px 30px 30px;
  z-index: 5;
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
  width: 60px;
  height: 25px;
  background: #FFFFFF;
  border-radius: 0 0 30px 30px;
}

.shirt-tie {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 50px;
  background: linear-gradient(180deg, #8C7CF0 0%, #6B5DD3 100%);
  border-radius: 10px 10px 5px 5px;
}

.arm {
  position: absolute;
  width: 35px;
  height: 90px;
  background: linear-gradient(180deg, #2C3E50 0%, #1A252F 100%);
  border-radius: 17px;
  top: 160px;
  z-index: 8;
}

.arm.left {
  left: 55px;
  transform: rotate(-20deg);
  transform-origin: top center;
}

.arm.right {
  right: 55px;
  transform: rotate(20deg);
  transform-origin: top center;
}

.hand-holding {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 40px;
}

.pointer {
  position: absolute;
  width: 8px;
  height: 60px;
  bottom: 0;
}

.pointer-stick {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #8B4513 0%, #654321 100%);
  border-radius: 4px;
}

.pointer-tip {
  position: absolute;
  width: 12px;
  height: 12px;
  background: linear-gradient(180deg, #8C7CF0 0%, #6B5DD3 100%);
  border-radius: 50%;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
}

.hand-wave {
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 3px;
}

.finger {
  width: 10px;
  height: 25px;
  background: linear-gradient(180deg, #FFE4C4 0%, #FFDAB9 100%);
  border-radius: 5px;
  animation: wave-finger 0.8s ease-in-out infinite alternate;
}

.finger.f1 {
  transform: rotate(-15deg);
  animation-delay: 0s;
}

.finger.f2 {
  transform: rotate(0deg);
  animation-delay: 0.1s;
}

.finger.f3 {
  transform: rotate(15deg);
  animation-delay: 0.2s;
}

@keyframes wave-finger {
  0% {
    transform: rotate(-15deg);
  }
  100% {
    transform: rotate(15deg);
  }
}

.leg {
  position: absolute;
  width: 45px;
  height: 90px;
  background: linear-gradient(180deg, #2C3E50 0%, #1A252F 100%);
  border-radius: 10px;
  bottom: 0;
  z-index: 4;
}

.leg.left {
  left: 90px;
}

.leg.right {
  right: 90px;
}

.shoe {
  position: absolute;
  width: 55px;
  height: 30px;
  background: linear-gradient(180deg, #1A252F 0%, #0F1419 100%);
  border-radius: 15px 15px 5px 5px;
  bottom: -5px;
  z-index: 6;
}

.shoe.left {
  left: 85px;
}

.shoe.right {
  right: 85px;
}

.teacher-decorations {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.book {
  position: absolute;
  font-size: 28px;
  animation: float-book 3s ease-in-out infinite;
}

.book.b1 {
  top: 50px;
  left: 20px;
  animation-delay: 0s;
}

.book.b2 {
  bottom: 80px;
  right: 30px;
  animation-delay: 1s;
}

@keyframes float-book {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(5deg);
  }
}

.star {
  position: absolute;
  font-size: 20px;
  animation: twinkle 2s ease-in-out infinite;
}

.star.s1 {
  top: 30px;
  right: 40px;
  animation-delay: 0.5s;
}

.star.s2 {
  bottom: 120px;
  left: 40px;
  animation-delay: 1s;
}

@keyframes twinkle {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.speech-bubble {
  position: absolute;
  top: 20px;
  right: 20px;
  background: #FFFFFF;
  padding: 8px 16px;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2);
  font-size: 14px;
  font-weight: 600;
  color: #8C7CF0;
  animation: bubble-float 2s ease-in-out infinite;
}

.speech-bubble::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 20px;
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 10px solid #FFFFFF;
}

@keyframes bubble-float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.welcome-content {
  flex: 1;
}

.welcome-title {
  font-size: 36px;
  font-weight: 700;
  color: #1A202C;
  margin: 0 0 16px 0;
  background: linear-gradient(135deg, #8C7CF0 0%, #6B5DD3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  font-size: 18px;
  color: #8B9BB4;
  margin: 0 0 32px 0;
  font-weight: 500;
}

.welcome-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #F8F9FF 0%, #FFFFFF 100%);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(140, 124, 240, 0.15);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
}

.stat-icon.students {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
}

.stat-icon.courses {
  background: linear-gradient(135deg, #A8D5BA, #8BC4A8);
}

.stat-icon.assignments {
  background: linear-gradient(135deg, #FFE082, #FFB74D);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1A202C;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #8B9BB4;
  font-weight: 500;
}

.overview-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.overview-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
}

.card-icon.exam {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
}

.card-icon.tasks {
  background: linear-gradient(135deg, #A8D5BA, #8BC4A8);
}

.card-icon.messages {
  background: linear-gradient(135deg, #FFE082, #FFB74D);
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1A202C;
  margin: 0 0 8px 0;
}

.card-description {
  font-size: 14px;
  color: #8B9BB4;
  margin: 0 0 16px 0;
}

.card-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #F0F2F5;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF);
  border-radius: 4px;
  transition: width 0.6s ease;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #8C7CF0;
  min-width: 40px;
  text-align: right;
}

.bottom-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.activity-section,
.todo-section {
  padding: 24px;
}

.section-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #F0F2F5;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1A202C;
  margin: 0;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: #F5F7FA;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #FFFFFF;
}

.activity-icon.assignment {
  background: linear-gradient(135deg, #FFE082, #FFB74D);
}

.activity-icon.exam {
  background: linear-gradient(135deg, #FFB74D, #FFB6C1);
}

.activity-icon.message {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  color: #4A5568;
  font-weight: 500;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 12px;
  color: #8B9BB4;
}

@media (max-width: 1200px) {
  .welcome-card {
    flex-direction: column;
    text-align: center;
    padding: 40px;
  }

  .welcome-stats {
    grid-template-columns: 1fr;
  }

  .overview-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-content {
    padding: 16px;
  }

  .overview-section {
    grid-template-columns: 1fr;
  }

  .bottom-section {
    grid-template-columns: 1fr;
  }

  .welcome-title {
    font-size: 24px;
  }

  .welcome-illustration {
    width: 300px;
    height: 300px;
  }
}
</style>
