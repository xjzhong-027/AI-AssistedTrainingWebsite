<template>
  <div class="login-container">
    <div class="login-card">
      <div class="card-header">
        <h2>英语听力教学网站</h2>
        <p>请登录</p>
      </div>
      <el-form :model="form" label-width="80px" @submit.prevent="handleLogin">
        <el-form-item label="用户名">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="form.role">
            <el-radio label="student">学生</el-radio>
            <el-radio label="teacher">教师</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            @click="handleLogin"
            :loading="loading"
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>
        <el-form-item v-if="errorMessage" class="error-item">
          <el-alert :title="errorMessage" type="error" :closable="false" />
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { login, getCurrentUser } from '@/api/user'
import type { User } from '@/types/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const form = ref({
  username: '',
  password: '',
  role: 'student' as 'student' | 'teacher' | 'admin'
})

const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  // 验证输入
  if (!form.value.username) {
    errorMessage.value = '请输入用户名'
    return
  }
  if (!form.value.password) {
    errorMessage.value = '请输入密码'
    return
  }
  if (!form.value.role) {
    errorMessage.value = '请选择角色'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    // 调用登录API
    const loginResponse = await login({
      username: form.value.username,
      password: form.value.password,
      role: form.value.role
    })

    // 保存 Token
    userStore.setToken(loginResponse.access, loginResponse.refresh)

    // 获取用户信息
    try {
      const userInfo = await getCurrentUser()
      // 后端返回的格式：{ username, role, user_id }
      // 转换为前端 User 格式
      const user: User = {
        id: userInfo.user_id,
        username: userInfo.username,
        realName: userInfo.username, // 如果没有真实姓名，使用用户名
        email: '',
        role: userInfo.role.toUpperCase() as User['role'],
        createdAt: '',
        updatedAt: ''
      }
      userStore.setUser(user)
    } catch (error) {
      // 如果获取用户信息失败，使用登录返回的信息创建用户对象
      const user: User = {
        id: loginResponse.user_id,
        username: loginResponse.username,
        realName: loginResponse.username,
        email: '',
        role: loginResponse.role.toUpperCase() as User['role'],
        createdAt: '',
        updatedAt: ''
      }
      userStore.setUser(user)
    }

    ElMessage.success('登录成功')

    // 跳转到目标页面或根据角色跳转
    const redirect = (route.query.redirect as string) || getDefaultRedirect(loginResponse.role)
    await router.push(redirect)
  } catch (error: any) {
    console.error('登录失败', error)
    errorMessage.value = error?.message || '登录失败，请检查用户名、密码和角色是否正确'
    ElMessage.error(errorMessage.value)
  } finally {
    loading.value = false
  }
}

// 根据角色获取默认跳转路径
const getDefaultRedirect = (role: string): string => {
  switch (role) {
    case 'teacher':
      return '/teacher/dashboard'
    case 'student':
      return '/student/index'
    case 'admin':
      return '/teacher/dashboard'
    default:
      return '/dashboard'
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #1A1A1A; /* 主背景 - 深色 */
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background-color: #F9F8F3; /* 浅色背景 */
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.card-header h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 24px;
}

.card-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.error-item {
  margin-bottom: 0;
}

:deep(.el-form-item__label) {
  color: #333;
}

:deep(.el-input__wrapper) {
  background-color: #FFFFFF;
}

:deep(.el-radio-group) {
  width: 100%;
}

:deep(.el-radio) {
  margin-right: 20px;
}
</style>

