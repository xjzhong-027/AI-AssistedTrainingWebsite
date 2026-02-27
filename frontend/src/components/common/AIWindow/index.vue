<template>
  <div class="ai-window-container">
    <FloatingButton :unread-count="unreadCount" @click="handleButtonClick" />
    <AIWindow
      v-model:visible="windowVisible"
      :practice-id="practiceId"
      :page-id="pageId"
      :sub-question-id="subQuestionId"
      :show-grade-button="showGradeButton"
      :style="windowStyle"
      :on-grade-request="onGradeRequest"
      @window-state-change="handleWindowStateChange"
      @grade-complete="handleGradeComplete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import FloatingButton from './FloatingButton.vue'
import AIWindow from './AIWindow.vue'
import type { GradeResult, WindowState } from './types'

interface Props {
  practiceId?: number
  pageId?: number
  subQuestionId?: number
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
  defaultVisible?: boolean
  autoLoadHistory?: boolean
  showGradeButton?: boolean
  onGradeRequest?: () => Promise<void>
}

const props = withDefaults(defineProps<Props>(), {
  position: 'bottom-right',
  defaultVisible: false,
  autoLoadHistory: false,
  showGradeButton: false
})

const emit = defineEmits<{
  'grade-complete': [result: GradeResult]
  'window-state-change': [state: WindowState]
}>()

const windowVisible = ref(props.defaultVisible)
const unreadCount = ref(0)
const windowState = ref<WindowState>('close')

const handleResize = () => {}
onMounted(() => {
  window.addEventListener('resize', handleResize)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})

const windowStyle = computed(() => ({
  bottom: '100px',
  right: '140px',
  top: 'auto',
  left: 'auto'
}))

const handleButtonClick = () => {
  windowVisible.value = !windowVisible.value
  if (windowVisible.value) {
    windowState.value = 'open'
    unreadCount.value = 0
  }
}

const handleWindowStateChange = (state: WindowState) => {
  windowState.value = state
  if (state === 'close') windowVisible.value = false
  emit('window-state-change', state)
}

const handleGradeComplete = (result: GradeResult) => {
  emit('grade-complete', result)
}

defineExpose({
  open: () => { windowVisible.value = true; windowState.value = 'open' },
  close: () => { windowVisible.value = false; windowState.value = 'close' },
  toggle: () => {
    windowVisible.value = !windowVisible.value
    windowState.value = windowVisible.value ? 'open' : 'close'
  },
  setUnreadCount: (count: number) => { unreadCount.value = count }
})
</script>

<style scoped>
.ai-window-container {
  position: relative;
}
</style>
