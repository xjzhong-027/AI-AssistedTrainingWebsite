<template>
  <div class="attendance-page">
      <el-card>
        <template #header>
          <div class="card-header">
            <h3>考勤管理</h3>
            <el-button @click="goBack">返回</el-button>
          </div>
        </template>

        <!-- 查询表单 -->
        <el-form :model="queryForm" :inline="true" class="query-form">
          <el-form-item label="班级">
            <el-select v-model="queryForm.class_id" placeholder="请选择班级" style="width: 200px" @change="handleQuery">
              <el-option
                v-for="cls in classList"
                :key="cls.id"
                :label="cls.class_name"
                :value="cls.id"
              ></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="周次">
            <el-input-number v-model="queryForm.week" :min="1" :max="20" placeholder="请输入周次" @change="handleQuery"></el-input-number>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleQuery" :loading="loading">查询</el-button>
          </el-form-item>
        </el-form>

        <!-- 考勤记录表格 -->
        <el-table :data="attendanceList" v-loading="loading" stripe border style="margin-top: 20px">
          <el-table-column prop="student_name" label="学生姓名" width="120"></el-table-column>
          <el-table-column prop="week" label="周次" width="80"></el-table-column>
          <el-table-column prop="attendance_status" label="考勤状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.attendance_status || row.status)">
                {{ row.status_display || getStatusText(row.attendance_status || row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="记录时间" width="180">
            <template #default="{ row }">
              {{ row.created_at ? formatDateTime(row.created_at) : '-' }}
            </template>
          </el-table-column>
        </el-table>

        <!-- 空状态 -->
        <el-empty v-if="!loading && attendanceList.length === 0" description="暂无考勤记录"></el-empty>
      </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { queryAttendance } from '@/api/query'
import { getAllClasses } from '@/api/user'
import { formatDateTime } from '@/utils/format'
import type { AttendanceRecord } from '@/types/query'

const router = useRouter()
const loading = ref(false)
const attendanceList = ref<AttendanceRecord[]>([])
const classList = ref<any[]>([])

const queryForm = ref({
  class_id: undefined as number | undefined,
  week: 1
})

// 获取班级列表
const loadClasses = async () => {
  try {
    classList.value = await getAllClasses()
    if (classList.value.length > 0) {
      queryForm.value.class_id = classList.value[0].id
    }
  } catch (error: any) {
    console.error('加载班级列表失败', error)
    ElMessage.error(error.message || '加载班级列表失败')
  }
}

// 查询考勤记录
const handleQuery = async () => {
  if (!queryForm.value.class_id || !queryForm.value.week) {
    ElMessage.warning('请选择班级和周次')
    return
  }

  loading.value = true
  try {
    attendanceList.value = await queryAttendance(queryForm.value.class_id, queryForm.value.week)
    if (attendanceList.value.length === 0) {
      ElMessage.info('该班级该周次暂无考勤记录')
    }
  } catch (error: any) {
    console.error('查询考勤记录失败', error)
    ElMessage.error(error.message || '查询考勤记录失败')
  } finally {
    loading.value = false
  }
}

// 获取状态类型（兼容后端 status：normal/absent/late/early-leave 等）
const getStatusType = (status: string): string => {
  const typeMap: Record<string, string> = {
    normal: 'success',
    present: 'success',
    absent: 'danger',
    late: 'warning',
    'early-leave': 'info',
    'late and early-leave': 'warning',
    abnormal: 'warning',
    vacation: 'info'
  }
  return typeMap[status || ''] || 'info'
}

// 获取状态文本（后端无 status_display 时兜底）
const getStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    normal: '正常出勤',
    present: '出勤',
    absent: '缺勤',
    late: '迟到',
    'early-leave': '早退',
    'late and early-leave': '迟到+早退',
    abnormal: '异常挂机',
    vacation: '假期'
  }
  return textMap[status || ''] || (status || '-')
}

const goBack = () => {
  router.back()
}

onMounted(async () => {
  await loadClasses()
  if (queryForm.value.class_id) {
    handleQuery()
  }
})
</script>

<style scoped>
.attendance-page {
  padding: 20px;
  background-color: #F9F8F3;
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.query-form {
  margin-top: 10px;
}

:deep(.el-card) {
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}
</style>
