<template>
  <div class="hint-panel duo-animate-slide-up">
    <div class="hint-panel__header">
      <span class="hint-panel__title">
        <el-icon><info-filled /></el-icon>
        理解提示
      </span>
      <DuoBadge :variant="levelVariant" size="small">
        {{ levelLabel }}
      </DuoBadge>
    </div>
    <div class="hint-panel__content">
      {{ hintContent }}
    </div>
    <div v-if="requestTime" class="hint-panel__time">
      <el-icon><clock /></el-icon>
      {{ requestTime }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DuoBadge from '@/components/common/DuoBadge.vue'
import { InfoFilled, Clock } from '@element-plus/icons-vue'

const props = defineProps<{
  hintContent: string
  level: number
  requestTime?: string
}>()

const levelLabel = computed(() => {
  const map: Record<number, string> = { 1: '轻提示', 2: '方向提示', 3: '详细解释' }
  return map[props.level] || `级别${props.level}`
})

const levelVariant = computed(() => {
  const map: Record<number, 'info' | 'warning' | 'success'> = {
    1: 'info',
    2: 'warning',
    3: 'success'
  }
  return map[props.level] || 'info'
})
</script>

<style scoped lang="scss">
@import '@/styles/duolingo-design-system.scss';

.hint-panel {
  margin-top: $duo-spacing-3;
  padding: $duo-spacing-4;
  background: linear-gradient(135deg, $duo-gray-200 0%, $duo-gray-300 100%);
  border-radius: $duo-radius-lg;
  border-left: 4px solid $duo-blue-primary;
  box-shadow: $duo-shadow-sm;

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $duo-spacing-2;
    margin-bottom: $duo-spacing-2;
  }

  &__title {
    display: inline-flex;
    align-items: center;
    gap: $duo-spacing-2;
    font-size: $duo-font-size-sm;
    font-weight: $duo-font-weight-semibold;
    color: $duo-text-secondary;
  }

  &__content {
    font-size: $duo-font-size-base;
    line-height: 1.6;
    color: $duo-text-primary;
    white-space: pre-wrap;
    word-break: break-word;
  }

  &__time {
    margin-top: $duo-spacing-2;
    font-size: $duo-font-size-xs;
    color: $duo-text-tertiary;
    display: flex;
    align-items: center;
    gap: $duo-spacing-1;
  }
}
</style>
