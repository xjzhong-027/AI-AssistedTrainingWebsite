<template>
  <div class="question-bank">
    <div class="header">
      <button @click="goHome">返回首页</button>
      <h2>Question Management</h2>
      <button @click="goToNewTaskPackage">New task package</button>
    </div>

    <h1 style="text-align: center">媒体素材列表</h1>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Title</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="3" style="text-align: center">加载中...</td>
          </tr>
          <tr v-else-if="paginatedMaterials.length === 0">
            <td colspan="3" style="text-align: center">暂无媒体素材</td>
          </tr>
          <tr v-else v-for="(material, index) in paginatedMaterials" :key="material.id">
            <td>
              <a @click="viewMaterialDetail(material.id)">{{ (currentPage - 1) * pageSize + index + 1 }}</a>
            </td>
            <td>
              <a @click="viewMaterialDetail(material.id)">{{ material.title }}</a>
            </td>
            <td>
              <button @click="addQuestion(material.id)" class="btn-add">添加题目</button>
              &nbsp;&nbsp;
              <button @click="deleteMaterial(material.id)" class="btn-delete">删除</button>
              &nbsp;&nbsp;
              <button @click="createPage(material.id)" class="btn-create">组卷</button>
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

    <!-- 媒体素材详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="媒体素材详情"
      width="800px"
      :close-on-click-modal="false"
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
  router.push('/teacher/index')
}

const goToNewTaskPackage = () => {
  router.push({
    name: 'CreateUnit'
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

.header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
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

.btn-delete,
.btn-create {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
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

.btn-create {
  background-color: #99B6B4;
  color: #fff;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.btn-create:hover {
  background-color: #7A9E9C;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-add {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  background-color: #E8D5B7;
  color: #333;
  transition: all 0.3s ease;
}

.btn-add:hover {
  background-color: #D4C4A0;
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

/* 详情对话框样式 */
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
</style>

