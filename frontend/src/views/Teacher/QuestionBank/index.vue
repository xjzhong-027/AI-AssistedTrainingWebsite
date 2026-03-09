<template>
  <div class="question-bank">

    <div class="question-bank-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7,10 12,15 17,10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </div>
          <h2>题库管理</h2>
        </div>
        <div class="header-actions">
          <el-button @click="goHome" type="default" class="secondary-button">返回首页</el-button>
          <el-button @click="goToNewMaterial" type="primary" class="primary-button">新建媒体素材</el-button>
          <el-button @click="goToNewTaskPackage" type="default" class="secondary-button">新建任务包</el-button>
        </div>
      </div>

      <h3 class="section-title">媒体素材列表</h3>
      
      <el-table :data="paginatedMaterials" style="width: 100%" v-loading="loading" class="modern-table">
        <el-table-column prop="id" label="#" width="80" />
        <el-table-column prop="title" label="标题" min-width="300">
          <template #default="{ row }">
            <a @click="viewMaterialDetail(row.id)" class="material-title">{{ row.title }}</a>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="addQuestion(row.id)" class="text-button">添加题目</el-button>
            <el-button size="small" @click="createPage(row.id)" class="secondary-button small">组卷</el-button>
            <el-button size="small" type="danger" @click="deleteMaterial(row.id)" class="danger-button small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页控件 -->
      <div class="pagination" v-if="totalPages > 1">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="materials.length"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="modern-pagination"
        />
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && materials.length === 0" class="empty-state">
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
        <p class="empty-text">暂无媒体素材</p>
        <p class="empty-subtext">点击"新建媒体素材"开始创建您的第一个素材</p>
      </div>

      <!-- 媒体素材详情对话框 -->
      <el-dialog
        v-model="detailDialogVisible"
        title="媒体素材详情"
        width="800px"
        :close-on-click-modal="false"
        custom-class="modern-dialog"
      >
        <div v-loading="detailLoading" class="material-detail">
          <div v-if="currentMaterial" class="detail-content">
            <div class="detail-item">
              <span class="label">标题：</span>
              <span class="value">{{ currentMaterial.title }}</span>
            </div>
            <div class="detail-item">
              <span class="label">关联题目数：</span>
              <span class="value">{{ questionCount }} 道大题</span>
            </div>
          <div v-if="currentMaterial.theme" class="detail-item">
            <span class="label">主题：</span>
            <span class="value">{{ currentMaterial.theme }}</span>
          </div>
          <div v-if="currentMaterial.abstract" class="detail-item">
            <span class="label">摘要：</span>
            <span class="value">{{ currentMaterial.abstract }}</span>
          </div>
          <div v-if="currentMaterial.keywords" class="detail-item">
            <span class="label">关键词：</span>
            <span class="value">{{ currentMaterial.keywords }}</span>
          </div>
          <div v-if="currentMaterial.transcript" class="detail-item">
            <span class="label">文本内容：</span>
            <div class="value transcript">{{ currentMaterial.transcript }}</div>
          </div>
          <div v-if="currentMaterial.media_url" class="detail-item">
            <span class="label">媒体文件：</span>
            <span class="value">
              <a :href="getMediaUrl(currentMaterial.media_url)" target="_blank" class="media-link">
                {{ currentMaterial.media_url }}
              </a>
            </span>
          </div>
          <div v-if="currentMaterial.image_url" class="detail-item">
            <span class="label">图片：</span>
            <div class="value">
              <img
                v-for="(img, index) in getImageUrls(currentMaterial.image_url)"
                :key="index"
                :src="img"
                alt="素材图片"
                class="material-image"
              />
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleDetailCreatePage">组卷</el-button>
        <el-button type="danger" @click="handleDetailDelete">删除</el-button>
      </template>
    </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElDialog } from 'element-plus'
import { getAllMediaMaterials, getMediaMaterialById, deleteMediaMaterial, getMaterialQuestions } from '@/api/content'
import type { MediaMaterial } from '@/api/content'

const router = useRouter()

const materials = ref<MediaMaterial[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalPages = ref(1)
const detailDialogVisible = ref(false)
const currentMaterial = ref<MediaMaterial | null>(null)
const questionCount = ref(0)
const detailLoading = ref(false)

const pageRange = computed(() => {
  const range: number[] = []
  for (let i = 1; i <= totalPages.value; i++) {
    range.push(i)
  }
  return range
})

const paginatedMaterials = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return materials.value.slice(start, end)
})

const goHome = () => {
  router.push('/teacher/dashboard')
}

const goToNewTaskPackage = () => {
  router.push({
    name: 'CreateUnit'
  })
}

const goToNewMaterial = () => {
  router.push({
    name: 'MaterialCreate'
  })
}

const viewMaterialDetail = async (materialId: number) => {
  detailLoading.value = true
  detailDialogVisible.value = true
  currentMaterial.value = null
  questionCount.value = 0
  try {
    const [material, questions] = await Promise.all([
      getMediaMaterialById(materialId),
      getMaterialQuestions(materialId)
    ])
    currentMaterial.value = material
    questionCount.value = Array.isArray(questions) ? questions.length : 0
  } catch (error: any) {
    ElMessage.error(error.message || '加载媒体素材详情失败')
    detailDialogVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

const handleDetailCreatePage = () => {
  if (!currentMaterial.value) return
  detailDialogVisible.value = false
  createPage(currentMaterial.value.id)
}

const handleDetailDelete = () => {
  if (!currentMaterial.value) return
  detailDialogVisible.value = false
  deleteMaterial(currentMaterial.value.id)
}

const deleteMaterial = async (materialId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个媒体素材吗？删除后将无法恢复。', '提示', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: false
    })
    
    try {
      await deleteMediaMaterial(materialId)
      ElMessage.success('删除成功')
      // 重新加载列表
      await loadMaterials()
    } catch (error: any) {
      console.error('删除失败', error)
      ElMessage.error(error.message || '删除失败')
    }
  } catch (error) {
    // 用户取消删除，不做任何操作
  }
}

const createPage = (materialId: number) => {
  router.push({
    name: 'CreatePaperPage',
    params: { materialId: materialId.toString() }
  })
}

const addQuestion = (materialId: number) => {
  router.push({
    name: 'QuestionType',
    params: { materialId: materialId.toString() }
  })
}

const goToPage = (page: number) => {
  currentPage.value = page
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (current: number) => {
  currentPage.value = current
}

const loadMaterials = async () => {
  loading.value = true
  try {
    const data = await getAllMediaMaterials()
    materials.value = data
    totalPages.value = Math.ceil(materials.value.length / pageSize.value)
  } catch (error) {
    console.error('加载媒体素材列表失败', error)
    ElMessage.error('加载媒体素材列表失败')
  } finally {
    loading.value = false
  }
}

// 获取媒体文件URL
const getMediaUrl = (mediaUrl: string): string => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  if (mediaUrl.startsWith('http')) {
    return mediaUrl
  }
  return `${apiBaseUrl}${mediaUrl.startsWith('/') ? '' : '/'}${mediaUrl}`
}

// 解析图片URL（可能是逗号分隔的多个URL）
const getImageUrls = (imageUrl: string): string[] => {
  if (!imageUrl) return []
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return imageUrl.split(',').map(url => {
    const trimmedUrl = url.trim()
    if (trimmedUrl.startsWith('http')) {
      return trimmedUrl
    }
    return `${apiBaseUrl}${trimmedUrl.startsWith('/') ? '' : '/'}${trimmedUrl}`
  })
}

onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.question-bank {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

/* 插画样式 */
.illustration-header {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  animation: fadeIn 0.8s ease-out;
}

.illustration-content {
  position: relative;
  animation: float 3s ease-in-out infinite;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

/* 卡片样式 */
.question-bank-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.question-bank-card::before {
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
  padding: 10px 20px !important;
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
  padding: 10px 20px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.secondary-button:hover {
  border-color: #8C7CF0 !important;
  color: #8C7CF0 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2) !important;
}

.secondary-button.small {
  padding: 6px 12px !important;
  font-size: 12px !important;
}

.text-button {
  background: transparent !important;
  border: none !important;
  color: #8C7CF0 !important;
  padding: 6px 12px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.text-button:hover {
  background: rgba(140, 124, 240, 0.1) !important;
  border-radius: 6px !important;
}

.danger-button {
  background: linear-gradient(135deg, #F56565, #F8B7B7) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 12px !important;
  padding: 6px 12px !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
}

.danger-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(245, 101, 101, 0.4) !important;
}

/* 标题样式 */
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #4A5568;
  margin-bottom: 16px;
  padding-left: 8px;
  border-left: 4px solid #8C7CF0;
}

/* 表格样式 */
.modern-table {
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 10px rgba(140, 124, 240, 0.1) !important;
  margin-bottom: 24px !important;
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

.material-title {
  color: #8C7CF0 !important;
  text-decoration: none !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.material-title:hover {
  color: #6A5AE0 !important;
  text-decoration: underline !important;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

.modern-pagination {
  --el-pagination-fill: #8C7CF0 !important;
  --el-pagination-hover-fill: #C6B9FF !important;
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

/* 详情对话框样式 */
.modern-dialog {
  border-radius: 16px !important;
  overflow: hidden !important;
}

.modern-dialog .el-dialog__header {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  color: #FFFFFF;
  padding: 20px 24px;
  margin: 0 !important;
}

.modern-dialog .el-dialog__title {
  color: #FFFFFF !important;
  font-size: 16px !important;
  font-weight: 600 !important;
}

.modern-dialog .el-dialog__body {
  padding: 24px;
}

.material-detail {
  min-height: 200px;
}

.detail-content {
  padding: 10px 0;
}

.detail-item {
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
}

.detail-item .label {
  font-weight: 600;
  color: #606266;
  min-width: 100px;
  margin-right: 10px;
}

.detail-item .value {
  flex: 1;
  color: #303133;
  word-break: break-word;
}

.detail-item .value.transcript {
  white-space: pre-wrap;
  line-height: 1.8;
  max-height: 300px;
  overflow-y: auto;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.media-link {
  color: #409eff;
  text-decoration: none;
}

.media-link:hover {
  text-decoration: underline;
}

.material-image {
  max-width: 200px;
  max-height: 200px;
  margin-right: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

/* 加载状态 */
:deep(.el-loading-spinner .path) {
  stroke: #8C7CF0 !important;
}
</style>

