<template>
  <div class="unit-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>任务详情</span>
          <div>
            <el-button @click="goBack">返回</el-button>
            <el-button v-if="userStore.isTeacher()" @click="addPage">添加页面</el-button>
            <el-button v-if="userStore.isTeacher()" type="primary" @click="editUnit">编辑</el-button>
          </div>
        </div>
      </template>

      <div v-if="unit" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ unit.id }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">
            <el-tag :type="unit.type === 'exam' ? 'danger' : 'success'">
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
        </el-descriptions>

        <!-- 页面列表 -->
        <div v-if="pages && pages.length > 0" style="margin-top: 30px">
          <el-divider>页面列表</el-divider>
          <el-table :data="pages" style="width: 100%" stripe>
            <el-table-column prop="order" label="序号" width="80" />
            <el-table-column prop="text" label="页面标题" min-width="200" />
            <el-table-column prop="limited_time" label="限时（秒）" width="120" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewPage(row.id)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else style="margin-top: 30px">
          <el-empty description="暂无页面">
            <el-button v-if="userStore.isTeacher()" type="primary" @click="addPage">添加页面（组卷）</el-button>
          </el-empty>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
  console.log('跳转到编辑页面，unitId:', unit.value.id)
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
  padding: 20px;
  background-color: #F9F8F3;
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-content {
  padding: 20px 0;
}
</style>

