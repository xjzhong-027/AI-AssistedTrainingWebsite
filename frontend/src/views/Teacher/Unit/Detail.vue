<template>
  <div class="unit-detail">
    <div class="unit-detail-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
              <line x1="8" y1="21" x2="16" y2="21"></line>
              <line x1="12" y1="17" x2="12" y2="21"></line>
            </svg>
          </div>
          <h2>任务详情</h2>
        </div>
        <div class="header-actions">
          <el-button @click="goBack" class="secondary-button">返回</el-button>
          <el-button v-if="userStore.isTeacher()" @click="addPage" class="secondary-button">添加页面</el-button>
          <el-button v-if="userStore.isTeacher()" type="primary" @click="editUnit" class="primary-button">编辑</el-button>
        </div>
      </div>

      <div v-if="unit" class="detail-content">
        <el-descriptions :column="2" border class="modern-descriptions">
          <el-descriptions-item label="任务ID">{{ unit.id }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">
            <el-tag :type="unit.type === 'exam' ? 'danger' : 'success'" class="modern-tag">
              {{ unit.type === 'exam' ? '考试' : '练习' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="任务标题" :span="2">
            {{ unit.title || unit.name || unit.unit_name }}
          </el-descriptions-item>
          <el-descriptions-item label="所属班级" v-if="unit.class_name">
            {{ unit.class_name }}
          </el-descriptions-item>
          <el-descriptions-item label="排序" v-if="unit.order !== undefined">
            {{ unit.order }}
          </el-descriptions-item>
          <el-descriptions-item label="开放周次">
            {{ weekDisplay }}
            <span class="week-hint">（周次以班级开课日期为起点，在班级管理中设置）</span>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 页面列表 -->
        <div v-if="pages && pages.length > 0" style="margin-top: 30px">
          <el-divider class="modern-divider">页面列表</el-divider>
          <el-table :data="pages" style="width: 100%" class="modern-table">
            <el-table-column prop="order" label="序号" width="80" />
            <el-table-column prop="text" label="页面标题" min-width="200" />
            <el-table-column prop="limited_time" label="限时（秒）" width="120" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewPage(row.id)" class="link-button">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else style="margin-top: 30px">
          <el-empty description="暂无页面" class="modern-empty">
            <el-button v-if="userStore.isTeacher()" type="primary" @click="addPage" class="primary-button">添加页面（组卷）</el-button>
          </el-empty>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getUnitById, getPagesByUnit } from '@/api/content'
import type { Unit } from '@/api/content'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const unit = ref<Unit | null>(null)
const pages = ref<any[]>([])

/** 开放周次展示：0=始终开放，1-20=第N周起 */
const weekDisplay = computed(() => {
  const w = unit.value?.week
  if (w === undefined || w === null) return '未设置'
  if (w === 0) return '始终开放'
  return `第 ${w} 周起`
})

// 加载单元详情
const loadUnit = async () => {
  const id = Number(route.params.id)
  if (!id) {
    ElMessage.error('任务ID无效')
    router.push('/teacher/exam-bank')
    return
  }

  loading.value = true
  try {
    unit.value = await getUnitById(id)
    // 兼容处理：确保有title字段
    if (!unit.value.title) {
      unit.value.title = unit.value.name || unit.value.unit_name || `任务${id}`
    }
    // 兼容处理：确保有type字段
    if (!unit.value.type && unit.value.unit_type) {
      unit.value.type = unit.value.unit_type
    }
    
    // 加载页面列表
    pages.value = await getPagesByUnit(id)
  } catch (error: any) {
    console.error('加载任务详情失败', error)
    ElMessage.error(error.message || '加载任务详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/teacher/exam-bank')
}

const editUnit = () => {
  if (!unit.value || !unit.value.id) {
    ElMessage.warning('无法获取任务信息')
    return
  }
  router.push({
    name: 'UnitEdit',
    params: { id: unit.value.id }
  }).catch((err) => {
    console.error('路由跳转失败:', err)
    ElMessage.error(`跳转失败: ${err.message || '请检查路由配置'}`)
  })
}

const viewPage = (pageId: number) => {
  router.push(`/teacher/pages/${pageId}`)
}

/** 添加页面：先选媒体素材，再进入组卷页（会预填当前任务包） */
const addPage = () => {
  if (!unit.value?.id) return
  router.push({
    name: 'UnitAddPage',
    params: { id: unit.value.id.toString() }
  })
}

onMounted(() => {
  loadUnit()
})
</script>

<style scoped>
.unit-detail {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

/* 卡片样式 */
.unit-detail-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: none;
}

.unit-detail-card::before {
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
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
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
}

.secondary-button:hover {
  border-color: #8C7CF0 !important;
  color: #8C7CF0 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2) !important;
}

.link-button {
  color: #8C7CF0 !important;
  font-weight: 500 !important;
}

.link-button:hover {
  color: #6A5AE0 !important;
}

/* 内容样式 */
.detail-content {
  padding: 24px 0;
}

/* 描述信息样式 */
.modern-descriptions {
  border-radius: 12px !important;
  overflow: hidden !important;
  margin-bottom: 24px !important;
}

.modern-descriptions th {
  background: #F0F2F5 !important;
  color: #4A5568 !important;
  font-weight: 600 !important;
}

.modern-descriptions td {
  color: #4A5568 !important;
}

/* 标签样式 */
.modern-tag {
  border-radius: 8px !important;
  padding: 4px 12px !important;
  font-size: 12px !important;
  font-weight: 600 !important;
}

/* 分割线样式 */
.modern-divider {
  margin: 24px 0 !important;
}

/* 表格样式 */
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

/* 空状态样式 */
.modern-empty {
  padding: 40px 0 !important;
}

/* 提示信息样式 */
.week-hint {
  font-size: 12px;
  color: #718096;
  margin-left: 8px;
  padding-left: 8px;
  border-left: 3px solid #C6B9FF;
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

