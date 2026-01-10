<template>
  <div class="week-task">
    <div class="header">
      <button @click="goHome">返回首页</button>
      <h2>周任务</h2>
      <button @click="goToNewTaskPackage">New task package</button>
    </div>
    <h1>周任务</h1>
    <p>点击左侧边栏中的栏目以进行相应操作。</p>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/teacher/index')
}

const goToNewTaskPackage = () => {
  // TODO: 导航到新建任务包页面
  // router.push('/teacher/week-task/package-add')
}
</script>

<style scoped>
.week-task {
  padding: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.header button {
  padding: 10px 20px;
  background-color: #E8ECA;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.header button:hover {
  background-color: #D8D8F6;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.week-task h1 {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 15px;
  text-align: center;
}

.week-task p {
  font-size: 16px;
  color: #666;
  text-align: center;
  line-height: 1.6;
}
</style>





