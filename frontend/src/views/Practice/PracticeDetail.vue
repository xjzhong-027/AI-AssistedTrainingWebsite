<template>
  <div class="practice-detail-page">
    <el-card v-loading="loading">
      <div class="card-header">
        <h3>{{ practiceTitle }}</h3>
        <el-button @click="goBack">返回结果页</el-button>
      </div>

      <!-- 视频播放区域 -->
      <div v-if="media" class="media-section">
        <MediaPlayer 
          :mediaUrl="media.url" 
          :transcript="media.transcript" 
          :isVideo="media.isVideo" 
        />
      </div>

      <!-- 题目列表区域 -->
      <div class="questions-section">
        <h4>答题详情</h4>
        <div v-if="questions.length > 0">
          <QuestionDetail 
            v-for="question in questions" 
            :key="question.id"
            :question="question"
            :userAnswer="question.userAnswer"
            :correctAnswer="question.correctAnswer"
            :score="question.score"
            :transcript="media?.transcript || ''"
          />
        </div>
        <div v-else class="no-questions">
          <el-empty description="暂无题目数据" />
        </div>
      </div>

      <!-- 推荐学习素材区域 -->
      <div v-if="aiRecommendation" class="recommendation-section">
        <h4>推荐学习素材</h4>
        <AIRecommendation :recommendation="aiRecommendation" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPracticeDetail, getAIRecommendation } from '@/api/practice'
import MediaPlayer from '@/components/practice/MediaPlayer.vue'
import QuestionDetail from '@/components/practice/QuestionDetail.vue'
import AIRecommendation from '@/components/practice/AIRecommendation.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const practiceTitle = ref('')
const media = ref<any>(null)
const questions = ref<any[]>([])
const aiRecommendation = ref<any>(null)

const loadData = async () => {
  const practiceId = Number(route.params.id)
  // 从路由参数中获取pageId
  const pageId = Number(route.params.pageId) || 1
  
  console.log('答题详情参数:', { practiceId, pageId, originalPageId: route.params.pageId })
  
  if (!practiceId || !pageId) {
    ElMessage.error('参数错误')
    router.push('/practice/list')
    return
  }
  
  try {
    // 获取练习详情
    const detailResponse = await getPracticeDetail(practiceId, pageId)
    console.log('练习详情响应:', detailResponse)
    
    practiceTitle.value = detailResponse.practice.title
    
    // 处理媒体数据
    console.log('媒体数据:', detailResponse.media)
    if (detailResponse.media) {
      media.value = {
        id: detailResponse.media.id,
        url: detailResponse.media.url,
        isVideo: detailResponse.media.is_video,
        transcript: detailResponse.media.transcript
      }
      console.log('设置媒体URL:', media.value.url)
    } else {
      media.value = null
      console.log('没有媒体数据')
    }
    
    // 尝试从不同字段获取题目数据
    questions.value = detailResponse.questions || []
    
    // 如果没有questions字段，尝试从graded_answers、scores和answers构建
    if (questions.value.length === 0 && detailResponse.graded_answers && detailResponse.scores && detailResponse.answers) {
      const gradedAnswers = detailResponse.graded_answers
      const scores = detailResponse.scores
      const answers = detailResponse.answers
      
      // 构建题目数据
      for (const [questionId, correctAnswer] of Object.entries(gradedAnswers)) {
        const score = scores[questionId] || 0
        const userAnswer = answers[questionId] || ''
        questions.value.push({
          id: Number(questionId),
          question_text: `题目 ${questionId}`,
          question_type: 'unknown',
          userAnswer: userAnswer,
          correctAnswer: correctAnswer,
          score: score
        })
      }
    }
    
    console.log('题目数据:', questions.value)
    console.log('题目数量:', questions.value.length)
    console.log('练习详情响应完整数据:', detailResponse)
    console.log('页面ID:', pageId)
    console.log('练习ID:', practiceId)
    console.log('练习详情响应的所有键:', Object.keys(detailResponse))
    
    // 获取AI推荐：
    // 只要有练习标题，就生成一份基于标题 +（可选）transcript 的通用推荐，
    // 不再强依赖 media 是否存在。
    if (detailResponse.practice && detailResponse.practice.title) {
      try {
        const recommendationResponse = await getAIRecommendation({
          practice_title: detailResponse.practice.title,
          transcript: detailResponse.media?.transcript || ''
        })
        aiRecommendation.value = recommendationResponse
      } catch (e) {
        console.error('获取AI推荐失败', e)
      }
    }
  } catch (error: any) {
    console.error('加载失败', error)
    console.error('错误详情:', error.response?.data || error.message)
    ElMessage.error(error.response?.data?.error || error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push(`/practice/${route.params.id}/result`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.practice-detail-page {
  padding: 40px;
  background: linear-gradient(135deg, #FAFBFC 0%, #F8F7FF 50%, #F5F3FF 100%);
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.practice-detail-page :deep(.el-card) {
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(140, 124, 240, 0.12);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 0 8px;
}

.card-header h3 {
  margin: 0;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.card-header :deep(.el-button) {
  background: linear-gradient(135deg, #8C7CF0 0%, #A898F0 100%);
  border: none;
  color: white;
  font-weight: 600;
  padding: 12px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.3);
  transition: all 0.3s ease;
}

.card-header :deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(140, 124, 240, 0.4);
}

.media-section {
  margin-bottom: 40px;
}

.media-section :deep(.media-player) {
  background: linear-gradient(135deg, #F8F7FF 0%, #F0EFFF 100%);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.08);
}

.questions-section {
  margin-bottom: 40px;
}

.questions-section h4 {
  margin: 0 0 24px 0;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.3px;
  padding: 0 8px;
}

.questions-section :deep(.question-detail) {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.08);
  border: 1px solid rgba(198, 185, 255, 0.2);
  transition: all 0.3s ease;
}

.questions-section :deep(.question-detail:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.15);
}

.questions-section :deep(.no-questions) {
  background: linear-gradient(135deg, #F8F7FF 0%, #F0EFFF 100%);
  border-radius: 20px;
  padding: 60px 20px;
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.08);
}

.recommendation-section {
  background: linear-gradient(135deg, #F8F7FF 0%, #F0EFFF 100%);
  padding: 32px;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(140, 124, 240, 0.12);
  border: 1px solid rgba(198, 185, 255, 0.3);
}

.recommendation-section h4 {
  margin: 0 0 24px 0;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.recommendation-section :deep(.recommendation) {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.08);
}

.recommendation-section :deep(.recommendation-header h5) {
  background: linear-gradient(135deg, #8C7CF0 0%, #A898F0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 12px 0;
}

.recommendation-section :deep(.recommendation-header p) {
  color: #5A5A7E;
  font-size: 14px;
  line-height: 1.7;
  margin: 0;
}

.recommendation-section :deep(.keyword-tag) {
  background: linear-gradient(135deg, #E8E4FF 0%, #F0EFFF 100%);
  border: 1px solid rgba(198, 185, 255, 0.4);
  color: #8C7CF0;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 10px;
}

.recommendation-section :deep(.material-item) {
  background: linear-gradient(135deg, #F8F7FF 0%, #F0EFFF 100%);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(198, 185, 255, 0.2);
  transition: all 0.3s ease;
}

.recommendation-section :deep(.material-item:hover) {
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.15);
}

.recommendation-section :deep(.material-type) {
  background: linear-gradient(135deg, #8C7CF0 0%, #A898F0 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 12px;
}

.recommendation-section :deep(.material-title) {
  color: #5A5A7E;
  font-weight: 600;
  transition: all 0.3s ease;
}

.recommendation-section :deep(.material-title:hover) {
  color: #8C7CF0;
}
</style>

