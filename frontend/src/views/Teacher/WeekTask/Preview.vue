<template>
  <div class="week-task-preview">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>预览周任务 - {{ unitInfo?.title }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <!-- 任务基本信息 -->
      <el-descriptions v-if="unitInfo" :column="2" border class="unit-info">
        <el-descriptions-item label="任务标题">{{ unitInfo.title }}</el-descriptions-item>
        <el-descriptions-item label="任务类型">
          <el-tag v-if="unitInfo.type === 'task'" type="success">作业</el-tag>
          <el-tag v-else-if="unitInfo.type === 'exam'" type="danger">考试</el-tag>
          <el-tag v-else-if="unitInfo.type === 'practice'" type="warning">练习</el-tag>
          <el-tag v-else type="info">{{ unitInfo.type }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="所属班级">{{ unitInfo.class_name }}</el-descriptions-item>
        <el-descriptions-item label="周次">
          <el-tag v-if="unitInfo.week">第{{ unitInfo.week }}周</el-tag>
          <el-tag v-else type="info">未设置</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag v-if="unitInfo.status === '进行中'" type="success">{{ unitInfo.status }}</el-tag>
          <el-tag v-else-if="unitInfo.status === '未开始'" type="info">{{ unitInfo.status }}</el-tag>
          <el-tag v-else-if="unitInfo.status === '已结束'" type="danger">{{ unitInfo.status }}</el-tag>
          <el-tag v-else type="warning">{{ unitInfo.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="排序">{{ unitInfo.order }}</el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <!-- 页面和题目列表 -->
      <div v-if="pages && pages.length > 0" class="pages-content">
        <h3>任务内容 (共{{ pages.length }}页)</h3>

        <el-collapse v-model="activePages">
          <el-collapse-item
            v-for="(page, pageIdx) in pages"
            :key="page.id"
            :name="page.id"
            :title="`第${page.order + 1}页 (${page.main_questions?.length || 0}道大题)`"
          >
            <div class="page-info">
              <p><strong>页面文本:</strong> {{ page.text }}</p>
              <p v-if="page.limited_time"><strong>时间限制:</strong> {{ page.limited_time }}分钟</p>
              <p><strong>允许修改答案:</strong> {{ page.can_modify ? '是' : '否' }}</p>
            </div>

            <el-divider />

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
                    <audio v-if="mainQ.media_material_url && isAudio(mainQ.media_material_url)" controls>
                      <source :src="mainQ.media_material_url" />
                    </audio>
                    <video v-else-if="mainQ.media_material_url" controls style="max-width: 100%; height: auto;">
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
                          <el-tag :type="option.is_answer ? 'success' : 'info'" size="small">
                            {{ option.option_label }}
                          </el-tag>
                          {{ option.option_content }}
                        </div>
                      </div>

                      <!-- 连线题选项 -->
                      <div v-if="subQ.matchingOptions && subQ.matchingOptions.length > 0" class="matching-options">
                        <p><strong>连线选项:</strong></p>
                        <div v-for="option in subQ.matchingOptions" :key="option.id" class="option-item">
                          <el-tag size="small">{{ option.option_label }}</el-tag>
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
            <el-empty v-else description="该页面暂无题目" />
          </el-collapse-item>
        </el-collapse>
      </div>
      <el-empty v-else description="该任务暂无内容" />

      <div class="button-group">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="handleEdit">编辑任务</el-button>
      </div>
    </el-card>
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
  router.back()
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
.week-task-preview {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.unit-info {
  margin-bottom: 20px;
}

.pages-content {
  margin-top: 20px;
}

.pages-content h3 {
  margin-bottom: 15px;
  color: #333;
}

.page-info {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 15px;
}

.page-info p {
  margin: 8px 0;
}

.main-questions {
  margin-top: 15px;
}

.main-question-item {
  padding: 15px;
  background-color: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 15px;
}

.main-question-item h4 {
  margin: 0 0 15px 0;
  color: #409eff;
}

.main-question-content p {
  margin: 8px 0;
  line-height: 1.6;
}

.media-info {
  margin: 15px 0;
  padding: 10px;
  background-color: #f0f9ff;
  border-radius: 4px;
}

.sub-questions {
  margin-top: 20px;
  padding: 15px;
  background-color: #fafafa;
  border-radius: 4px;
}

.sub-questions h5 {
  margin: 0 0 15px 0;
  color: #606266;
}

.sub-question-item {
  padding: 12px;
  background-color: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 12px;
}

.sub-question-item p {
  margin: 6px 0;
}

.answer {
  color: #67c23a;
  font-weight: 500;
}

.score {
  color: #e6a23c;
}

.tips {
  color: #909399;
  font-size: 14px;
}

.analysis {
  color: #606266;
  font-size: 14px;
}

.options,
.matching-options,
.corrections {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.option-item,
.correction-item {
  padding: 6px 0;
  border-bottom: 1px dashed #e4e7ed;
}

.option-item:last-child,
.correction-item:last-child {
  border-bottom: none;
}

.button-group {
  margin-top: 30px;
  text-align: center;
}
</style>
