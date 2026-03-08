<template>
  <div class="change-password-page">
    <div class="container card">
      <!-- 返回首页按钮 -->
      <button class="back-button" @click="goToDashboard">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        返回首页
      </button>

      <h1>修改密码</h1>

      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
        class="password-form"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input
            v-model="form.oldPassword"
            type="password"
            placeholder="请输入旧密码"
            show-password
            autocomplete="off"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="form.newPassword"
            type="password"
            placeholder="请输入新密码"
            show-password
            autocomplete="off"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
            autocomplete="off"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit" class="submit-button">
            确定
          </el-button>
          <el-button @click="handleReset" class="reset-button">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { changePassword } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirm = (_rule: unknown, value: string, callback: (e?: Error) => void) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== form.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const formRules: FormRules = {
  oldPassword: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}

const handleReset = () => {
  form.oldPassword = ''
  form.newPassword = ''
  form.confirmPassword = ''
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await changePassword(form.oldPassword, form.newPassword)
      ElMessage.success('密码修改成功，请重新登录')
      handleReset()
      setTimeout(() => {
        userStore.logout()
        router.push('/login')
      }, 2000)
    } catch (error: any) {
      ElMessage.error(error.message || '修改密码失败')
    } finally {
      submitting.value = false
    }
  })
}

const goToDashboard = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.change-password-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #FAFBFC 0%, #F5F7FA 100%);
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.container {
  width: 90%;
  max-width: 600px;
  padding: 32px;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
}

.card {
  background-color: #FFFFFF;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  position: relative;
  overflow: hidden;
  width: 100%;
  display: flex;
  flex-direction: column;
  max-width: 600px;
}

.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF);
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background-color: #FFFFFF;
  color: #8C7CF0;
  border: 2px solid #E8E4FF;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
  margin-bottom: 24px;
  align-self: flex-start;
}

.back-button:hover {
  background-color: #E8E4FF;
  border-color: #8C7CF0;
  transform: translateX(-4px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2);
}

h1 {
  text-align: center;
  color: #1A202C;
  margin-bottom: 32px;
  font-size: 28px;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

.password-form {
  width: 100%;
  max-width: 400px;
  align-self: center;
}

:deep(.el-form-item__label) {
  color: #4A5568;
  font-weight: 500;
  font-size: 14px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid #F0F2F5;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: #E8E4FF;
  box-shadow: 0 0 0 2px rgba(140, 124, 240, 0.1);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #8C7CF0;
  box-shadow: 0 0 0 2px rgba(140, 124, 240, 0.2);
}

:deep(.el-button) {
  border-radius: 12px;
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.submit-button {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF) !important;
  border: none !important;
  color: #FFFFFF !important;
  margin-right: 12px;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3) !important;
}

.reset-button {
  background-color: #FFFFFF !important;
  border: 2px solid #E8E4FF !important;
  color: #8C7CF0 !important;
}

.reset-button:hover {
  background-color: #E8E4FF !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.1) !important;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__error) {
  font-size: 12px;
  color: #F56C6C;
}
</style>
