<template>
  <div class="exam-bank">
    <div class="header">
      <button @click="goHome">返回首页</button>
      <select v-model="selectedClass" @change="filterUnits" id="selected_class">
        <option value="All">全部班级</option>
        <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
          {{ classItem.class_name }}
        </option>
      </select>
      <button @click="goToManagement" class="btn-management">高级管理</button>
    </div>

    <div class="main">
      <h1 style="text-align: center">任务列表</h1>
      <div class="table-container">
        <table id="unit_table">
          <thead>
            <tr>
              <th style="display: none">unit_id</th>
              <th>#</th>
              <th>任务类型</th>
              <th>任务标题</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="4" style="text-align: center">加载中...</td>
            </tr>
            <tr v-else-if="filteredUnits.length === 0">
              <td colspan="4" style="text-align: center">暂无试题</td>
            </tr>
            <tr v-else v-for="(unit, index) in filteredUnits" :key="unit.id">
              <td style="display: none">{{ unit.id }}</td>
              <td>
                <a @click="viewExamDetail(unit.id)">{{ (currentPage - 1) * pageSize + index + 1 }}</a>
              </td>
              <td>{{ unit.type === 'exam' ? '考试' : unit.type === 'practice' ? '练习' : unit.type }}</td>
              <td>
                <a @click="viewExamDetail(unit.id)">{{ unit.title }}</a>
              </td>
              <td>
                <button @click="viewExamDetail(unit.id)" class="btn-view">查看</button>
                &nbsp;&nbsp;&nbsp;&nbsp;
                <button @click="editExam(unit.id)" class="btn-edit">编辑</button>
                &nbsp;&nbsp;&nbsp;&nbsp;
                <button @click="deleteExam(unit.id)" class="btn-delete">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页控件 -->
      <div class="pagination" v-if="totalPages > 1">
        <button v-if="currentPage > 1" @click="goToPage(1)">首页</button>
        <button v-if="currentPage > 1" @click="goToPage(currentPage - 1)">上一页</button>
        <span
          v-for="num in pageRange"
          :key="num"
          :class="['page-number', { active: num === currentPage }]"
          @click="goToPage(num)"
        >
          {{ num }}
        </span>
        <button v-if="currentPage < totalPages" @click="goToPage(currentPage + 1)">下一页</button>
        <button v-if="currentPage < totalPages" @click="goToPage(totalPages)">尾页</button>
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
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalPages = ref(1)

const filteredUnits = computed(() => {
  let filtered = units.value
  if (selectedClass.value !== 'All') {
    filtered = units.value.filter((unit) => unit.class_id === Number(selectedClass.value))
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
  router.push('/teacher/index')
}

const goToManagement = () => {
  router.push({ name: 'ExamBankManagement' })
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

const goToPage = (page: number) => {
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
      title: unit.unit_name || unit.name || '未命名',
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
  padding: 20px;
  background-color: #F9F8F3;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.header button {
  padding: 10px 20px;
  background-color: #E8ECA;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.header button:hover {
  background-color: #D8D8F6;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  background-color: #fff;
}

.main {
  margin-top: 20px;
}

h1 {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 20px;
}

.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
  background-color: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.table-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #99B6B4, #BACFCE, #D48982, #DFB199);
  z-index: 1;
}

table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
}

thead {
  background-color: rgba(186, 207, 206, 0.2);
}

th,
td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

th {
  font-weight: 600;
  color: #555;
}

tbody tr:hover {
  background-color: rgba(186, 207, 206, 0.1);
}

tbody a {
  color: #007bff;
  text-decoration: none;
  cursor: pointer;
}

tbody a:hover {
  text-decoration: underline;
}

.btn-view,
.btn-edit,
.btn-delete {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-view {
  background-color: #007bff;
  color: #fff;
}

.btn-view:hover {
  background-color: #0056b3;
}

.btn-edit {
  background-color: #ffc107;
  color: #333;
}

.btn-edit:hover {
  background-color: #e0a800;
}

.btn-delete {
  background-color: #D48982;
  color: #fff;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.btn-delete:hover {
  background-color: #C07770;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-management {
  padding: 8px 16px;
  background-color: #99B6B4;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-management:hover {
  background-color: #7A9E9C;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 16px;
  background-color: #fff;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.pagination button:hover {
  background-color: #f0f0f0;
  border-color: #E8ECA;
}

.page-number {
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.page-number:hover {
  background-color: #f0f0f0;
}

.page-number.active {
  background-color: #1A1A1A;
  color: #fff;
  font-weight: 600;
}
</style>

