<template>
  <div class="dashboard">
    <div class="dashboard-content">
      <!-- 欢迎卡片 -->
      <div class="welcome-card card">
        <div class="welcome-illustration">
          <div class="english-student">
            <!-- 身体 -->
            <div class="student-body">
              <!-- 头部 -->
              <div class="student-head">
                <!-- 头发 -->
                <div class="hair-back"></div>
                <div class="hair-front">
                  <div class="bang bang-1"></div>
                  <div class="bang bang-2"></div>
                  <div class="bang bang-3"></div>
                </div>
                <!-- 脸部 -->
                <div class="student-face">
                  <!-- 眼睛 -->
                  <div class="student-eyes">
                    <div class="student-eye left">
                      <div class="eye-pupil"></div>
                      <div class="eye-shine"></div>
                    </div>
                    <div class="student-eye right">
                      <div class="eye-pupil"></div>
                      <div class="eye-shine"></div>
                    </div>
                  </div>
                  <!-- 眉毛 -->
                  <div class="eyebrow left"></div>
                  <div class="eyebrow right"></div>
                  <!-- 腮红 -->
                  <div class="student-blush left"></div>
                  <div class="student-blush right"></div>
                  <!-- 嘴巴 -->
                  <div class="student-mouth">
                    <div class="mouth-smile"></div>
                  </div>
                </div>
              </div>
              <!-- 耳机 -->
              <div class="headphones">
                <div class="headband"></div>
                <div class="earcup left">
                  <div class="earcup-inner"></div>
                </div>
                <div class="earcup right">
                  <div class="earcup-inner"></div>
                </div>
              </div>
              <!-- 身体部分 -->
              <div class="student-torso">
                <!-- 衣服 -->
                <div class="shirt">
                  <div class="shirt-collar"></div>
                  <div class="shirt-logo">ABC</div>
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
              <!-- 腿 -->
              <div class="leg left"></div>
              <div class="leg right"></div>
              <!-- 脚 -->
              <div class="shoe left"></div>
              <div class="shoe right"></div>
            </div>
            <!-- 装饰元素 -->
            <div class="student-decorations">
              <div class="letter l1">A</div>
              <div class="letter l2">B</div>
              <div class="letter l3">C</div>
              <div class="star s1">⭐</div>
              <div class="star s2">✨</div>
              <div class="speech-bubble">
                <span>Hello!</span>
              </div>
            </div>
          </div>
        </div>
        <div class="welcome-content">
          <h1 class="welcome-title">欢迎回来, {{ userStore.userInfo?.realName || '同学' }}!</h1>
          <p class="welcome-subtitle">准备好开始今天的学习之旅了吗？</p>
          <div class="welcome-stats">
            <div class="stat-item">
              <div class="stat-icon completed">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.completedTasks }}</div>
                <div class="stat-label">已完成任务</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon score">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
      </div>

      <!-- 学习概览卡片 -->
      <div class="overview-section">
        <div class="section-header">
          <h2 class="section-title">学习概览</h2>
          <span class="section-subtitle">本周学习情况</span>
        </div>
        <div class="overview-grid">
          <div class="overview-card card">
            <div class="card-icon practice">
              <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
              </svg>
            </div>
            <div class="card-content">
              <h3 class="card-title">练习</h3>
              <p class="card-description">完成 {{ statistics.practiceCount }} 个练习任务</p>
              <div class="card-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: statistics.practiceProgress + '%' }"></div>
                </div>
                <span class="progress-text">{{ statistics.practiceProgress }}%</span>
              </div>
            </div>
          </div>
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
              <h3 class="card-title">考试</h3>
              <p class="card-description">参加 {{ statistics.examCount }} 次考试</p>
              <div class="card-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: statistics.examProgress + '%' }"></div>
                </div>
                <span class="progress-text">{{ statistics.examProgress }}%</span>
              </div>
            </div>
          </div>
          <div class="overview-card card">
            <div class="card-icon forum">
              <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <div class="card-content">
              <h3 class="card-title">论坛</h3>
              <p class="card-description">发布 {{ statistics.forumCount }} 条帖子</p>
              <div class="card-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: statistics.forumProgress + '%' }"></div>
                </div>
                <span class="progress-text">{{ statistics.forumProgress }}%</span>
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
import { getStudentPracticeRecords } from '@/api/practice'
import { getAllExams } from '@/api/exam'
import { getAllPosts } from '@/api/forum'
import AIWindow from '@/components/common/AIWindow/index.vue'
import type { ExamRecord } from '@/api/practice'

const userStore = useUserStore()

const statistics = ref({
  completedTasks: 0,
  averageScore: 0,
  studyTime: '0h',
  practiceCount: 0,
  practiceProgress: 0,
  examCount: 0,
  examProgress: 0,
  forumCount: 0,
  forumProgress: 0
})

const loadStatistics = async () => {
  try {
    const studentId = userStore.userInfo?.id
    
    // 获取练习记录
    const practiceRecords = await getStudentPracticeRecords(studentId)
    const completedPractices = practiceRecords.filter((r: ExamRecord) => r.status === 'completed' && r.total_score != null)
    
    // 计算已完成任务数
    statistics.value.completedTasks = completedPractices.length
    
    // 计算平均得分
    const totalScore = completedPractices.reduce((sum: number, r: ExamRecord) => sum + (parseFloat(String(r.total_score)) || 0), 0)
    statistics.value.averageScore = completedPractices.length > 0 
      ? Math.round((totalScore / completedPractices.length) * 10) / 10 
      : 0
    
    // 计算学习时长（本周）
    const now = new Date()
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    const studyMinutes = completedPractices.reduce((sum: number, r: ExamRecord) => {
      const start = r.start_time ? new Date(r.start_time).getTime() : 0
      const end = r.submit_time ? new Date(r.submit_time).getTime() : 0
      return sum + (end > start ? Math.round((end - start) / 60000) : 0)
    }, 0)
    const studyHours = Math.floor(studyMinutes / 60)
    const studyMins = studyMinutes % 60
    statistics.value.studyTime = studyHours > 0 ? `${studyHours}h${studyMins}min` : `${studyMins}min`
    
    // 练习统计
    statistics.value.practiceCount = completedPractices.length
    statistics.value.practiceProgress = Math.min(100, completedPractices.length * 10)
    
    // 获取考试记录
    const examRecords = await getAllExams(studentId, 'exam')
    const completedExams = examRecords.filter((r: any) => r.status === 'completed' || r.submitted)
    statistics.value.examCount = completedExams.length
    statistics.value.examProgress = Math.min(100, completedExams.length * 20)
    
    // 获取论坛帖子数
    const posts = await getAllPosts({ author: studentId })
    statistics.value.forumCount = posts.length
    statistics.value.forumProgress = Math.min(100, posts.length * 10)
    
  } catch (error) {
    console.error('加载统计数据失败', error)
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #FAFBFC 0%, #F5F7FA 100%);
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

/* 欢迎卡片 */
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

/* 英语学习小人 */
.english-student {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.student-body {
  width: 300px;
  height: 380px;
  position: relative;
  animation: student-bounce 2.5s ease-in-out infinite;
}

@keyframes student-bounce {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-12px) rotate(1deg);
  }
}

/* 头部 */
.student-head {
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

/* 头发 - 后面 */
.hair-back {
  position: absolute;
  width: 200px;
  height: 120px;
  background: linear-gradient(180deg, #5D4E37 0%, #4A3F2F 100%);
  border-radius: 50% 50% 30% 30%;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 8;
}

/* 头发 - 前面刘海 */
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
  background: linear-gradient(180deg, #5D4E37 0%, #4A3F2F 100%);
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

/* 脸部 */
.student-face {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -45%);
  width: 140px;
  height: 100px;
}

/* 眉毛 */
.eyebrow {
  position: absolute;
  width: 30px;
  height: 4px;
  background: #5D4E37;
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

/* 眼睛 */
.student-eyes {
  display: flex;
  justify-content: space-between;
  width: 90px;
  margin: 30px auto 0;
}

.student-eye {
  width: 32px;
  height: 38px;
  background: #FFFFFF;
  border-radius: 50%;
  position: relative;
  border: 2px solid #E8E4FF;
  animation: student-blink 4s ease-in-out infinite;
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

@keyframes student-blink {
  0%, 92%, 100% {
    transform: scaleY(1);
  }
  96% {
    transform: scaleY(0.1);
  }
}

/* 腮红 */
.student-blush {
  position: absolute;
  width: 28px;
  height: 18px;
  background: linear-gradient(180deg, rgba(255, 182, 193, 0.7) 0%, rgba(255, 160, 180, 0.5) 100%);
  border-radius: 50%;
  top: 55px;
}

.student-blush.left {
  left: 8px;
}

.student-blush.right {
  right: 8px;
}

/* 嘴巴 */
.student-mouth {
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

/* 耳机 */
.headphones {
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 220px;
  height: 140px;
  z-index: 15;
}

.headband {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 100px;
  border: 12px solid #8C7CF0;
  border-bottom: none;
  border-radius: 100px 100px 0 0;
}

.earcup {
  position: absolute;
  width: 50px;
  height: 70px;
  background: linear-gradient(180deg, #8C7CF0 0%, #6B5DD3 100%);
  border-radius: 15px;
  top: 60px;
}

.earcup.left {
  left: 0;
}

.earcup.right {
  right: 0;
}

.earcup-inner {
  position: absolute;
  width: 30px;
  height: 50px;
  background: linear-gradient(180deg, #C6B9FF 0%, #A89AE8 100%);
  border-radius: 10px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 身体 */
.student-torso {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  width: 140px;
  height: 130px;
  background: linear-gradient(180deg, #8C7CF0 0%, #6B5DD3 100%);
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

.shirt-logo {
  position: absolute;
  top: 45px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
  background: linear-gradient(135deg, #FFE082 0%, #FFB74D 100%);
  padding: 5px 12px;
  border-radius: 15px;
  letter-spacing: 2px;
}

/* 手臂 */
.arm {
  position: absolute;
  width: 35px;
  height: 90px;
  background: linear-gradient(180deg, #8C7CF0 0%, #6B5DD3 100%);
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

/* 左手拿书 */
.hand-holding {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 40px;
}

.book {
  position: absolute;
  width: 45px;
  height: 35px;
  bottom: 0;
}

.book-cover {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #A8D5BA 0%, #8BC4A8 100%);
  border-radius: 3px;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
}

.book-pages {
  position: absolute;
  width: 35px;
  height: 30px;
  background: #FFFFFF;
  right: 0;
  top: 2px;
  border-radius: 0 3px 3px 0;
}

/* 右手比耶 */
.hand-peace {
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
}

.finger.f1 {
  transform: rotate(-10deg);
}

.finger.f2 {
  transform: rotate(10deg);
  height: 28px;
}

/* 腿 */
.leg {
  position: absolute;
  width: 45px;
  height: 90px;
  background: linear-gradient(180deg, #2D3748 0%, #1A202C 100%);
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

/* 鞋子 */
.shoe {
  position: absolute;
  width: 55px;
  height: 30px;
  background: linear-gradient(180deg, #8C7CF0 0%, #6B5DD3 100%);
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

/* 装饰元素 */
.student-decorations {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.letter {
  position: absolute;
  font-size: 28px;
  font-weight: 700;
  color: #8C7CF0;
  animation: letter-float 3s ease-in-out infinite;
  text-shadow: 2px 2px 4px rgba(140, 124, 240, 0.3);
}

.letter.l1 {
  top: 30px;
  left: 20px;
  animation-delay: 0s;
}

.letter.l2 {
  top: 80px;
  right: 30px;
  font-size: 24px;
  color: #A8D5BA;
  animation-delay: 0.5s;
}

.letter.l3 {
  bottom: 120px;
  left: 40px;
  font-size: 22px;
  color: #FFB74D;
  animation-delay: 1s;
}

.star {
  position: absolute;
  font-size: 20px;
  animation: letter-float 2.5s ease-in-out infinite;
}

.star.s1 {
  top: 50px;
  right: 20px;
  animation-delay: 0.3s;
}

.star.s2 {
  bottom: 150px;
  right: 50px;
  font-size: 16px;
  animation-delay: 0.8s;
}

@keyframes letter-float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.8;
  }
  50% {
    transform: translateY(-15px) rotate(5deg);
    opacity: 1;
  }
}

/* 对话气泡 */
.speech-bubble {
  position: absolute;
  top: -20px;
  right: 20px;
  background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FF 100%);
  padding: 12px 20px;
  border-radius: 20px 20px 5px 20px;
  box-shadow: 0 4px 15px rgba(140, 124, 240, 0.2);
  animation: bubble-pop 3s ease-in-out infinite;
  z-index: 20;
}

.speech-bubble span {
  font-size: 18px;
  font-weight: 600;
  color: #8C7CF0;
  letter-spacing: 1px;
}

.speech-bubble::before {
  content: '';
  position: absolute;
  bottom: -10px;
  right: 0;
  width: 0;
  height: 0;
  border-left: 15px solid transparent;
  border-top: 15px solid #FFFFFF;
}

@keyframes bubble-pop {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.welcome-content {
  flex: 1;
  min-width: 0;
}

.welcome-title {
  font-size: 48px;
  font-weight: 700;
  color: #1A202C;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.welcome-subtitle {
  font-size: 20px;
  color: #4A5568;
  margin-bottom: 40px;
  line-height: 1.6;
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
  background: linear-gradient(135deg, #FAFBFC 0%, #F5F7FA 100%);
  border-radius: 16px;
  border: 2px solid #F0F2F5;
  transition: all 0.3s ease;
}

.stat-item:hover {
  border-color: #E8E4FF;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.15);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  flex-shrink: 0;
}

.stat-icon.completed {
  background: linear-gradient(135deg, #A8D5BA 0%, #8BC4A8 100%);
}

.stat-icon.score {
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
}

.stat-icon.time {
  background: linear-gradient(135deg, #FFE082 0%, #FFB74D 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1A202C;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #8B9BB4;
  font-weight: 500;
}

/* 学习概览 */
.overview-section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #1A202C;
  margin: 0;
}

.section-subtitle {
  font-size: 16px;
  color: #8B9BB4;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.overview-card {
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  flex-shrink: 0;
}

.card-icon.practice {
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
}

.card-icon.exam {
  background: linear-gradient(135deg, #A8D5BA 0%, #8BC4A8 100%);
}

.card-icon.forum {
  background: linear-gradient(135deg, #FFE082 0%, #FFB74D 100%);
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 22px;
  font-weight: 700;
  color: #1A202C;
  margin: 0 0 8px 0;
}

.card-description {
  font-size: 16px;
  color: #4A5568;
  margin: 0 0 16px 0;
  line-height: 1.5;
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
  background: linear-gradient(90deg, #8C7CF0 0%, #C6B9FF 100%);
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

@media (max-width: 1200px) {
  .welcome-card {
    flex-direction: column;
    text-align: center;
    padding: 40px;
  }

  .welcome-illustration {
    width: 300px;
    height: 300px;
  }

  .character-body {
    width: 210px;
    height: 240px;
  }

  .character-head {
    width: 165px;
    height: 150px;
  }

  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-content {
    padding: 20px;
  }

  .welcome-stats {
    grid-template-columns: 1fr;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

  .welcome-title {
    font-size: 32px;
  }

  .section-title {
    font-size: 24px;
  }
}
</style>