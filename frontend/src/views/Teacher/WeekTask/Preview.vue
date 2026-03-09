<template>
  <div class="week-task-preview-container">
    <div class="week-task-preview-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          </div>
          <h2>预览周任务 - {{ unitInfo?.title }}</h2>
        </div>
        <el-button @click="goBack" type="default" class="secondary-button">返回</el-button>
      </div>

      <!-- 任务基本信息 -->
      <el-descriptions v-if="unitInfo" :column="2" border class="unit-info modern-descriptions">
        <el-descriptions-item label="任务标题">{{ unitInfo.title }}</el-descriptions-item>
        <el-descriptions-item label="任务类型">
          <el-tag v-if="unitInfo.type === 'task'" class="status-tag success">作业</el-tag>
          <el-tag v-else-if="unitInfo.type === 'exam'" class="status-tag error">考试</el-tag>
          <el-tag v-else-if="unitInfo.type === 'practice'" class="status-tag warning">练习</el-tag>
          <el-tag v-else class="status-tag info">{{ unitInfo.type }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="所属班级">{{ unitInfo.class_name }}</el-descriptions-item>
        <el-descriptions-item label="周次">
          <el-tag v-if="unitInfo.week" class="status-tag info">{{ unitInfo.week }}周</el-tag>
          <el-tag v-else class="status-tag info">未设置</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag v-if="unitInfo.status === '进行中'" class="status-tag success">{{ unitInfo.status }}</el-tag>
          <el-tag v-else-if="unitInfo.status === '未开始'" class="status-tag info">{{ unitInfo.status }}</el-tag>
          <el-tag v-else-if="unitInfo.status === '已结束'" class="status-tag error">{{ unitInfo.status }}</el-tag>
          <el-tag v-else class="status-tag warning">{{ unitInfo.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="排序">{{ unitInfo.order }}</el-descriptions-item>
      </el-descriptions>

      <el-divider class="modern-divider" />

      <!-- 页面和题目列表 -->
      <div v-if="pages && pages.length > 0" class="pages-content">
        <h3>任务内容 (共{{ pages.length }}页)</h3>

        <el-collapse v-model="activePages" class="modern-collapse">
          <el-collapse-item
            v-for="(page, pageIdx) in pages"
            :key="page.id"
            :name="page.id"
            :title="`第${page.order + 1}页 (${page.main_questions?.length || 0}道大题)`"
            class="modern-collapse-item"
          >
            <div class="page-info">
              <p><strong>页面文本:</strong> {{ page.text }}</p>
              <p v-if="page.limited_time"><strong>时间限制:</strong> {{ page.limited_time }}分钟</p>
              <p><strong>允许修改答案:</strong> {{ page.can_modify ? '是' : '否' }}</p>
            </div>

            <el-divider class="modern-divider" />

            <!-- 大题列表 -->
            <div v-if="page.main_questions && page.main_questions.length > 0" class="main-questions">
              <div
                v-for="(mainQ, mainIdx) in page.main_questions"
                :key="mainQ.id"
                class="main-question-item"
              >
                <h4>大题{{ mainIdx + 1 }}: {{ getQuestionTypeName(mainQ.question_type) }}</h4>

                <div class="main-question-content">
                  <p><strong>题干:</strong> {{ mainQ.question_text }}</p>

                  <el-row :gutter="20">
                    <el-col :span="12">
                      <p><strong>最大播放次数:</strong> {{ mainQ.maximum_play }}</p>
                      <p><strong>最小播放次数:</strong> {{ mainQ.minimum_play }}</p>
                    </el-col>
                    <el-col :span="12">
                      <p v-if="mainQ.start_time"><strong>开始时间:</strong> {{ mainQ.start_time }}</p>
                      <p v-if="mainQ.end_time"><strong>结束时间:</strong> {{ mainQ.end_time }}</p>
                    </el-col>
                  </el-row>

                  <p><strong>允许暂停:</strong> {{ mainQ.allow_pause ? '是' : '否' }}</p>
                  <p v-if="mainQ.limited_time"><strong>时间限制:</strong> {{ mainQ.limited_time }}</p>
                  <p><strong>不需要媒体:</strong> {{ mainQ.no_media ? '是' : '否' }}</p>

                  <div v-if="mainQ.media_material_title" class="media-info">
                    <p><strong>关联素材:</strong> {{ mainQ.media_material_title }}</p>
                    <audio v-if="mainQ.media_material_url && isAudio(mainQ.media_material_url)" controls class="media-player">
                      <source :src="mainQ.media_material_url" />
                    </audio>
                    <video v-else-if="mainQ.media_material_url" controls class="media-player">
                      <source :src="mainQ.media_material_url" />
                    </video>
                  </div>

                  <!-- 小题列表 -->
                  <div v-if="mainQ.sub_questions && mainQ.sub_questions.length > 0" class="sub-questions">
                    <h5>小题列表 (共{{ mainQ.sub_questions.length }}题)</h5>
                    <div
                      v-for="(subQ, subIdx) in mainQ.sub_questions"
                      :key="subQ.id"
                      class="sub-question-item"
                    >
                      <p><strong>{{ subIdx + 1 }}.</strong> {{ subQ.question_text }}</p>
                      <p class="answer"><strong>答案:</strong> {{ subQ.answer }}</p>
                      <p class="score"><strong>分值:</strong> {{ subQ.score }}分</p>
                      <p v-if="subQ.tips" class="tips"><strong>提示:</strong> {{ subQ.tips }}</p>
                      <p v-if="subQ.analysis" class="analysis"><strong>解析:</strong> {{ subQ.analysis }}</p>

                      <!-- 选择题选项 -->
                      <div v-if="subQ.options && subQ.options.length > 0" class="options">
                        <p><strong>选项:</strong></p>
                        <div v-for="option in subQ.options" :key="option.id" class="option-item">
                          <el-tag :class="option.is_answer ? 'status-tag success' : 'status-tag info'" size="small">
                            {{ option.option_label }}
                          </el-tag>
                          {{ option.option_content }}
                        </div>
                      </div>

                      <!-- 连线题选项 -->
                      <div v-if="subQ.matchingOptions && subQ.matchingOptions.length > 0" class="matching-options">
                        <p><strong>连线选项:</strong></p>
                        <div v-for="option in subQ.matchingOptions" :key="option.id" class="option-item">
                          <el-tag class="status-tag info" size="small">{{ option.option_label }}</el-tag>
                          {{ option.option_content }}
                        </div>
                      </div>

                      <!-- 改错题 -->
                      <div v-if="subQ.corrections && subQ.corrections.length > 0" class="corrections">
                        <p><strong>改错项:</strong></p>
                        <div v-for="correction in subQ.corrections" :key="correction.id" class="correction-item">
                          类型: {{ correction.type }}, 位置: {{ correction.index }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="该页面暂无题目" class="modern-empty" />
          </el-collapse-item>
        </el-collapse>
      </div>
      <el-empty v-else description="该任务暂无内容" class="modern-empty" />

      <div class="button-group">
        <el-button @click="goBack" class="secondary-button">返回</el-button>
        <el-button type="primary" @click="handleEdit" class="primary-button">编辑任务</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUnitById, getPagesByUnit } from '@/api/content'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const unitId = ref(Number(route.params.id))
const unitInfo = ref<any>(null)
const pages = ref<any[]>([])
const activePages = ref<number[]>([])

const questionTypeMap: Record<string, string> = {
  choice: '选择题',
  matching: '连线题',
  correction: '改错题',
  comprehension: '主观题',
  text: '纯文本',
  blank: '填空题'
}

const goBack = () => {
  router.push('/teacher/dashboard')
}

const handleEdit = () => {
  router.push(`/teacher/units/${unitId.value}/edit`)
}

const getQuestionTypeName = (type: string) => {
  return questionTypeMap[type] || type
}

const isAudio = (url: string) => {
  const audioExtensions = ['.mp3', '.wav', '.ogg', '.m4a']
  return audioExtensions.some(ext => url.toLowerCase().includes(ext))
}

const loadUnitInfo = async () => {
  loading.value = true
  try {
    unitInfo.value = await getUnitById(unitId.value)
  } catch (error: any) {
    ElMessage.error(error.message || '加载任务信息失败')
  } finally {
    loading.value = false
  }
}

const loadPages = async () => {
  try {
    pages.value = await getPagesByUnit(unitId.value)
    // 默认展开第一页
    if (pages.value.length > 0) {
      activePages.value = [pages.value[0].id]
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载页面内容失败')
  }
}

onMounted(() => {
  loadUnitInfo()
  loadPages()
})
</script>

<style scoped>
.week-task-preview-container {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

.week-task-preview-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.week-task-preview-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
}

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

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

.card-header h2 {
  margin: 0;
  color: #1A202C;
  font-size: 18px;
  font-weight: 600;
}

/* 描述列表样式 */
.modern-descriptions {
  margin-bottom: 24px;
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 10px rgba(140, 124, 240, 0.1) !important;
}

.modern-descriptions :deep(.el-descriptions__label) {
  background: #F0F2F5 !important;
  color: #4A5568 !important;
  font-weight: 500 !important;
  padding: 12px 16px !important;
}

.modern-descriptions :deep(.el-descriptions__content) {
  padding: 12px 16px !important;
  color: #4A5568 !important;
}

/* 分隔线样式 */
.modern-divider {
  margin: 24px 0 !important;
  background: #F0F2F5 !important;
}

/* 页面内容样式 */
.pages-content {
  margin-top: 20px;
}

.pages-content h3 {
  margin-bottom: 16px;
  color: #1A202C;
  font-size: 16px;
  font-weight: 600;
}

/* 折叠面板样式 */
.modern-collapse {
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 10px rgba(140, 124, 240, 0.1) !important;
}

.modern-collapse-item {
  border-radius: 12px !important;
  overflow: hidden !important;
}

.modern-collapse :deep(.el-collapse-item__header) {
  background: #F5F7FA !important;
  color: #4A5568 !important;
  font-weight: 500 !important;
  padding: 16px 20px !important;
  border-bottom: 1px solid #F0F2F5 !important;
  transition: all 0.3s ease !important;
}

.modern-collapse :deep(.el-collapse-item__header:hover) {
  background: #E8E4FF !important;
  color: #8C7CF0 !important;
}

.modern-collapse :deep(.el-collapse-item__content) {
  padding: 20px !important;
  background: #FFFFFF !important;
}

/* 页面信息样式 */
.page-info {
  padding: 16px;
  background-color: #F5F7FA;
  border-radius: 12px;
  margin-bottom: 16px;
}

.page-info p {
  margin: 8px 0;
  color: #4A5568;
  line-height: 1.6;
}

/* 大题样式 */
.main-questions {
  margin-top: 16px;
}

.main-question-item {
  padding: 20px;
  background-color: #FFFFFF;
  border: 1px solid #F0F2F5;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.05);
  transition: all 0.3s ease;
}

.main-question-item:hover {
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.1);
  transform: translateY(-2px);
}

.main-question-item h4 {
  margin: 0 0 16px 0;
  color: #8C7CF0;
  font-size: 16px;
  font-weight: 600;
}

.main-question-content p {
  margin: 8px 0;
  line-height: 1.6;
  color: #4A5568;
}

/* 媒体信息样式 */
.media-info {
  margin: 16px 0;
  padding: 16px;
  background-color: #E8E4FF;
  border-radius: 12px;
  border-left: 4px solid #8C7CF0;
}

.media-player {
  width: 100%;
  max-width: 400px;
  margin-top: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.15);
}

/* 小题样式 */
.sub-questions {
  margin-top: 20px;
  padding: 16px;
  background-color: #F5F7FA;
  border-radius: 12px;
}

.sub-questions h5 {
  margin: 0 0 16px 0;
  color: #4A5568;
  font-size: 14px;
  font-weight: 600;
}

.sub-question-item {
  padding: 16px;
  background-color: #FFFFFF;
  border: 1px solid #F0F2F5;
  border-radius: 12px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(140, 124, 240, 0.05);
}

.sub-question-item p {
  margin: 6px 0;
  color: #4A5568;
}

.answer {
  color: #2E7D32;
  font-weight: 500;
}

.score {
  color: #F57F17;
  font-weight: 500;
}

.tips {
  color: #8B9BB4;
  font-size: 14px;
}

.analysis {
  color: #4A5568;
  font-size: 14px;
}

/* 选项样式 */
.options,
.matching-options,
.corrections {
  margin-top: 12px;
  padding: 12px;
  background-color: #F9F9F9;
  border-radius: 8px;
}

.option-item,
.correction-item {
  padding: 8px 0;
  border-bottom: 1px dashed #F0F2F5;
  color: #4A5568;
}

.option-item:last-child,
.correction-item:last-child {
  border-bottom: none;
}

/* 按钮样式 */
.primary-button {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 12px !important;
  padding: 12px 24px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3) !important;
  transition: all 0.3s ease !important;
}

.primary-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(140, 124, 240, 0.4) !important;
}

.secondary-button {
  background: #FFFFFF !important;
  border: 2px solid #8C7CF0 !important;
  color: #8C7CF0 !important;
  border-radius: 12px !important;
  padding: 12px 24px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.secondary-button:hover {
  background: #E8E4FF !important;
}

/* 按钮组样式 */
.button-group {
  margin-top: 32px;
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #F0F2F5;
}

/* 状态标签样式 */
.status-tag {
  border-radius: 8px !important;
  padding: 4px 12px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  border: none !important;
}

.status-tag.success {
  background: #A8D5BA !important;
  color: #2E7D32 !important;
}

.status-tag.warning {
  background: #FFE082 !important;
  color: #F57F17 !important;
}

.status-tag.error {
  background: #FFB6C1 !important;
  color: #C62828 !important;
}

.status-tag.info {
  background: #C6B9FF !important;
  color: #6B5BCE !important;
}

/* 空状态样式 */
.modern-empty :deep(.el-empty__description) {
  color: #8B9BB4 !important;
  font-size: 14px !important;
}

/* 加载动画样式 */
:deep(.el-loading-spinner) {
  font-size: 16px !important;
  color: #8C7CF0 !important;
}

:deep(.el-loading-spinner .path) {
  stroke: #8C7CF0 !important;
}
</style>
