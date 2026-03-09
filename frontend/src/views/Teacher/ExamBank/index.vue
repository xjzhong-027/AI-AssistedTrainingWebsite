<template>
  <div class="exam-bank">

    <div class="exam-bank-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 20h9"></path>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
          </div>
          <h2>任务管理</h2>
        </div>
        <div class="header-actions">
          <button @click="goHome" class="secondary-button">返回首页</button>
          <button @click="goToManagement" class="primary-button">高级管理</button>
        </div>
      </div>

      <!-- 筛选和搜索区域 -->
      <div class="filter-section">
        <div class="filter-left">
          <select v-model="selectedClass" @change="filterUnits" class="modern-select">
            <option value="All">全部班级</option>
            <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
              {{ classItem.class_name }}
            </option>
          </select>
        </div>
        <div class="filter-right">
          <el-input
            v-model="searchQuery"
            placeholder="搜索任务标题"
            class="modern-input"
            @input="handleSearch"
          >
            <template #prefix>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </template>
          </el-input>
        </div>
      </div>

      <!-- 任务列表 -->
      <div class="table-section">
        <el-table :data="filteredUnits" v-loading="loading" class="modern-table">
          <el-table-column prop="id" label="#" width="80" />
          <el-table-column label="任务类型" width="120">
            <template #default="{ row }">
              <el-tag :type="row.type === 'exam' ? 'danger' : 'success'" class="modern-tag">
                {{ row.type === 'exam' ? '考试' : row.type === 'practice' ? '练习' : row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="任务标题" min-width="300" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewExamDetail(row.id)" class="link-button">查看</el-button>
              <el-button type="primary" link @click="editExam(row.id)" class="link-button">编辑</el-button>
              <el-button type="danger" link @click="deleteExam(row.id)" class="link-button danger-link">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 空状态 -->
        <el-empty v-if="!loading && filteredUnits.length === 0" description="暂无任务" class="modern-empty">
          <el-button type="primary" @click="goToCreateUnit" class="primary-button">新建任务</el-button>
        </el-empty>
      </div>

      <!-- 分页控件 -->
      <div class="pagination-section" v-if="totalPages > 1">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredUnits.length"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="modern-pagination"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllClasses } from '@/api/user'
import { getAllUnits, deleteUnit } from '@/api/content'
import { useUserStore } from '@/stores/user'
import type { Class } from '@/api/user'
import type { Unit } from '@/api/content'

const router = useRouter()
const userStore = useUserStore()

const classes = ref<Class[]>([])
const units = ref<Unit[]>([])
const selectedClass = ref<string>('All')
const searchQuery = ref('')
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalPages = ref(1)

const filteredUnits = computed(() => {
  let filtered = units.value
  if (selectedClass.value !== 'All') {
    filtered = units.value.filter((unit) => unit.class_id === Number(selectedClass.value))
  }
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter((unit) => unit.title.toLowerCase().includes(query))
  }
  totalPages.value = Math.ceil(filtered.length / pageSize.value)
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

const pageRange = computed(() => {
  const range: number[] = []
  for (let i = 1; i <= totalPages.value; i++) {
    range.push(i)
  }
  return range
})

const goHome = () => {
  router.push('/teacher/dashboard')
}

const goToManagement = () => {
  router.push({ name: 'ExamBankManagement' })
}

const goToCreateUnit = () => {
  router.push('/teacher/unit/create')
}

const filterUnits = () => {
  currentPage.value = 1
}

const viewExamDetail = (unitId: number) => {
  console.log('跳转到详情页面，unitId:', unitId)
  router.push({
    name: 'UnitDetail',
    params: { id: unitId }
  }).catch((err) => {
    console.error('路由跳转失败:', err)
    ElMessage.error(`跳转失败: ${err.message || '请检查路由配置'}`)
  })
}

const editExam = (unitId: number) => {
  console.log('跳转到编辑页面，unitId:', unitId)
  router.push({
    name: 'UnitEdit',
    params: { id: unitId }
  }).catch((err) => {
    console.error('路由跳转失败:', err)
    ElMessage.error(`跳转失败: ${err.message || '请检查路由配置'}`)
  })
}

const deleteExam = async (unitId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗？删除后将无法恢复，且会删除所有相关的页面和题目。', '提示', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: false
    })
    
    try {
      await deleteUnit(unitId)
      ElMessage.success('删除成功')
      // 重新加载列表
      await loadUnits()
    } catch (error: any) {
      console.error('删除失败', error)
      ElMessage.error(error.message || '删除失败')
    }
  } catch (error) {
    // 用户取消删除，不做任何操作
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const loadClasses = async () => {
  try {
    const teacherId = userStore.userInfo?.id
    const data = await getAllClasses(teacherId)
    classes.value = data
  } catch (error) {
    console.error('加载班级列表失败', error)
    ElMessage.error('加载班级列表失败')
  }
}

const loadUnits = async () => {
  loading.value = true
  try {
    const classId = selectedClass.value !== 'All' ? Number(selectedClass.value) : undefined
    const data = await getAllUnits(classId)
    units.value = data.map((unit: any) => ({
      id: unit.id,
      type: unit.unit_type || unit.type || 'exam',
      title: unit.title || unit.unit_name || unit.name || '未命名',
      class_id: unit.class_id
    }))
  } catch (error) {
    console.error('加载任务列表失败', error)
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadClasses()
  loadUnits()
})
</script>

<style scoped>
.exam-bank {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}



/* 卡片样式 */
.exam-bank-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: none;
}

.exam-bank-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
}

/* 头部样式 */
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
  padding: 10px 24px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
  cursor: pointer !important;
}

.primary-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.4) !important;
}

.secondary-button {
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  color: #4A5568 !important;
  border-radius: 12px !important;
  padding: 10px 24px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
  cursor: pointer !important;
}

.secondary-button:hover {
  border-color: #8C7CF0 !important;
  color: #8C7CF0 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2) !important;
}

/* 筛选和搜索区域 */
.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: #F8F5FF;
  border-radius: 12px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.modern-select {
  padding: 10px 16px;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  background: #FFFFFF;
  font-size: 14px;
  color: #4A5568;
  transition: all 0.3s ease;
  min-width: 200px;
}

.modern-select:focus {
  outline: none;
  border-color: #8C7CF0;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1);
}

.modern-input {
  border-radius: 12px !important;
  border: 1px solid #E2E8F0 !important;
  transition: all 0.3s ease !important;
  width: 300px;
}

.modern-input:focus {
  border-color: #8C7CF0 !important;
  box-shadow: 0 0 0 3px rgba(140, 124, 240, 0.1) !important;
}

/* 表格区域 */
.table-section {
  margin-bottom: 24px;
}

.modern-table {
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1) !important;
}

:deep(.el-table th) {
  background: #F0F2F5 !important;
  color: #4A5568 !important;
  font-weight: 600 !important;
  font-size: 14px !important;
}

:deep(.el-table tr:hover > td) {
  background: #F8F5FF !important;
}

:deep(.el-table__row:nth-child(even)) {
  background: #FAFAFA !important;
}

/* 标签样式 */
.modern-tag {
  border-radius: 8px !important;
  padding: 4px 12px !important;
  font-size: 12px !important;
  font-weight: 600 !important;
}

/* 链接按钮 */
.link-button {
  color: #8C7CF0 !important;
  font-weight: 500 !important;
}

.link-button:hover {
  color: #6A5AE0 !important;
}

.danger-link {
  color: #F56C6C !important;
}

.danger-link:hover {
  color: #E6A23C !important;
}

/* 空状态 */
.modern-empty {
  padding: 60px 0 !important;
  margin-top: 24px;
}

/* 分页区域 */
.pagination-section {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

.modern-pagination {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-pagination__item:hover) {
  color: #8C7CF0 !important;
}

:deep(.el-pagination__item.is-active) {
  background-color: #8C7CF0 !important;
  border-color: #8C7CF0 !important;
  color: #FFFFFF !important;
}

/* 动画效果 */
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

/* 加载状态 */
:deep(.el-loading-spinner .path) {
  stroke: #8C7CF0 !important;
}
</style>