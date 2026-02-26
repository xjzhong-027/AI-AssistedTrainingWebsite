<template>
  <div class="unit-add-page">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>添加页面（组卷）</span>
          <el-button @click="goBack">返回任务详情</el-button>
        </div>
      </template>

      <p v-if="unit" class="unit-info">
        当前任务包：<strong>{{ unit.title || unit.name || unit.unit_name }}</strong>
        <el-tag :type="unit.type === 'exam' ? 'danger' : 'success'" size="small" style="margin-left: 8px">
          {{ unit.type === 'exam' ? '考试' : '练习' }}
        </el-tag>
      </p>
      <p class="tip">选择下方一个媒体素材，将基于该素材下的题目组卷并加入本任务包。</p>

      <el-table :data="materials" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="素材标题" min-width="200" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" link @click="goToCreatePage(row.id)">用该素材组卷</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && materials.length === 0" description="暂无媒体素材，请先在题库管理中新建媒体素材" />
    </el-card>
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
  padding: 20px;
  background-color: #f9f8f3;
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.unit-info {
  margin-bottom: 8px;
  color: #606266;
}

.tip {
  margin-bottom: 16px;
  font-size: 13px;
  color: #909399;
}
</style>
