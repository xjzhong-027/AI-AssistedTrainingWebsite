<template>
  <div class="ai-question-assistant">
    <FloatingButton @click="showWindow = true" />
    <AIQuestionWindow
      v-model:visible="showWindow"
      :material-id="materialId"
      :transcript="transcript"
      :default-question-type="defaultQuestionType"
      @questions-applied="handleQuestionsApplied"
      @fill-form="handleFillForm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FloatingButton from './FloatingButton.vue'
import AIQuestionWindow from './AIQuestionWindow.vue'
import type { GeneratedQuestion } from '@/api/questionGeneration'

interface Props {
  materialId: number
  transcript?: string
  defaultQuestionType?: 'choice' | 'fill-blank' | 'comprehension'
}

const props = withDefaults(defineProps<Props>(), {
  defaultQuestionType: 'choice'
})

const emit = defineEmits<{
  'questions-applied': [questions: GeneratedQuestion[]]
  'fill-form': [questions: GeneratedQuestion[]]
}>()

const showWindow = ref(false)

const handleQuestionsApplied = (questions: GeneratedQuestion[]) => {
  emit('questions-applied', questions)
}

const handleFillForm = (questions: GeneratedQuestion[]) => {
  emit('fill-form', questions)
}
</script>

<style scoped>
.ai-question-assistant {
  position: relative;
}
</style>

