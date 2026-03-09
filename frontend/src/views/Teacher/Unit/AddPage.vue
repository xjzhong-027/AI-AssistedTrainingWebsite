<template>
  <div class="unit-add-page">
    <div class="unit-add-page-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <h2>添加页面（组卷）</h2>
        </div>
        <el-button @click="goBack" class="secondary-button">返回任务详情</el-button>
      </div>

      <div v-if="unit" class="unit-info">
        <p class="unit-title">
          当前任务包：<strong>{{ unit.title || unit.name || unit.unit_name }}</strong>
          <el-tag :type="unit.type === 'exam' ? 'danger' : 'success'" class="modern-tag">
            {{ unit.type === 'exam' ? '考试' : '练习' }}
          </el-tag>
        </p>
      </div>
      <p class="tip">选择下方一个媒体素材，将基于该素材下的题目组卷并加入本任务包。</p>

      <el-table :data="materials" style="width: 100%" class="modern-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="素材标题" min-width="200" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" link @click="goToCreatePage(row.id)" class="link-button">用该素材组卷</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && materials.length === 0" description="暂无媒体素材，请先在题库管理中新建媒体素材" class="modern-empty" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUnitById, getAllMediaMaterials } from '@/api/content'
import type { Unit } from '@/api/content'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const unit = ref<Unit | null>(null)
const materials = ref<any[]>([])

const unitId = computed(() => Number(route.params.id))

const loadData = async () => {
  const id = unitId.value
  if (!id) {
    ElMessage.error('任务包ID无效')
    router.push('/teacher/exam-bank')
    return
  }

  loading.value = true
  try {
    const [u, list] = await Promise.all([
      getUnitById(id),
      getAllMediaMaterials()
    ])
    unit.value = u
    if (!unit.value?.title) {
      unit.value!.title = (unit.value as any).name || (unit.value as any).unit_name || `任务${id}`
    }
    materials.value = Array.isArray(list) ? list : []
  } catch (error: any) {
    ElMessage.error(error?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({ name: 'UnitDetail', params: { id: route.params.id as string } })
}

/** 进入组卷页，并带上当前任务包 ID，组卷页会预选该任务包 */
const goToCreatePage = (materialId: number) => {
  router.push({
    name: 'CreatePaperPage',
    params: { materialId: String(materialId) },
    query: { unit_id: String(unitId.value) }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.unit-add-page {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

/* 卡片样式 */
.unit-add-page-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: none;
}

.unit-add-page-card::before {
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

/* 按钮样式 */
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

/* 任务信息样式 */
.unit-info {
  margin-bottom: 16px;
  padding: 16px;
  background: #F8F5FF;
  border-radius: 12px;
  border-left: 4px solid #8C7CF0;
}

.unit-title {
  margin: 0;
  color: #4A5568;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.unit-title strong {
  color: #1A202C;
  font-weight: 600;
}

/* 标签样式 */
.modern-tag {
  border-radius: 8px !important;
  padding: 4px 12px !important;
  font-size: 12px !important;
  font-weight: 600 !important;
}

/* 提示信息样式 */
.tip {
  margin-bottom: 24px;
  font-size: 14px;
  color: #718096;
  padding: 12px;
  background: #F0F2F5;
  border-radius: 8px;
  border-left: 4px solid #C6B9FF;
}

/* 表格样式 */
.modern-table {
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1) !important;
  margin-bottom: 24px;
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
  padding: 60px 0 !important;
  margin-top: 24px;
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
