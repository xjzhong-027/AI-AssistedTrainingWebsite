<template>
  <div class="practice-take-page">
    <el-card v-loading="loading">
      <div class="card-header">
        <div>
          <h3>{{ practice?.unit_name }}</h3>
          <div class="practice-info">
            <span>当前页面：第 {{ currentPageOrder + 1 }} 页 / 共 {{ totalPages }} 页</span>
            <span v-if="pageRecord?.remaining_time !== undefined">
              剩余时间：
              <el-tag :type="timeLeftType" size="small">
                {{ formatTime(pageRecord.remaining_time) }}
              </el-tag>
            </span>
          </div>
        </div>
        <div>
          <el-button @click="savePage" :loading="saving">保存当前页</el-button>
          <el-button v-if="isLastPage" type="success" @click="handleSubmit" :disabled="submitting">
            提交练习
          </el-button>
          <el-button v-else type="primary" @click="nextPage">下一页</el-button>
        </div>
      </div>

      <div v-if="mainQuestions.length > 0" class="practice-content">
        <div v-for="(mainQuestion, mainIndex) in mainQuestions" :key="mainQuestion.id" class="main-question">
          <div class="main-question-header">
            <h4>{{ mainIndex + 1 }}. {{ mainQuestion.question_text }}</h4>
            <el-tag>{{ getQuestionTypeText(mainQuestion.question_type) }}</el-tag>
          </div>

          <!-- 媒体播放器 -->
          <div v-if="mainQuestion.media_material_id" class="media-player">
            <template v-if="hasMediaUrl(mainQuestion)">
              <video
                v-if="isVideoUrl(mainQuestion)"
                :ref="el => setAudioRef(el, mainQuestion.id)"
                :src="getMediaUrl(mainQuestion)"
                controls
                playsinline
                class="media-element"
                @play="handlePlay(mainQuestion)"
                @pause="handlePause(mainQuestion)"
                @error="onMediaError(mainQuestion.id)"
              ></video>
              <audio
                v-else
                :ref="el => setAudioRef(el, mainQuestion.id)"
                :src="getMediaUrl(mainQuestion)"
                controls
                class="media-element"
                @play="handlePlay(mainQuestion)"
                @pause="handlePause(mainQuestion)"
                @error="onMediaError(mainQuestion.id)"
              ></audio>
              <div class="play-info">
                <span>最多播放次数：{{ mainQuestion.maximum_play || '无限制' }}</span>
                <span>已播放：{{ getPlayCount(mainQuestion.id) }} 次</span>
              </div>
            </template>
            <div v-else class="no-media-tip">
              <span>暂无音频/视频</span>
              <p class="tip-desc">请在「题库管理」中为该素材填写或上传媒体文件地址后即可播放。</p>
            </div>
          </div>

          <!-- 小题列表 -->
          <div v-for="(subQuestion, subIndex) in mainQuestion.sub_questions" :key="subQuestion.id" class="sub-question">
            <div class="sub-question-header">
              <span class="sub-question-number">{{ mainIndex + 1 }}.{{ subIndex + 1 }}</span>
              <span class="sub-question-text">{{ subQuestion.question_text }}</span>
            </div>

            <!-- 答案输入区域 -->
            <div class="answer-input">
              <!-- 选择题 -->
              <el-radio-group
                v-if="subQuestion.question_type === 'choice'"
                v-model="answers[subQuestion.id]"
                @change="onAnswerChange(subQuestion.id)"
              >
                <el-radio
                  v-for="(option, optIndex) in getChoiceOptions(subQuestion)"
                  :key="optIndex"
                  :label="option.value"
                  style="display: block; margin-bottom: 10px"
                >
                  {{ String.fromCharCode(65 + optIndex) }}. {{ option.text }}
                </el-radio>
              </el-radio-group>

              <!-- 匹配题 -->
              <div v-else-if="subQuestion.question_type === 'matching'" class="matching-answer">
                <div
                  v-for="(option, optIndex) in getMatchingOptions(subQuestion)"
                  :key="optIndex"
                  class="matching-item"
                >
                  <span>{{ option.left }}</span>
                  <el-select v-model="answers[subQuestion.id + '_' + optIndex]" placeholder="请选择" style="width: 200px">
                    <el-option
                      v-for="(rightOption, rightIndex) in getMatchingRightOptions(subQuestion)"
                      :key="rightIndex"
                      :label="rightOption"
                      :value="rightIndex"
                    ></el-option>
                  </el-select>
                </div>
              </div>

              <!-- 填空题 -->
              <div v-else-if="subQuestion.question_type === 'blank'" class="blank-answer">
                <div
                  v-for="(blank, blankIndex) in getBlankCount(subQuestion)"
                  :key="blankIndex"
                  class="blank-item"
                >
                  <span>空{{ blankIndex + 1 }}：</span>
                  <el-input
                    v-model="answers[subQuestion.id + '_' + blankIndex]"
                    placeholder="请输入答案"
                    style="width: 300px"
                    @input="onAnswerChange(subQuestion.id)"
                  ></el-input>
                </div>
              </div>

              <!-- 理解导向提示：选择题、填空题可请求分级提示 -->
              <div v-if="canShowHint(subQuestion)" class="hint-section">
                <div class="hint-actions">
                  <span class="hint-label">需要提示？</span>
                  <el-button size="small" :loading="hintLoading[subQuestion.id]" @click="requestHint(subQuestion, 1)">轻提示</el-button>
                  <el-button size="small" :loading="hintLoading[subQuestion.id]" @click="requestHint(subQuestion, 2)">方向提示</el-button>
                  <el-button size="small" type="primary" :loading="hintLoading[subQuestion.id]" @click="requestHint(subQuestion, 3)">详细解释</el-button>
                </div>
                <HintPanel
                  v-if="hintResults[subQuestion.id]"
                  :hint-content="hintResults[subQuestion.id].content"
                  :level="hintResults[subQuestion.id].level"
                  :request-time="hintResults[subQuestion.id].request_time"
                />
              </div>

              <!-- 改错题 -->
              <div v-else-if="subQuestion.question_type === 'correction'" class="correction-answer">
                <div
                  v-for="(correction, corrIndex) in getCorrectionData(subQuestion)"
                  :key="corrIndex"
                  class="correction-item"
                >
                  <span>错误{{ corrIndex + 1 }}：</span>
                  <el-input
                    v-model="answers[subQuestion.id + '_' + corrIndex]"
                    placeholder="请输入改正后的内容"
                    style="width: 300px"
                    @input="onAnswerChange(subQuestion.id)"
                  ></el-input>
                </div>
              </div>

              <!-- 简答题/理解题 -->
              <div v-else>
                <el-input
                  v-model="answers[subQuestion.id]"
                  type="textarea"
                  :rows="6"
                  placeholder="请输入您的答案"
                  maxlength="2000"
                  show-word-limit
                  @input="onAnswerChange(subQuestion.id)"
                ></el-input>

                <!-- AI评分按钮 -->
                <div class="ai-scoring-section" style="margin-top: 15px;">
                  <el-button
                    type="primary"
                    size="small"
                    :loading="aiScoring[subQuestion.id]"
                    @click="requestAIScoring(subQuestion)"
                  >
                    {{ aiScoring[subQuestion.id] ? 'AI评分中...' : '请求AI评分' }}
                  </el-button>
                </div>

                <!-- AI评分结果 -->
                <div v-if="scoringResults[subQuestion.id]" class="ai-feedback" style="margin-top: 15px;">
                  <el-alert
                    :type="scoringResults[subQuestion.id].score >= 60 ? 'success' : 'warning'"
                    :closable="false"
                  >
                    <template #title>
                      <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>AI评分结果</span>
                        <el-tag :type="scoringResults[subQuestion.id].score >= 60 ? 'success' : 'warning'">
                          得分: {{ scoringResults[subQuestion.id].score }}
                        </el-tag>
                      </div>
                    </template>
                    <div style="margin-top: 10px;">
                      <p><strong>反馈:</strong> {{ scoringResults[subQuestion.id].feedback }}</p>
                      <p v-if="scoringResults[subQuestion.id].suggestions">
                        <strong>建议:</strong> {{ scoringResults[subQuestion.id].suggestions }}
                      </p>
                    </div>
                  </el-alert>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <el-empty description="该页面暂无题目"></el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { startExam, getExamPage, saveAnswers, submitExam, getExamResult, updateMediaPlayRecord } from '@/api/exam'
import { getUnitById, getPagesByUnit, getPageQuestions } from '@/api/content'
import { startPractice } from '@/api/practice'
import { useUserStore } from '@/stores/user'
import { scoringApi } from '@/api/scoring'
import { hintsApi } from '@/api/hints'
import HintPanel from '@/components/common/HintPanel.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const saving = ref(false)
const submitting = ref(false)

const practice = ref<any>(null)
const pages = ref<any[]>([])
const currentPageOrder = ref(0)
const currentPage = ref<any>(null)
const pageRecord = ref<any>(null)
const mainQuestions = ref<any[]>([])
const answers = ref<Record<number | string, any>>({})
const audioRefs = ref<Record<number, HTMLAudioElement>>({})
const playCounts = ref<Record<number, number>>({})
const pauseTimes = ref<Record<number, number>>({})
const practiceRecordId = ref<number | null>(null)

// AI评分相关状态
const aiScoring = ref<Record<number, boolean>>({})
const scoringResults = ref<Record<number, any>>({})

// AI 提示相关（选择/填空）
const hintLoading = ref<Record<number, boolean>>({})
const hintResults = ref<Record<number, { content: string; level: number; request_time: string }>>({})

const totalPages = computed(() => pages.value.length)
const isLastPage = computed(() => currentPageOrder.value === totalPages.value - 1)

// 设置音频引用
const setAudioRef = (el: any, questionId: number) => {
  if (el) {
    audioRefs.value[questionId] = el
  }
}

// 获取媒体URL
const getMediaUrl = (mainQuestion: any): string => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  
  // 优先使用media_material的media_url字段
  if (mainQuestion.media_material_url) {
    // 如果是完整URL，直接返回
    if (mainQuestion.media_material_url.startsWith('http')) {
      return mainQuestion.media_material_url
    }
    
    // 如果已经包含 /media_material/，直接添加后端地址（避免重复）
    if (mainQuestion.media_material_url.includes('/media_material/')) {
      // 如果已经是完整路径，直接使用
      if (mainQuestion.media_material_url.startsWith('/media_material/')) {
        return `${apiBaseUrl}${mainQuestion.media_material_url}`
      }
      // 如果包含但不在开头，提取正确的路径
      const match = mainQuestion.media_material_url.match(/\/media_material\/.*$/)
      if (match) {
        return `${apiBaseUrl}${match[0]}`
      }
    }
    
    // 如果是以 media/ 开头（相对路径），需要添加 /media_material/ 前缀
    if (mainQuestion.media_material_url.startsWith('media/')) {
      return `${apiBaseUrl}/media_material/${mainQuestion.media_material_url}`
    }
    
    // 如果是其他相对路径（如 /xxx.mp3），添加 /media_material/media/ 前缀
    if (mainQuestion.media_material_url.startsWith('/')) {
      // 检查是否已经包含 media_material
      if (!mainQuestion.media_material_url.includes('media_material')) {
        return `${apiBaseUrl}/media_material/media${mainQuestion.media_material_url}`
      } else {
        return `${apiBaseUrl}${mainQuestion.media_material_url}`
      }
    }
    
    // 如果是文件名（如 xxx.mp3），添加完整路径
    return `${apiBaseUrl}/media_material/media/${mainQuestion.media_material_url}`
  }
  
  // 如果没有media_url，尝试使用API路径
  if (mainQuestion.media_material_id) {
    return `${apiBaseUrl}/api/v1/content/media-materials/${mainQuestion.media_material_id}/media/`
  }
  
  return ''
}

/** 是否有可用的媒体地址（仅当已填写 media_url 时显示播放器，否则显示提示） */
const hasMediaUrl = (mainQuestion: any): boolean => {
  return !!(mainQuestion.media_material_url && String(mainQuestion.media_material_url).trim())
}

/** 是否为视频（按扩展名），视频用 <video> 显示画面，否则用 <audio> */
const isVideoUrl = (mainQuestion: any): boolean => {
  const url = mainQuestion.media_material_url || ''
  const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']
  return videoExtensions.some(ext => String(url).toLowerCase().includes(ext))
}

const onMediaError = (_questionId: number) => {
  ElMessage.warning('媒体加载失败，请确认该素材已上传或填写正确的媒体文件地址')
}

// 获取播放次数
const getPlayCount = (questionId: number): number => {
  return playCounts.value[questionId] || 0
}

// 处理播放
const handlePlay = async (mainQuestion: any) => {
  if (!practiceRecordId.value || !mainQuestion.id) return
  
  try {
    const count = (playCounts.value[mainQuestion.id] || 0) + 1
    playCounts.value[mainQuestion.id] = count
    
    // 检查是否超过最大播放次数
    if (mainQuestion.maximum_play && count > mainQuestion.maximum_play) {
      ElMessage.warning(`已达到最大播放次数（${mainQuestion.maximum_play}次）`)
      const audio = audioRefs.value[mainQuestion.id]
      if (audio) {
        audio.pause()
      }
      return
    }
    
    // 更新播放记录API
    await updateMediaPlayRecord(practiceRecordId.value, {
      main_question_id: mainQuestion.id,
      media_material_id: mainQuestion.media_material_id,
      play_count: count,
      last_pause_time: pauseTimes.value[mainQuestion.id] || 0
    })
  } catch (error: any) {
    console.error('更新播放记录失败', error)
  }
}

// 处理暂停
const handlePause = async (mainQuestion: any) => {
  if (!practiceRecordId.value || !mainQuestion.id) return
  
  try {
    const audio = audioRefs.value[mainQuestion.id]
    if (audio) {
      const currentTime = audio.currentTime
      pauseTimes.value[mainQuestion.id] = currentTime
      
      // 更新暂停时间API
      await updateMediaPlayRecord(practiceRecordId.value, {
        main_question_id: mainQuestion.id,
        media_material_id: mainQuestion.media_material_id,
        play_count: playCounts.value[mainQuestion.id] || 0,
        last_pause_time: currentTime
      })
    }
  } catch (error: any) {
    console.error('更新暂停时间失败', error)
  }
}

// 获取题目类型文本
const getQuestionTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    choice: '选择题',
    matching: '匹配题',
    blank: '填空题',
    correction: '改错题',
    comprehension: '理解题',
    text: '文本题'
  }
  return typeMap[type] || type
}

// 获取选择题选项
const getChoiceOptions = (subQuestion: any): Array<{ value: string; text: string }> => {
  if (!subQuestion.options) return []
  
  // 如果options是数组（后端返回的对象数组）
  if (Array.isArray(subQuestion.options)) {
    return subQuestion.options.map((opt: any, index: number) => ({
      value: opt.option_label || String.fromCharCode(65 + index),
      text: opt.option_content || opt.option_label || ''
    }))
  }
  
  // 如果options是字符串（JSON格式）
  try {
    const options = typeof subQuestion.options === 'string' 
      ? JSON.parse(subQuestion.options) 
      : subQuestion.options
    if (Array.isArray(options)) {
      return options.map((opt: any, index: number) => {
        if (typeof opt === 'string') {
          return {
            value: String.fromCharCode(65 + index),
            text: opt
          }
        } else {
          return {
            value: opt.option_label || String.fromCharCode(65 + index),
            text: opt.option_content || opt.option_label || ''
          }
        }
      })
    }
  } catch {
    return []
  }
  
  return []
}

// 获取匹配题选项
const getMatchingOptions = (subQuestion: any): Array<{ left: string }> => {
  if (!subQuestion.options) return []
  try {
    const options = JSON.parse(subQuestion.options)
    return options.map((opt: string) => ({ left: opt }))
  } catch {
    return []
  }
}

const getMatchingRightOptions = (subQuestion: any): string[] => {
  // 从subQuestion.matchingOptions中获取右侧选项
  if (!subQuestion.matchingOptions || !Array.isArray(subQuestion.matchingOptions)) {
    return []
  }
  
  return subQuestion.matchingOptions.map((opt: any) => {
    if (typeof opt === 'string') {
      return opt
    }
    return opt.option_content || opt.option_label || ''
  }).filter((opt: string) => opt)
}

// 获取填空题数量
const getBlankCount = (subQuestion: any): number[] => {
  // 从subQuestion.blanks中获取空白数量
  if (subQuestion.blanks && Array.isArray(subQuestion.blanks)) {
    return subQuestion.blanks.map((blank: any, index: number) => index)
  }
  
  // 如果没有blanks字段，尝试从question_text中解析空白数量
  if (subQuestion.question_text) {
    const blankMatches = subQuestion.question_text.match(/_{2,}/g)
    if (blankMatches) {
      return blankMatches.map((_: any, index: number) => index)
    }
    
    const bracketMatches = subQuestion.question_text.match(/[\(（]\s*[\)）]/g)
    if (bracketMatches) {
      return bracketMatches.map((_: any, index: number) => index)
    }
  }
  
  return [0]
}

// 是否显示提示入口（选择题、填空题）
const canShowHint = (subQuestion: any): boolean => {
  const t = subQuestion?.question_type
  return t === 'choice' || t === 'blank'
}

// 请求分级提示（后端会自动从题目关联的媒体素材带出 transcript）
const requestHint = async (subQuestion: any, level: 1 | 2 | 3) => {
  hintLoading.value[subQuestion.id] = true
  try {
    const mainQ = mainQuestions.value.find((mq: any) => mq.sub_questions?.some((sq: any) => sq.id === subQuestion.id))
    const transcript = mainQ?.media_material?.transcript ?? ''
    const res = await hintsApi.request({
      sub_question_id: subQuestion.id,
      level,
      transcript,
      context: { page_id: pageRecord.value?.id }
    })
    hintResults.value[subQuestion.id] = {
      content: res.content,
      level: res.level,
      request_time: res.request_time
    }
    if (res.message) ElMessage.info(res.message)
    else ElMessage.success('已获取提示')
  } catch (e: any) {
    ElMessage.error(e?.message || '获取提示失败')
  } finally {
    hintLoading.value[subQuestion.id] = false
  }
}

// 获取改错题数据
const getCorrectionData = (subQuestion: any): number[] => {
  // 从subQuestion.corrections中获取错误数量
  if (subQuestion.corrections && Array.isArray(subQuestion.corrections)) {
    return subQuestion.corrections.map((correction: any, index: number) => index)
  }
  
  // 如果没有corrections字段，尝试从question_text中解析错误数量
  if (subQuestion.question_text) {
    const errorMatches = subQuestion.question_text.match(/错误\s*\d+/g)
    if (errorMatches) {
      return errorMatches.map((_: any, index: number) => index)
    }
  }
  
  return [0]
}

// 格式化时间
const formatTime = (seconds: number): string => {
  if (seconds <= 0) return '00:00:00'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

const timeLeftType = computed(() => {
  if (!pageRecord.value?.remaining_time) return 'info'
  const time = pageRecord.value.remaining_time
  if (time <= 300) return 'danger' // 5分钟
  if (time <= 600) return 'warning' // 10分钟
  return 'success'
})

// 答案变化
const onAnswerChange = (subQuestionId: number) => {
  // 自动保存逻辑可以在这里实现
}

// AI评分功能
const requestAIScoring = async (subQuestion: any) => {
  const studentAnswer = answers.value[subQuestion.id]
  if (!studentAnswer || !studentAnswer.trim()) {
    ElMessage.warning('请先输入答案')
    return
  }

  aiScoring.value[subQuestion.id] = true
  try {
    const mainQuestion = mainQuestions.value.find(mq =>
      mq.sub_questions.some((sq: any) => sq.id === subQuestion.id)
    )

    const response = await scoringApi.subjective({
      sub_question_id: subQuestion.id,
      student_answer: studentAnswer,
      transcript: mainQuestion?.media_material?.transcript || ''
    })

    scoringResults.value[subQuestion.id] = response.data.data
    ElMessage.success('AI评分完成')
  } catch (error: any) {
    console.error('AI评分失败', error)
    ElMessage.error(error.message || 'AI评分失败')
  } finally {
    aiScoring.value[subQuestion.id] = false
  }
}

// 保存当前页
const savePage = async () => {
  if (!pageRecord.value) return

  saving.value = true
  try {
    const answerList: Array<{ sub_question_id: number; text: string }> = []
    const processedSubQuestions = new Set<number>()

    // 处理匹配题、填空题、改错题的复合答案
    for (const [key, value] of Object.entries(answers.value)) {
      const parts = key.split('_')
      const subQuestionId = parseInt(parts[0])
      if (isNaN(subQuestionId)) continue

      // 如果是复合答案（匹配题、填空题、改错题）
      if (parts.length > 1) {
        if (!processedSubQuestions.has(subQuestionId)) {
          const answerParts: string[] = []
          let index = 0
          while (answers.value[`${subQuestionId}_${index}`] !== undefined) {
            const partValue = answers.value[`${subQuestionId}_${index}`]
            answerParts.push(String(partValue || ''))
            index++
          }
          
          if (answerParts.length > 0) {
            answerList.push({
              sub_question_id: subQuestionId,
              text: answerParts.join('_')
            })
            processedSubQuestions.add(subQuestionId)
          }
        }
      } else {
        // 普通答案（选择题、简答题等）
        if (!processedSubQuestions.has(subQuestionId)) {
          let answerText = ''
          if (Array.isArray(value)) {
            answerText = value.join(',')
          } else if (typeof value === 'object') {
            answerText = JSON.stringify(value)
          } else {
            answerText = String(value || '')
          }

          answerList.push({
            sub_question_id: subQuestionId,
            text: answerText
          })
          processedSubQuestions.add(subQuestionId)
        }
      }
    }

    await saveAnswers(pageRecord.value.id, answerList)
    ElMessage.success('答案已保存')
  } catch (error: any) {
    console.error('保存失败', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 下一页
const nextPage = async () => {
  // 先保存当前页
  await savePage()

  if (currentPageOrder.value < totalPages.value - 1) {
    currentPageOrder.value++
    await loadPage()
  }
}

// 提交练习
const handleSubmit = async () => {
  if (!pageRecord.value) return

  try {
    await ElMessageBox.confirm('确定要提交吗？提交后将无法修改答案，并立即显示得分与正确答案。', '提交确认', {
      confirmButtonText: '确定提交',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 先保存当前页
    await savePage()

    submitting.value = true
    const practiceId = Number(route.params.id)
    // 提交接口需要传 unit_id（任务包 ID），不是 exam_record_id
    await submitExam(practiceId)
    
    ElMessage.success('练习提交成功')
    router.push(`/practice/${practiceId}/result`)
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('提交失败', error)
      ElMessage.error(error.message || '提交失败')
    }
  } finally {
    submitting.value = false
  }
}

// 加载页面
const loadPage = async () => {
  const practiceId = Number(route.params.id)
  if (!practiceId || !userStore.userInfo?.id) {
    router.push('/practice/list')
    return
  }

  loading.value = true
  try {
    // 已提交则直接进入结果页，不可再作答
    try {
      const res = await getExamResult(practiceId)
      if (res && res.submitted) {
        router.replace(`/practice/${practiceId}/result`)
        return
      }
    } catch {
      // 无记录或未提交，继续答题流程
    }

    // 获取单元信息
    practice.value = await getUnitById(practiceId)
    if (!practice.value) {
      ElMessage.error('练习不存在')
      router.push('/practice/list')
      return
    }

    // 获取所有页面
    pages.value = await getPagesByUnit(practiceId)
    if (pages.value.length === 0) {
      ElMessage.error('该练习暂无页面')
      router.push('/practice/list')
      return
    }

    // 获取当前页面
    currentPage.value = pages.value[currentPageOrder.value]
    if (!currentPage.value) {
      ElMessage.error('页面不存在')
      router.push('/practice/list')
      return
    }

    // 获取页面记录（使用考试API，因为练习和考试使用相同的流程）
    const practiceRecord = await startExam(practiceId)
    practiceRecordId.value = practiceRecord.id || practiceRecord.exam_record_id || null
    pageRecord.value = await getExamPage(practiceId, currentPage.value.order)
    
    // 加载播放记录
    if (practiceRecordId.value && pageRecord.value?.play_records) {
      for (const playRecord of pageRecord.value.play_records) {
        if (playRecord.main_question_id) {
          playCounts.value[playRecord.main_question_id] = playRecord.play_count || 0
          pauseTimes.value[playRecord.main_question_id] = playRecord.last_pause_time || 0
        }
      }
    }

    // 获取页面题目
    mainQuestions.value = await getPageQuestions(currentPage.value.id)

    // 加载已有答案
    if (pageRecord.value.answers) {
      for (const answer of pageRecord.value.answers) {
        // 处理匹配题、填空题、改错题的复合答案
        if (answer.text && answer.text.includes('_')) {
          const parts = answer.text.split('_')
          if (parts.length > 1) {
            parts.forEach((part: string, index: number) => {
              answers.value[`${answer.sub_question_id}_${index}`] = part
            })
          } else {
            answers.value[answer.sub_question_id] = answer.text
          }
        } else {
          answers.value[answer.sub_question_id] = answer.text
        }
      }
    }
  } catch (error: any) {
    console.error('加载失败', error)
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPage()
})

// 页面卸载前保存
onBeforeUnmount(() => {
  savePage()
})
</script>

<style scoped>
.practice-take-page {
  padding: 20px;
  background-color: #F9F8F3;
  min-height: 100vh;
}

/* 卡片样式 - 符合UI设计规范 */
:deep(.el-card) {
  background-color: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.5s ease-out;
}

:deep(.el-card)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #99B6B4, #BACFCE, #D48982, #DFB199);
  z-index: 1;
}

:deep(.el-card__body) {
  padding: 30px;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(186, 207, 206, 0.2);
}

.card-header h3 {
  margin: 0 0 10px 0;
  color: #1A1A1A;
  font-size: 20px;
  font-weight: 500;
}

.practice-info {
  display: flex;
  gap: 20px;
  align-items: center;
  font-size: 14px;
  color: #606266;
}

.practice-content {
  margin-top: 20px;
}

.main-question {
  margin-bottom: 40px;
  padding: 20px;
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  position: relative;
}

.main-question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(186, 207, 206, 0.2);
}

.main-question-header h4 {
  margin: 0;
  flex: 1;
  color: #1A1A1A;
  font-size: 18px;
  font-weight: 500;
}

.media-player {
  margin: 20px 0;
  padding: 20px;
  background: #F9F8F3;
  border-radius: 12px;
  border: 1px solid rgba(186, 207, 206, 0.2);
}

.media-element {
  display: block;
  max-width: 100%;
}
.media-element video {
  width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.play-info {
  display: flex;
  gap: 20px;
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.no-media-tip {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  color: #909399;
  font-size: 14px;
}

.no-media-tip .tip-desc {
  margin: 8px 0 0;
  font-size: 12px;
  color: #c0c4cc;
}

.sub-question {
  margin: 20px 0;
  padding: 20px;
  background: #F9F8F3;
  border-radius: 12px;
  border: 1px solid rgba(186, 207, 206, 0.1);
}

.sub-question-header {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  font-weight: 500;
  color: #1A1A1A;
}

.sub-question-number {
  color: #99B6B4;
  font-weight: bold;
  font-size: 16px;
}

.sub-question-text {
  color: #1A1A1A;
  font-size: 15px;
}

.answer-input {
  margin-top: 15px;
}

.matching-answer,
.blank-answer,
.correction-answer {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.matching-item,
.blank-item,
.correction-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
  background: #FFFFFF;
  border-radius: 8px;
  border: 1px solid rgba(186, 207, 206, 0.2);
}

.matching-item span,
.blank-item span,
.correction-item span {
  color: #1A1A1A;
  font-weight: 500;
  min-width: 60px;
}

/* 理解导向提示区域 */
.hint-section {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(186, 207, 206, 0.3);
}
.hint-section .hint-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
}
.hint-section .hint-label {
  font-size: 14px;
  color: #666;
  margin-right: 8px;
}

/* 按钮样式优化 */
:deep(.el-button) {
  border-radius: 6px;
  transition: all 0.3s ease;
}

:deep(.el-button--primary) {
  background-color: #99B6B4;
  border-color: #99B6B4;
}

:deep(.el-button--primary:hover) {
  background-color: #7A9E9C;
  border-color: #7A9E9C;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-button--success) {
  background-color: #99B6B4;
  border-color: #99B6B4;
}

:deep(.el-button--success:hover) {
  background-color: #7A9E9C;
  border-color: #7A9E9C;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-tag) {
  border-radius: 6px;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

/* AI评分样式 */
.ai-scoring-section {
  display: flex;
  gap: 10px;
  align-items: center;
}

.ai-feedback {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ai-feedback :deep(.el-alert) {
  border-radius: 12px;
  border-left: 4px solid #99B6B4;
}

.ai-feedback :deep(.el-alert--success) {
  background-color: rgba(153, 182, 180, 0.1);
  border-left-color: #99B6B4;
}

.ai-feedback :deep(.el-alert--warning) {
  background-color: rgba(223, 177, 153, 0.1);
  border-left-color: #DFB199;
}

.ai-feedback p {
  margin: 8px 0;
  line-height: 1.6;
  color: #1A1A1A;
}

.ai-feedback strong {
  color: #99B6B4;
  font-weight: 600;
}
</style>

