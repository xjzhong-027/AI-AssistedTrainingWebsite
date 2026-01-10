<template>
  <div class="container">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <ul>
        <!-- 学生端菜单 -->
        <template v-if="userStore.isStudent()">
          <li>
            <router-link to="/dashboard">首页</router-link>
          </li>
          <li>
            <router-link to="/student/dashboard">个人信息</router-link>
          </li>
          <li>
            <router-link to="/practice/list">练习</router-link>
          </li>
          <li>
            <router-link to="/exams">考试</router-link>
          </li>
          <li>
            <router-link to="/forum">论坛</router-link>
          </li>
          <li>
            <router-link to="/announcements">公告栏</router-link>
          </li>
          <li>
            <router-link to="/messages">消息箱</router-link>
          </li>
        </template>
        <!-- 教师端菜单 -->
        <template v-else-if="userStore.isTeacher()">
          <li>
            <router-link to="/teacher/week-task">周任务</router-link>
          </li>
          <li>
            <router-link to="/teacher/question-bank">题库管理</router-link>
          </li>
          <li>
            <router-link to="/teacher/exam-bank">任务管理</router-link>
          </li>
          <li>
            <router-link to="/teacher/forum">论坛管理</router-link>
          </li>
          <li>
            <router-link to="/announce/announcements">公告管理</router-link>
          </li>
          <li>
            <router-link to="/announce/messages">消息箱</router-link>
          </li>
          <li>
            <router-link to="/query">检索面板</router-link>
          </li>
          <li>
            <router-link to="/teacher/index">附件下载</router-link>
          </li>
        </template>
        <!-- 退出登录 -->
        <li>
          <a @click="handleLogout">退出登录</a>
        </li>
      </ul>
    </aside>

    <!-- 内容区域 -->
    <main class="content">
      <!-- 显示消息 -->
      <div v-if="messages.length > 0" class="messages">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['alert', `alert-${message.type}`]"
        >
          {{ message.text }}
        </div>
      </div>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 消息提示（可以从 store 或全局状态管理获取）
const messages = ref<Array<{ type: string; text: string }>>([])

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      userStore.clearUser()
      ElMessage.success('已退出登录')
      router.push('/login')
    })
    .catch(() => {})
}
</script>

<style scoped>
.container {
  display: flex;
  min-height: 100vh;
  position: relative;
}

/* 侧边栏样式 - 新设计 */
.sidebar {
  width: 180px;
  background-color: #FFFFFF;
  padding: 20px;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  z-index: 100;
  overflow-y: auto;
  box-sizing: border-box;
}

.sidebar ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.sidebar ul li {
  margin-bottom: 15px;
}

.sidebar ul li a {
  color: #1A1A1A;
  text-decoration: none;
  font-size: 16px;
  display: block;
  padding: 10px;
  border-radius: 6px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.sidebar ul li a:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #1A1A1A;
}

/* 选中状态的侧边栏链接 - 深色背景 */
.sidebar ul li a.router-link-active,
.sidebar ul li a.router-link-exact-active {
  background-color: #1A1A1A;
  color: #FFFFFF;
}

/* 主要内容区域样式 */
.content {
  flex-grow: 1;
  padding: 30px;
  background-color: #F9F8F3;
  margin-left: 180px;
  min-height: 100vh;
  width: calc(100% - 180px);
  box-sizing: border-box;
}

/* 消息提示区域 */
.messages {
  margin: 10px;
  padding: 10px;
}

.alert {
  padding: 10px;
  margin: 5px 0;
  border-radius: 4px;
}

.alert-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

/* 按钮样式 */
.btn {
  display: inline-block;
  padding: 10px 20px;
  font-size: 16px;
  color: #fff;
  background-color: #3498db;
  border: none;
  border-radius: 4px;
  text-align: center;
  text-decoration: none;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #2980b9;
}

.btn-primary {
  background-color: #3498db;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.mb-4 {
  margin-bottom: 1.5rem;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

