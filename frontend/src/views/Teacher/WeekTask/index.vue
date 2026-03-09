<template>
  <div class="week-task-container">
    <div class="week-task-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <h2>周任务管理</h2>
        </div>
        <div class="header-actions">
          <el-button @click="goHome" type="default" class="secondary-button">返回首页</el-button>
          <el-button @click="goToNewTaskPackage" type="primary" class="primary-button">新建任务包</el-button>
        </div>
      </div>

      <el-table :data="taskList" style="width: 100%" v-loading="loading" class="modern-table">
        <el-table-column prop="week" label="周次" width="100" sortable>
          <template #default="{ row }">
            <el-tag v-if="row.week" class="status-tag info">{{ row.week }}周</el-tag>
            <el-tag v-else class="status-tag info">未设置</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="任务包名称" min-width="200" />
        <el-table-column prop="class_name" label="班级" width="150" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'task'" class="status-tag success">作业</el-tag>
            <el-tag v-else-if="row.type === 'exam'" class="status-tag error">考试</el-tag>
            <el-tag v-else-if="row.type === 'practice'" class="status-tag warning">练习</el-tag>
            <el-tag v-else class="status-tag info">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.status === '进行中'" class="status-tag success">{{ row.status }}</el-tag>
            <el-tag v-else-if="row.status === '未开始'" class="status-tag info">{{ row.status }}</el-tag>
            <el-tag v-else-if="row.status === '已结束'" class="status-tag error">{{ row.status }}</el-tag>
            <el-tag v-else class="status-tag warning">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handlePreview(row)" class="text-button">预览</el-button>
            <el-button size="small" @click="handleImport(row)" class="text-button">导入</el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)" class="primary-button small">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="!loading && taskList.length === 0" class="empty-state">
        <div class="empty-illustration">
          <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" fill="#E8E4FF" stroke="none"/>
            <path d="M8 14s1.5 2 4 2 4-2 4-2" stroke="#8C7CF0"/>
            <line x1="9" y1="9" x2="9.01" y2="9" stroke="#8C7CF0" stroke-width="2"/>
            <line x1="15" y1="9" x2="15.01" y2="9" stroke="#8C7CF0" stroke-width="2"/>
            <path d="M12 2v4" stroke="#C6B9FF"/>
            <path d="M12 18v4" stroke="#C6B9FF"/>
            <path d="M4.93 4.93l2.83 2.83" stroke="#C6B9FF"/>
            <path d="M16.24 16.24l2.83 2.83" stroke="#C6B9FF"/>
            <path d="M2 12h4" stroke="#C6B9FF"/>
            <path d="M18 12h4" stroke="#C6B9FF"/>
            <path d="M4.93 19.07l2.83-2.83" stroke="#C6B9FF"/>
            <path d="M16.24 7.76l2.83-2.83" stroke="#C6B9FF"/>
          </svg>
        </div>
        <p class="empty-text">暂无周任务</p>
        <p class="empty-subtext">点击"新建任务包"开始创建您的第一个周任务</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAllUnits, type Unit } from '@/api/content'

const router = useRouter()
const loading = ref(false)
const taskList = ref<Unit[]>([])

const goHome = () => {
  router.push('/teacher/dashboard')
}

const goToNewTaskPackage = () => {
  router.push('/teacher/week-task/create')
}

const handlePreview = (row: Unit) => {
  router.push(`/teacher/week-task/preview/${row.id}`)
}

const handleImport = (row: Unit) => {
  router.push(`/teacher/week-task/import/${row.id}`)
}

const handleEdit = (row: Unit) => {
  router.push(`/teacher/units/${row.id}/edit`)
}

const loadTaskList = async () => {
  loading.value = true
  try {
    const data = await getAllUnits()
    taskList.value = data
  } catch (error: any) {
    ElMessage.error(error.message || '加载任务列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTaskList()
})
</script>

<style scoped>
.week-task-container {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

.week-task-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.week-task-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #F0F2F5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

.card-header h2 {
  margin: 0;
  color: #1A202C;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 按钮样式 */
.primary-button {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 12px !important;
  padding: 12px 24px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3) !important;
  transition: all 0.3s ease !important;
}

.primary-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.4) !important;
}

.primary-button.small {
  padding: 8px 16px !important;
  font-size: 12px !important;
}

.secondary-button {
  background: #FFFFFF !important;
  border: 2px solid #8C7CF0 !important;
  color: #8C7CF0 !important;
  border-radius: 12px !important;
  padding: 12px 24px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.secondary-button:hover {
  background: #E8E4FF !important;
}

.text-button {
  background: transparent !important;
  color: #8C7CF0 !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 8px 16px !important;
  font-size: 14px !important;
  transition: all 0.3s ease !important;
}

.text-button:hover {
  background: rgba(140, 124, 240, 0.1) !important;
}

/* 表格样式 */
.modern-table {
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 10px rgba(140, 124, 240, 0.1) !important;
}

.modern-table th {
  background: #F0F2F5 !important;
  color: #4A5568 !important;
  font-weight: 600 !important;
  padding: 16px !important;
  font-size: 14px !important;
}

.modern-table td {
  padding: 16px !important;
  font-size: 14px !important;
  color: #4A5568 !important;
  border-bottom: 1px solid #F0F2F5 !important;
}

.modern-table tr:hover {
  background: #F5F7FA !important;
}

/* 状态标签样式 */
.status-tag {
  border-radius: 8px !important;
  padding: 4px 12px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  border: none !important;
}

.status-tag.success {
  background: #A8D5BA !important;
  color: #2E7D32 !important;
}

.status-tag.warning {
  background: #FFE082 !important;
  color: #F57F17 !important;
}

.status-tag.error {
  background: #FFB6C1 !important;
  color: #C62828 !important;
}

.status-tag.info {
  background: #C6B9FF !important;
  color: #6B5BCE !important;
}

/* 加载动画样式 */
:deep(.el-loading-spinner) {
  font-size: 16px !important;
  color: #8C7CF0 !important;
}

:deep(.el-loading-spinner .path) {
  stroke: #8C7CF0 !important;
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-illustration {
  margin-bottom: 24px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.empty-text {
  font-size: 18px;
  color: #1A202C;
  font-weight: 600;
  margin-bottom: 8px;
}

.empty-subtext {
  font-size: 14px;
  color: #8B9BB4;
  margin-bottom: 24px;
}
</style>





