<template>
  <div
    :class="[
      'duo-card',
      `duo-card--${variant}`,
      {
        'duo-card--hoverable': hoverable,
        'duo-card--clickable': clickable
      }
    ]"
    @click="handleClick"
  >
    <!-- 卡片头部 -->
    <div v-if="$slots.header || title" class="duo-card__header">
      <slot name="header">
        <h3 class="duo-card__title">{{ title }}</h3>
        <p v-if="subtitle" class="duo-card__subtitle">{{ subtitle }}</p>
      </slot>
    </div>

    <!-- 卡片内容 -->
    <div class="duo-card__body">
      <slot></slot>
    </div>

    <!-- 卡片底部 -->
    <div v-if="$slots.footer" class="duo-card__footer">
      <slot name="footer"></slot>
    </div>

    <!-- 角标 -->
    <div v-if="badge" class="duo-card__badge" :class="`duo-card__badge--${badgeType}`">
      {{ badge }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  subtitle?: string
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
  hoverable?: boolean
  clickable?: boolean
  badge?: string | number
  badgeType?: 'success' | 'warning' | 'danger' | 'info'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  hoverable: false,
  clickable: false,
  badgeType: 'success'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
@use '@/styles/duolingo-design-system.scss' as *;

.duo-card {
  @include duo-card-base;
  position: relative;

  // 头部
  &__header {
    margin-bottom: $duo-spacing-4;
  }

  &__title {
    font-size: $duo-font-size-xl;
    font-weight: $duo-font-weight-bold;
    color: $duo-text-primary;
    margin: 0;
  }

  &__subtitle {
    font-size: $duo-font-size-sm;
    color: $duo-text-secondary;
    margin: $duo-spacing-1 0 0;
  }

  // 内容
  &__body {
    color: $duo-text-primary;
  }

  // 底部
  &__footer {
    margin-top: $duo-spacing-4;
    padding-top: $duo-spacing-4;
    border-top: 2px solid $duo-gray-400;
  }

  // 角标
  &__badge {
    position: absolute;
    top: -8px;
    right: -8px;
    padding: $duo-spacing-1 $duo-spacing-3;
    font-size: $duo-font-size-xs;
    font-weight: $duo-font-weight-bold;
    color: $duo-text-inverse;
    border-radius: $duo-radius-full;
    box-shadow: $duo-shadow-base;

    &--success {
      background: $duo-green-primary;
    }

    &--warning {
      background: $duo-yellow-primary;
      color: $duo-text-primary;
    }

    &--danger {
      background: $duo-red-primary;
    }

    &--info {
      background: $duo-blue-primary;
    }
  }

  // 变体样式
  &--success {
    border: 3px solid $duo-green-primary;
    background: linear-gradient(135deg, $duo-green-lighter 0%, $duo-bg-primary 100%);
  }

  &--warning {
    border: 3px solid $duo-yellow-primary;
    background: linear-gradient(135deg, $duo-yellow-lighter 0%, $duo-bg-primary 100%);
  }

  &--danger {
    border: 3px solid $duo-red-primary;
    background: linear-gradient(135deg, $duo-red-lighter 0%, $duo-bg-primary 100%);
  }

  &--info {
    border: 3px solid $duo-blue-primary;
    background: linear-gradient(135deg, $duo-blue-lighter 0%, $duo-bg-primary 100%);
  }

  // 可悬停
  &--hoverable {
    cursor: pointer;
    transition: all $duo-duration-base $duo-ease-out;

    &:hover {
      transform: translateY(-4px);
      box-shadow: $duo-shadow-lg;
    }
  }

  // 可点击
  &--clickable {
    cursor: pointer;

    &:active {
      transform: scale(0.98);
    }
  }
}
</style>
