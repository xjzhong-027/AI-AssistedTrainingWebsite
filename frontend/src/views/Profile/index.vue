<template>
  <div class="profile">
    <el-card>
      <template #header>
        <span>个人中心</span>
      </template>

      <div v-if="userStore.userInfo" class="profile-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户ID">{{ userStore.userInfo.id }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ userStore.userInfo.username }}</el-descriptions-item>
          <el-descriptions-item label="真实姓名">{{ userStore.userInfo.realName }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ userStore.userInfo.email }}</el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag :type="getRoleType(userStore.userInfo.role)">
              {{ getRoleText(userStore.userInfo.role) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间">
            {{ formatDateTime(userStore.userInfo.createdAt) }}
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 30px">
          <el-button type="primary" @click="handleEdit">编辑信息</el-button>
          <el-button type="default" @click="router.push('/profile/change-password')">修改密码</el-button>
        </div>
      </div>
    </el-card>

    <!-- 编辑信息对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑个人信息"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" :rules="editFormRules" ref="editFormRef" label-width="100px">
        <el-form-item label="真实姓名" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入真实姓名"></el-input>
        </el-form-item>
        <el-form-item v-if="userStore.userInfo?.role === 'STUDENT'" label="座位号" prop="seatNumber">
          <el-input v-model="editForm.seatNumber" placeholder="请输入座位号"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelEdit">取消</el-button>
          <el-button type="primary" @click="saveEdit" :loading="editSubmitting">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { formatDateTime } from '@/utils/format'
import { updateStudentProfile, updateTeacherProfile, getUserById } from '@/api/user'
import type { UserRole } from '@/types/user'

const router = useRouter()
const userStore = useUserStore()

const editDialogVisible = ref(false)
const editSubmitting = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = ref({
  name: '',
  seatNumber: ''
})

const editFormRules: FormRules = {
  name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

const getRoleText = (role?: UserRole): string => {
  const roleMap = {
    STUDENT: '学生',
    TEACHER: '教师',
    ADMIN: '管理员'
  }
  return role ? roleMap[role] : '未知'
}

const getRoleType = (role?: UserRole): string => {
  const typeMap = {
    STUDENT: 'success',
    TEACHER: 'warning',
    ADMIN: 'danger'
  }
  return role ? typeMap[role] : 'info'
}

const handleEdit = async () => {
  if (!userStore.userInfo) return

  // 获取完整的用户信息
  try {
    const user = await getUserById(userStore.userInfo.id, userStore.userInfo.role)
    editForm.value = {
      name: (user as any).name || userStore.userInfo.realName || '',
      seatNumber: (user as any).seat_number || (user as any).seatNumber || ''
    }
    editDialogVisible.value = true
  } catch (error: any) {
    console.error('获取用户信息失败', error)
    // 如果获取失败，使用当前存储的信息
    editForm.value = {
      name: userStore.userInfo.realName || '',
      seatNumber: ''
    }
    editDialogVisible.value = true
  }
}

const cancelEdit = () => {
  editDialogVisible.value = false
  editForm.value = {
    name: '',
    seatNumber: ''
  }
}

const saveEdit = async () => {
  if (!editFormRef.value || !userStore.userInfo) return

  await editFormRef.value.validate(async (valid) => {
    if (!valid) return

    editSubmitting.value = true
    try {
      const role = userStore.userInfo?.role
      const userId = userStore.userInfo?.id

      if (role === 'STUDENT') {
        await updateStudentProfile(userId!, {
          name: editForm.value.name,
          seat_number: editForm.value.seatNumber
        })
      } else if (role === 'TEACHER') {
        await updateTeacherProfile(userId!, {
          name: editForm.value.name
        })
      } else {
        ElMessage.warning('管理员信息暂不支持修改')
        return
      }

      ElMessage.success('个人信息更新成功')
      editDialogVisible.value = false

      // 更新用户信息
      if (userStore.userInfo) {
        userStore.userInfo.realName = editForm.value.name
      }
    } catch (error: any) {
      console.error('更新个人信息失败', error)
      ElMessage.error(error.message || '更新失败')
    } finally {
      editSubmitting.value = false
    }
  })
}
</script>

<style scoped>
.profile {
  padding: 20px;
}

.profile-content {
  padding: 20px 0;
}
</style>
