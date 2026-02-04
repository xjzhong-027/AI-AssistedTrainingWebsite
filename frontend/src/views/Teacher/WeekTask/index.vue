<template>
  <div class="week-task">
    <div class="header">
      <el-button @click="goHome" type="default">返回首页</el-button>
      <h2>周任务管理</h2>
      <el-button @click="goToNewTaskPackage" type="primary">新建任务包</el-button>
    </div>

    <el-table :data="taskList" style="width: 100%" v-loading="loading">
      <el-table-column prop="week" label="周次" width="100" sortable>
        <template #default="{ row }">
          <el-tag v-if="row.week">第{{ row.week }}周</el-tag>
          <el-tag v-else type="info">未设置</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="任务包名称" min-width="200" />
      <el-table-column prop="class_name" label="班级" width="150" />
      <el-table-column prop="type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.type === 'task'" type="success">作业</el-tag>
          <el-tag v-else-if="row.type === 'exam'" type="danger">考试</el-tag>
          <el-tag v-else-if="row.type === 'practice'" type="warning">练习</el-tag>
          <el-tag v-else type="info">{{ row.type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.status === '进行中'" type="success">{{ row.status }}</el-tag>
          <el-tag v-else-if="row.status === '未开始'" type="info">{{ row.status }}</el-tag>
          <el-tag v-else-if="row.status === '已结束'" type="danger">{{ row.status }}</el-tag>
          <el-tag v-else type="warning">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handlePreview(row)">预览</el-button>
          <el-button size="small" @click="handleImport(row)">导入</el-button>
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
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
  router.push('/teacher/index')
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
</style>





