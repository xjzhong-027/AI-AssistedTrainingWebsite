<template>
  <div class="container">
    <!-- 顶部导航栏 - 仅在首页显示 -->
    <header v-if="isDashboardPage" class="top-nav">
      <div class="top-nav-content">
        <div class="top-nav-left">
          <span class="logo">AI-AssistedTrainingWebsite</span>
        </div>
        <div class="top-nav-right">
          <router-link v-if="userStore.isStudent()" to="/profile/change-password" class="top-nav-item">
            <svg class="top-nav-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <span>修改密码</span>
          </router-link>
          <a @click="handleLogout" class="top-nav-item">
            <svg class="top-nav-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            <span>退出登录</span>
          </a>
          <span class="user-name">{{ userStore.userInfo?.realName || '用户' }}</span>
          <div class="user-avatar">
            {{ userStore.userInfo?.realName?.charAt(0) || 'U' }}
          </div>
        </div>
      </div>
    </header>

    <!-- 侧边栏 - 仅在首页显示 -->
    <aside v-if="isDashboardPage" class="sidebar">
      <ul>
        <!-- 学生端菜单 -->
        <template v-if="userStore.isStudent()">
          <li>
            <router-link to="/dashboard" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              <span>首页</span>
            </router-link>
          </li>
          <li>
            <router-link to="/student/dashboard" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 20h9"></path>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
              </svg>
              <span>学习行为评估</span>
            </router-link>
          </li>
          <li>
            <router-link to="/practice/list" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
              </svg>
              <span>练习</span>
            </router-link>
          </li>
          <li>
            <router-link to="/exams" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              <span>考试</span>
            </router-link>
          </li>
          <li>
            <router-link to="/forum" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
              <span>论坛</span>
            </router-link>
          </li>
          <li>
            <router-link to="/announcements" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              </svg>
              <span>公告栏</span>
            </router-link>
          </li>
          <li>
            <router-link to="/messages" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
              </svg>
              <span>消息箱</span>
            </router-link>
          </li>
        </template>
        <!-- 教师端菜单 -->
        <template v-else-if="userStore.isTeacher()">
          <li>
            <router-link to="/teacher/dashboard" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              <span>首页</span>
            </router-link>
          </li>
          <li>
            <router-link to="/teacher/week-task" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              <span>周任务</span>
            </router-link>
          </li>
          <li>
            <router-link to="/teacher/question-bank" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
              </svg>
              <span>题库管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/teacher/exam-bank" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 20h9"></path>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
              </svg>
              <span>任务管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/teacher/course" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              </svg>
              <span>课程管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/teacher/class" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              <span>班级管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/teacher/forum" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
              <span>论坛管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/teacher/announcements" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              </svg>
              <span>公告管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/announce/messages" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
              </svg>
              <span>消息箱</span>
            </router-link>
          </li>
          <li>
            <router-link to="/query" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <span>检索面板</span>
            </router-link>
          </li>
          <li>
            <router-link to="/teacher/index" class="nav-item">
              <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              <span>附件下载</span>
            </router-link>
          </li>
        </template>
      </ul>
    </aside>

    <!-- 内容区域 -->
    <main class="content" :class="{ 'has-sidebar': isDashboardPage }">
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
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 判断是否为首页
const isDashboardPage = computed(() => {
  return route.path === '/dashboard' || route.path === '/' || route.path === '/student/index' || route.path.startsWith('/teacher/')
})

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

/* 顶部导航栏 */
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background-color: #FFFFFF;
  z-index: 100;
  border-bottom: 1px solid #F0F2F5;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
}

.top-nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 32px;
}

.top-nav-left .logo {
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.top-nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.top-nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #4A5568;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.top-nav-item:hover {
  background-color: #F5F7FA;
  color: #8C7CF0;
}

.top-nav-icon {
  width: 20px;
  height: 20px;
  color: #8B9BB4;
  flex-shrink: 0;
}

.top-nav-item:hover .top-nav-icon {
  color: #8C7CF0;
}

.user-name {
  font-size: 14px;
  color: #4A5568;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-size: 16px;
  font-weight: 600;
}

/* 侧边栏样式 - Modern Soft-Neo UI */
.sidebar {
  width: 240px;
  background-color: #FFFFFF;
  padding: 24px 16px;
  position: fixed;
  left: 0;
  top: 64px;
  height: calc(100vh - 64px);
  box-shadow: 0 0 20px rgba(140, 124, 240, 0.1);
  border-right: 1px solid #F0F2F5;
  z-index: 99;
  overflow-y: auto;
  box-sizing: border-box;
}

.sidebar ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.sidebar ul li {
  margin-bottom: 4px;
}

.nav-item {
  color: #4A5568;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.nav-icon {
  width: 24px;
  height: 24px;
  color: #8B9BB4;
  flex-shrink: 0;
}

.nav-item:hover {
  background-color: #F5F7FA;
  color: #8C7CF0;
}

.nav-item:hover .nav-icon {
  color: #8C7CF0;
}

/* 选中状态的侧边栏链接 - Modern Soft-Neo UI */
.nav-item.router-link-active,
.nav-item.router-link-exact-active {
  background: linear-gradient(135deg, #E8E4FF, #F5F3FF);
  color: #8C7CF0;
}

.nav-item.router-link-active .nav-icon,
.nav-item.router-link-exact-active .nav-icon {
  color: #8C7CF0;
}

/* 主要内容区域样式 */
.content {
  flex-grow: 1;
  padding: 32px;
  background-color: #FAFBFC;
  margin-left: 0;
  margin-top: 0;
  min-height: 100vh;
  width: 100%;
  box-sizing: border-box;
  transition: all 0.2s ease;
}

.content.has-sidebar {
  margin-left: 240px;
  width: calc(100% - 240px);
  margin-top: 64px;
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

