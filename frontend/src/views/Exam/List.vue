<template>
  <div class="exam-list">
    <div class="container card">
      <div class="card-header">
        <h1>考试列表</h1>
        <el-button v-if="userStore.isTeacher()" type="primary" @click="goCreate">
          <el-icon><Plus /></el-icon>
          创建考试
        </el-button>
      </div>

      <!-- 筛选区域 -->
      <div class="filter-area">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索考试标题"
          style="width: 300px"
          clearable
          @clear="loadExams"
          @keyup.enter="loadExams"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="filterStatus"
          placeholder="筛选状态"
          style="width: 150px; margin-left: 10px"
          clearable
          @change="loadExams"
        >
          <el-option label="未开始" value="NOT_STARTED" />
          <el-option label="进行中" value="IN_PROGRESS" />
          <el-option label="已结束" value="ENDED" />
        </el-select>
        <el-button type="primary" style="margin-left: 10px" @click="loadExams">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetFilter">重置</el-button>
      </div>

      <!-- 表格 -->
      <el-table
        v-loading="loading"
        :data="examList"
        style="width: 100%; margin-top: 20px"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="考试标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column prop="startTime" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.startTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="endTime" label="结束时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.endTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长（分钟）" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row.id)">查看</el-button>
            <el-button
              v-if="userStore.isTeacher() && row.creatorId === userStore.userInfo?.id"
              link
              type="warning"
              @click="editExam(row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-if="userStore.isStudent() && row.status === 'IN_PROGRESS'"
              link
              type="success"
              @click="takeExam(row.id)"
            >
              参加考试
            </el-button>
            <el-button
              v-if="userStore.isTeacher() && row.creatorId === userStore.userInfo?.id"
              link
              type="danger"
              @click="handleDelete(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="!loading && examList.length === 0" description="暂无考试数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getAllExams, getExamsByStatus, getExamsByCreatorId, deleteExam } from '@/api/exam'
import { formatDateTime } from '@/utils/format'
import type { Exam } from '@/types/exam'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const examList = ref<Exam[]>([])
const searchKeyword = ref('')
const filterStatus = ref<string>('')

// 加载考试列表
const loadExams = async () => {
  loading.value = true
  try {
    let exams: Exam[] = []

    // 根据后端API，使用统一的getAllExams接口
    if (userStore.isStudent()) {
      // 学生：获取自己的考试记录（unit_type=exam）
      const studentId = userStore.userInfo?.id
      exams = await getAllExams(studentId, 'exam')
    } else if (userStore.isTeacher()) {
      // 教师：获取所有考试（这里可能需要调整，根据实际后端API）
      exams = await getAllExams(undefined, 'exam')
    } else {
      exams = await getAllExams()
    }

    // 搜索过滤
    if (searchKeyword.value) {
      exams = exams.filter((exam) => {
        const title = (exam as any).unit_name || exam.title || ''
        return title.toLowerCase().includes(searchKeyword.value.toLowerCase())
      })
    }

    // 转换数据格式以适配前端显示
    examList.value = exams.map((exam: any) => ({
      id: exam.id,
      title: exam.unit_name || exam.title || '未命名考试',
      description: exam.description || '',
      startTime: exam.start_time || exam.startTime || '',
      endTime: exam.submit_time || exam.endTime || '',
      duration: exam.duration || 0,
      status: exam.status || 'NOT_STARTED',
      creatorId: exam.creator_id || exam.creatorId || 0
    }))
  } catch (error) {
    console.error('加载考试列表失败', error)
    ElMessage.error('加载考试列表失败')
  } finally {
    loading.value = false
  }
}

// 重置筛选
const resetFilter = () => {
  searchKeyword.value = ''
  filterStatus.value = ''
  loadExams()
}

// 获取状态文本
const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    NOT_STARTED: '未开始',
    IN_PROGRESS: '进行中',
    ENDED: '已结束'
  }
  return statusMap[status] || status
}

// 获取状态类型
const getStatusType = (status: string): string => {
  const typeMap: Record<string, string> = {
    NOT_STARTED: 'info',
    IN_PROGRESS: 'success',
    ENDED: 'warning'
  }
  return typeMap[status] || ''
}

// 查看详情
const viewDetail = (id: number) => {
  router.push(`/exams/${id}`)
}

// 编辑考试
const editExam = (id: number) => {
  router.push(`/exams/${id}/edit`)
}

// 参加考试
const takeExam = (id: number) => {
  router.push(`/exams/${id}/take`)
}

// 删除考试
const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个考试吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteExam(id)
    ElMessage.success('删除成功')
    loadExams()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败', error)
    }
  }
}

// 创建考试
const goCreate = () => {
  router.push('/exams/create')
}

onMounted(() => {
  loadExams()
})
</script>

<style scoped>
.exam-list {
  width: 100%;
  padding: 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px;
}

.card {
  background-color: #FFFFFF;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
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

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #99B6B4, #BACFCE, #D48982, #DFB199);
}

h1 {
  text-align: center;
  color: #1A1A1A;
  margin-bottom: 30px;
  font-size: 36px;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

h1::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #99B6B4, #D48982);
  border-radius: 2px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.card-header h1 {
  font-size: 36px;
  font-weight: 700;
  color: #1A1A1A;
  margin: 0;
  position: relative;
  z-index: 1;
}

.card-header h1::after {
  content: '';
  position: absolute;
  bottom: -15px;
  left: 0;
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #99B6B4, #D48982);
  border-radius: 2px;
}

.filter-area {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
</style>
