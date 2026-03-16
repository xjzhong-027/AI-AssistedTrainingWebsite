<template>
  <div class="query-page">
      <div class="container card">
        <h1>检索面板</h1>
        <p class="description">数据查询和管理功能</p>
        
        <div class="query-sections">
          <div class="query-section card">
            <h3>考勤管理</h3>
            <p>查询和管理学生考勤记录</p>
            <button class="query-button" @click="goToAttendance">进入</button>
          </div>
          
          <div class="query-section card">
            <h3>调课补课管理</h3>
            <p>管理课程调整和补课安排</p>
            <button class="query-button" @click="goToScheduleAdjustment">进入</button>
          </div>
          
          <div class="query-section card">
            <h3>学习记录管理</h3>
            <p>查询学生学习记录和进度</p>
            <button class="query-button" @click="goToLearningRecord">进入</button>
          </div>
          
          <div class="query-section card">
            <h3>数据统计分析</h3>
            <p>查看班级和学生的统计数据</p>
            <button class="query-button" @click="goToStatistics">进入</button>
          </div>
          
          <div class="query-section card">
            <h3>逾期扣分规则</h3>
            <p>管理逾期作业和考试的扣分规则</p>
            <button class="query-button" @click="goToOverdueRules">进入</button>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goToAttendance = () => {
  router.push('/query/attendance')
}

const goToScheduleAdjustment = () => {
  router.push('/query/schedule-adjustment')
}

const goToLearningRecord = () => {
  router.push('/query/learning-record')
}

const goToStatistics = () => {
  router.push('/query/statistics')
}

const goToOverdueRules = () => {
  router.push('/query/overdue-rules')
}
</script>

<style scoped>
.query-page {
  width: 100%;
  padding: 0;
}

.container {
  max-width: 1200px;
  margin: 30px auto;
  padding: 40px;
}

h1 {
  text-align: center;
  color: #1A1A1A;
  margin-bottom: 10px;
  font-size: 36px;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

h1::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #99B6B4, #D48982);
  border-radius: 2px;
}

.description {
  text-align: center;
  color: #666;
  margin-bottom: 40px;
  font-size: 16px;
}

.query-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.query-section {
  padding: 30px;
  text-align: center;
  transition: all 0.3s ease;
}

.query-section:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.query-section h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 12px 0;
}

.query-section p {
  color: #666;
  margin: 0 0 20px 0;
  line-height: 1.6;
}

.query-button {
  padding: 10px 24px;
  background-color: #D48982;
  color: #FFFFFF;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.query-button:hover {
  background-color: #c07770;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>





