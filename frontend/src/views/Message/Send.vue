<template>
  <div class="send-message-page">
    <!-- 背景装饰元素 -->
    <div class="illustration-bg">
      <div class="illustration-circle circle-1"></div>
      <div class="illustration-circle circle-2"></div>
      <div class="illustration-star star-1"></div>
      <div class="illustration-star star-2"></div>
      <div class="illustration-star star-3"></div>
    </div>
    
    <div class="container card">
      <!-- 插画区域 -->
      <div class="illustration-header">
        <div class="illustration-email">
          <div class="email-body">
            <div class="email-top"></div>
            <div class="email-content">
              <div class="email-line line-1"></div>
              <div class="email-line line-2"></div>
              <div class="email-line line-3"></div>
            </div>
          </div>
          <div class="email-flag"></div>
          <div class="email-shine"></div>
        </div>
      </div>
      
      <!-- 返回按钮 -->
      <button class="back-button" @click="goBack">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        返回
      </button>
      
      <h1 class="title">发送消息</h1>
      
      <!-- 发送消息表单 -->
      <div class="send-message-form">
        <el-form :model="messageForm" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="接收者" prop="receiverId">
            <el-select v-model="messageForm.receiverId" placeholder="选择接收者" class="w-full">
              <el-option
                v-for="user in users"
                :key="`${user.type}-${user.id}`"
                :label="user.name"
                :value="`${user.type}-${user.id}`"
              />
            </el-select>
          </el-form-item>
          
  
          
          <el-form-item label="消息内容" prop="content">
            <el-input
              v-model="messageForm.content"
              type="textarea"
              placeholder="请输入消息内容"
              :rows="6"
              class="w-full"
            />
          </el-form-item>
          
          <el-form-item>
            <div class="form-actions">
              <button type="button" class="cancel-button" @click="goBack">
                取消
              </button>
              <button type="button" class="submit-button" @click="submitMessage" :disabled="loading">
                <span v-if="loading">发送中...</span>
                <span v-else>发送消息</span>
              </button>
            </div>
          </el-form-item>
        </el-form>
      </div>
      
      <AIWindow :show-grade-button="false" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { sendMessage } from '@/api/message'
import { getTeacherList, getAllClasses, getClassStudents } from '@/api/user'
import AIWindow from '@/components/common/AIWindow/index.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const users = ref<any[]>([])

const messageForm = ref({
  receiverId: '',
  content: ''
})

const rules = {
  receiverId: [
    { required: true, message: '请选择接收者', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入消息内容', trigger: 'blur' },
    { min: 1, max: 500, message: '内容长度应在1-500个字符之间', trigger: 'blur' }
  ]
}

const loadUsers = async () => {
  try {
    let teacherUsers: any[] = []
    let studentUsers: any[] = []
    
    // 获取教师列表
    try {
      const teachers = await getTeacherList()
      teacherUsers = teachers.map((teacher: any) => ({
        id: teacher.id,
        name: teacher.name || teacher.username || '未知教师',
        username: teacher.username,
        type: 'teacher'
      }))
    } catch (error) {
      console.error('获取教师列表失败', error)
      // 继续执行，不中断流程
    }
    
    // 获取班级列表和学生列表
    try {
      const classes = await getAllClasses()
      
      // 并行获取所有班级的学生列表
      const studentPromises = classes.map(async (cls: any) => {
        try {
          const students = await getClassStudents(cls.id)
          return students.map((student: any) => ({
            id: student.id,
            name: student.name || student.username || '未知学生',
            username: student.username,
            type: 'student'
          }))
        } catch (error) {
          console.error(`获取班级${cls.id}的学生列表失败`, error)
          return []
        }
      })
      
      const studentResults = await Promise.all(studentPromises)
      studentUsers = studentResults.flat()
    } catch (error) {
      console.error('获取学生列表失败', error)
      // 继续执行，不中断流程
    }
    
    // 合并教师和学生列表
    users.value = [...teacherUsers, ...studentUsers]
    
    // 打印用户列表，用于调试
    console.log('加载的用户列表:', users.value)
    
    // 如果没有用户，显示提示
    if (users.value.length === 0) {
      ElMessage.warning('暂无可用的接收者')
    }
  } catch (error) {
    console.error('加载用户列表失败', error)
    ElMessage.error('加载用户列表失败')
  }
}

const submitMessage = async () => {
  if (!formRef.value) return
  
  try {
    console.log('开始提交消息')
    
    await formRef.value.validate()
    
    loading.value = true
    
    console.log('表单验证通过，表单数据:', messageForm.value)
    console.log('当前用户列表:', users.value)
    
    // 从用户列表中找到选中的用户，获取其用户名
    console.log('查找用户，receiverId:', messageForm.value.receiverId, '类型:', typeof messageForm.value.receiverId)
    console.log('用户列表:', users.value)
    
    // 检查receiverId是否为空
    if (!messageForm.value.receiverId) {
      ElMessage.error('请选择接收者')
      return
    }
    
    // 解析receiverId，格式为"type-id"
    const [type, id] = messageForm.value.receiverId.split('-')
    console.log('解析后的类型:', type, 'ID:', id)
    
    const selectedUser = users.value.find(user => user.type === type && user.id === Number(id))
    console.log('找到的用户:', selectedUser)
    
    if (!selectedUser) {
      ElMessage.error('未找到选中的接收者')
      return
    }
    
    console.log('选中的用户:', selectedUser)
    
    const messageData = {
      receiver: selectedUser.username,
      content: messageForm.value.content
    }
    console.log('发送消息的API数据:', messageData)
    
    console.log('准备调用sendMessage API')
    await sendMessage(messageData)
    console.log('消息发送成功')
    ElMessage.success('消息发送成功')
    if (userStore.isTeacher()) {
      router.push('/announce/messages')
    } else {
      router.push('/messages')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('发送消息失败:', error)
      console.error('错误详情:', error.response?.data)
      ElMessage.error('发送消息失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.send-message-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #FAFBFC 0%, #F5F3FF 100%);
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.illustration-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.illustration-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
}

.circle-1 {
  top: 10%;
  right: 8%;
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.15) 0%, transparent 70%);
  animation: float 10s ease-in-out infinite;
}

.circle-2 {
  bottom: 15%;
  left: 5%;
  width: 140px;
  height: 140px;
  background: radial-gradient(circle, rgba(255, 193, 7, 0.12) 0%, transparent 70%);
  animation: float 12s ease-in-out infinite 2s;
}

.illustration-star {
  position: absolute;
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #FFD54F 0%, #FF9800 100%);
  border-radius: 50%;
  opacity: 0.8;
  animation: twinkle 3s ease-in-out infinite;
}

.star-1 {
  top: 20%;
  left: 15%;
  animation-delay: 0s;
}

.star-2 {
  top: 35%;
  right: 12%;
  animation-delay: 1s;
}

.star-3 {
  bottom: 30%;
  right: 20%;
  animation-delay: 2s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) scale(1);
  }
  50% {
    transform: translateY(-40px) scale(1.08);
  }
}

@keyframes twinkle {
  0%, 100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.illustration-header {
  position: fixed;
  top: 20px;
  right: 5%;
  z-index: 2;
  animation: characterFloat 6s ease-in-out infinite;
}

@keyframes characterFloat {
  0%, 100% {
    transform: translateY(0px) rotate(-2deg);
  }
  50% {
    transform: translateY(-15px) rotate(2deg);
  }
}

.illustration-email {
  position: relative;
  width: 140px;
  height: 120px;
  animation: emailFloat 4s ease-in-out infinite;
}

@keyframes emailFloat {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(2deg);
  }
}

.email-body {
  position: relative;
  width: 140px;
  height: 100px;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  border-radius: 12px 12px 8px 8px;
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.3);
  overflow: hidden;
}

.email-top {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 30px;
  background: linear-gradient(135deg, #6B5BCE 0%, #8C7CF0 100%);
  clip-path: polygon(0 0, 50% 100%, 100% 0);
  animation: emailTopMove 3s ease-in-out infinite;
}

@keyframes emailTopMove {
  0%, 100% {
    height: 30px;
  }
  50% {
    height: 35px;
  }
}

.email-content {
  position: absolute;
  top: 40px;
  left: 20px;
  right: 20px;
  height: 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.email-line {
  height: 4px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 2px;
  animation: linePulse 2s ease-in-out infinite;
}

.line-1 {
  width: 80%;
  animation-delay: 0s;
}

.line-2 {
  width: 100%;
  animation-delay: 0.5s;
}

.line-3 {
  width: 60%;
  animation-delay: 1s;
}

@keyframes linePulse {
  0%, 100% {
    opacity: 0.7;
    transform: scaleX(1);
  }
  50% {
    opacity: 1;
    transform: scaleX(1.05);
  }
}

.email-flag {
  position: absolute;
  top: -10px;
  right: 15px;
  width: 0;
  height: 0;
  border-left: 15px solid transparent;
  border-right: 15px solid transparent;
  border-bottom: 25px solid #FFD54F;
  animation: flagWave 1s ease-in-out infinite;
}

@keyframes flagWave {
  0%, 100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(15deg);
  }
}

.email-shine {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 40px;
  height: 40px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, transparent 70%);
  border-radius: 50%;
  animation: shineMove 3s ease-in-out infinite;
}

@keyframes shineMove {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(10px, 10px);
  }
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #FFFFFF 0%, #F5F3FF 100%);
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
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.back-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s ease, height 0.4s ease;
}

.back-button:hover::before {
  width: 200px;
  height: 200px;
}

.back-button:hover {
  background: linear-gradient(135deg, #E8E4FF 0%, #D4C8FF 100%);
  border-color: #8C7CF0;
  transform: translateX(-6px) translateY(-2px);
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.25);
}

.back-button:active {
  transform: translateX(-4px) translateY(0px) scale(0.95);
}

.container {
  width: 90%;
  padding: 32px;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.card {
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  position: relative;
  overflow: hidden;
  width: 90%;
  display: flex;
  flex-direction: column;
  animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #C6B9FF, #A8D5BA, #FFD54F);
  background-size: 300% 100%;
  animation: gradientFlow 8s ease infinite;
}

@keyframes gradientFlow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.title {
  text-align: center;
  color: #1A202C;
  margin-bottom: 32px;
  font-size: 32px;
  font-weight: 700;
  position: relative;
  z-index: 1;
  background: linear-gradient(135deg, #8C7CF0 0%, #6B5BCE 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: titleGlow 3s ease-in-out infinite;
}

@keyframes titleGlow {
  0%, 100% {
    filter: drop-shadow(0 0 2px rgba(140, 124, 240, 0.3));
  }
  50% {
    filter: drop-shadow(0 0 8px rgba(140, 124, 240, 0.6));
  }
}

.send-message-form {
  width: 100%;
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

.cancel-button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #FFFFFF 0%, #F5F3FF 100%);
  color: #8C7CF0;
  border: 2px solid #E8E4FF;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.cancel-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s ease, height 0.4s ease;
}

.cancel-button:hover::before {
  width: 200px;
  height: 200px;
}

.cancel-button:hover {
  background: linear-gradient(135deg, #E8E4FF 0%, #D4C8FF 100%);
  border-color: #8C7CF0;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.25);
}

.cancel-button:active {
  transform: translateY(0px) scale(0.95);
}

.submit-button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #8C7CF0 0%, #6B5BCE 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.submit-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s ease, height 0.4s ease;
}

.submit-button:hover::before {
  width: 200px;
  height: 200px;
}

.submit-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #9E8CFF 0%, #8C7CF0 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.4);
}

.submit-button:active:not(:disabled) {
  transform: translateY(0px) scale(0.95);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #4A5568;
  font-size: 14px;
}

:deep(.el-input__inner) {
  border-radius: 10px;
  border: 2px solid #F0F2F5;
  transition: all 0.3s ease;
  font-size: 14px;
  padding: 10px 16px;
}

:deep(.el-input__inner:hover) {
  border-color: #C6B9FF;
  box-shadow: 0 0 8px rgba(140, 124, 240, 0.2);
}

:deep(.el-input__inner:focus) {
  border-color: #8C7CF0;
  box-shadow: 0 0 12px rgba(140, 124, 240, 0.3);
}

:deep(.el-textarea__inner) {
  border-radius: 10px;
  border: 2px solid #F0F2F5;
  transition: all 0.3s ease;
  font-size: 14px;
  padding: 12px 16px;
  resize: vertical;
}

:deep(.el-textarea__inner:hover) {
  border-color: #C6B9FF;
  box-shadow: 0 0 8px rgba(140, 124, 240, 0.2);
}

:deep(.el-textarea__inner:focus) {
  border-color: #8C7CF0;
  box-shadow: 0 0 12px rgba(140, 124, 240, 0.3);
}

:deep(.el-select .el-input__inner) {
  border-radius: 10px;
  border: 2px solid #F0F2F5;
  transition: all 0.3s ease;
  font-size: 14px;
  padding: 10px 16px;
}

:deep(.el-select .el-input__inner:hover) {
  border-color: #C6B9FF;
  box-shadow: 0 0 8px rgba(140, 124, 240, 0.2);
}

:deep(.el-select .el-input__inner:focus) {
  border-color: #8C7CF0;
  box-shadow: 0 0 12px rgba(140, 124, 240, 0.3);
}

:deep(.el-select-dropdown) {
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.2);
  border: 1px solid #E8E4FF;
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%);
}

:deep(.el-select-dropdown__item) {
  border-radius: 8px;
  transition: all 0.3s ease;
  padding: 10px 16px;
}

:deep(.el-select-dropdown__item:hover) {
  background: linear-gradient(135deg, #E8E4FF 0%, #D4C8FF 100%);
  color: #8C7CF0;
}

:deep(.el-select-dropdown__item.selected) {
  background: linear-gradient(135deg, #8C7CF0 0%, #6B5BCE 100%);
  color: white;
}

:deep(.el-form-item__error) {
  color: #F56C6C;
  font-size: 12px;
  margin-top: 4px;
}
</style>