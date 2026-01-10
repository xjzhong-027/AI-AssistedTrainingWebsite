<template>
  <div class="dashboard">
      <!-- 欢迎卡片 -->
      <div class="welcome-card">
        <h1>欢迎, {{ userStore.userInfo?.realName || '用户' }}!</h1>
        <p>点击左侧边栏中的栏目以进行相应操作。</p>
      </div>
    </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
</script>

<style scoped>
.dashboard {
  padding: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 60px);
}

.welcome-card {
  background-color: #FFFFFF;
  border-radius: 20px;
  padding: 80px 100px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 800px;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #99B6B4, #BACFCE, #D48982, #DFB199);
}

.welcome-card::after {
  content: '';
  position: absolute;
  bottom: -50px;
  right: -50px;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(153, 182, 180, 0.1), transparent);
  border-radius: 50%;
}

.welcome-card h1 {
  font-size: 52px;
  font-weight: 700;
  color: #1A1A1A;
  margin-bottom: 30px;
  text-align: center;
  letter-spacing: 1px;
  position: relative;
  z-index: 1;
}

.welcome-card h1::after {
  content: '';
  position: absolute;
  bottom: -15px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #99B6B4, #D48982);
  border-radius: 2px;
}

.welcome-card p {
  font-size: 20px;
  color: #666;
  text-align: center;
  line-height: 2;
  position: relative;
  z-index: 1;
}
</style>

